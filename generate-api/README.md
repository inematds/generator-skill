# /generate — versão API

Skill de geração de imagem e vídeo para quem **não tem modelo rodando na própria
máquina**. Tudo passa por API paga. Um comando só: o agente escolhe a rota, cota
o custo, espera aprovação, gera, salva plano e registra o gasto.

Como aqui toda geração custa dinheiro, a skill vale menos pelo modelo que
escolhe e mais pelos três problemas que impede:

1. **Rota cara escolhida por distração** — preço em arquivo, com data, não por
   palpite do agente na hora.
2. **Conta que cresce sem ninguém ver** — cotação antes de cada execução **e**
   teto mensal acumulado.
3. **Prompt bom que se perde** — um JSON ao lado de cada arquivo, com prompt,
   modelo, parâmetros e custo.

## O que a skill faz

Quando alguém escreve *"gera uma miniatura sobre X"*, o agente roda:

1. **Rotear** — escolher o modelo e a rota mais barata capaz, e ler a receita.
2. **Cotar** — dizer o dólar e esperar o "pode".
3. **Preparar referências** — carregar as imagens reais de `refs/`. Nunca
   descrever um logo ou rosto em palavras.
4. **Gerar** — chamar conforme a receita; se for assíncrono, consultar o status
   e baixar imediatamente, porque URL de resultado expira em horas.
5. **Registrar** — sidecar JSON + linha no livro-caixa.

## Roteamento

| Tarefa | Rota | Custo aproximado |
|---|---|---|
| Imagem — rascunho, variação, exploração | modelo barato | $0,01–0,04 |
| Imagem — final, ou com texto legível dentro | modelo top | $0,05–0,15 |
| Vídeo | modelo de vídeo | $0,20–0,35 **por segundo** |

**A regra que mais economiza:** rascunhe no modelo barato e só rode no caro
depois que a pessoa escolher um favorito. A diferença entre $0,02 e $0,10 é
irrelevante numa imagem e é a fatura inteira em quarenta.

Vídeo é a via que surpreende: dez segundos custam o mesmo que cem rascunhos.
Nunca gerar vídeo "para ver como fica".

## Estrutura

```
generate/
├── SKILL.md                  as regras — o agente lê isto toda vez
├── models/
│   ├── _template.md          copie para registrar um modelo novo
│   ├── imagem-rascunho.md    a rota do dia a dia
│   ├── imagem-final.md       só depois de escolher um rascunho
│   └── video.md              a via cara, assíncrona
├── references/
│   ├── setup.md              chaves, config, primeira rodada
│   └── pricing.md            preços com data
└── scripts/
    ├── gerar.py              cota (--estimar) e executa (--confirmar)
    └── registrar.py          log externo · `--saldo` · `--corrigir`
```

Por que uma receita por modelo: modelos mudam todo mês. Modelo novo = um arquivo
Markdown de dez minutos, e nada mais muda. Se uma chamada voltar "model not
found", o ID envelheceu: abra a página do modelo, copie o ID novo, atualize a
receita. É a única manutenção que este sistema pede.

## Instalar

```bash
cp -r generate-api <workspace>/.claude/skills/generate
```

Depois siga `references/setup.md`: duas chaves (fal.ai e Kie AI), um `.env` no
`.gitignore`, e um `_config.json` com a pasta de saída e o teto mensal. Cinco
minutos, uma vez.

Dica de limite: **carregue pouco crédito no primeiro pagamento** ($10–20). É o
limite mais confiável que existe — o provider não gasta o que não tem.

## Uso

```bash
# cotar (não gasta nada — é isto que se mostra antes de pedir o "pode")
python3 scripts/gerar.py --rota fal --model <id> --prompt "..." \
    --projeto capa --desc hero --custo 0.04 --estimar

# executar, depois da aprovação
python3 scripts/gerar.py ... --confirmar

# vídeo assíncrono: submete, faz poll, baixa e guarda o task id
python3 scripts/gerar.py --rota kie --model <id> ... --custo 1.75 --async --confirmar

python3 scripts/registrar.py --saldo                         # quanto já gastei
python3 scripts/registrar.py --corrigir <run_id> --cost 1.9  # valor real da fatura
```

Sem `--confirmar` o script **se recusa** a chamar a API. A aprovação fica
explícita no comando, não na memória de quem está conduzindo.

## O livro-caixa

O lançamento acontece **quando o provider aceita o job**, antes de o arquivo
chegar. Isso é deliberado: se a geração falhar depois disso, o dinheiro já saiu
e precisa aparecer no saldo. `--saldo` mostra separadamente os runs que foram
cobrados e não viraram entrega:

```
2 run(s) cobrados sem arquivo salvo — dinheiro gasto que não virou entrega:
  1785564495-1f5462ee  incompleto  $0.40
  1785564495-fb8bb889  falhou      $2.00  task T3
```

O valor lançado é a **estimativa**; quando a fatura chegar, corrija com
`--corrigir`. Com o tempo o livro-caixa corrigido vira uma fonte de preço melhor
que a tabela.

## Pasta plana

Todos os arquivos num lugar só, sem subpastas, com `refs/` dentro. Parece
bagunça e é o contrário: qualquer galeria, script ou busca lê a biblioteca
inteira sem configuração. Entrega para o cliente final é uma **cópia** para a
pasta do trabalho — o original fica na biblioteca.

## Autenticação — o tropeço nº 1

Mesma ideia, três formatos diferentes. Acertar uma vez por provider resolve
todos os modelos dele:

| Provider | Como a chave viaja |
|---|---|
| fal.ai | cabeçalho `Authorization: Key {FAL_KEY}` |
| Kie AI | cabeçalho `Authorization: Bearer {KIE_API_KEY}` |
| Google AI Studio | na própria URL: `?key={GOOGLE_KEY}` |

`Key` vs `Bearer` é a causa mais comum de erro 401. O script já traduz 401/403 e
404 em mensagens que dizem o que fazer.

## Síncrono vs assíncrono

Modelos de imagem costumam responder com o resultado na mesma chamada. Modelos
de vídeo devolvem um id de job e exigem consulta periódica ao status. Anote qual
é qual na receita de cada modelo: confundir os dois é a razão nº 1 de uma
primeira chamada parecer travada.

No assíncrono, o **task id é salvo no log assim que existe**. Se o poll cair, o
job continua rodando e já foi pago; com o id em mãos consulta-se o resultado
depois, em vez de pagar de novo.

## Cuidado com upload

Alguns providers oferecem "sobe o arquivo e recebe uma URL pública" para mandar
uma imagem local como referência. Isso **publica** o arquivo. Rosto de cliente,
documento ou peça sob NDA não sobem sem alguém decidir isso conscientemente.

## Sobre os IDs de modelo

Todo ID marcado **NÃO VERIFICADO** veio de material de terceiros, não de uma
chamada real. Confirme na página do provider antes do primeiro uso e troque a
marca por `verificado em AAAA-MM-DD`.

## O que foi testado

Exercitado de verdade, sem gastar: cotação, recusa quando falta `--confirmar`,
aviso de estouro de teto, erro claro de chave ausente, extração da mídia em
quatro formatos de resposta (URL do fal, JSON aninhado do Kie, base64 puro,
data-URI), e — com as respostas do provider simuladas — os três caminhos de
perda de dinheiro: resposta sem mídia, job que falha no provider, e o envelope
`{"msg":"success","data":{"state":"waiting"}}`, que não pode ser lido como job
pronto. Nos três, o gasto aparece no `--saldo` marcado como pendente.

**Não testado contra a API real:** os corpos de request/response de cada modelo
e as mensagens de 401/403/404 — dependem de chave e crédito. É o primeiro passo
de quem instalar, sempre com `--estimar` antes.

Referência técnica geral (autenticação, padrão assíncrono, tabela de modelos):
`doc/guia-skill-generate-ptbr.md`.
