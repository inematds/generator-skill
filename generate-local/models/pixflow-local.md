# pixflow — vídeo a partir de imagens, local e de graça

Não é um modelo de vídeo: é um motor de render (depth + parallax 2.5D + câmera +
grain/LUT/vinheta) que transforma imagens paradas em plano de filme. Roda local,
determinístico, custo zero. **É a rota padrão de vídeo neste setup.**

| Campo | Valor |
|---|---|
| Como chamar | skill `pixflow-motion` (e `pixflow-trailer` para peça narrada inteira) |
| Método | render local (Depth-Anything-V2 → Three.js/GLSL → Remotion → FFmpeg) |
| Tipo | Vídeo |
| Custo | **$0** |
| Entrada | uma ou mais imagens (tipicamente geradas pelo flux2-klein) + movie spec YAML |

## Quando isto resolve

Praticamente todo "faz um vídeo disso" que nasce de imagem parada: push-in,
travelling, ken burns com profundidade real, transição entre planos, look de
cinema, trailer com narração e trilha. O resultado é mais controlável que
vídeo generativo — você escolhe o movimento em vez de torcer para o modelo
acertar.

## Quando isto NÃO resolve

Movimento que não existe na cena: alguém virando o rosto, líquido escorrendo,
tecido balançando, um objeto se transformando. Aí é vídeo generativo pago —
ver `kling-kie.md`, e cotar antes.

## Fluxo típico

1. Gerar os planos como imagem no flux2-klein (`gerar-local.py`).
2. Invocar `pixflow-motion` com essas imagens e a intenção de câmera.
3. Salvar o MP4 em `~/projetos/output/generations/` e escrever o sidecar com
   `registrar.py --cost 0 --route local:pixflow`.

Áudio (narração, trilha, SFX) vem do `inemavox`, não daqui — voz `rachel` no
engine `chatterbox`, música/SFX pelo downloader do próprio inemavox.
