import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_portability.py"


def load_portability_checker():
    spec = importlib.util.spec_from_file_location("check_portability", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PortabilityAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = load_portability_checker()

    def test_skill_assets_and_dependencies_are_portable(self):
        report = self.checker.run_checks(ROOT)
        failed = [check for check in report["checks"] if not check["ok"]]

        self.assertFalse(failed, failed)
        check_names = {check["name"] for check in report["checks"]}
        for name in [
            "required_files_exist",
            "font_assets_load",
            "preview_gifs_load",
            "default_spec_loads",
            "python_dependencies_available",
            "ffprobe_available",
            "no_machine_local_paths",
            "font_candidates_start_with_bundled_assets",
        ]:
            self.assertIn(name, check_names)


if __name__ == "__main__":
    unittest.main()
