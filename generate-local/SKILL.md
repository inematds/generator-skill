---
name: generate
description: >
  Gera IMAGENS e VÍDEOS por API/modelo, roteando sempre para a rota mais barata
  capaz — que neste setup é LOCAL e de graça (inemaimg/flux2-klein na GPU,
  pixflow para vídeo) — e só escala para rota paga (fal.ai / Kie AI) quando o
  local comprovadamente não dá conta. Salva tudo plano em
  ~/projetos/output/generations/ com um log JSON ao lado de cada arquivo e um
  livro-caixa do que foi gasto. Use SEMPRE que o usuário pedir "/generate",
  "gera uma imagem", "cria uma thumbnail", "faz um vídeo disso", "anima essa
  foto", "gera uma capa/poster/mockup", "preciso de uma arte", ou passar um
  prompt visual esperando um arquivo de volta — mesmo sem dizer "generate".
  Use também quando pedirem para variar/refinar uma imagem já gerada, ou
  perguntarem quanto custou / quanto já gastaram em geração. NÃO use para
  editar vídeo já gravado (reel-edita-*), curso, landing ou avatar HeyGen.
---

# /generate

Um comando para toda geração de mídia. A regra que organiza tudo: **a rota mais
barata capaz vem primeiro, e aqui a mais barata é local e custa zero**. Só se
paga quando o local não consegue fazer o trabalho — e nunca sem o usuário
aprovar antes.

## Pipeline

1. **Rotear** — escolher a rota pela tabela abaixo e ler a receita do modelo.
2. **Preparar refs** — carregar as imagens de referência reais de
   `generations/refs/`. Nunca descrever um logo ou um rosto em texto.
3. **Gerar** — chamar conforme a receita. Se for assíncrono, fazer poll e
   baixar na hora (URLs de resultado expiram em horas).
4. **Logar** — sidecar JSON ao lado do arquivo + linha no livro-caixa.

## Roteamento

| Tarefa | Rota padrão | Custo | Receita |
|---|---|---|---|
| Imagem (qualquer coisa) | inemaimg / flux2-klein, GPU local | **$0** | `models/flux2-klein-local.md` |
| Imagem com texto legível dentro (placa, cartaz, UI, embalagem) | fal.ai / GPT Image 2 | ~$0,05 | `models/gpt-image-2-fal.md` |
| "Vídeo" a partir de imagens (parallax 2.5D, câmera, look de cinema) | skill `pixflow-motion` | **$0** | `models/pixflow-local.md` |
| Vídeo generativo de verdade (movimento novo que não existe na imagem) | Kie AI / Kling | pago, ver `references/pricing.md` | `models/kling-kie.md` |

Leia a receita do modelo **antes** de cada geração — é onde estão endpoint,
autenticação, formato do corpo e onde o arquivo aparece na resposta.

**Por que local primeiro:** a GPU já está aqui, o flux2-klein entrega uma imagem
em ~6 segundos e o custo marginal é zero. Rodar 20 variações não pesa em nada.
Isso inverte o incentivo do guia original: em vez de "rascunhar barato e
finalizar caro", aqui é **rascunhar e finalizar local**, e a rota paga é
exceção justificada, não etapa final automática.

**Quando escalar para pago (as duas únicas razões honestas):**
- A imagem precisa de **texto legível** renderizado dentro dela. Modelos locais
  de 4–9B erram letra; é a falha mais previsível deles.
- O pedido é **vídeo generativo** — movimento que não pode ser extraído das
  imagens que já existem (uma pessoa virando de costas, água correndo, um
  objeto que muda de forma). Se o movimento couber em câmera + profundidade
  sobre uma imagem parada, `pixflow-motion` resolve de graça e melhor.

Não escale por "vai ficar mais bonito". Se você achar que a rota paga vale a
pena por qualidade, diga isso ao usuário com o custo e deixe ele decidir.

## Portão de custo

Antes de **qualquer** chamada paga:

- Declarar rota, modelo, duração/quantidade e o **dólar estimado**, e esperar um
  "pode" explícito. Cotar não é aprovar. **Uma aprovação = uma execução.**
- Se o gasto acumulado do mês (`scripts/registrar.py --saldo`) passar de **$20**,
  avisar antes de pedir a aprovação. O portão por execução não protege contra
  trinta execuções de $2.
- Nunca trocar de rota em silêncio. Se caiu para o fallback, dizer qual rota
  rodou e por quê.

Preços em `references/pricing.md`, com data. Se a data estiver com mais de ~60
dias, tratar como estimativa e conferir na página do provider antes de cotar.

## Saída

- Tudo **plano** em `~/projetos/output/generations/`. Sem subpastas.
- Referências (logos, rostos, estilo) em `~/projetos/output/generations/refs/`.
- Nome: `{projeto}_{descricao-curta}_{timestamp}.{ext}`, minúsculo com hífens.

Esta pasta é uma exceção deliberada ao padrão `~/projetos/output/<projeto>/` do
CLAUDE.md: uma biblioteca plana é o que permite galeria, script ou busca simples
lerem tudo sem configuração. Entrega final de um projeto continua indo para a
pasta do projeto — copie o arquivo para lá, não mova.

## Log

Depois de cada arquivo salvo, um JSON de mesmo nome-base ao lado:

```json
{
  "model": "flux2-klein",
  "route": "local:inemaimg",
  "prompt": "o texto exato enviado",
  "refs": ["refs/logo.png"],
  "params": { "steps": 4, "seed": 7, "size": "1024x1024" },
  "cost_usd": 0,
  "created": "2026-08-01T14:03:00Z"
}
```

Os scripts já escrevem isso. Em rota paga, registrar com `scripts/registrar.py`,
que também soma no livro-caixa (`generations/_ledger.jsonl`) — é o que faz
`--saldo` funcionar. Um arquivo sem log vira, em três semanas, um arquivo cujo
prompt ninguém recupera.

## Scripts

```bash
# imagem local (padrão) — gera, salva e loga em um passo
python3 <SKILL_DIR>/scripts/gerar-local.py --prompt "..." --projeto capa-curso \
  --desc "hero-ia" [--steps 4] [--seed 7] [--w 1024] [--h 1024] [-n 3]

# registrar um arquivo vindo de rota paga + lançar o custo no livro-caixa
python3 <SKILL_DIR>/scripts/registrar.py --file <arquivo> --model gpt-image-2 \
  --route fal --prompt "..." --cost 0.05

# quanto já gastei
python3 <SKILL_DIR>/scripts/registrar.py --saldo
```

`gerar-local.py` falha limpo se o servidor do inemaimg estiver fora do ar e diz
como subir. Não improvise outro caminho para imagem local: é esse servidor.

## Chaves

Leia em runtime de `~/projetos/wifi/.env` (`FAL_KEY`, `KIE_API_KEY`,
`GEMINI_API_KEY`). Nunca copiar a chave para outro arquivo, nunca imprimir o
valor, nunca colar dentro de código. Não existe conta WaveSpeed neste setup —
os fallbacks são fal.ai e Kie AI, nessa ordem.

## Referências reais, nunca descritas

Um logo descrito em palavras volta errado toda vez: forma errada, cor errada,
detalhe inventado. Se o pedido envolve uma marca, um rosto ou um estilo
específico, o arquivo real precisa estar em `refs/` e ser passado na chamada.
Se não estiver lá, **pare e peça** — é mais barato do que gerar cinco versões
erradas de um logo.

## Uma de cada vez

Gerações em série, não em paralelo. Local, porque a GPU tem uma fila só e
disputar VRAM derruba o servidor; pago, porque rate limit devolve erro que você
paga do mesmo jeito.
