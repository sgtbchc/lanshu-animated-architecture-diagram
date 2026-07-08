import importlib.util
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "render_animated_diagram.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_animated_diagram", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BundledFontsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = load_renderer()
        cls.image = Image.new("RGBA", (1200, 300), (0, 0, 0, 0))
        cls.draw = ImageDraw.Draw(cls.image)

    def test_hand_font_uses_readable_bundled_font_on_windows(self):
        font = self.renderer.load_font(47, hand=True, bold=True)

        width, height = self.renderer.text_size(self.draw, "Memory Pack", font)

        self.assertGreater(width, self.renderer.c(200))
        self.assertGreater(height, self.renderer.c(35))

    def test_cjk_font_uses_readable_bundled_font_on_windows(self):
        font = self.renderer.load_font(24, cjk=True, bold=True)

        width, height = self.renderer.text_size(self.draw, "记忆资产归档流程", font)

        self.assertGreater(width, self.renderer.c(150))
        self.assertGreater(height, self.renderer.c(20))


if __name__ == "__main__":
    unittest.main()
