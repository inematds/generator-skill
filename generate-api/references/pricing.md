# Preços — snapshot

**Data deste snapshot: 2026-08-01.**

Preço de API muda rápido e sem aviso. Se hoje passou de ~60 dias desta data,
trate tudo abaixo como ordem de grandeza e confira na página do provider antes
de cotar. O ponto desta tabela não é ser eterna — é fazer com que "a rota mais
barata" seja uma **consulta a um arquivo**, e não um palpite do agente na hora.

| Rota | Modelo | Custo | Confiança |
|---|---|---|---|
| fal | `openai/gpt-image-2` | ~$0,05 / imagem (medium) | **NÃO VERIFICADO** — conferir no fal.ai |
| fal | `bytedance/seedance-2.0/fast/reference-to-video` | ~$0,24/s → 5 s ≈ $1,21 | **NÃO VERIFICADO** |
| kie | `kling-3.0/video` | ~$0,20–0,35/s | **NÃO VERIFICADO** |
| google | `gemini-3.1-flash-lite-image` (Nano Banana Lite) | ~$0,034 / imagem | **NÃO VERIFICADO** |

Todos os IDs acima vieram de material de terceiros, não de uma chamada real.
Antes do primeiro uso de cada um: abrir a página do modelo, copiar o ID, anotar
o preço real e trocar a marca de confiança por `verificado em AAAA-MM-DD`.

## Como usar

1. Encontre a rota mais barata que faz a tarefa.
2. Multiplique pela quantidade (ou pela duração, em vídeo).
3. **Cote e espere aprovação.**
4. O script lança a **estimativa** no livro-caixa na hora — é o que permite o
   saldo existir mesmo quando a geração falha depois de cobrada. Quando a fatura
   do provider chegar, corrija os lançamentos
   (`registrar.py --corrigir <run_id> --cost <real>`); `--saldo` mostra quantos
   ainda estão com valor estimado. Com o tempo, o livro-caixa corrigido vira uma
   fonte de preço melhor do que esta tabela.

## Teto

O teto mensal fica em `_config.json` (`teto_mensal_usd`). Ao ultrapassar, a
skill avisa antes de cotar a próxima rota paga. Não bloqueia — mas garante que
ninguém descubra o total só na fatura.
