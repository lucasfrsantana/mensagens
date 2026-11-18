---
name: terror-short
description: Produz um short de terror vertical 9:16 de 60s a partir de um jogo 3D em HTML (Three.js) — versão em vídeo com roteiro automático, legendas, trilha procedural e botão de gravar; texto das vozes para a ElevenLabs; e montagem do MP4 final com as vozes sincronizadas. Use quando o usuário trouxer um novo jogo HTML de terror para virar vídeo, pedir "faça o mesmo" para outro jogo, mandar narrações da ElevenLabs ou uma gravação de um episódio, ou pedir o vídeo final de um episódio da pasta terror-shorts.
---

# Terror Short 9:16

Projeto: `~/Documentos/terror-shorts/` no Linux ou `~/Documents/terror-shorts/` no Windows/Mac
(use a que existir; no Windows rode o script com `python` em vez de `python3`) (leia o `README.md` de lá: estrutura, regras do formato e
contrato do `video_9x16.html`). Script: `scripts/terror.py` (`texto`, `plano`, `montar`).
Responda em português do Brasil.

## Etapas

Descubra em que etapa o episódio está olhando os arquivos da pasta e continue dali.

### 1. Novo episódio
- Crie `episodios/NN-nome/` (NN = próximo número) e mova o jogo para `jogo.html`
  (mova, não copie; se estiver em Downloads, diga que moveu).
- Leia o jogo inteiro antes de escrever qualquer coisa.

### 2. `video_9x16.html`
- Parta do `video_9x16.html` do episódio mais recente: mantenha compositor, gravação, UI,
  `ScoreAudio` (helpers + corte de silêncio) e o formato das legendas; troque cena, `CAM_KEYS`,
  `SEGMENTS`, `SUBTITLES`, eventos e `scheduleRun`.
- Roteiro de 60s: gancho forte em 0–5s, escalada, **silêncio absoluto** (corta a saída mestre),
  clímax, investida final e **corte seco para preto ~57s**, com uma linha curta no preto.
- **Corrija incoerências da história do jogo** (objetos que não poderiam estar onde estão, trancas
  que somem, falas que contradizem a ação, horários) e liste-as para o usuário com a correção.
  Prefira transformar a incoerência em ponto da trama.
- Legendas em primeira pessoa do personagem; falas de outras pessoas ganham `voice` próprio
  (ex.: `voice: "radio"` + cor verde). Frase-chave em vermelho.
- Tudo determinístico em função de `t`. Valide com Chrome headless renderizando `?t=` em 7–9
  instantes (swiftshader) e olhe os quadros; corrija enquadramentos bloqueados por objetos.

### 3. Vozes
- Rode `python3 scripts/terror.py texto <episódio>` e entregue um bloco de texto por voz.
- Explique: um arquivo por voz na ElevenLabs; voz do rádio gerada limpa; salvar como
  `voz_<nome>.*` na pasta do episódio. O narrador costuma ser a voz "Lax Whisper".

### 4. Gravação
- O usuário grava no Chrome (botão **Gravar Vídeo 60s**) e o arquivo vai para Downloads.
  Mova para a pasta como `gravacao.mp4` (ou `.webm`). Se não achar, procure em `~` antes de pedir.

### 5. Final
- Mova as vozes de Downloads para a pasta com os nomes do contrato.
- `python3 scripts/terror.py plano <episódio>`: confira se cada fala caiu na legenda certa
  (o texto ao lado de cada linha). Se algo estiver estranho, investigue o áudio
  (envelope por banda) antes de montar.
- `python3 scripts/terror.py montar <episódio>` → `final.mp4`.
- Relate: onde ficou, duração/codec, avisos do plano (ex.: rádio tocado contínuo — "confira de ouvido"),
  e o que não foi verificado (você não ouve o áudio).
