import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adaptive_planner import (subject_metrics, block_readiness, estimate_readiness, exam_pace, next_spacing_date, build_adaptive_question_set, build_caixa_weighted_mock, OBJECTIVE_QUESTIONS, mission_subject)
from campaign_data import build_campaign_missions
from game_data import default_profile


class AdaptivePlannerTests(unittest.TestCase):
    def profile(self, key):
        p = default_profile(key)
        p["mission_data"] = build_campaign_missions(key)
        p["completed_missions"] = []
        p["quiz_stats"] = {}
        p["quiz_attempt_log"] = []
        p["diagnostic_results"] = {}
        p["calendar_settings"].update({"daily_minimum": 2, "daily_minutes": 120, "exam_date": "2026-12-01"})
        return p

    def test_unknown_subjects_are_diagnostic_first_not_fabricated(self):
        p = self.profile("caixa")
        metrics = subject_metrics(p, "caixa", date(2026, 10, 13))
        banking = next(x for x in metrics if x["subject"] == "Conhecimentos Bancários")
        self.assertIsNone(banking["accuracy"])
        self.assertEqual(banking["status"], "Diagnóstico necessário")
        self.assertGreater(banking["priority_score"], next(x for x in metrics if x["subject"] == "Língua Portuguesa")["priority_score"])

    def test_weak_high_weight_topic_ranks_above_strong_low_weight_topic(self):
        p = self.profile("caixa")
        today = date(2026, 10, 13).isoformat()
        p["diagnostic_results"] = {
            "Conhecimentos Bancários": {"score": 2, "total": 5, "date": today},
            "Língua Portuguesa": {"score": 5, "total": 5, "date": today},
        }
        metrics = subject_metrics(p, "caixa", date(2026, 10, 13))
        ranking = {x["subject"]: x["rank"] for x in metrics}
        self.assertLess(ranking["Conhecimentos Bancários"], ranking["Língua Portuguesa"])

    def test_diagnostic_changes_priority(self):
        p = self.profile("caixa")
        before = {x["subject"]: x for x in subject_metrics(p, "caixa", date(2026, 10, 13))}
        p["diagnostic_results"]["Matemática Financeira"] = {"score": 1, "total": 5, "date": "2026-10-13"}
        after = {x["subject"]: x for x in subject_metrics(p, "caixa", date(2026, 10, 13))}
        self.assertGreater(after["Matemática Financeira"]["priority_score"], before["Matemática Financeira"]["priority_score"] - .01)
        self.assertEqual(after["Matemática Financeira"]["status"], "Ponto crítico")

    def test_failed_lesson_attempts_are_used(self):
        p = self.profile("python")
        m = next(x for x in p["mission_data"] if x["chapter_title"] == "A primeira centelha: lógica e sintaxe")
        p["quiz_attempt_log"] = [{"lesson_id": m["id"], "date": "2026-10-13", "score": 1, "total": 4}]
        metric = next(x for x in subject_metrics(p, "python", date(2026, 10, 13)) if x["subject"] == "A primeira centelha: lógica e sintaxe")
        self.assertAlmostEqual(metric["accuracy"], .25)
        self.assertEqual(metric["status"], "Ponto crítico")

    def test_exam_pace_flags_unrealistic_load(self):
        p = self.profile("caixa")
        p["calendar_settings"].update({"exam_date": "2026-10-14", "daily_minimum": 1, "daily_minutes": 20})
        result = exam_pace(p, "caixa", date(2026, 10, 13))
        self.assertEqual(result["days_left"], 1)
        self.assertIn("Ajuste necessário", result["status"])

    def test_exam_pace_suggests_higher_minimum_when_time_budget_can_fit(self):
        p = self.profile("caixa")
        p["calendar_settings"].update({"exam_date": "2026-11-12", "daily_minimum": 1, "daily_minutes": 480})
        result = exam_pace(p, "caixa", date(2026, 10, 13))
        self.assertIn("Ajuste o mínimo", result["status"])

    def test_readiness_stays_uncalibrated_without_data(self):
        p = self.profile("caixa")
        self.assertEqual(estimate_readiness(subject_metrics(p, "caixa"), "caixa")["label"], "Calibração pendente")

    def test_objective_blocks_are_weighted_by_question_count(self):
        p = self.profile("caixa")
        today = "2026-10-13"
        # Banking: 5/5 (weight 15); other specific subjects: 0/5.
        p["diagnostic_results"] = {
            "Conhecimentos Bancários": {"score": 5, "total": 5, "date": today},
            "Atendimento Bancário": {"score": 0, "total": 5, "date": today},
            "Tecnologia da Informação e Comunicação": {"score": 0, "total": 5, "date": today},
            "Conhecimentos e Comportamentos Digitais": {"score": 0, "total": 5, "date": today},
        }
        metrics = subject_metrics(p, "caixa", date(2026, 10, 13))
        blocks = {x["block"]: x for x in block_readiness(metrics, "caixa", .85)}
        # Weighted by 15+10+5+5 points, not a simple mean of four subject percentages.
        self.assertAlmostEqual(blocks["Conhecimentos Específicos"]["accuracy"], 15 / 35)
        self.assertTrue(blocks["Conhecimentos Específicos"]["complete_coverage"])
        self.assertEqual(blocks["Conhecimentos Específicos"]["known_subjects"], 4)

    def test_incomplete_block_diagnostic_is_explicitly_partial(self):
        p = self.profile("caixa")
        p["diagnostic_results"] = {"Conhecimentos Bancários": {"score": 4, "total": 5, "date": "2026-10-13"}}
        metrics = subject_metrics(p, "caixa", date(2026, 10, 13))
        specific = next(x for x in block_readiness(metrics, "caixa", .85) if x["block"] == "Conhecimentos Específicos")
        self.assertFalse(specific["complete_coverage"])
        self.assertEqual(specific["known_subjects"], 1)
        self.assertEqual(specific["total_subjects"], 4)
        self.assertAlmostEqual(specific["accuracy"], .8)

    def test_personal_accuracy_target_changes_consolidation_status(self):
        p = self.profile("python")
        p["calendar_settings"]["target_score"] = .95
        p["diagnostic_results"]["A primeira centelha: lógica e sintaxe"] = {"score": 9, "total": 10, "date": "2026-10-13"}
        metric = next(x for x in subject_metrics(p, "python", date(2026, 10, 13)) if x["subject"] == "A primeira centelha: lógica e sintaxe")
        self.assertEqual(metric["status"], "Consolidar")
        self.assertIn("95%", metric["recommendation"])

    def test_essay_metric_uses_only_explicit_writing_self_assessment(self):
        p = self.profile("caixa")
        essay_mission = next(m for m in p["mission_data"] if "Redação" in m.get("chapter_title", ""))
        p["quiz_attempt_log"] = [{"lesson_id": essay_mission["id"], "date": "2026-10-13", "score": 4, "total": 4}]
        metric = next(x for x in subject_metrics(p, "caixa", date(2026, 10, 13)) if x["is_essay"])
        self.assertFalse(metric["known"])
        p["essay_practice_log"] = [{"date": "2026-10-13", "rubric_score": 3}]
        metric = next(x for x in subject_metrics(p, "caixa", date(2026, 10, 13)) if x["is_essay"])
        self.assertTrue(metric["known"])
        self.assertAlmostEqual(metric["accuracy"], .6)

    def test_caixa_mock_matches_objective_edital_distribution(self):
        p = self.profile("caixa")
        questions = build_caixa_weighted_mock(p)
        self.assertEqual(len(questions), 60)
        self.assertEqual(len({q["q"] for q in questions}), 60)
        counts = {}
        for question in questions:
            subject = question["_planner_subject"]
            counts[subject] = counts.get(subject, 0) + 1
            self.assertIn(question["_exam_block"], {"Conhecimentos Básicos", "Conhecimentos Específicos"})
        self.assertEqual(counts, OBJECTIVE_QUESTIONS)
        self.assertFalse(any("redação" in subject.casefold() for subject in counts))

    def test_adaptive_simulation_has_twenty_questions_and_excludes_essay(self):
        p = self.profile("caixa")
        questions = build_adaptive_question_set(p, "caixa", count=20)
        self.assertEqual(len(questions), 20)
        self.assertFalse(any("redação" in q.get("_planner_subject", "").casefold() for q in questions))
        self.assertTrue(all(q.get("_planner_subject") in OBJECTIVE_QUESTIONS for q in questions))

    def test_spaced_review_intervals(self):
        day = date(2026, 10, 13)
        self.assertEqual(next_spacing_date(day, 1), date(2026, 10, 14))
        self.assertEqual(next_spacing_date(day, 2), date(2026, 10, 20))
        self.assertEqual(next_spacing_date(day, 3), date(2026, 11, 12))
        self.assertIsNone(next_spacing_date(day, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
