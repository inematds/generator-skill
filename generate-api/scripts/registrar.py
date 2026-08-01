#!/usr/bin/env python3
"""registrar.py — sidecar JSON + livro-caixa para arquivos vindos de rota paga
(ou de rota local que nao passou pelo gerar-local.py, como o pixflow).

  python3 registrar.py --file capa.png --model gpt-image-2 --route fal \
      --prompt "..." --cost 0.05 [--refs refs/logo.png] [--params '{"size":"2K"}']
  python3 registrar.py --saldo            # gasto do mes + total
"""
import argparse, json, os, sys
from collections import defaultdict
from datetime import datetime, timezone

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _config():
    p = os.path.join(AQUI, "_config.json")
    c = {"pasta": "~/generations", "teto_mensal_usd": 50}
    if os.path.exists(p):
        try:
            with open(p) as f:
                c.update(json.load(f))
        except json.JSONDecodeError:
            print(f"[aviso] {p} nao e JSON valido; usando os padroes.", file=sys.stderr)
    return os.path.expanduser(c["pasta"]), float(c.get("teto_mensal_usd", 50))


OUT, TETO_MES = _config()
LEDGER = os.path.join(OUT, "_ledger.jsonl")


def _linhas():
    if not os.path.exists(LEDGER):
        return []
    saida = []
    with open(LEDGER) as f:
        for linha in f:
            try:
                saida.append(json.loads(linha))
            except json.JSONDecodeError:
                continue
    return saida


def _consolidar(linhas):
    """Um run e lancado ao submeter e regravado ao concluir (e pode ser
    corrigido depois). A ultima linha de cada run_id e a verdade; linhas sem
    run_id (registro manual) sao independentes."""
    por_run, soltas = {}, []
    for e in linhas:
        if e.get("run_id"):
            por_run[e["run_id"]] = e
        else:
            soltas.append(e)
    return list(por_run.values()) + soltas


def saldo():
    eventos = _consolidar(_linhas())
    if not eventos:
        print("livro-caixa vazio — nada gasto ainda ($0).")
        return
    por_mes, por_rota = defaultdict(float), defaultdict(float)
    total = 0.0
    pendentes = []
    for e in eventos:
        c = float(e.get("cost_usd") or 0)
        total += c
        por_mes[(e.get("created") or "?")[:7]] += c
        por_rota[e.get("route", "?")] += c
        if e.get("status") not in (None, "ok"):
            pendentes.append(e)
    mes = datetime.now(timezone.utc).strftime("%Y-%m")
    atual = por_mes.get(mes, 0.0)
    estimados = sum(1 for e in eventos if e.get("cost_source") == "estimativa")

    print(f"{len(eventos)} geracoes registradas · total ${total:.2f}")
    print(f"mes {mes}: ${atual:.2f} (teto de aviso ${TETO_MES:.0f})")
    for r, c in sorted(por_rota.items(), key=lambda x: -x[1]):
        print(f"  {r:<20} ${c:.2f}")
    if estimados:
        print(f"\n{estimados} lancamento(s) ainda com valor ESTIMADO. Confira a "
              f"fatura e corrija com --corrigir <run_id> --cost <valor real>.")
    if pendentes:
        print(f"\n{len(pendentes)} run(s) cobrados sem arquivo salvo — dinheiro "
              f"gasto que nao virou entrega:")
        for e in pendentes:
            print(f"  {e.get('run_id')}  {e.get('status'):<16} ${float(e.get('cost_usd') or 0):.2f}"
                  f"  {('task ' + e['task_id']) if e.get('task_id') else ''}")
    if atual >= TETO_MES:
        print(f"\nATENCAO: o mes ja passou de ${TETO_MES:.0f}. Avise o usuario "
              f"antes de cotar a proxima rota paga.")


def corrigir(run_id, custo):
    """Regrava o lancamento de um run com o custo real da fatura."""
    alvo = None
    for e in _linhas():
        if e.get("run_id") == run_id:
            alvo = e
    if not alvo:
        sys.exit(f"run_id {run_id} nao existe no livro-caixa. Veja os ids em --saldo.")
    antigo = float(alvo.get("cost_usd") or 0)
    alvo["cost_usd"] = custo
    alvo["cost_source"] = "fatura"
    alvo["corrigido_em"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(LEDGER, "a") as f:
        f.write(json.dumps(alvo, ensure_ascii=False) + "\n")
    print(f"OK run {run_id}: ${antigo:.2f} (estimado) -> ${custo:.2f} (fatura)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saldo", action="store_true")
    ap.add_argument("--corrigir", metavar="RUN_ID",
                    help="regrava o custo de um run com o valor real da fatura")
    ap.add_argument("--file")
    ap.add_argument("--model")
    ap.add_argument("--route", help="fal | kie | local:pixflow | ...")
    ap.add_argument("--prompt")
    ap.add_argument("--cost", type=float, default=0.0, help="custo REAL em USD")
    ap.add_argument("--refs", nargs="*", default=[])
    ap.add_argument("--params", default="{}", help="JSON dos parametros")
    ap.add_argument("--task-id", default=None, help="id do job async, p/ poder retomar")
    a = ap.parse_args()

    if a.saldo:
        return saldo()
    if a.corrigir:
        return corrigir(a.corrigir, a.cost)

    faltando = [k for k in ("file", "model", "route", "prompt") if not getattr(a, k)]
    if faltando:
        sys.exit(f"faltam argumentos: {', '.join('--' + k for k in faltando)} "
                 f"(ou use --saldo)")

    caminho = a.file if os.path.isabs(a.file) else os.path.join(OUT, a.file)
    if not os.path.exists(caminho):
        sys.exit(f"arquivo nao existe: {caminho}. Salve-o em {OUT} antes de registrar.")
    if os.path.dirname(os.path.abspath(caminho)) != os.path.abspath(OUT):
        print(f"[aviso] arquivo fora de {OUT} — a biblioteca e plana, mova-o para la.",
              file=sys.stderr)

    try:
        params = json.loads(a.params)
    except json.JSONDecodeError as e:
        sys.exit(f"--params nao e JSON valido: {e}")

    log = {
        "model": a.model, "route": a.route, "prompt": a.prompt, "refs": a.refs,
        "params": params, "cost_usd": a.cost,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if a.task_id:
        log["task_id"] = a.task_id

    base = os.path.splitext(caminho)[0]
    with open(base + ".json", "w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    os.makedirs(OUT, exist_ok=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps({"file": os.path.basename(caminho), **log},
                           ensure_ascii=False) + "\n")
    print(f"OK log -> {base}.json  (${a.cost:.2f} lancado no livro-caixa)")


if __name__ == "__main__":
    main()
