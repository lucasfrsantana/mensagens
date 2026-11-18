---
name: boa-noite
description: Cria um vídeo vertical 9:16 de "Boa noite" (12 s) a partir de uma imagem enviada pelo usuário — zoom lento, estrelas piscando, vaga-lumes, brilho da lua, fumaça, luz nas janelas, lago ondulando, estrela cadente, texto espiritual criativo, chamada de compartilhamento com coração pulsando e trilha suave gerada. Use quando o usuário mandar uma imagem e pedir "boa noite", mensagem de boa noite ou "faça o mesmo" do vídeo de boa noite.
---

# Vídeo de Boa Noite

O usuário só envia a imagem (e às vezes um tema/frase). Você faz o resto, **sem perguntar nada** e **rápido**.

Arquivos desta skill (`~/.claude/skills/boa-noite/`): `boanoite.py` (renderiza), `audio.py` (trilha), `fonts/`.

## Passos

1. **Olhe a imagem** (Read). Anote, em pixels da imagem ORIGINAL (dimensões via `python3 -c "from PIL import Image;print(Image.open('IMG').size)"`; se a imagem foi mostrada reduzida, multiplique pelo fator informado):
   - `moon`: `[x, y, raio]` da lua (se houver; senão omita — as estrelas ignoram essa área).
   - `stars_max_y`: y abaixo do qual não há céu (horizonte).
   - `windows`: `[x, y]` do centro das janelas acesas (omita se não houver casa).
   - `chimney`: `[x, y]` da boca da chaminé (omita se não houver — sem isso não há fumaça).
   - `water`: `[y_topo, y_base]` do lago/mar (omita se não houver água).
   - `reflection_x`: x do reflexo da lua na água.
   - `shooting_from` / `shooting_to`: início e fim da estrela cadente, numa área vazia do céu.
   Se a imagem NÃO tiver essas coisas, omita as chaves: os efeitos correspondentes ficam desligados. (Sem config nenhum, valem os padrões da imagem original da casa no lago.) Para localizar coordenadas, corte e veja regiões com PIL (`crop`) — uma ou duas checagens bastam.

2. **Escreva um config JSON** no scratchpad com os textos. Seja criativo e mude a mensagem a cada vídeo (espiritual, acolhedora, em português, curta):
   ```json
   {"title":"Boa noite","line1":"frase curta 1","line2a":"frase 2 linha a","line2b":"frase 2 linha b",
    "share":"Envie esta paz para quem você ama","share2":"e durma com o coração leve",
    "moon":[1142,578,206],"stars_max_y":1600,"windows":[1092,1893],"chimney":[1122,1792],
    "water":[2045,2420],"reflection_x":1000,"shooting_from":[560,420],"shooting_to":[130,760],
    "title_y":70,"fast":false}
   ```
   Limites de texto: `line1` ≤ ~34 caracteres, `line2a/b` ≤ ~30 cada (largura 1080). O título pode variar ("Boa noite", "Boa noite, abençoada", "Durma em paz"). **Sempre** manter a chamada de compartilhamento ("compartilhe/envie para quem você ama") com o coração. Se o título ficar sobre a lua ou algo importante, ajuste `title_y`.

3. **Gere a trilha e renderize** (use o scratchpad como pasta de trabalho; as fontes já são achadas pelo script):
   ```bash
   cd <scratchpad> && python3 ~/.claude/skills/boa-noite/audio.py   # grava trilha.wav no diretório atual
   python3 ~/.claude/skills/boa-noite/boanoite.py IMAGEM.jpg SAIDA.mp4 trilha.wav config.json
   ```
   - Renderização em 1080x1920 leva ~5 min; com `"fast": true` (720x1280) ~2 min. **Padrão: use `fast: true` sem perguntar** (o usuário quer rapidez) e rode com `run_in_background`; só renderize em 1080p se ele pedir qualidade máxima.
   - Salve em `~/Downloads/Boa_noite_<nome>.mp4`.

4. **Confira UM quadro** (ex.: `ffmpeg -ss 11 -i SAIDA.mp4 -frames:v 1 c.jpg`) para ver se texto não cobre elementos importantes e está legível. Corrija só se houver problema real, senão entregue.

5. **Responda curto**: caminho do arquivo, os textos usados e uma linha sobre as animações.

## Notas
- Dependências: Python com numpy, scipy, Pillow e ffmpeg (já instalados).
- A imagem deve ser vertical, de preferência noturna/escura (o brilho das estrelas é aditivo).
- Estrelas são detectadas automaticamente como pontos brilhantes pouco saturados; vaga-lumes são adicionados na parte de baixo da imagem.
