#!/usr/bin/env python3
"""gerar.py — geracao paga com portao de custo, download e log.

Duas etapas de proposito: --estimar mostra a cotacao sem gastar nada, e a
chamada real so acontece com --confirmar. A aprovacao fica explicita no comando
em vez de depender da memoria de quem esta conduzindo.

Regra de ouro do livro-caixa: assim que o provider aceita o job, o gasto e
lancado — mesmo que tudo de errado dali para frente. Dinheiro gasto que nao
aparece no saldo e pior do que nao ter saldo nenhum.

  # cotar (nao gasta)
  python3 gerar.py --rota fal --model <id> --prompt "..." \
      --projeto capa --desc hero --custo 0.04 --estimar

  # rodar
  python3 gerar.py ... --confirmar
  python3 gerar.py ... --async --confirmar      # video / job assincrono
"""
import argparse, base64, json, os, re, sys, time, uuid, urllib.error, urllib.request
from datetime import datetime, timezone

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PADRAO = {"pasta": "~/generations", "teto_mensal_usd": 50}
EXT = {"image/png": ".png", "image/jpeg": ".jpg", "video/mp4": ".mp4"}
ESTADO_OK = {"success", "succeeded", "completed", "complete", "finished", "done", "ok"}
ESTADO_ERRO = {"fail", "failed", "error", "cancelled", "canceled"}

PASTA = None   # definidos em main()
RUN_ID = None


# ---------------------------------------------------------------- config/env
def config():
    p = os.path.join(AQUI, "_config.json")
    if not os.path.exists(p):
        with open(p, "w") as f:
            json.dump(CONFIG_PADRAO, f, indent=2)
        print(f"[setup] criei {p} com os valores padrao. Ajuste 'pasta' e "
              f"'teto_mensal_usd' antes de continuar (ver references/setup.md).",
              file=sys.stderr)
    with open(p) as f:
        c = json.load(f)
    c["pasta"] = os.path.expanduser(c.get("pasta", CONFIG_PADRAO["pasta"]))
    return c


def env(nome):
    """Le do ambiente ou do .env da pasta de trabalho. Nunca imprime o valor."""
    if os.environ.get(nome):
        return os.environ[nome]
    for base in (os.getcwd(), AQUI, os.path.expanduser("~")):
        p = os.path.join(base, ".env")
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for linha in f:
                linha = linha.strip()
                if linha.startswith(f"{nome}="):
                    return linha.split("=", 1)[1].strip().strip('"\'')
    sys.exit(f"chave {nome} nao encontrada. Coloque-a num .env na pasta de "
             f"trabalho (ver references/setup.md). Nao cole a chave no comando.")


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


# ---------------------------------------------------------------- livro-caixa
def gasto_do_mes(pasta):
    """Soma do mes corrente. Linhas com o mesmo run_id contam uma vez so
    (a ultima vence), porque um run e lancado ao submeter e reescrito ao
    concluir."""
    led = os.path.join(pasta, "_ledger.jsonl")
    if not os.path.exists(led):
        return 0.0
    mes = datetime.now(timezone.utc).strftime("%Y-%m")
    por_run, solto = {}, 0.0
    with open(led) as f:
        for linha in f:
            try:
                e = json.loads(linha)
            except json.JSONDecodeError:
                continue
            if not (e.get("created") or "").startswith(mes):
                continue
            c = float(e.get("cost_usd") or 0)
            if e.get("run_id"):
                por_run[e["run_id"]] = c
            else:
                solto += c
    return solto + sum(por_run.values())


def lancar(log, status, arquivo=None):
    """Grava (ou regrava) a linha deste run no livro-caixa. Chamado assim que o
    provider aceita o job e de novo quando o arquivo chega."""
    e = {"run_id": RUN_ID, "status": status, "file": arquivo, **log}
    with open(os.path.join(PASTA, "_ledger.jsonl"), "a") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")


def morrer(msg, log=None, status="incompleto"):
    """Sai com erro sem perder o lancamento do que ja foi cobrado."""
    if log is not None:
        lancar(log, status)
        msg += (f"\n[livro-caixa] gasto de ${log['cost_usd']:.2f} lancado como "
                f"'{status}' (run {RUN_ID}) — o provider ja cobrou.")
    sys.exit(msg)


# ---------------------------------------------------------------- HTTP
def post(url, corpo, headers, timeout=600):
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(),
                                 headers={"content-type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        corpo_erro = e.read().decode(errors="replace")[:600]
        # Erro HTTP aqui = job recusado = nada cobrado. Nao lanca no livro-caixa.
        if e.code in (401, 403):
            sys.exit(f"AUTENTICACAO recusada ({e.code}). Confira a palavra do "
                     f"cabecalho: fal usa 'Key', Kie usa 'Bearer'. Resposta: {corpo_erro}")
        if e.code == 404:
            sys.exit(f"MODELO NAO ENCONTRADO ({e.code}). O ID envelheceu: abra a "
                     f"pagina do modelo, copie o ID novo e atualize a receita. {corpo_erro}")
        sys.exit(f"ERRO HTTP {e.code} (nada cobrado): {corpo_erro}")
    except Exception as e:
        sys.exit(f"ERRO de rede (provavelmente nada cobrado): {e}")


def get(url, headers, timeout=60):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def achar_saida(j):
    """Acha a midia na resposta sem depender do formato exato do provider.
    Devolve ('url', str), ('b64', str) ou (None, None). URL tem preferencia:
    quando os dois existem, a URL e o arquivo completo."""
    urls, b64s = [], []

    def anda(v):
        if isinstance(v, str):
            if re.match(r"^https?://", v) and re.search(
                    r"\.(png|jpe?g|webp|mp4|mov|webm)(\?|$)", v, re.I):
                urls.append(v)
            elif v.startswith("data:") and "," in v:
                b64s.append(v.split(",", 1)[1])
            elif len(v) > 2000 and re.fullmatch(r"[A-Za-z0-9+/=\s]+", v[:400] or ""):
                b64s.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                anda(x)
        elif isinstance(v, list):
            for x in v:
                anda(x)

    anda(j)
    if urls:
        return "url", urls[0]
    if b64s:
        return "b64", b64s[0]
    return None, None


def achar_task_id(j):
    """Procura o id do job por nome de campo exato, do mais especifico para o
    menos. 'id' generico fica por ultimo porque casa com recordId, modelId,
    uuid e afins."""
    achados = {}

    def anda(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(x, str) and x:
                    achados.setdefault(k.lower(), x)
                anda(x)
        elif isinstance(v, list):
            for x in v:
                anda(x)

    anda(j)
    for k in ("taskid", "task_id", "jobid", "job_id", "requestid", "request_id", "id"):
        if k in achados:
            return achados[k]
    return None


def estado_do_job(st):
    """Le o estado num campo de estado de verdade. Envelopes tipo
    {"code":200,"msg":"success","data":{"state":"waiting"}} sao a armadilha
    classica: o 'success' e da CONSULTA, nao do job. Estado desconhecido =
    continuar esperando, nunca 'pronto'."""
    for chave in ("state", "status", "taskstatus", "job_status", "jobstatus"):
        v = _buscar_chave(st, chave)
        if isinstance(v, str):
            v = v.strip().lower()
            if v in ESTADO_OK:
                return "ok"
            if v in ESTADO_ERRO:
                return "erro"
            return "aguardando"
        if isinstance(v, int):          # alguns providers usam codigo numerico
            return {1: "ok", 2: "erro"}.get(v, "aguardando")
    return "aguardando"


def _buscar_chave(v, alvo):
    if isinstance(v, dict):
        for k, x in v.items():
            if k.lower() == alvo:
                return x
            r = _buscar_chave(x, alvo)
            if r is not None:
                return r
    elif isinstance(v, list):
        for x in v:
            r = _buscar_chave(x, alvo)
            if r is not None:
                return r
    return None


def baixar(url, destino):
    with urllib.request.urlopen(url, timeout=300) as r:
        dados = r.read()
        tipo = r.headers.get("content-type", "")
    ext = EXT.get(tipo.split(";")[0].strip())
    if not ext:
        m = re.search(r"\.(png|jpe?g|webp|mp4|mov|webm)(\?|$)", url, re.I)
        ext = "." + m.group(1).lower() if m else ".bin"
    destino += ext
    with open(destino, "wb") as f:
        f.write(dados)
    return destino


# ---------------------------------------------------------------- main
def main():
    global PASTA, RUN_ID
    ap = argparse.ArgumentParser()
    ap.add_argument("--rota", required=True, choices=["fal", "kie"])
    ap.add_argument("--model", required=True, help="ID exato do modelo")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--desc", required=True)
    ap.add_argument("--custo", type=float, required=True,
                    help="custo estimado em USD desta execucao")
    ap.add_argument("--estimar", action="store_true", help="so cota, nao gasta")
    ap.add_argument("--confirmar", action="store_true", help="autoriza a chamada paga")
    ap.add_argument("--async", dest="assincrono", action="store_true")
    ap.add_argument("--extra", default="{}", help="JSON com campos extras do corpo")
    ap.add_argument("--refs", nargs="*", default=[])
    ap.add_argument("--poll", type=int, default=12, help="segundos entre consultas")
    ap.add_argument("--max-poll", type=int, default=60)
    a = ap.parse_args()

    if a.assincrono and a.rota != "kie":
        sys.exit("--async so esta implementado para a rota kie. Para um modelo "
                 "assincrono em outro provider, escreva o poll na receita do "
                 "modelo antes de rodar — nao chame sem saber consultar o "
                 "status, porque o job e cobrado mesmo se voce perder o id.")

    c = config()
    PASTA = c["pasta"]
    os.makedirs(os.path.join(PASTA, "refs"), exist_ok=True)
    mes = gasto_do_mes(PASTA)
    teto = float(c.get("teto_mensal_usd", 50))

    # ---- cotacao
    print(f"COTACAO\n  rota      {a.rota}\n  modelo    {a.model}\n"
          f"  custo     ${a.custo:.2f}\n"
          f"  mes atual ${mes:.2f} de ${teto:.0f} -> ficaria ${mes + a.custo:.2f}")
    if mes + a.custo > teto:
        print(f"  ATENCAO: esta execucao passa o teto mensal de ${teto:.0f}. "
              f"Avise a pessoa antes de pedir aprovacao.")
    if a.estimar or not a.confirmar:
        print("\nNada foi gasto. Para rodar, repita o comando com --confirmar "
              "depois da aprovacao explicita.")
        return

    try:
        extra = json.loads(a.extra)
    except json.JSONDecodeError as e:
        sys.exit(f"--extra nao e JSON valido: {e}")

    # uuid, nao timestamp+pid: dois runs no mesmo segundo colidiriam e o
    # livro-caixa fundiria os dois num so, escondendo gasto.
    RUN_ID = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    log = {"model": a.model, "route": a.rota, "prompt": a.prompt, "refs": a.refs,
           "params": extra, "cost_usd": a.custo, "cost_source": "estimativa",
           "created": datetime.now(timezone.utc).isoformat(timespec="seconds")}

    # ---- submissao (a partir daqui, o dinheiro pode ter saido)
    if a.rota == "fal":
        j = post(f"https://fal.run/{a.model}", {"prompt": a.prompt, **extra},
                 {"Authorization": f"Key {env('FAL_KEY')}"})
        lancar(log, "submetido")
    else:
        h = {"Authorization": f"Bearer {env('KIE_API_KEY')}"}
        j = post("https://api.kie.ai/api/v1/jobs/createTask",
                 {"model": a.model, "input": {"prompt": a.prompt, **extra}}, h)
        task_id = achar_task_id(j)
        if task_id:
            log["task_id"] = task_id
        lancar(log, "submetido")

        if a.assincrono:
            if not task_id:
                morrer(f"job submetido mas nao achei o task id na resposta:\n"
                       f"{json.dumps(j)[:400]}\nPegue o id no painel do provider "
                       f"— o job esta rodando e ja foi pago.", log)
            print(f"task id {task_id} — se o poll cair, o job continua e ja foi "
                  f"pago; consulte por este id em vez de rodar de novo.")
            for i in range(a.max_poll):
                time.sleep(a.poll)
                try:
                    st = get(f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}", h)
                except Exception as e:
                    print(f"  falha ao consultar ({e}) — tentando de novo", file=sys.stderr)
                    continue
                estado = estado_do_job(st)
                if estado == "ok":
                    j = st
                    break
                if estado == "erro":
                    morrer(f"job falhou no provider: {json.dumps(st)[:400]}", log, "falhou")
                print(f"  aguardando... ({(i + 1) * a.poll}s)")
            else:
                morrer(f"job nao concluiu em {a.max_poll * a.poll}s. Task id "
                       f"{task_id} — consulte o status depois; NAO rode de novo, "
                       f"seria cobrado outra vez.", log)

    # ---- resultado
    tipo, dado = achar_saida(j)
    if not tipo:
        morrer(f"chamada feita (e cobrada) mas nao achei a midia na resposta.\n"
               f"Resposta: {json.dumps(j)[:600]}\nAtualize a secao 'Response' da "
               f"receita deste modelo com o campo correto.", log)

    base = os.path.join(PASTA, f"{slug(a.projeto)}_{slug(a.desc)}_{int(time.time())}")
    try:
        if tipo == "url":
            caminho = baixar(dado, base)      # baixar na hora: a URL expira
        else:
            caminho = base + (".mp4" if a.assincrono else ".png")
            with open(caminho, "wb") as f:
                f.write(base64.b64decode(dado))
    except Exception as e:
        morrer(f"nao consegui salvar o arquivo: {e}\nURL/origem: {str(dado)[:200]}",
               log, "arquivo-perdido")

    with open(os.path.splitext(caminho)[0] + ".json", "w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    lancar(log, "ok", os.path.basename(caminho))

    print(f"OK {caminho}  (${a.custo:.2f} estimado · mes agora "
          f"${mes + a.custo:.2f})")
    print("Se a fatura mostrar outro valor, corrija com: "
          f"registrar.py --corrigir {RUN_ID} --cost <valor real>")


if __name__ == "__main__":
    main()
