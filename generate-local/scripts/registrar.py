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

OUT = os.path.expanduser("~/projetos/output/generations")
LEDGER = os.path.join(OUT, "_ledger.jsonl")
TETO_MES = 20.0


def saldo():
    if not os.path.exists(LEDGER):
        print("livro-caixa vazio — nada gasto ainda ($0).")
        return
    por_mes, por_rota = defaultdict(float), defaultdict(float)
    total, n = 0.0, 0
    with open(LEDGER) as f:
        for linha in f:
            try:
                e = json.loads(linha)
            except json.JSONDecodeError:
                continue
            c = float(e.get("cost_usd") or 0)
            total += c
            n += 1
            por_mes[(e.get("created") or "?")[:7]] += c
            por_rota[e.get("route", "?")] += c
    mes = datetime.now(timezone.utc).strftime("%Y-%m")
    atual = por_mes.get(mes, 0.0)
    print(f"{n} geracoes registradas · total ${total:.2f}")
    print(f"mes {mes}: ${atual:.2f} (teto de aviso ${TETO_MES:.0f})")
    for r, c in sorted(por_rota.items(), key=lambda x: -x[1]):
        print(f"  {r:<20} ${c:.2f}")
    if atual >= TETO_MES:
        print(f"\nATENCAO: o mes ja passou de ${TETO_MES:.0f}. Avise o usuario "
              f"antes de cotar a proxima rota paga.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saldo", action="store_true")
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
