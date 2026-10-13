"""Calendar and adaptive study planning for Hunter System.

The campaign order is sacred: forecasts never mark, remove, or skip unfinished content.
Extra completed work moves the starting point forward. Missed work remains the next lesson;
future dates are forecasts and cannot unlock a later page before prerequisites are completed.
"""
from __future__ import annotations
from datetime import date, timedelta
from typing import Any

DEFAULT_MINIMUMS = {"python": 1, "caixa": 2, "custom": 1}
MINIMUMS = {"python": 1, "caixa": 1, "custom": 1}
MAXIMUMS = {"python": 5, "caixa": 5, "custom": 5}
DEFAULT_MINUTES = {"python": 60, "caixa": 120, "custom": 45}


def ensure_calendar(profile: dict[str, Any], profile_key: str, today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    cfg = profile.setdefault("calendar_settings", {})
    cfg.setdefault("start_date", today.isoformat())
    cfg.setdefault("daily_minimum", DEFAULT_MINIMUMS.get(profile_key, 1))
    cfg.setdefault("daily_minutes", DEFAULT_MINUTES.get(profile_key, 60))
    cfg.setdefault("exam_date", "")
    cfg.setdefault("target_score", 0.85)
    cfg.setdefault("version", 2)
    try:
        date.fromisoformat(str(cfg["start_date"]))
    except (ValueError, TypeError):
        cfg["start_date"] = today.isoformat()
    try:
        cfg["daily_minimum"] = max(MINIMUMS.get(profile_key, 1), min(MAXIMUMS.get(profile_key, 5), int(cfg["daily_minimum"])))
    except (ValueError, TypeError):
        cfg["daily_minimum"] = DEFAULT_MINIMUMS.get(profile_key, 1)
    try:
        cfg["daily_minutes"] = max(20, min(480, int(cfg["daily_minutes"])))
    except (ValueError, TypeError):
        cfg["daily_minutes"] = DEFAULT_MINUTES.get(profile_key, 60)
    try:
        cfg["target_score"] = max(0.5, min(1.0, float(cfg["target_score"])))
    except (ValueError, TypeError):
        cfg["target_score"] = 0.85
    if cfg.get("exam_date"):
        try:
            date.fromisoformat(str(cfg["exam_date"]))
        except (ValueError, TypeError):
            cfg["exam_date"] = ""
    profile.setdefault("calendar_completed_on", {})
    profile.setdefault("diagnostic_results", {})
    profile.setdefault("quiz_attempt_log", [])
    profile.setdefault("simulados", [])
    profile.setdefault("essay_practice_log", [])
    return cfg


def estimated_minutes(mission: dict[str, Any], profile_key: str) -> int:
    if profile_key == "python":
        return 55
    if profile_key == "custom":
        return 35
    subject = str(mission.get("chapter_title", mission.get("topic", "")))
    if "Redação" in subject:
        return 50
    weight = int(mission.get("weight", 5) or 5)
    return 30 + 2 * weight


def completion_count_on(profile: dict[str, Any], day: date) -> int:
    done_on = profile.get("calendar_completed_on", {})
    return sum(1 for _mission_id, completed_day in done_on.items() if completed_day == day.isoformat())


def _ordered_missions(profile: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(profile.get("mission_data", []), key=lambda m: int(m.get("global_index", 0)))


def _first_pending_index(missions: list[dict[str, Any]], completed: set[str]) -> int:
    for index, mission in enumerate(missions):
        if mission.get("id") not in completed:
            return index
    return len(missions)


def planned_lessons_for_date(
    profile: dict[str, Any], profile_key: str, target: date,
    today: date | None = None, blocked_by_boss: bool = False,
) -> list[dict[str, Any]]:
    """Return a rolling sequential forecast for a selected day.

    Historic dates use actual records. Today begins with the first incomplete lesson. Future
    dates project from that point onward, shifting forward when the user gets ahead. If the
    user is behind, the oldest open lesson remains first; later forecasts never constitute an
    unlock or a completion record.
    """
    today = today or date.today()
    cfg = ensure_calendar(profile, profile_key, today)
    missions = _ordered_missions(profile)
    completed = set(profile.get("completed_missions", []))
    if target < today:
        completed_on = profile.get("calendar_completed_on", {})
        return [m for m in missions if completed_on.get(m.get("id")) == target.isoformat()]
    try:
        start_date = date.fromisoformat(str(cfg["start_date"]))
    except (ValueError, TypeError):
        start_date = today
    if target < start_date or blocked_by_boss:
        return []
    first_pending = _first_pending_index(missions, completed)
    if first_pending >= len(missions):
        return []
    daily_minimum = int(cfg["daily_minimum"])
    days_ahead = max(0, (target - today).days)
    if target == today:
        start_index = first_pending
    else:
        expected_before_today = max(0, (today - start_date).days) * daily_minimum
        if first_pending < expected_before_today:
            # Behind schedule: project the oldest unfinished lesson first. Later dates show
            # what could follow if the earlier pending work is recovered; access remains locked.
            start_index = first_pending + max(0, days_ahead - 1) * daily_minimum
        else:
            # On/ahead of pace: completed bonus work pulls the future forward; baseline dates
            # prevent the same lesson from appearing on consecutive future days.
            rolling_start = first_pending + max(0, days_ahead - 1) * daily_minimum
            baseline_start = max(0, (target - start_date).days) * daily_minimum
            start_index = max(rolling_start, baseline_start)
    return missions[start_index:start_index + daily_minimum]


def reviews_for_date(profile: dict[str, Any], target: date, today: date | None = None) -> list[dict[str, Any]]:
    today = today or date.today()
    if target <= today:
        due_check = lambda r: str(r.get("due_date", "9999-12-31")) <= target.isoformat()
    else:
        due_check = lambda r: str(r.get("due_date", "")) == target.isoformat()
    return [r for r in profile.get("review_queue", []) if not r.get("done") and due_check(r)]


def day_summary(
    profile: dict[str, Any], profile_key: str, target: date,
    today: date | None = None, blocked_by_boss: bool = False,
) -> dict[str, Any]:
    today = today or date.today()
    cfg = ensure_calendar(profile, profile_key, today)
    completed_today = completion_count_on(profile, target)
    lessons = planned_lessons_for_date(profile, profile_key, target, today, blocked_by_boss)
    reviews = reviews_for_date(profile, target, today)
    if target < today:
        label = f"{len(lessons)} concluída(s)"
    elif blocked_by_boss and target >= today:
        label = "Guardião"
    elif target < date.fromisoformat(cfg["start_date"]):
        label = "Antes do início"
    else:
        label = f"{len(lessons)} tópico(s) previsto(s)"
    return {
        "lessons": lessons,
        "reviews": reviews,
        "completed_count": completed_today,
        "minimum": int(cfg["daily_minimum"]),
        "daily_minutes": int(cfg["daily_minutes"]),
        "bonus_mode": target == today and completed_today >= int(cfg["daily_minimum"]),
        "label": label,
        "estimated_minutes": sum(estimated_minutes(m, profile_key) for m in lessons),
    }


def priority_label(mission: dict[str, Any], profile_key: str, metrics: list[dict[str, Any]] | None = None) -> str:
    if profile_key != "caixa":
        return "Trilha cronológica" if profile_key == "python" else "Jornada personalizada"
    subject = str(mission.get("chapter_title", mission.get("topic", "")))
    if "Redação" in subject:
        return "Prioridade recorrente · etapa eliminatória"
    metric = next((m for m in (metrics or []) if m.get("subject") == subject), None)
    weight = int(mission.get("weight", 5) or 5)
    if metric and metric.get("known"):
        accuracy = float(metric.get("accuracy", 0.0))
        if accuracy < 0.55:
            return f"Ponto crítico · {round(accuracy * 100)}% nos diagnósticos/questões"
        if accuracy < 0.70:
            return f"Reforço prioritário · {round(accuracy * 100)}% de acerto"
    if weight >= 15:
        return "Peso 15 · 15 questões · prioridade por retorno"
    if weight >= 10:
        return "Peso 10 · 10 questões · prioridade alta"
    return "Peso 5 · não negligenciar o bloco"
