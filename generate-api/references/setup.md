# Setup — cinco minutos, uma vez

## 1. Duas chaves

Você não precisa de conta em cada laboratório de IA. Agregadores hospedam
dezenas de modelos atrás de uma chave e uma fatura só.

| Provider | Cadastro | Nome da chave | Por que está aqui |
|---|---|---|---|
| fal.ai | fal.ai | `FAL_KEY` | Catálogo grande, a melhor documentação. Rota principal. |
| Kie AI | kie.ai | `KIE_API_KEY` | Costuma ser a rota mais barata dos modelos populares. Fallback. |

Duas bastam para começar. Só adicione um terceiro provider quando faltar um
modelo específico — cada provider a mais é mais uma fatura para conferir.

Ambos cobram por uso, com crédito pré-pago. **Coloque um valor pequeno no
primeiro carregamento** ($10–20). É o limite mais confiável que existe: o
provider não gasta o que não tem.

## 2. O arquivo `.env`

Na pasta de trabalho:

```
FAL_KEY=sua_chave_aqui
KIE_API_KEY=sua_chave_aqui
```

E, imediatamente, coloque `.env` no `.gitignore`. Chave commitada em repositório
é varrida por robô em minutos, e a conta é sua.

## 3. Configuração da skill

`scripts/gerar.py` cria `_config.json` na primeira execução. Ajuste os dois
campos:

```json
{
  "pasta": "~/generations",
  "teto_mensal_usd": 50
}
```

- **pasta** — onde tudo é salvo, plano. Escolha uma e não mude mais: a
  biblioteca inteira depende de ficar num lugar só.
- **teto_mensal_usd** — a partir daqui a skill avisa antes de cotar. Não é
  bloqueio, é a luz do painel. Comece baixo; é fácil subir depois.

## 4. Primeira rodada

```bash
python3 scripts/gerar.py --rota fal --model <id-do-modelo-de-imagem> \
  --prompt "um cubo vermelho sobre fundo bege" \
  --projeto teste --desc cubo --custo 0.04 --estimar
```

Isso **não gasta nada** — imprime a cotação. Repita com `--confirmar` para
rodar de verdade. Se voltar erro de autenticação, quase sempre é a palavra do
cabeçalho: fal usa `Key`, Kie usa `Bearer`. É o tropeço nº 1.

## 5. Ordem de leitura

1. `SKILL.md` — as regras.
2. `models/_template.md` — como registrar cada modelo.
3. `references/pricing.md` — quanto custa cada rota, com data.

## Custos típicos, para calibrar expectativa

| Trabalho | Ordem de grandeza |
|---|---|
| Imagem de rascunho | $0,01–0,03 — itere à vontade |
| Imagem final, modelo top | $0,05–0,15 — só depois de escolher um rascunho |
| Vídeo | $0,20–0,35 **por segundo** — 10 s custam $2 a $3,50 |

A linha do vídeo é a razão de o portão de custo existir. Uma tarde explorando
vídeo sem cotação vira uma fatura de três dígitos sem ninguém perceber.
