# motion-presenter

Narrated presentation films and multi-chapter demo series for any product or project, made by an agent from code and existing screen recordings. One look, one narrator voice and one track across every chapter. Text and voice can change later without re-rendering the picture.

## How to use it

Type `/motion-presenter` and say what you want to present. The agent first asks about:

- **Theme:** the neutral default theme, or your own colours, logo and fonts
- **Voice:** Bella (default), or your own sample, with consent
- **Music:** the default track, your own, or a free track it finds for you
- **Series:** chapters, length per chapter, language
- **People and story rules:** names on screen (they go into `scenes.json`), what must never show, how logins are handled
- **Scenes:** it proposes scenes from the scene library for each chapter, and you swap them

Later changes ("change this line", "other voice", "louder music") go the cheapest way: text, voice and music need no re-render (see `reference/changes.md`).

Author: Alejandro Roman. The film engine is the sibling skill `../motion-designer`, [motion-designer](https://github.com/kaventro/motion-designer) by kaventro (MIT, see the repository's `LICENSE` and `NOTICE`).

## Install

The repository README has the install command; it installs both skills side by side, which is how this skill finds the engine. Then install the tools (Ubuntu / Debian):

```bash
bash <skills folder>/motion-presenter/install.sh
```

It checks each requirement below, installs only what is missing, asks before every `sudo` step, and ends with a full check. Options: `--yes` answers yes to everything, `--no-voice` skips the 4 GB Chatterbox install, and `--kokoro` adds the small draft voices. Running it again is safe. It does not link the skills anywhere; the skills installer owns that.

On other systems, install the tables below by hand and run `../motion-designer/scripts/doctor.sh`.

## Requirements

### Required

| Tool | Version | Why | Install (Ubuntu) |
|---|---|---|---|
| Node.js | 22 or newer | drives headless Chrome for checks and renders | `bash ../motion-designer/scripts/install.sh node` |
| Chrome | Chrome, Chromium or Chrome for Testing | draws every frame | `bash ../motion-designer/scripts/install.sh chrome` (no admin rights, goes to `~/.cache/motion-designer`; set `CHROME=/path` to use your own) |
| ffmpeg + ffprobe | 6.x | video encoding, audio cuts and mixes, footage edits | `sudo apt install ffmpeg` |
| Python | 3.9 or newer | music analysis, voice pipeline, single-file build | preinstalled |
| uv | any | creates the Python environments for the voice models | `bash ../motion-designer/scripts/install.sh uv` |
| Pillow | any | contact sheets for checking stills | `sudo apt install python3-pil` |

Check everything at once:

```bash
bash <skills folder>/motion-designer/scripts/doctor.sh
```

### Voice (the default narrator)

| Tool | Size | Why | Install |
|---|---|---|---|
| Chatterbox | about 4 GB, plus about 3 GB of model weights on first use | clones the narrator from `defaults/voice/narrator.wav` | `bash ../motion-designer/scripts/install.sh chatterbox` |
| Kokoro (optional) | about 0.6 GB | fast preset voices for timing drafts only; flatter delivery | `bash ../motion-designer/scripts/install.sh kokoro` |

Keep the model weights out of `/tmp` so they survive a reboot: run the voice pipeline once, then `cp -r /tmp/motion-presenter-cache/hf/hub/* ~/.cache/huggingface/hub/`, and from then on set `HF_HOME=~/.cache/huggingface`.

### Fonts

The neutral theme uses DejaVu Sans and DejaVu Sans Mono, which most Linux systems have. A project theme names its own fonts; pack them into each film with `assets.py --font`, so they must exist on the machine that builds it.

### Hardware

| | Minimum | Used for this skill's first series |
|---|---|---|
| CPU | 4 cores | 12 cores |
| RAM | 8 GB (16 GB with Chatterbox) | 62 GB |
| Disk | 10 GB free | about 12 GB with all models |
| GPU | not needed | none |

Expect about 1 s per frame at 1x (a 60 s chapter is about an hour; 2x supersampling about three times longer) and about 40 s per narration line with Chatterbox on CPU. Renders can run several chapters in parallel; voice generation runs one chapter at a time, because each Chatterbox process takes every core.

## What is bundled

| Path | What |
|---|---|
| `SKILL.md` | setup interview, theme and scene data inputs, defaults and the series workflow the agent follows |
| `reference/scenes.md` | scene library: 15 ready scenes, when to use them, and the scene data contract |
| `reference/theme.md` | the theme contract: tokens and logo |
| `reference/changes.md` | how to change a finished film, cheapest path first |
| `reference/voice.md` | voice setup, timing and playback lessons |
| `defaults/scenes/` | working example code for every scene in the library and the neutral example data `scenes.json` |
| `defaults/theme/` | the neutral default theme (`film.css`) and logo |
| `tools/film.py` | voice-first `render`, `preview` (with the contact sheet), `render <series> --chapter NN`, `join` and `playground` |
| `tools/join.py`, `tools/contact_sheet.py`, `tools/playground.py` | the long video with chapter markers, the per-line contact sheet, the preset test pages |
| `tools/voice_all.py`, `tools/reflow.py` | v1 films with fixed start times: voice, re-time, mix and remux without a re-render |
| `defaults/voice/` | narrator sample and its consent terms |
| `defaults/music/` | "pulse" (default, original, made with ACE-Step 1.5) and "Industrial Cinematic" by Kevin MacLeod (CC BY 4.0), their beat grids and credit lines |

The engine features this skill relies on (voice-first timing with `timing.py`, `footage.py` and `silence.py`, the motion presets in `templates/shared/presets.js` and the preset playground) live in `../motion-designer`.

## Licences and private material

- Code: MIT (the repository's `LICENSE`); `NOTICE` lists the upstream commit and the credits.
- Music: "pulse" is original (ACE-Step 1.5, MIT, no attribution required; some platforms ask for AI-generated audio to be labelled). "Industrial Cinematic" is CC BY 4.0: every film that uses it credits it. Both credit lines are in `defaults/music/SOURCE.md`.
- Narrator voices: the default `narrator.wav` is Bella, a synthetic voice generated locally with Kokoro-82M (Apache-2.0), so films made with it are royalty-free. Voices of real people stay outside the skill.
- Chatterbox adds Resemble AI's inaudible watermark to generated speech.

## Watching the results on Linux

The films are H.264 with stereo AAC. If a player is silent, the player is the problem: `ffplay -autoexit <file>` proves the sound is there. For mpv, add `ao=pulse,alsa` to `~/.config/mpv/mpv.conf`; for GNOME Videos install `gstreamer1.0-libav`, or make mpv the default with `xdg-mime default mpv.desktop video/mp4`.
