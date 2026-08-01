# Imagem — modelo final (só depois de escolher um rascunho)

O modelo caro. Duas situações justificam vir para cá: a peça é final e vai ser
publicada, ou precisa de **texto legível** renderizado dentro da imagem — placa,
cartaz, menu, embalagem, mockup de interface. É onde os modelos baratos falham
de forma previsível.

| Campo | Valor |
|---|---|
| Model ID | `openai/gpt-image-2` — **NÃO VERIFICADO** |
| Provider | fal.ai |
| Método | Sync |
| Tipo | Imagem |
| Chave | `.env` → `FAL_KEY` |
| Custo | ~$0,05 / imagem em qualidade média — ver `references/pricing.md` |
| Verificado em | — preencher na primeira chamada real |

## Endpoint

```
POST https://fal.run/{model-id}
Authorization: Key {FAL_KEY}
```

Edição de uma imagem existente costuma ser o mesmo caminho com `/edit` no fim —
confirmar na documentação do modelo.

## Request / Response

Preencher com o corpo exato da doc na primeira vez. Aqui vale mais do que no
modelo de rascunho: cada tentativa-e-erro custa cinco vezes mais.

## A regra que economiza

Chegue aqui com o prompt **já resolvido** no modelo barato. O papel deste
modelo é executar uma decisão que já foi tomada, não ajudar a decidir. Quem
explora no modelo caro paga preço de final por rascunho descartável — e a
diferença some numa imagem, mas em quarenta é a fatura inteira.

Cote antes: modelo, quantidade, dólar. Espere o "pode".
