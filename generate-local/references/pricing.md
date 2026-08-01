# Preços — snapshot

**Data do snapshot: 2026-08-01.** Preço de API muda rápido. Se hoje passou de
~60 dias desta data, trate os números abaixo como ordem de grandeza e confira na
página do provider antes de cotar. O ponto desta tabela não é ser eterna: é que
"a rota mais barata" seja uma **consulta**, não um palpite do agente.

| Rota | Modelo | Custo | Fonte / confiança |
|---|---|---|---|
| local:inemaimg | flux2-klein | **$0** | verificado — GPU própria, chamada real 6,2 s |
| local:inemaimg | qwen-image-edit-2511 | **$0** | local, mesma GPU |
| local:pixflow | render 2.5D | **$0** | local, CPU/GPU própria |
| fal | openai/gpt-image-2 | ~$0,05 / imagem (medium) | estimativa de material de terceiros, não conferida no fal |
| fal | bytedance/seedance-2.0/fast/reference-to-video | ~$0,24/s (5 s ≈ $1,21) | idem |
| kie | kling-3.0 | ~$0,20–0,35/s | idem |
| runcomfy | kling-3.0 standard / pro / 4K | $0,084 / $0,112 / $0,42 por segundo | skill `kling-3-0` — **CLI não instalado**, só referência |
| google | veo-3.1-generate-preview | clipes de 8 s, preço não levantado | não confirmado |

## Como usar isto

1. Rota local disponível para a tarefa? Use. Fim.
2. Não? Pegue o custo aqui, multiplique pela quantidade/duração, e **cote antes**.
3. Depois de rodar, lance o custo real com `scripts/registrar.py --cost`. O
   custo real é o que entra no livro-caixa, não a estimativa.

## Teto

Aviso ao usuário quando o acumulado do mês passar de **$20**
(`registrar.py --saldo`). Não é bloqueio — é o número que impede trinta
aprovações de $2 passarem despercebidas, que é o furo clássico de um portão que
só olha uma execução por vez.
