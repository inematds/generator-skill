---
name: generate
description: >
  Gera IMAGENS e VÍDEOS por API, roteando cada pedido para o provider mais
  barato capaz, cotando o custo em dólar e esperando aprovação antes de
  qualquer chamada paga, com teto de orçamento mensal que não deixa gasto
  pequeno virar conta grande. Salva tudo plano numa pasta única com um log JSON
  ao lado de cada arquivo, para nenhum prompt se perder. Use SEMPRE que pedirem
  "/generate", "gera uma imagem", "cria uma thumbnail/capa/poster/mockup",
  "faz um vídeo disso", "anima essa imagem", "preciso de uma arte", ou passarem
  um prompt visual esperando um arquivo de volta — mesmo sem dizer "generate".
  Use também para variar/refinar algo já gerado, e quando perguntarem quanto
  custou ou quanto já gastaram. NÃO use para editar vídeo já filmado, montar
  site ou escrever texto.
---

# /generate

Um comando para toda geração de mídia. Aqui **tudo custa dinheiro**, então a
skill vale menos pelo modelo que escolhe e mais pelo que impede: rota cara
escolhida por distração, conta que cresce sem ninguém ver, e prompt bom que se
perde.

## Antes do primeiro uso

Leia `references/setup.md`. Você precisa de duas chaves e de uma linha de
configuração dizendo onde salvar e qual o teto de gasto. Cinco minutos, uma vez.

## Pipeline

1. **Rotear** — escolher a rota pela tabela, consultando `references/pricing.md`.
2. **Cotar** — dizer o dólar e esperar o "pode". Isto é obrigatório, não é etapa
   opcional (ver Portão de custo).
3. **Preparar refs** — carregar as imagens de referência reais de `refs/`.
   Nunca descrever um logo ou um rosto em texto.
4. **Gerar** — chamar conforme a receita do modelo. Se for assíncrono, fazer
   poll e baixar na hora: URLs de resultado expiram em horas.
5. **Logar** — sidecar JSON + linha no livro-caixa. O lançamento acontece assim
   que o provider aceita o job, **antes** de o arquivo chegar: se algo falhar
   depois disso, o dinheiro já saiu e precisa aparecer no saldo. Vai com o custo
   estimado; quando a fatura chegar, corrija com
   `registrar.py --corrigir <run_id> --cost <valor real>`.

## Roteamento

| Tarefa | Rota padrão | Custo aprox. | Receita |
|---|---|---|---|
| Imagem — rascunho, variação, exploração | modelo barato de imagem | $0,01–0,04 | `models/imagem-rascunho.md` |
| Imagem — final, ou com texto legível dentro | modelo top de imagem | $0,05–0,15 | `models/imagem-final.md` |
| Vídeo | modelo de vídeo | $0,20–0,35 **por segundo** | `models/video.md` |

Leia a receita **antes** de cada geração — é onde estão endpoint, autenticação,
formato do corpo e onde o arquivo aparece na resposta.

**A regra que economiza mais:** rascunhe no modelo barato e só rode no caro
depois que a pessoa escolher um favorito. A diferença entre $0,02 e $0,10 é
irrelevante numa imagem e enorme em quarenta. Explorar é a fase em que se gera
muito; finalizar é a fase em que se gera uma vez.

**Fallback:** se a rota mais barata não tiver o modelo, recusar o job ou falhar
na autenticação, cair para o próximo provider — e **dizer qual rota rodou e por
quê**. Troca de rota em silêncio muda o preço sem a pessoa saber.

## Portão de custo

Este é o item que justifica a skill existir.

- Antes de **qualquer** chamada paga: declarar modelo, quantidade (ou duração e
  resolução, em vídeo) e o **dólar estimado**, e esperar aprovação explícita.
- **Cotar não é aprovar. Uma aprovação vale uma execução.** Se o resultado não
  agradou e vai rodar de novo, cota de novo.
- Vídeo é a via cara e a que mais surpreende: 10 segundos custam o mesmo que
  cem imagens de rascunho. Nunca gerar vídeo "para ver como fica".
- Antes de cotar, conferir o acumulado (`scripts/registrar.py --saldo`). Se o
  mês já passou do teto configurado, avisar **antes** de pedir aprovação.

Por que o teto acumulado importa: um portão que só olha uma execução por vez
aprova trinta gastos de $2 sem nunca disparar. O limite mensal é o que enxerga
o total.

## Saída

- Tudo **plano** na pasta configurada. Sem subpastas.
- Referências (logos, rostos, estilo) em `refs/`, dentro dela.
- Nome: `{projeto}_{descricao-curta}_{timestamp}.{ext}`, minúsculo com hífens.

Uma pasta plana parece bagunça e é o contrário: qualquer galeria, script ou
busca do sistema lê a biblioteca inteira sem configuração. Organizar em
subpastas por projeto quebra isso e, meses depois, ninguém lembra o critério de
organização que usou. Entrega para o cliente final é uma **cópia** para a pasta
do trabalho — o original fica na biblioteca.

## Log

Depois de cada arquivo salvo, um JSON de mesmo nome-base ao lado:

```json
{
  "model": "modelo-usado",
  "route": "fal",
  "prompt": "o texto exato enviado à API",
  "refs": ["refs/logo.png"],
  "params": { "aspect": "16:9", "size": "2K" },
  "cost_usd": 0.05,
  "created": "2026-08-01T09:41:00Z"
}
```

`scripts/gerar.py` já escreve isso. O contrato é simples: mesmo nome-base,
extensão `.json`. Daqui a três meses, alguém olha uma imagem, quer o prompt que
a fez, e ele está ali — inclusive numa busca de arquivos comum.

## Scripts

```bash
# gerar (cota antes com --estimar, roda com --confirmar)
python3 <SKILL_DIR>/scripts/gerar.py --rota fal --model <model-id> \
  --prompt "..." --projeto capa-lp --desc "hero" --custo 0.04 --estimar
python3 <SKILL_DIR>/scripts/gerar.py ... --confirmar

# vídeo assíncrono: submete, faz poll, baixa e loga (guarda o task id)
python3 <SKILL_DIR>/scripts/gerar.py --rota kie --model <model-id> \
  --prompt "..." --projeto x --desc y --custo 1.75 --async --confirmar

# quanto já gastei (mostra também runs cobrados que não viraram arquivo)
python3 <SKILL_DIR>/scripts/registrar.py --saldo

# corrigir um lançamento com o valor real da fatura
python3 <SKILL_DIR>/scripts/registrar.py --corrigir <run_id> --cost 1.75
```

`--estimar` só imprime a cotação e sai sem gastar nada. É o que se mostra à
pessoa antes de pedir o "pode". Sem `--confirmar`, o script se recusa a chamar
a API — a aprovação fica explícita no comando, não na memória do agente.

## Chaves

Ler em runtime do `.env` da pasta de trabalho. Nunca colar a chave dentro de
código, nunca imprimir o valor, nunca commitar o `.env` (ele entra no
`.gitignore` no primeiro dia). Se uma chave vaza, quem paga a conta é o dono
dela.

## Referências reais, nunca descritas

Um logo descrito em palavras volta errado toda vez: forma errada, cor errada,
detalhe inventado. Se o pedido envolve uma marca, um rosto ou um estilo
específico, o arquivo real precisa estar em `refs/` e ser passado na chamada.
Se não estiver, **pare e peça**. Custa uma pergunta; adivinhar custa cinco
gerações erradas, e aqui cada uma delas é paga.

## Uma de cada vez

Gerações em série, não em paralelo. Rate limit devolve erro que, dependendo do
provider, já foi cobrado.

## Cuidado com upload

Alguns providers oferecem "sobe o arquivo e recebe uma URL pública" para mandar
uma imagem local como referência. Isso **publica** o arquivo. Rosto de cliente,
documento, material sob NDA ou peça não lançada não sobem sem alguém decidir
isso conscientemente.

## Adicionar um modelo novo

Modelos mudam de mês em mês. Quando sair um melhor: copie
`models/_template.md`, preencha com a doc do provider (dez minutos), e adicione
a linha em `references/pricing.md` com a data. Nada mais muda — é por isso que a
receita mora num arquivo só dela.

Se uma chamada voltar "model not found", o ID envelheceu: abra a página do
modelo, copie o ID novo, atualize a receita. É a única manutenção que este
sistema pede.
