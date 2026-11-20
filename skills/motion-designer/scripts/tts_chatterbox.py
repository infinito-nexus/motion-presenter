import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import librosa
import numpy as np
import torch
import torchaudio

DEVICE = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
SEEDS = (1, 2, 3)
REVISIONS = {
    "ResembleAI/chatterbox": "5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18",
    "ResembleAI/chatterbox-turbo": "749d1c1a46eb10492095d68fbcf55691ccf137cd",
}
lines = json.loads(Path(sys.argv[1]).read_text())
cache = Path(sys.argv[2])
_model = None


def weights(repo, files=None):
    from huggingface_hub import hf_hub_download, snapshot_download
    if files:
        return Path([hf_hub_download(repo, f, revision=REVISIONS[repo]) for f in files][0]).parent
    return snapshot_download(repo_id=repo, revision=REVISIONS[repo],
                             allow_patterns=["*.safetensors", "*.json", "*.txt", "*.pt", "*.model"])


def model():
    global _model
    if _model is None:
        from chatterbox.tts import ChatterboxTTS
        files = ["ve.safetensors", "t3_cfg.safetensors", "s3gen.safetensors", "tokenizer.json", "conds.pt"]
        _model = ChatterboxTTS.from_local(weights("ResembleAI/chatterbox", files), DEVICE)
    return _model


def turbo_sample(voice):
    path = cache / f"{voice}-voice.wav"
    if not path.exists():
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        turbo = ChatterboxTurboTTS.from_local(weights("ResembleAI/chatterbox-turbo"), DEVICE)
        torch.manual_seed(11)
        wav = turbo.generate("Hi there. Let me show you something simple. You add what you spend, and you always know "
                             "where your money went, what is left for the month, and what comes next.")
        torchaudio.save(str(path), wav, turbo.sr)
    return str(path)


def measure(wav, sr):
    y = librosa.resample(wav.squeeze(0).numpy(), orig_sr=sr, target_sr=16000)
    rms = librosa.feature.rms(y=y, frame_length=320, hop_length=320)[0]
    voiced = np.where(rms > rms.max() * 0.03)[0]
    body = rms[voiced[0]:voiced[-1] + 1] if len(voiced) else rms
    gap = run = 0
    for v in body:
        run = run + 1 if v < rms.max() * 0.02 else 0
        gap = max(gap, run)
    f0, ok, _ = librosa.pyin(y, fmin=60, fmax=420, sr=16000)
    f0 = f0[ok]
    semis = 12 * np.log2(f0 / np.median(f0)) if len(f0) > 10 else np.zeros(1)
    return {"length": len(body) * 0.02, "gap": gap * 0.02, "range": float(np.percentile(semis, 90) - np.percentile(semis, 10))}


report_path = cache / "takes.json"
report = json.loads(report_path.read_text()) if report_path.exists() else {}
for line in lines:
    s = dict(line.get("settings", {}))
    kw = {k: s[k] for k in ("exaggeration", "cfg_weight", "temperature") if k in s}
    sample = s.get("sample")
    if sample == "turbo":
        kw["audio_prompt_path"] = turbo_sample(line["voice"])
    elif sample:
        kw["audio_prompt_path"] = sample
    lo, hi = line.get("fit", (0.8, 1.3))
    takes = []
    for seed in SEEDS:
        seed += len(SEEDS) * line.get("attempt", 0)
        torch.manual_seed(seed)
        wav = model().generate(line["text"], **kw)
        m = measure(wav, model().sr)
        ratio = m["length"] / line["plain"]
        miss = max(lo - ratio, ratio - hi, 0)
        takes.append((miss, abs(m["range"] - 8), seed, wav, m))
    takes.sort(key=lambda x: (x[0], x[1]))
    miss, _, seed, wav, m = takes[0]
    if miss:
        print(f"{line['id']}: no take within {lo}-{hi}x, keeping the closest", flush=True)
    torchaudio.save(str(cache / f"{line['id']}.wav"), wav, model().sr)
    report[line["id"]] = {"seed": seed, "text": line["text"], **m}
    print(f"{line['id']}: take {seed}, {m['length']:.2f}s, pitch range {m['range']:.1f} semitones  {line['text']}", flush=True)
report_path.write_text(json.dumps(report, indent=1))
