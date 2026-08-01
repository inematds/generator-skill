# Análise — guia "Build your own /generate skill"

Fonte: `doc/generate-skill-guide.pdf` (9 páginas, texto extraído em `doc/out.txt`).

## O que o documento é

Guia de build de uma **skill `/generate`** para Claude Code: um comando que gera
imagens e vídeos via APIs, roteia sempre para o provider mais barato capaz, exige
aprovação antes de gasto com vídeo e joga todo output numa pasta única e plana.

Pipeline em 4 passos: **Route → Prep refs → Generate → Log**.

## Arquitetura proposta

```
workspace/
├── .claude/skills/generate/
│   ├── SKILL.md              roteamento + regras (o "cérebro")
│   └── models/*.md           1 receita por modelo (endpoint, auth, request, response)
├── generations/              tudo plano, sem subpastas
│   └── refs/                 logos, rostos, referências de estilo
└── .env                      chaves
```

Três decisões de design, e são as boas ideias do guia:

1. **Pasta plana única** — qualquer galeria/script lê a biblioteca sem config.
2. **Uma receita markdown por modelo** — modelo novo = 1 arquivo, nada mais muda.
   É o que dá vida útil ao sistema, já que model IDs mudam todo mês.
3. **Regras dentro do SKILL.md** — o agente relê a cada execução, então gate de
   custo e regra de pasta escritas uma vez valem para sempre.

## Providers e modelos citados

Agregadores: **Kie AI** (`KIE_API_KEY`, header `Bearer`), **fal.ai** (`FAL_KEY`,
header `Key` — não Bearer), **WaveSpeed** (`WAVESPEED_API_KEY`). Google AI Studio
autentica com a key **na query string** (`?key=`).

| Modelo | Uso | Provider | ID | Custo aprox. |
|---|---|---|---|---|
| Nano Banana 2 (Lite) | imagem cotidiana, forte com refs | Google AI Studio / fal | `gemini-3.1-flash-lite-image` | ~$0,034/1K img |
| GPT Image 2 | texto legível dentro da imagem | fal.ai | `openai/gpt-image-2` | ~$0,05/img |
| Kling 3.0 | vídeo default | Kie AI | `kling-3.0/video` | 3–15s, std 720p |
| Veo 3.1 | vídeo de qualidade a partir de frame | Google AI Studio | `veo-3.1-generate-preview` | clipes de 8s |
| Seedance 2.0 Fast | referência→vídeo (até 9 imagens) | fal.ai | `bytedance/seedance-2.0/fast/reference-to-video` | $0,24/s (5s ≈ $1,21) |

Recomendação do guia: começar só com **Nano Banana 2 Lite (sync) + Kling 3.0
(async)** — cobre a maioria dos pedidos e já ensina os dois padrões.

## Guardrails (a parte que realmente importa)

- **Cotar antes de vídeo.** Agente declara modelo/duração/resolução/custo e espera
  "vai". Cotação ≠ aprovação; uma aprovação = uma execução.
- **Rascunhar barato, finalizar caro.** Só reroda no modelo premium o favorito.
- **Referência real, nunca descrita.** Logo descrito em texto sempre volta errado —
  passar o arquivo de `generations/refs/`; se faltar, parar e pedir.
- **Uma pasta plana.** Subpasta "organizada" quebra toda ferramenta que lê a lib.
- **Uma geração por vez** (rate limit).
- **Sidecar log**: JSON de mesmo basename ao lado de cada mídia, com
  `model`, `prompt`, `refs`, `params`, `created`. Contrato simples, recupera
  qualquer prompt meses depois.

Padrão async (maioria dos vídeos): POST → task id → poll 5–15s → URL pronta →
**baixar imediatamente** (URLs expiram em horas) → salvar → logar. O guia aponta que
confundir sync/async é a causa nº 1 de "primeira tentativa travou".

## Bônus

Um prompt verbatim que gera uma **galeria bento/masonry** local self-contained
(1 arquivo, hover dá play em vídeo, clique abre lightbox) apontando para
`generations/` — e manda gravar a regra da pasta no CLAUDE.md, para skill e galeria
nunca se desalinharem.

## Avaliação crítica

**Forte:**
- O valor está no sistema (roteamento, gate de custo, log), não no "gerar imagem
  bonita" — o próprio guia diz isso e está certo.
- Receita-por-modelo é uma abstração de manutenção genuinamente boa; envelhece bem.
- Sidecar JSON é barato e resolve um problema real (prompt perdido).

**Fraco / a completar:**
- **Roteamento "mais barato" não é operacionalizável como está.** O SKILL.md manda
  "escolha o provider mais barato", mas não há tabela de preços versionada nem
  fonte de verdade — o agente vai adivinhar. Faltaria um `pricing.md` com data.
- **Nenhum orçamento acumulado.** O gate é por execução; nada impede 30 aprovações
  de $2. Um contador diário/mensal no log resolveria.
- **Sem tratamento de falha/idempotência.** Se o download expira ou o poll morre no
  meio, o dinheiro já foi gasto e não há retomada por task id.
- **Preços e model IDs são voláteis** (o próprio doc avisa) — Nano Banana/Veo/Kling
  nas versões citadas envelhecem em semanas. Tratar a tabela da p.6 como snapshot.
- **Segurança:** `.env` fora do git é mencionado, mas upload de imagem local para
  "URL pública" (Kie) publica conteúdo — merece um aviso explícito.
- O material original termina em divulgação de uma versão paga pré-pronta; a parte técnica é o que interessa aqui.

## Aplicabilidade aqui

O guia pressupõe que toda geração é paga e remota. Aqui não é: o `inemaimg`
serve **flux2-klein** na GPU local, o que torna a rota mais barata gratuita e
inverte o roteamento inteiro. As chaves já vivem em
`~/projetos/openpcbotv2/.env` / `~/projetos/wifi/.env`, então a p.3 do guia
some. A pasta plana é uma escolha nova — `~/projetos/output` é organizado por
projeto, então a biblioteca ganhou um lugar próprio (`output/generations/`) em
vez de reaproveitar a convenção existente.

Disso saíram duas skills, em `generate-local/` e `generate-api/` — ver os
READMEs de cada uma.
