import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/motion-designer/scripts"
INSTALL = SCRIPTS / "install.sh"
OUTER = ROOT / "skills/motion-presenter/install.sh"
PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")


def run(*args, **kw):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, stdin=subprocess.DEVNULL, **kw)


class Installers(unittest.TestCase):
    def test_engine_installer_refuses_without_terminal(self):
        p = run("bash", INSTALL, "swift")
        self.assertEqual(p.returncode, 1)
        self.assertIn("+ xcode-select --install", p.stdout)
        self.assertIn("No terminal", p.stderr)

    def test_engine_installer_dry_run_runs_nothing(self):
        p = run("bash", INSTALL, "swift", "--dry-run")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("+ xcode-select --install", p.stdout)

    def test_outer_ask_says_no_without_terminal(self):
        ask = re.search(r"^ask\(\) \{.*?^\}", OUTER.read_text(), re.S | re.M)[0]
        p = run("bash", "-c", f"{ask}\nyes=0\nask 'Install?' && echo YES || echo NO")
        self.assertEqual(p.stdout.strip(), "NO")


class SingleFile(unittest.TestCase):
    def film(self, ref):
        film = Path(tempfile.mkdtemp(prefix="motion-hardening-")) / "film"
        (film / "src").mkdir(parents=True)
        (film / "audio").mkdir()
        (film / "audio/a.wav").write_bytes(b"RIFF")
        (film.parent / "secret.js").write_text("SECRET")
        (film / "src/index.html").write_text(f'<script src="{ref}"></script>')
        return film

    def build(self, film):
        return run(sys.executable, SCRIPTS / "build_single.py", film / "src/index.html", film / "dist/one.html")

    def test_refuses_a_file_outside_the_film(self):
        film = self.film("../../secret.js")
        p = self.build(film)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("outside the film folder", p.stderr)
        self.assertFalse((film / "dist/one.html").exists())

    def test_refuses_an_absolute_path(self):
        film = self.film("/etc/hostname")
        self.assertIn("outside the film folder", self.build(film).stderr)

    def test_inlines_the_film_audio(self):
        film = self.film("../audio/a.wav")
        (film / "src/index.html").write_text('<audio src="../audio/a.wav"></audio>')
        p = self.build(film)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("data:audio/wav;base64,", (film / "dist/one.html").read_text())


class Assets(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="motion-hardening-"))

    def test_refuses_a_non_image(self):
        key = self.dir / "key.pem"
        key.write_text("-----BEGIN PRIVATE KEY-----")
        p = run(sys.executable, SCRIPTS / "assets.py", self.dir / "assets.js", "--img", f"k={key}")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("not an image or font", p.stderr)

    def test_refuses_a_symbol_outside_its_folder(self):
        sym = self.dir / "sym"
        sym.mkdir()
        (self.dir / "x__regular.png").write_bytes(PNG)
        (sym / "manifest.json").write_text(json.dumps({"../x@regular": {"w": 1, "h": 1}}))
        p = run(sys.executable, SCRIPTS / "assets.py", self.dir / "assets.js", "--sym", sym)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("symbol outside", p.stderr)


class Ids(unittest.TestCase):
    def test_id_pattern(self):
        sys.path.insert(0, str(SCRIPTS))
        import timing
        for ok in ("hook", "s1", "end-card", "outro_2"):
            self.assertTrue(timing.ID.fullmatch(ok), ok)
        for bad in ("../x", "a'b", "a\nfile '/etc/passwd'", "a b", ""):
            self.assertFalse(timing.ID.fullmatch(bad), bad)

    def test_voiceover_refuses_a_line_id_with_a_path(self):
        script = Path(tempfile.mkdtemp(prefix="motion-hardening-")) / "voiceover.json"
        script.write_text(json.dumps({"lines": [{"id": "../../escape", "text": "Hello there.", "voice": "n"}],
                                      "scenes": [{"id": "s", "lines": ["../../escape"]}], "voices": {"n": {}}}))
        p = run(sys.executable, SCRIPTS / "voiceover.py", script)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("use letters, digits", p.stderr)


if __name__ == "__main__":
    unittest.main()
