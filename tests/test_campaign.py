import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from campaign_data import build_campaign_missions, chapter_boss_thresholds
from game_data import create_save, default_profile


class CampaignDataTests(unittest.TestCase):
    def check_campaign(self, key, expected_count):
        missions = build_campaign_missions(key)
        self.assertEqual(len(missions), expected_count)
        self.assertEqual([m["global_index"] for m in missions], list(range(1, len(missions) + 1)))
        self.assertEqual(len({m["id"] for m in missions}), len(missions))
        required = {
            "id", "chapter_title", "chapter_index", "chapter_total", "lesson_index",
            "lessons_in_chapter", "global_index", "title", "description", "practice",
            "success_criteria", "story_intro", "story_outro", "quiz", "xp", "coins",
            "is_chapter_start", "is_chapter_end",
        }
        for mission in missions:
            self.assertTrue(required.issubset(mission), f"Campos ausentes em {mission.get('id')}: {required - set(mission)}")
            self.assertEqual(len(mission["quiz"]), 4)
            for question in mission["quiz"]:
                self.assertEqual(len(question["options"]), 4)
                self.assertGreaterEqual(question["a"], 0)
                self.assertLess(question["a"], len(question["options"]))
                self.assertTrue(question["why"])
            self.assertIn(mission["title"], mission["quiz"][1]["q"])
            self.assertIn(mission["description"], mission["quiz"][1]["options"])
            self.assertIn(mission["practice"], mission["quiz"][3]["options"])
        thresholds = chapter_boss_thresholds(missions, 5)
        self.assertEqual(len(thresholds), 5)
        self.assertEqual(thresholds[-1], len(missions))
        self.assertEqual(thresholds, sorted(thresholds))
        self.assertTrue(all(1 <= threshold <= len(missions) for threshold in thresholds))

    def test_python_campaign_is_detailed_and_linear(self):
        self.check_campaign("python", 141)

    def test_caixa_campaign_is_detailed_and_linear(self):
        self.check_campaign("caixa", 82)

    def test_custom_campaign_is_editable_and_structured(self):
        missions = build_campaign_missions("custom", ["Astronomia", "Desenho"])
        self.assertEqual(len(missions), 10)
        self.assertEqual(missions[0]["chapter_title"], "Astronomia")
        self.assertEqual(missions[-1]["chapter_title"], "Desenho")

    def test_default_save_has_three_separate_slots(self):
        save = create_save()
        self.assertEqual(set(save["profiles"]), {"python", "caixa", "custom"})
        self.assertEqual(save["version"], 3)
        for key in save["profiles"]:
            profile = default_profile(key)
            self.assertEqual(profile["campaign_schema"], 3)
            self.assertIn("review_queue", profile)
            self.assertIn("boss_exam_results", profile)
            self.assertIn("calendar_settings", profile)
            self.assertIn("calendar_completed_on", profile)
            self.assertEqual(save["profiles"][key]["mission_data"][0]["id"], profile["mission_data"][0]["id"])

    def test_caixa_curriculum_uses_non_it_track(self):
        missions = build_campaign_missions("caixa")
        chapters = {m["chapter_title"] for m in missions}
        self.assertIn("Conhecimentos Bancários", chapters)
        self.assertIn("Atendimento Bancário", chapters)
        self.assertIn("Redação: a última prova", chapters)
        self.assertIn("Tecnologia da Informação e Comunicação", chapters)  # O TBN comum também tem este eixo no edital 2024.
        self.assertNotIn("Tecnologia da Informação", chapters)  # Não usa o eixo específico de 30 questões do cargo TBN-TI.


if __name__ == "__main__":
    unittest.main(verbosity=2)
