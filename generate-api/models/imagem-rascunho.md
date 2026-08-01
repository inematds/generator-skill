# Imagem — modelo de rascunho (a rota do dia a dia)

O modelo barato onde se explora. É aqui que 90% das gerações acontecem: variação
de conceito, teste de composição, busca de direção visual. A ordem de grandeza é
$0,01–0,04 por imagem, então dez tentativas custam menos que um cafezinho — e é
exatamente esse o ponto.

| Campo | Valor |
|---|---|
| Model ID | `gemini-3.1-flash-lite-image` (Nano Banana Lite) — **NÃO VERIFICADO** |
| Provider | fal.ai (também direto no Google AI Studio) |
| Método | Sync |
| Tipo | Imagem |
| Chave | `.env` → `FAL_KEY` |
| Custo | ~$0,034 / imagem — conferir em `references/pricing.md` |
| Verificado em | — preencher na primeira chamada real |

## Endpoint

```
POST https://fal.run/{model-id}
Authorization: Key {FAL_KEY}
```

fal usa `Key`, não `Bearer`.

## Request / Response

Copie o corpo exato da página do modelo no fal (prompt, proporção, tamanho,
imagem de referência) e cole aqui na primeira vez que usar, junto com onde a
imagem aparece na resposta. `scripts/gerar.py` acha URL ou base64 sozinho, mas
ter o formato escrito aqui é o que permite depurar quando muda.

## Como usar bem

- **Gere variações mudando a semente, não o prompt**, quando quiser ver outras
  possibilidades da mesma ideia. Mudar o prompt e a semente ao mesmo tempo
  impede saber o que causou a diferença.
- Este modelo costuma ser forte com **imagem de referência** — passe o arquivo
  real de `refs/` em vez de descrever a marca.
- Ponto fraco previsível: **texto dentro da imagem**. Se precisa de letra
  legível, é caso para o modelo final (ver `imagem-final.md`) — ou, muitas
  vezes melhor, gerar o fundo aqui e compor o texto por cima em HTML/canvas,
  que dá tipografia perfeita, editável e de graça.
