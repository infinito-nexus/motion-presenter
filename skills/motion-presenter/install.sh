#!/usr/bin/env bash
# Param: --yes       answer yes to every question (unattended install)
# Param: --no-voice  skip Chatterbox (about 4 GB); films still build, narration needs it later
# Param: --kokoro    also install Kokoro (about 0.6 GB) for quick timing drafts
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
engine="$here/../motion-designer/scripts"
yes=0 voice=1 kokoro=0
for arg in "$@"; do
  case "$arg" in
    --yes) yes=1 ;;
    --no-voice) voice=0 ;;
    --kokoro) kokoro=1 ;;
    -h|--help) sed -n '2,4p' "$0" | sed 's/^# Param: /  /'; exit 0 ;;
    *) echo "unknown option: $arg (try --help)" >&2; exit 2 ;;
  esac
done

has() { command -v "$1" >/dev/null 2>&1; }
say() { printf '\n\033[1;34m==>\033[0m %s\n' "$*"; }
ok() { printf '  \033[32m✓\033[0m %s\n' "$*"; }
ask() {
  [ "$yes" = 1 ] && return 0
  if [ ! -t 0 ]; then
    echo "  $1 skipped: no terminal to answer (run it in a terminal, or pass --yes)" >&2
    return 1
  fi
  read -r -p "  $1 [y/N] " reply || return 1
  case "$reply" in [yY]*) return 0 ;; *) return 1 ;; esac
}

if [ "$(uname -s)" != Linux ] || ! has apt-get; then
  echo "This installer covers Ubuntu and Debian. Elsewhere, follow README.md and run ../motion-designer/scripts/doctor.sh." >&2
  exit 1
fi

say "System packages"
pkgs=()
has ffmpeg || pkgs+=(ffmpeg)
python3 -c "import PIL" 2>/dev/null || pkgs+=(python3-pil)
fc-list 2>/dev/null | grep -qi "DejaVu Sans Mono" || pkgs+=(fonts-dejavu-core)
has curl || pkgs+=(curl)
dpkg -s gstreamer1.0-libav >/dev/null 2>&1 || pkgs+=(gstreamer1.0-libav)
if [ "${#pkgs[@]}" -eq 0 ]; then
  ok "ffmpeg, Pillow, DejaVu fonts, curl, AAC playback already installed"
elif ask "Install ${pkgs[*]} with sudo apt?"; then
  sudo apt-get update
  sudo apt-get install -y "${pkgs[@]}"
fi

say "Node.js 22+"
node_major="$(node -v 2>/dev/null | sed 's/^v\([0-9]*\).*/\1/' || true)"
if [ -n "$node_major" ] && [ "$node_major" -ge 22 ]; then
  ok "node $(node -v)"
elif ask "Install Node 22 (fnm, in your home folder, no sudo)?"; then
  bash "$engine/install.sh" node --yes
fi

say "uv"
if has uv; then ok "uv $(uv --version | cut -d' ' -f2)"; elif ask "Install uv?"; then bash "$engine/install.sh" uv --yes; fi

say "Chrome for rendering"
if bash "$engine/doctor.sh" 2>/dev/null | grep -q '✓ chrome'; then
  ok "chrome found"
elif ask "Install Chrome for Testing (about 150 MB, no sudo)?"; then
  bash "$engine/install.sh" chrome --yes
fi

if [ "$voice" = 1 ]; then
  say "Chatterbox narrator voice (about 4 GB, plus about 3 GB of weights on first use)"
  if bash "$engine/doctor.sh" 2>/dev/null | grep -q '✓ chatterbox'; then
    ok "chatterbox installed"
  elif ask "Install Chatterbox?"; then
    bash "$engine/install.sh" chatterbox --yes
  fi
fi
if [ "$kokoro" = 1 ]; then
  say "Kokoro draft voices"
  bash "$engine/install.sh" kokoro --yes
fi

say "Sound in mpv"
conf="$HOME/.config/mpv/mpv.conf"
if has mpv && ! grep -qs '^ao=' "$conf"; then
  if ask "Send mpv audio through PulseAudio (fixes silent playback on PipeWire)?"; then
    mkdir -p "$(dirname "$conf")"
    echo 'ao=pulse,alsa' >> "$conf"
  fi
else
  ok "nothing to do"
fi

say "Check"
bash "$engine/doctor.sh" || true
echo
echo "Done. The tools are in place; the skills installer links the skills (see the repository README)."
