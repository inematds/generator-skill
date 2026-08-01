# Crie sua própria skill `/generate`

Crie um único comando para seu agente de IA gerar imagens e vídeos sob demanda, selecionar o modelo adequado com o menor custo possível, controlar gastos e salvar todos os resultados em um único lugar.

> **Nota:** IDs de modelos, preços e endpoints mudam com frequência. Antes de usar em produção, confirme os dados na documentação atual de cada provedor.

---

## 1. O que você está construindo

Uma **skill** é uma pasta com arquivos Markdown que o agente lê antes de agir, como um manual operacional.

A skill `/generate` funciona como um manual para geração de mídia. Quando você escreve algo como:

```text
gere uma miniatura sobre X
```

o agente executa este fluxo:

1. **Roteamento**  
   Escolhe o modelo mais adequado para a tarefa e, entre os provedores disponíveis, seleciona a rota de menor custo. Depois, lê o arquivo de instruções daquele modelo.

2. **Preparação das referências**  
   Carrega imagens reais de referência, como logotipos, rostos e estilos, a partir da pasta `refs`. Não descreve logotipos ou rostos apenas em texto.

3. **Geração**  
   Chama a API conforme a receita do modelo. Se o processo for assíncrono, consulta o status até a conclusão. Salva o arquivo diretamente na pasta `generations`.

4. **Registro**  
   Cria um pequeno arquivo JSON ao lado da mídia, registrando prompt, modelo, parâmetros e referências utilizadas.

### Estrutura de pastas

```text
seu-workspace/
├── .claude/skills/generate/
│   ├── SKILL.md
│   └── models/
│       ├── image-model.md
│       └── video-model.md
├── generations/
│   └── refs/
└── .env
```

- `SKILL.md`: regras, roteamento e comportamento geral.
- `models/`: uma receita Markdown para cada modelo.
- `generations/`: todos os arquivos gerados, sem subpastas.
- `generations/refs/`: logotipos, rostos e referências reutilizáveis.
- `.env`: chaves de API.

### Por que usar uma pasta única

Todos os arquivos ficam em um único local. Isso facilita a leitura por galerias, dashboards, scripts e mecanismos de busca.

### Por que criar uma receita para cada modelo

Os modelos mudam com frequência. Quando surgir uma opção melhor, basta adicionar ou atualizar um arquivo Markdown. O restante da skill permanece igual.

### Por que manter regras dentro da skill

O agente lê essas regras sempre que a skill é acionada. Limites de custo, padrões de nome e exigências de referência passam a ser aplicados de forma consistente.

---

## 2. Configuração das chaves

Não é necessário ter conta em todos os laboratórios de IA. Provedores agregadores disponibilizam vários modelos por meio de uma única chave e uma única conta.

| Provedor | Site | Variável no `.env` | Finalidade |
|---|---|---|---|
| Kie AI | `kie.ai` | `KIE_API_KEY` | Costuma oferecer rotas econômicas e inclui upload de arquivos para gerar URLs públicas. |
| fal.ai | `fal.ai` | `FAL_KEY` | Catálogo amplo, boa velocidade e documentação consistente. |
| WaveSpeed AI | `wavespeed.ai` | `WAVESPEED_API_KEY` | Catálogo variado e útil como rota alternativa. |

Crie um arquivo `.env`:

```env
KIE_API_KEY=your_key_here
FAL_KEY=your_key_here
WAVESPEED_API_KEY=your_key_here
```

Adicione `.env` ao `.gitignore`:

```gitignore
.env
```

A skill deve orientar o agente a ler as chaves do `.env`, sem copiá-las para o código.

### Faixas aproximadas de custo

| Tarefa | Faixa aproximada | Observação |
|---|---:|---|
| Imagem de rascunho, modelo econômico | US$ 0,01 a US$ 0,03 | Use como padrão para testar ideias. |
| Imagem final, modelo de alta qualidade | US$ 0,05 a US$ 0,15 | Use apenas depois de escolher um rascunho. |
| Vídeo por segundo | US$ 0,20 a US$ 0,35 | Um vídeo de 10 segundos pode custar de US$ 2,00 a US$ 3,50. |

Esses valores são apenas referências do período em que o material original foi escrito.

---

## 3. Arquivo principal da skill

Crie:

```text
.claude/skills/generate/SKILL.md
```

O *frontmatter* informa quando a skill deve ser acionada. O corpo define o comportamento.

```md
---
name: generate
description: Generate images and videos via AI model APIs. Triggers on
/generate, generate image, generate video, create image, thumbnail,
animate.
---

# /generate

## Models

| Task | Default model | Recipe |
|---|---|---|
| Image (default) | your cheap image model | models/image-model.md |
| Image (quality) | your hero image model | models/image-model-pro.md |
| Video (default) | your video model | models/video-model.md |

Read the recipe file before every generation.

## Provider routing

1. Default to the LOWEST COST provider that runs the model well
   (check Kie AI, fal.ai, WaveSpeed AI).
2. If the cheapest route lacks the model, fails auth, or errors,
   fall back to the next provider.
3. Never hide a provider swap. Say which route ran and why.

## Output

- Save every file FLAT into my generations folder: [your path here]
- No subfolders. Reference images live in generations/refs/
- Naming: {project}_{description}_{timestamp}.{ext}

## Rules

- Quote the cost and wait for my explicit go before any paid
  video run. One approval = one run.
- Draft on the cheap image model first. Only rerun on a quality
  model when I pick a favourite.
- Never describe a logo or face in text. Pass the real image
  file as a reference. If it's missing, stop and ask me for it.
- Run multiple generations one at a time to avoid rate limits.
- After every save, write the sidecar log.
```

### Pontos importantes

1. A linha `description` é essencial: ela define quando o agente decide usar a skill.
2. Substitua `[your path here]` pelo caminho absoluto da sua pasta `generations`.
3. A seção `Rules` funciona como um contrato operacional.

---

## 4. Uma receita por modelo

Cada modelo deve ter um arquivo próprio dentro de:

```text
.claude/skills/generate/models/
```

Modelo de receita:

```md
# Model Name

One line on what this model is best at and when to pick it.

| Field | Value |
|---|---|
| Model ID | the-exact-model-id |
| Provider | Kie AI / fal.ai / WaveSpeed AI |
| Method | Sync or Async |
| Type | Image or Video |
| API key | .env -> KEY_NAME |
| Docs | link to the provider's page for this model |
| Cost | rough price per image / per second |

## Endpoint

POST https://...

## Request format

The exact JSON body from the provider documentation, including:

- prompt;
- aspect ratio;
- resolution;
- reference image fields.

## Response handling

Document where the final media appears in the response:

- a Base64 field;
- a downloadable URL;
- or, for asynchronous jobs, a status endpoint and completion field.

## Notes

Record limits, maximum sizes, content restrictions, upload details and provider-specific quirks.
```

### Padrão assíncrono

A maioria dos modelos de vídeo segue este processo:

1. Enviar o job e receber um `task_id`.
2. Consultar o endpoint de status a cada 5 a 10 segundos.
3. Aguardar o status de conclusão.
4. Obter a URL do arquivo final.
5. Baixar imediatamente, pois URLs temporárias podem expirar.
6. Salvar o arquivo e criar o log JSON.

Comece com duas receitas: um modelo econômico de imagem e um modelo de vídeo.

---

## 5. Modelos sugeridos no material original

> Os nomes, IDs e preços abaixo são uma tradução do documento fornecido e podem estar desatualizados.

| Modelo | Melhor uso | Provedor indicado | ID e observações |
|---|---|---|---|
| Nano Banana 2 | Imagens do dia a dia, velocidade e uso de referências | Google AI Studio e fal.ai | `gemini-3.1-flash-image-preview`; versão Lite: `gemini-3.1-flash-lite-image` |
| GPT Image 2 | Texto legível em imagens, cartazes, menus, embalagens e interfaces | fal.ai | `openai/gpt-image-2`; edição adiciona `/edit` |
| Kling 3.0 | Vídeo geral, movimento consistente e custo equilibrado | Kie AI | `kling-3.0/video`; `std` para 720p e `pro` para 1080p |
| Veo 3.1 | Vídeo de maior qualidade a partir de um quadro inicial | Google AI Studio | `veo-3.1-generate-preview` |
| Seedance 2.0 Fast | Animação de até 9 imagens de referência | fal.ai | `bytedance/seedance-2.0/fast/reference-to-video` |

### Formas de autenticação

#### Google AI Studio

A chave é enviada na URL:

```text
POST .../models/{model-id}:generateContent?key={GOOGLE_KEY}
```

#### fal.ai

A chave é enviada no cabeçalho com `Key`:

```text
POST https://fal.run/{model-id}
Authorization: Key {FAL_KEY}
```

#### Kie AI

A chave é enviada no cabeçalho com `Bearer`:

```text
POST https://api.kie.ai/api/v1/jobs/createTask
Authorization: Bearer {KIE_API_KEY}
```

### Síncrono ou assíncrono

Segundo o material original:

- GPT Image 2, Nano Banana e Seedance retornam o resultado final em uma chamada.
- Kling e Veo retornam um job ID e exigem consultas periódicas ao endpoint de status.

Registre esse comportamento na receita de cada modelo.

### Implementação inicial recomendada

Comece com:

- Nano Banana 2 Lite para imagens;
- Kling 3.0 para vídeos.

Isso permite aprender os dois padrões básicos: execução síncrona e assíncrona.

Depois, adicione outros modelos conforme a necessidade:

- GPT Image 2 para texto legível;
- Veo 3.1 para cenas de maior qualidade;
- Seedance 2.0 Fast para animação baseada em referências.

---

## 6. Regras de controle e segurança

### Informe o custo antes de gerar vídeo

Antes de executar uma geração paga de vídeo, o agente deve informar:

- modelo;
- duração;
- resolução;
- custo estimado.

Depois, deve aguardar uma aprovação explícita. Uma aprovação vale para apenas uma execução.

### Use modelos econômicos para rascunhos

Faça as primeiras tentativas com o modelo mais barato. Use um modelo de qualidade apenas quando o usuário escolher o rascunho final.

### Use referências reais

Não descreva logotipos ou rostos somente em texto. Coloque os arquivos reais em:

```text
generations/refs/
```

Depois, envie-os como referência na chamada da API.

### Use uma única pasta de saída

Salve todos os arquivos diretamente em `generations/`, sem subpastas. Isso simplifica integrações futuras.

---

## 7. Registre cada geração

Depois de salvar uma mídia, crie um arquivo JSON com o mesmo nome-base.

Exemplo:

```text
hero_thumbnail_1774912000.jpg
hero_thumbnail_1774912000.json
```

Conteúdo do JSON:

```json
{
  "model": "your-image-model",
  "prompt": "the full text prompt that was sent to the API",
  "refs": ["refs/logo.png", "refs/headshot.jpg"],
  "params": {
    "aspect": "16:9",
    "size": "2K"
  },
  "created": "2026-07-30T09:41:00Z"
}
```

Esse registro permite descobrir posteriormente qual prompt, modelo e configuração produziram cada arquivo.

---

## 8. Galeria local de resultados

O prompt abaixo cria uma página única para exibir todas as imagens e vídeos da pasta `generations`.

```text
crie para mim uma única página web que mostre todas as imagens e vídeos gerados pela minha IA em um só lugar, como uma parede em estilo bento.

- leia uma pasta do meu computador chamada generations e mostre tudo o que estiver nela, com os arquivos mais recentes no topo
- organize em uma parede masonry: cada bloco mantém sua proporção, sem cortes ou distorções, com cartões arredondados, espaçamento uniforme, quatro colunas em telas grandes e menos colunas em telas menores
- vídeos começam a tocar sem som quando o cursor passa sobre eles e param quando o cursor sai; imagens permanecem estáticas
- ao clicar em um item, abra-o ampliado no centro da tela; ao clicar fora, feche
- não adicione pesquisa, filtros, abas ou painéis laterais; mostre apenas a parede com todos os arquivos
- mantenha tudo em um único arquivo, para funcionar apenas abrindo-o no navegador, e entregue uma interface finalizada

quando a página estiver pronta, adicione uma linha ao meu arquivo CLAUDE.md determinando que, a partir de agora, tudo o que a skill /generate produzir seja salvo diretamente nessa mesma pasta generations, para aparecer automaticamente na página. não abra a página automaticamente a cada geração; apenas salve o arquivo na pasta.
```

A galeria funciona sem precisar ser atualizada manualmente porque a skill sempre salva os novos arquivos na mesma pasta.

---

## 9. Resultado final

Ao concluir a configuração, você terá:

1. Chaves de provedores armazenadas em um arquivo `.env`.
2. Um arquivo `SKILL.md` para roteamento, regras e controle de custos.
3. Uma receita Markdown para cada modelo.
4. Regras para aprovação de vídeo, uso de rascunhos econômicos e referências reais.
5. Um arquivo JSON ao lado de cada mídia gerada.
6. Uma galeria local que exibe automaticamente os resultados.

O fluxo passa a ser:

```text
/generate
→ interpretar a solicitação
→ escolher modelo e provedor
→ validar custo e referências
→ executar a API
→ salvar a mídia
→ criar o log JSON
→ exibir na galeria
```
