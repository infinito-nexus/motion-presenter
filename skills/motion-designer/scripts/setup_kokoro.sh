#!/usr/bin/env bash
set -euo pipefail
home="${MOTION_DESIGNER_HOME:-$HOME/.cache/motion-designer}"
venv="${MOTION_DESIGNER_KOKORO_VENV:-$home/kokoro}"
models="${MOTION_DESIGNER_KOKORO_MODELS:-$venv/models}"
command -v uv >/dev/null || { echo "uv is required: https://docs.astral.sh/uv/getting-started/installation/" >&2; exit 1; }
uv venv "$venv" --python 3.12
VIRTUAL_ENV="$venv" uv pip install "kokoro-onnx==0.6.1" "soundfile==0.14.0"
mkdir -p "$models"
base=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
sha256() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }
while read -r sum file; do
  [ -s "$models/$file" ] || curl -fL --retry 3 -o "$models/$file" "$base/$file"
  [ "$(sha256 "$models/$file")" = "$sum" ] || { rm -f "$models/$file"; echo "$file: sha256 mismatch, deleted it" >&2; exit 1; }
done <<'SUMS'
7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5 kokoro-v1.0.onnx
bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d voices-v1.0.bin
SUMS
"$venv/bin/python" -c "from kokoro_onnx import Kokoro; k = Kokoro('$models/kokoro-v1.0.onnx', '$models/voices-v1.0.bin'); print('Kokoro ready:', len(k.get_voices()), 'voices in', '$venv')"
echo "Point voiceover.py at it with MOTION_DESIGNER_KOKORO_PYTHON=$venv/bin/python (and MOTION_DESIGNER_KOKORO_MODELS=$models) if it is not the default path."
