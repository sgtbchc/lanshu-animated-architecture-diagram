import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_animated_diagram.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_animated_diagram", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RenderOutputChecksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = load_renderer()
        cls.spec = json.loads((ROOT / "assets" / "default-spec.json").read_text(encoding="utf-8"))

    def test_generated_outputs_pass_contract_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.renderer.write_outputs(self.spec, Path(tmp), "sample")

            checks = self.renderer.check_outputs(result, self.spec)

        self.assertTrue(checks["ok"], checks)
        check_names = {check["name"] for check in checks["checks"]}
        self.assertIn("font_assets_available", check_names)
        self.assertIn("font_render_readable", check_names)
        self.assertIn("ffprobe_available", check_names)
        self.assertIn("ffprobe_media_parameters", check_names)

    def test_duration_seconds_derives_frame_count(self):
        spec = json.loads(json.dumps(self.spec))
        spec["canvas"]["duration_seconds"] = 6
        spec["canvas"]["fps"] = 10
        spec["canvas"].pop("frames", None)

        with tempfile.TemporaryDirectory() as tmp:
            result = self.renderer.write_outputs(spec, Path(tmp), "six-second")

            checks = self.renderer.check_outputs(result, spec)

        self.assertEqual(result["timing"]["fps"], 10)
        self.assertEqual(result["timing"]["frames"], 60)
        self.assertEqual(result["timing"]["duration_seconds"], 6.0)
        self.assertTrue(checks["ok"], checks)

    def test_auto_fps_uses_gif_safe_timing(self):
        spec = json.loads(json.dumps(self.spec))
        spec["canvas"]["duration_seconds"] = 2
        spec["canvas"]["fps"] = "auto"
        spec["canvas"].pop("frames", None)

        with tempfile.TemporaryDirectory() as tmp:
            result = self.renderer.write_outputs(spec, Path(tmp), "auto-fps")

            checks = self.renderer.check_outputs(result, spec)

        self.assertEqual(result["timing"]["fps"], 20)
        self.assertEqual(result["timing"]["frames"], 40)
        self.assertEqual(result["timing"]["gif_frame_duration_ms"], 50)
        self.assertTrue(checks["ok"], checks)

    def test_auto_fps_lowers_cadence_for_longer_gifs(self):
        spec = json.loads(json.dumps(self.spec))
        spec["canvas"]["duration_seconds"] = 6
        spec["canvas"]["fps"] = "auto"
        spec["canvas"].pop("frames", None)

        timing = self.renderer.resolve_animation_timing(spec)

        self.assertEqual(timing["fps"], 10)
        self.assertEqual(timing["frames"], 60)
        self.assertEqual(timing["duration_seconds"], 6.0)

    def test_unsafe_gif_fps_fails_before_rendering(self):
        spec = json.loads(json.dumps(self.spec))
        spec["canvas"]["fps"] = 30
        spec["canvas"]["frames"] = 60

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "GIF-safe"):
                self.renderer.write_outputs(spec, Path(tmp), "unsafe-fps")

    def test_load_spec_accepts_utf8_bom_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "bom-spec.json"
            spec_path.write_text(json.dumps(self.spec), encoding="utf-8-sig")

            loaded = self.renderer.load_spec(spec_path)

        self.assertEqual(loaded["canvas"]["width"], self.spec["canvas"]["width"])

    def test_contract_checks_report_invalid_excalidraw_font(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.renderer.write_outputs(self.spec, Path(tmp), "sample")
            excalidraw_path = Path(result["excalidraw"])
            excalidraw = json.loads(excalidraw_path.read_text(encoding="utf-8"))
            first_text = next(element for element in excalidraw["elements"] if element["type"] == "text")
            first_text["fontFamily"] = 1
            excalidraw_path.write_text(json.dumps(excalidraw), encoding="utf-8")

            checks = self.renderer.check_outputs(result, self.spec)

        self.assertFalse(checks["ok"])
        font_check = next(check for check in checks["checks"] if check["name"] == "excalidraw_text_font_family")
        self.assertFalse(font_check["ok"])


if __name__ == "__main__":
    unittest.main()
