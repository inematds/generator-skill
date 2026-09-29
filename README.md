# generator-skill

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

![Uma skill, todo o fluxo: /generate roteia para o modelo mais econômico, usa referências reais, gera imagem ou vídeo, salva tudo numa pasta única e registra prompt, modelo e parâmetros](assets/hero-fluxo.png)

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/generator-skill/guia/**

Duas versões da skill `/generate` — um comando para o agente gerar imagens e
vídeos sob demanda, escolher a rota de menor custo, controlar gasto e salvar
tudo num lugar só.

São duas porque a decisão mais importante da skill — **qual é a rota mais
barata** — tem respostas opostas dependendo da máquina.

## Qual usar

| | [`generate-local/`](generate-local/) | [`generate-api/`](generate-api/) |
|---|---|---|
| **Para** | máquina com modelo rodando nela | qualquer máquina, tudo via API |
| **Rota mais barata** | local, **$0** (flux2-klein na GPU) | modelo barato pago, ~$0,02 |
| **Modelo de cobrança** | hardware já pago, custo marginal zero | pay-as-you-go por chamada |
| **Rota paga** | exceção — duas razões só | é o único caminho |
| **Imagem padrão** | flux2-klein local, ~6 s | modelo barato de imagem |
| **Imagem com texto legível** | fal.ai, pago (local erra letra) | modelo top, pago |
| **Vídeo padrão** | render 2.5D local (`pixflow-motion`), $0 | modelo generativo, $0,20–0,35/s |
| **Portão de custo** | existe, quase nunca dispara | dispara em toda execução |
| **"Rascunhe barato, finalize caro"** | sem sentido — é o mesmo modelo | é a regra que mais economiza |
| **Livro-caixa** | existe, quase sempre zerado | é o coração da skill |
| **Depende de** | servidor `inemaimg` no ar (porta 8000) | `FAL_KEY` + `KIE_API_KEY` num `.env` |
| **Teto de aviso** | $20/mês | configurável, padrão $50/mês |

O que **não** muda entre as duas, porque é o que faz o sistema durar: uma receita
Markdown por modelo, biblioteca plana, log JSON ao lado de cada arquivo,
referência real em vez de descrita, e as regras dentro do `SKILL.md` — que o
agente relê a cada uso.

## Os cinco passos

O fluxo é o mesmo nas duas versões; muda só para onde o passo 1 aponta.

1. **Roteia para o modelo mais econômico** que dá conta da tarefa, e lê a receita
   daquele modelo antes de chamar.
2. **Usa referências reais** — logotipos, rostos, estilo — carregadas de `refs/`.
   Descrever um logo em palavras devolve logo errado toda vez.
3. **Gera** imagem ou vídeo. Se o modelo for assíncrono, consulta o status e
   baixa na hora, porque URL de resultado expira.
4. **Salva tudo numa pasta única e plana**, sem subpastas, com nome previsível.
5. **Registra prompt, modelo, parâmetros e custo** num JSON ao lado do arquivo.

## Por que agregador, e por que pay-as-you-go

![Modelos criativos (nano banana, kling, veo, seedance, gpt image) alcançáveis por duas rotas: um agregador por assinatura mensal, ou agregadores pay-as-you-go como Fal AI, Wavespeed AI e Kie AI](assets/rotas-assinatura-vs-payg.png)

Os mesmos modelos são alcançáveis por caminhos com contas muito diferentes.
Plataformas de **assinatura** cobram um valor fixo por mês — previsível, e boa
quando o uso é alto e constante. Agregadores **pay-as-you-go** (fal.ai, Kie AI)
cobram por chamada, com uma chave e uma fatura só para dezenas de modelos.

A versão `generate-api` assume pay-as-you-go, por três razões: começa em zero,
o custo é atribuível a cada geração (é o que alimenta o livro-caixa), e não se
paga mensalidade em mês parado. Se o volume subir a ponto de a assinatura sair
mais barata, o cálculo é simples — some o mês no `--saldo` e compare.

Na versão `generate-local` a discussão não existe: a GPU já está paga, e a rota
paga só entra nas duas exceções documentadas.

## Instalar

```bash
cp -r generate-local ~/.claude/skills/generate               # máquina com GPU
cp -r generate-api  <workspace>/.claude/skills/generate      # máquina sem modelo local
```

As duas declaram `name: generate`. Instale **uma** por workspace, ou renomeie.

## Documentação

- [`generate-local/README.md`](generate-local/README.md) e
  [`generate-api/README.md`](generate-api/README.md) — cada versão em detalhe.
- [`doc/guia-skill-generate-ptbr.md`](doc/guia-skill-generate-ptbr.md) — guia
  técnico traduzido: autenticação por provider, padrão assíncrono, tabela de
  modelos, faixas de custo.
- [`doc/analise-generate-skill-guide.md`](doc/analise-generate-skill-guide.md) —
  análise do material original: o que ele acerta e o que faltava (orçamento
  acumulado, preço versionado, retomada de job assíncrono — os três estão
  implementados aqui).

## Aviso que vale para as duas

IDs de modelo, preços e endpoints mudam com frequência. Tudo que não foi
confirmado por uma chamada real está marcado **NÃO VERIFICADO** nas receitas.
Confirme na documentação atual do provider antes de usar para valer.
