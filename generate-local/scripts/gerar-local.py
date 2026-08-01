#!/usr/bin/env python3
"""gerar-local.py — imagem na GPU local (inemaimg / flux2-klein), custo zero.

Gera, salva plano em ~/projetos/output/generations/ e escreve o sidecar JSON e a
linha do livro-caixa. Rota padrao da skill /generate.

Uso:
  python3 gerar-local.py --prompt "..." --projeto capa-curso --desc "hero-ia"
  python3 gerar-local.py --prompt "..." --projeto x --desc y -n 3 --seed 0
"""
import argparse, base64, json, os, re, sys, time, urllib.request
from datetime import datetime, timezone

OUT = os.path.expanduser("~/projetos/output/generations")
HOST = "http://localhost:8000"


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def health(host):
    try:
        with urllib.request.urlopen(f"{host}/health", timeout=5) as r:
            return json.loads(r.read())
    except Exception:
        return None


def gerar(host, body):
    req = urllib.request.Request(
        f"{host}/generate", data=json.dumps(body).encode(),
        headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--projeto", required=True, help="prefixo do nome do arquivo")
    ap.add_argument("--desc", required=True, help="descricao curta p/ o nome")
    ap.add_argument("--model", default="flux2-klein")
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--seed", type=int, default=None, help="omitido = aleatorio por variacao")
    ap.add_argument("--w", type=int, default=None)
    ap.add_argument("--h", type=int, default=None)
    ap.add_argument("-n", "--num", type=int, default=1, help="variacoes, geradas em serie")
    ap.add_argument("--refs", nargs="*", default=[], help="caminhos em refs/ usados como referencia")
    ap.add_argument("--host", default=HOST)
    a = ap.parse_args()

    h = health(a.host)
    if not h:
        sys.exit(f"inemaimg fora do ar em {a.host}. Suba o servidor "
                 f"(~/projetos/inemaimg, docker-compose up -d) e tente de novo. "
                 f"Nao troque para rota paga sem falar com o usuario.")
    if h.get("loaded_model") != a.model:
        print(f"[aviso] servidor com '{h.get('loaded_model')}' carregado; pedir "
              f"'{a.model}' vai recarregar pesos (dezenas de segundos).", file=sys.stderr)

    os.makedirs(os.path.join(OUT, "refs"), exist_ok=True)
    salvos = []
    for i in range(a.num):
        seed = a.seed if a.seed is not None else int(time.time() * 1000) % 2**31
        body = {"model": a.model, "prompt": a.prompt, "steps": a.steps, "seed": seed}
        if a.w:
            body["width"] = a.w
        if a.h:
            body["height"] = a.h
        try:
            j = gerar(a.host, body)
        except Exception as e:
            sys.exit(f"ERRO na geracao: {e}")

        b64 = j.get("image")
        if not isinstance(b64, str) or len(b64) < 100:
            sys.exit(f"ERRO: resposta sem o campo 'image'. Chaves: {list(j.keys())}. "
                     f"O servidor mudou de contrato — corrija models/flux2-klein-local.md.")
        if b64.startswith("data:"):
            b64 = b64.split(",", 1)[1]

        base = f"{slug(a.projeto)}_{slug(a.desc)}_{int(time.time())}"
        png = os.path.join(OUT, base + ".png")
        with open(png, "wb") as f:
            f.write(base64.b64decode(b64))

        log = {
            "model": j.get("model_used", a.model),
            "route": "local:inemaimg",
            "prompt": a.prompt,
            "refs": a.refs,
            "params": {"steps": a.steps, "seed": seed,
                       "size": f"{a.w}x{a.h}" if a.w and a.h else "default"},
            "cost_usd": 0,
            "generation_time_s": j.get("generation_time_s"),
            "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        with open(os.path.join(OUT, base + ".json"), "w") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
        with open(os.path.join(OUT, "_ledger.jsonl"), "a") as f:
            f.write(json.dumps({"file": base + ".png", **log}, ensure_ascii=False) + "\n")

        salvos.append(png)
        print(f"OK {png}  ({j.get('generation_time_s')}s, seed {seed}, $0)")

    if len(salvos) > 1:
        print(f"{len(salvos)} variacoes em {OUT}")


if __name__ == "__main__":
    main()
