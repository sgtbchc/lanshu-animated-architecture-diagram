import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillWorkflowGuidanceTest(unittest.TestCase):
    def test_workflow_requires_parameter_check_before_spec_authoring(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("生成 spec 之前", skill_text)
        self.assertIn("主动询问用户是否有参数要求", skill_text)
        self.assertIn("没有明确要求时", skill_text)
        self.assertIn("assets/default-spec.json", skill_text)
        self.assertIn("canvas.duration_seconds", skill_text)
        self.assertIn("canvas.fps", skill_text)


if __name__ == "__main__":
    unittest.main()
