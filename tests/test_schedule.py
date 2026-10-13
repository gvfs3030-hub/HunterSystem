import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from schedule_system import ensure_calendar, estimated_minutes, planned_lessons_for_date, day_summary, priority_label
from campaign_data import build_campaign_missions
from game_data import default_profile


class AdaptiveCalendarTests(unittest.TestCase):
    def make_profile(self, key):
        profile = default_profile(key)
        # Keep scheduler tests small but retain the mission format/priority fields.
        profile["mission_data"] = build_campaign_missions(key)[:8]
        profile["completed_missions"] = []
        profile["calendar_completed_on"] = {}
        profile["calendar_settings"] = {"start_date": "2026-10-13", "daily_minimum": {"python": 1, "caixa": 2, "custom": 1}[key], "version": 1}
        return profile

    def test_default_calendar_minimums_are_profile_specific(self):
        today = date(2026, 10, 13)
        for key, expected in (("python", 1), ("caixa", 2), ("custom", 1)):
            profile = self.make_profile(key)
            cfg = ensure_calendar(profile, key, today)
            self.assertEqual(cfg["daily_minimum"], expected)

    def test_schedule_is_linear_on_current_and_future_days(self):
        today = date(2026, 10, 13)
        profile = self.make_profile("python")
        current = planned_lessons_for_date(profile, "python", today, today)
        tomorrow = planned_lessons_for_date(profile, "python", today + timedelta(days=1), today)
        self.assertEqual(current[0]["id"], profile["mission_data"][0]["id"])
        self.assertEqual(tomorrow[0]["id"], profile["mission_data"][1]["id"])

    def test_extra_progress_adapts_future_forecast_without_deleting_progress(self):
        today = date(2026, 10, 13)
        profile = self.make_profile("caixa")
        before = planned_lessons_for_date(profile, "caixa", today + timedelta(days=1), today)
        self.assertEqual(len(before), 2)
        profile["completed_missions"] = [m["id"] for m in profile["mission_data"][:3]]
        profile["calendar_completed_on"] = {m["id"]: today.isoformat() for m in profile["mission_data"][:3]}
        after = planned_lessons_for_date(profile, "caixa", today + timedelta(days=1), today)
        self.assertEqual(after[0]["id"], profile["mission_data"][3]["id"])
        self.assertEqual(len(profile["completed_missions"]), 3)
        self.assertTrue(day_summary(profile, "caixa", today, today)["bonus_mode"])

    def test_unfinished_topics_are_never_marked_complete_by_scheduler(self):
        today = date(2026, 10, 13)
        profile = self.make_profile("python")
        tasks = planned_lessons_for_date(profile, "python", today, today)
        self.assertNotIn(tasks[0]["id"], profile["completed_missions"])
        self.assertEqual(len(profile["completed_missions"]), 0)

    def test_caixa_priority_time_reflects_exam_weights_and_essay(self):
        profile = self.make_profile("caixa")
        banking = next(m for m in build_campaign_missions("caixa") if m["chapter_title"] == "Conhecimentos Bancários")
        attendance = next(m for m in build_campaign_missions("caixa") if m["chapter_title"] == "Atendimento Bancário")
        essay = next(m for m in build_campaign_missions("caixa") if "Redação" in m["chapter_title"])
        self.assertGreater(estimated_minutes(banking, "caixa"), estimated_minutes(attendance, "caixa"))
        self.assertEqual(estimated_minutes(essay, "caixa"), 50)
        self.assertIn("15 questões", priority_label(banking, "caixa"))
        self.assertIn("eliminatória", priority_label(essay, "caixa"))

    def test_future_forecast_does_not_skip_open_lessons_after_extra_work(self):
        today = date(2026, 10, 13)
        profile = self.make_profile("python")
        profile["completed_missions"] = [m["id"] for m in profile["mission_data"][:3]]
        profile["calendar_completed_on"] = {m["id"]: today.isoformat() for m in profile["mission_data"][:3]}
        tomorrow = planned_lessons_for_date(profile, "python", today + timedelta(days=1), today)
        after_tomorrow = planned_lessons_for_date(profile, "python", today + timedelta(days=2), today)
        self.assertEqual([m["id"] for m in tomorrow], [profile["mission_data"][3]["id"]])
        self.assertEqual([m["id"] for m in after_tomorrow], [profile["mission_data"][4]["id"]])
        self.assertFalse(set(m["id"] for m in tomorrow + after_tomorrow) & set(profile["completed_missions"]))

    def test_blocked_boss_suspends_forecast(self):
        today = date(2026, 10, 13)
        profile = self.make_profile("python")
        self.assertEqual(planned_lessons_for_date(profile, "python", today, today, blocked_by_boss=True), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
