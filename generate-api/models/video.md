# Vídeo — a via cara

Vídeo custa **por segundo**, e é onde as surpresas de fatura nascem. Dez
segundos custam o equivalente a cem imagens de rascunho. Nunca gerar vídeo
"para ver como fica".

| Campo | Valor |
|---|---|
| Model ID | `kling-3.0/video` — **NÃO VERIFICADO** |
| Provider | Kie AI (fallback: fal.ai) |
| Método | **Async** — submete, recebe task id, faz poll |
| Tipo | Vídeo |
| Chave | `.env` → `KIE_API_KEY` |
| Custo | ~$0,20–0,35/s → 5 s ≈ $1–1,75; 10 s ≈ $2–3,50 |
| Verificado em | — preencher na primeira chamada real |

## Endpoint

```
POST https://api.kie.ai/api/v1/jobs/createTask
Authorization: Bearer {KIE_API_KEY}
```

Kie usa `Bearer`; fal usa `Key`. Trocar a palavra é o erro de autenticação mais
comum entre providers.

## O padrão assíncrono

1. POST do job → a resposta traz um **task id**.
2. Poll do status a cada 10–15 segundos, com paciência.
3. Status concluído → a resposta traz a URL do arquivo.
4. **Baixar na hora** — URLs de resultado costumam expirar em horas.
5. Salvar na pasta e registrar o custo real.

`scripts/gerar.py --async` faz isso e **guarda o task id no log**. Isso importa:
se o poll morrer no meio, o dinheiro já foi gasto e o job continua rodando lá.
Com o id em mãos, consulta-se o resultado depois; sem ele, paga-se de novo.

Confundir síncrono com assíncrono é a razão nº 1 de uma primeira chamada parecer
travada. Anote o método correto na tabela acima assim que descobrir.

## Antes de chamar

Cotar sempre: modelo, **duração em segundos**, resolução, e o dólar que dá.
Esperar aprovação explícita. Uma aprovação vale uma execução — se não agradou e
vai rodar de novo, cota de novo.

## Dica que corta custo pela metade

Muito pedido de "faz um vídeo disso" é, na verdade, movimento de câmera sobre
imagem parada — push-in, travelling, ken burns com profundidade. Isso não
precisa de modelo generativo: dá para fazer com ferramenta de composição sobre
uma imagem gerada barato, com mais controle sobre o movimento e a um custo
próximo de zero. Reserve o vídeo generativo para movimento que **não existe** na
cena: alguém virando o rosto, líquido escorrendo, tecido balançando.

## Upload

O Kie oferece upload que devolve URL pública para mandar imagem local como
referência. Isso **publica** o arquivo. Rosto de cliente, documento ou peça sob
NDA não sobem sem alguém decidir isso conscientemente.
