# /generate — versão local

Skill de geração de imagem e vídeo para uma máquina que **tem modelo rodando
nela**. Um comando só: o agente escolhe a rota, prepara as referências, gera,
salva plano numa pasta única e escreve um log ao lado de cada arquivo.

Aqui a rota mais barata capaz **é local e custa zero**, e é isso que muda tudo
em relação ao desenho original da ideia (que assume toda geração paga e remota).

## O que a skill faz

Quando você escreve algo como *"gera uma capa sobre X"*, o agente roda quatro
passos:

1. **Rotear** — escolher a rota e ler a receita daquele modelo.
2. **Preparar referências** — carregar as imagens reais de `refs/` (logotipos,
   rostos, estilo). Nunca descrever um logo em palavras.
3. **Gerar** — chamar conforme a receita; se for assíncrono, consultar o status
   e baixar na hora, porque URL de resultado expira.
4. **Registrar** — um JSON ao lado da mídia com prompt, modelo, parâmetros e
   custo.

## Roteamento

| Tarefa | Rota | Custo |
|---|---|---|
| Imagem (qualquer coisa) | inemaimg / flux2-klein na GPU local | **$0** |
| Imagem com texto legível dentro | fal.ai / GPT Image 2 | ~$0,05 |
| Vídeo a partir de imagens (câmera, parallax 2.5D) | skill `pixflow-motion`, local | **$0** |
| Vídeo generativo (movimento que não existe na cena) | Kie AI / Kling | pago, cota antes |

Com custo marginal zero, a regra clássica *"rascunhe barato, finalize caro"*
perde o sentido: rascunho e final são o mesmo modelo. Sobram **duas razões
honestas** para pagar, e só elas:

- a imagem precisa de **texto legível** renderizado dentro (modelos locais de
  4–9B erram letra de forma previsível);
- o pedido é **vídeo generativo** — movimento que não pode ser extraído das
  imagens existentes. Se couber em câmera sobre imagem parada, o pixflow resolve
  de graça e com mais controle.

## Estrutura

```
generate/
├── SKILL.md                     as regras — o agente lê isto toda vez
├── models/
│   ├── flux2-klein-local.md     a rota padrão, verificada
│   ├── pixflow-local.md         vídeo local
│   ├── gpt-image-2-fal.md       rota paga: texto na imagem
│   └── kling-kie.md             rota paga: vídeo generativo
├── references/pricing.md        preços com data
└── scripts/
    ├── gerar-local.py           gera + salva + loga, num passo
    └── registrar.py             loga arquivo externo · `--saldo`
```

Por que uma receita por modelo: modelos mudam todo mês. Quando sair um melhor,
você adiciona **um** arquivo Markdown e a skill aprende. Nada mais muda.

Por que as regras dentro do SKILL.md: o agente relê a cada uso. Limite de custo
e regra de pasta escritos uma vez passam a valer sempre.

## Instalar

```bash
cp -r generate-local ~/.claude/skills/generate
```

Requer o servidor do `inemaimg` no ar (`~/projetos/inemaimg`, porta 8000). A
skill checa `/health` antes de gerar e, se estiver fora, **falha dizendo como
subir** em vez de cair silenciosamente para uma rota paga.

## Uso

```bash
# imagem local — o caminho de todo dia
python3 scripts/gerar-local.py --prompt "..." --projeto capa-curso --desc hero
python3 scripts/gerar-local.py --prompt "..." --projeto x --desc y -n 3   # variações

# registrar algo que veio de fora (rota paga, ou saída do pixflow)
python3 scripts/registrar.py --file v.mp4 --model kling --route kie \
    --prompt "..." --cost 1.75

# quanto já gastei
python3 scripts/registrar.py --saldo
```

Saída em `~/projetos/output/generations/`, plana, com `refs/` dentro.

## Pasta plana

Todos os arquivos num lugar só, sem subpastas. Parece bagunça e é o contrário:
qualquer galeria, script ou busca lê a biblioteca inteira sem configuração — e
meses depois ninguém precisa lembrar do critério de organização que usou.

Isto é uma exceção deliberada ao padrão `~/projetos/output/<projeto>/`. Entrega
final continua indo para a pasta do projeto: **copie** o arquivo, não mova.

## Portão de custo

Quase nunca dispara, mas está lá:

- Antes de qualquer chamada paga: declarar rota, modelo, quantidade/duração e o
  dólar, e esperar um "pode" explícito. Cotar não é aprovar; **uma aprovação
  vale uma execução**.
- Se o acumulado do mês passar de **$20**, avisar antes de pedir aprovação. Um
  portão que só olha uma execução por vez deixa passar trinta gastos de $2.

## Log

Um JSON de mesmo nome-base ao lado de cada arquivo: modelo, rota, prompt,
referências, parâmetros, custo, data. Os scripts escrevem sozinhos. Daqui a três
meses, quando alguém olhar uma imagem e quiser o prompt que a fez, ele está ali
— inclusive numa busca de arquivos comum.

## Chaves

Lidas em runtime de `~/projetos/wifi/.env` (`FAL_KEY`, `KIE_API_KEY`). Nunca
copiadas para outro arquivo, nunca impressas, nunca coladas em código.

## O que está verificado e o que não está

Verificado por chamada real (2026-08-01): o endpoint do inemaimg, o campo
`image` na resposta, o tempo de ~6 s, e o ciclo completo gerar → salvar → log →
saldo, incluindo a falha limpa com o servidor fora do ar.

**Não verificado:** os IDs e preços das rotas pagas (`openai/gpt-image-2`,
`kling-3.0/video`) — vieram de material de terceiros e estão marcados como tal
nas receitas. Confirme na página do provider antes do primeiro uso e troque a
marca por `verificado em AAAA-MM-DD`. Um ID envelhecido devolve "model not
found" e gasta a chamada.

Referência técnica geral (autenticação por provider, padrão assíncrono, tabela
de modelos): `doc/guia-skill-generate-ptbr.md`.
