# Kling (Kie AI) — vídeo generativo, rota paga

Última rota, e a mais cara. Só quando o movimento pedido **não pode** ser
extraído de uma imagem parada (ver `pixflow-local.md`). Sempre com cotação
aprovada antes.

| Campo | Valor |
|---|---|
| Model ID | `kling-3.0/video` — **NÃO VERIFICADO**, confirmar na página do modelo em kie.ai antes do primeiro uso |
| Provider | Kie AI |
| Método | **Async** (submete, recebe task id, faz poll) |
| Tipo | Vídeo |
| API key | `~/projetos/wifi/.env` → `KIE_API_KEY` |
| Custo | estimativa $0,20–0,35/s → clipe de 5 s ≈ $1–1,75. Ver `references/pricing.md` |
| Fallback | fal.ai (`FAL_KEY`) se o Kie recusar o job ou não tiver o modelo |

## Endpoint e auth

```
POST https://api.kie.ai/api/v1/jobs/createTask
Authorization: Bearer {KIE_API_KEY}
```

Kie usa `Bearer`; fal usa `Key`. Não confundir.

Kie também tem upload de arquivo que devolve URL pública — é como se manda uma
imagem local para image-to-video. **Isso publica o arquivo**: não subir rosto,
documento ou material privado sem falar com o usuário.

## Padrão assíncrono

1. POST do job → a resposta traz um **task id**.
2. Poll do status a cada 10–15 s, com paciência.
3. Status `complete` → a resposta traz a URL do arquivo.
4. **Baixar na hora** — URLs de resultado expiram em horas.
5. Salvar em `generations/` e rodar `registrar.py` com o custo real.

Se o poll morrer no meio, **o dinheiro já foi gasto**: guarde o task id no
sidecar assim que ele existir, para poder retomar em vez de pagar de novo.

## Observação sobre a skill `kling-3-0`

Existe uma skill `kling-3-0` instalada com preços por segundo bem detalhados,
mas ela chama o CLI `runcomfy`, que **não está instalado nesta máquina**
(verificado em 2026-08-01). Serve como referência de preço e de escolha de tier;
não serve como caminho de execução enquanto o CLI não existir.
