# [Nome do modelo]

Uma linha: no que este modelo é bom e quando escolhê-lo em vez dos outros.

| Campo | Valor |
|---|---|
| Model ID | o ID exato, copiado da página do provider |
| Provider | fal.ai / Kie AI |
| Método | Sync (responde na hora) ou Async (submete, faz poll) |
| Tipo | Imagem ou Vídeo |
| Chave | `.env` → NOME_DA_CHAVE |
| Custo | por imagem, ou por segundo |
| Docs | link da página deste modelo no provider |
| Verificado em | data da última chamada real que funcionou |

## Endpoint

```
POST https://...
Authorization: ...        (fal usa "Key {chave}", Kie usa "Bearer {chave}")
```

## Request

Cole aqui o corpo JSON exato da documentação, com os campos que você de fato
usa: prompt, proporção, resolução, imagem de referência, duração.

## Response

Onde o arquivo aparece na resposta: campo base64, ou URL para baixar.
Se for assíncrono: qual endpoint consulta o status, e qual campo diz "pronto".

Preencher esta seção de verdade é o que evita tentativa-e-erro na primeira
chamada — e aqui cada tentativa custa dinheiro.

## Notas

Limites de taxa, tamanho máximo, regras de conteúdo, particularidades de upload,
qualquer coisa que já tenha dado errado uma vez.

---

**Marque como `NÃO VERIFICADO` qualquer ID que você copiou de um artigo, vídeo
ou tutorial em vez de ter chamado de verdade.** IDs de modelo mudam de versão
com frequência, e um ID errado gasta uma chamada e devolve "model not found" —
ou, pior, roda um modelo que não era o que você queria e cobra por ele.
