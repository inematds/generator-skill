# GPT Image 2 (fal.ai) — rota paga, só para texto dentro da imagem

Única razão para sair do flux2-klein numa imagem: **letra legível** renderizada
dentro da arte (placa, cartaz, menu, embalagem, mockup de UI). É onde os modelos
locais de 4–9B falham de forma previsível.

| Campo | Valor |
|---|---|
| Model ID | `openai/gpt-image-2` — **NÃO VERIFICADO**, confirmar na página do modelo em fal.ai antes do primeiro uso |
| Provider | fal.ai |
| Método | Sync |
| Tipo | Imagem |
| API key | `~/projetos/wifi/.env` → `FAL_KEY` |
| Custo | ~$0,05 por imagem em qualidade média (estimativa — ver `references/pricing.md`) |
| Docs | https://fal.ai/models |

## Endpoint e auth

```
POST https://fal.run/openai/gpt-image-2
Authorization: Key {FAL_KEY}
Content-Type: application/json
```

Atenção: fal usa `Key`, **não** `Bearer`. Trocar a palavra é o erro de auth mais
comum entre providers. Edição de imagem existente costuma ser o mesmo caminho
com `/edit` no fim — confirmar na doc.

## Request / Response

Copiar o corpo exato da página do modelo (campos de prompt, aspect ratio,
tamanho, imagem de referência) e colar aqui na primeira vez que usar, junto com
onde o arquivo aparece na resposta (URL ou base64). Preencher isto de verdade
custa dez minutos e evita toda tentativa-e-erro futura — que aqui é paga.

## Antes de chamar

Cotar para o usuário: modelo, quantidade, dólar estimado. Esperar o "pode".
Depois de salvar, `registrar.py --cost 0.05` para o gasto entrar no livro-caixa.

## Nota

Se o pedido é "imagem com uma frase por cima", muitas vezes o caminho certo nem
é este: gerar o fundo no flux2-klein e compor o texto por cima (HTML/ffmpeg/
canvas) dá tipografia perfeita, editável e de graça. Considerar isso antes de
gastar.
