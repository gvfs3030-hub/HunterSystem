"""Adaptive learning engine for Hunter System.

This module is deterministic and offline-first. It converts diagnostic and lesson-level
assessment evidence into subject priorities, time allocation and exam-readiness signals.
It never marks content complete or bypasses the linear campaign.
"""
from __future__ import annotations

from datetime import date, timedelta
from math import ceil, floor
from typing import Any

SPACED_REPETITION_DAYS = (1, 7, 30)
OBJECTIVE_QUESTIONS = {
    "Língua Portuguesa": 5,
    "Língua Inglesa": 5,
    "Matemática Financeira": 5,
    "Probabilidade e Estatística": 5,
    "Ética e Compliance": 5,
    "Conhecimentos Bancários": 15,
    "Tecnologia da Informação e Comunicação": 5,
    "Conhecimentos e Comportamentos Digitais": 5,
    "Atendimento Bancário": 10,
}


def mission_subject(mission: dict[str, Any]) -> str:
    return str(mission.get("chapter_title") or mission.get("topic") or "Geral")


def group_missions(profile: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for mission in profile.get("mission_data", []):
        grouped.setdefault(mission_subject(mission), []).append(mission)
    return grouped


def _parse_day(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _latest_attempt_per_lesson(profile: dict[str, Any], ids: set[str]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    attempts = profile.get("quiz_attempt_log", [])
    if isinstance(attempts, list):
        for attempt in attempts:
            lesson_id = attempt.get("lesson_id") if isinstance(attempt, dict) else None
            if lesson_id not in ids:
                continue
            old = latest.get(lesson_id)
            attempt_day = str(attempt.get("date", ""))
            if old is None or attempt_day >= str(old.get("date", "")):
                latest[lesson_id] = attempt
    # Compatibility with saves created before failed attempts were recorded.
    for lesson_id in ids:
        if lesson_id not in latest:
            stats = profile.get("quiz_stats", {}).get(lesson_id)
            if isinstance(stats, dict) and "last_score" in stats:
                latest[lesson_id] = {
                    "date": stats.get("date", ""),
                    "score": stats.get("last_score", 0),
                    "total": stats.get("total", 4),
                }
    return latest


def subject_metrics(profile: dict[str, Any], profile_key: str, today: date | None = None) -> list[dict[str, Any]]:
    """Return subjects sorted by expected study priority, not by a generic topic order.

    For Caixa, objective-question weight matters, with explicit protection for basic/specific
    block minimums and the eliminatory essay. Observed weakness and stale evidence change the
    ranking. Unknown performance receives a diagnostic-first recommendation rather than a
    fabricated score.
    """
    today = today or date.today()
    grouped = group_missions(profile)
    diagnostics = profile.get("diagnostic_results", {}) if isinstance(profile.get("diagnostic_results", {}), dict) else {}
    completed = set(profile.get("completed_missions", []))
    raw: list[dict[str, Any]] = []

    block_scores: dict[str, list[tuple[float, int]]] = {"Conhecimentos Básicos": [], "Conhecimentos Específicos": []}
    intermediate: list[dict[str, Any]] = []
    for subject, missions in grouped.items():
        ids = {str(m.get("id")) for m in missions}
        latest_by_lesson = _latest_attempt_per_lesson(profile, ids)
        lesson_rates = []
        for attempt in latest_by_lesson.values():
            try:
                lesson_rates.append(max(0.0, min(1.0, float(attempt.get("score", 0)) / max(1, float(attempt.get("total", 4))))))
            except (TypeError, ValueError):
                pass
        diagnostic = diagnostics.get(subject)
        assessment_rate = None
        assessment_date = None
        assessment_total = 0
        if isinstance(diagnostic, dict):
            try:
                assessment_rate = max(0.0, min(1.0, float(diagnostic.get("score", 0)) / max(1, float(diagnostic.get("total", 1)))))
                assessment_date = _parse_day(diagnostic.get("date"))
                assessment_total = safe_count(diagnostic.get("total", 0))
            except (TypeError, ValueError):
                assessment_rate = None
        # A recent adaptive simulation is assessment evidence too. Prefer the newest evidence
        # per subject, instead of silently ignoring a mock result after the initial diagnostic.
        for sim in reversed(profile.get("simulados", []) if isinstance(profile.get("simulados", []), list) else []):
            if not isinstance(sim, dict):
                continue
            day = _parse_day(sim.get("date"))
            subject_result = (sim.get("by_subject", {}) or {}).get(subject)
            if not day or not isinstance(subject_result, dict) or safe_count(subject_result.get("total", 0)) <= 0:
                continue
            sim_rate = safe_count(subject_result.get("score", 0)) / max(1, safe_count(subject_result.get("total", 1)))
            if assessment_date is None or day >= assessment_date:
                assessment_rate = max(0.0, min(1.0, sim_rate))
                assessment_date = day
                assessment_total = safe_count(subject_result.get("total", 0))
            break

        lesson_rate = sum(lesson_rates) / len(lesson_rates) if lesson_rates else None
        is_essay = "redação" in subject.casefold()
        essay_rate, essay_observations, essay_date = essay_metrics(profile) if is_essay else (None, 0, None)
        # Essay readiness must come from its explicit writing rubric. Quiz results about
        # essay concepts are useful for the objective study trail, but do not prove writing skill.
        if is_essay:
            accuracy = essay_rate
            observations = essay_observations
            evidence_dates = [essay_date] if essay_date else []
        elif lesson_rate is not None and assessment_rate is not None:
            accuracy = lesson_rate * 0.55 + assessment_rate * 0.45
            observations = len(latest_by_lesson) + assessment_total
            evidence_dates = [_parse_day(x.get("date")) for x in latest_by_lesson.values()]
            evidence_dates = [x for x in evidence_dates if x]
            if assessment_date:
                evidence_dates.append(assessment_date)
        elif lesson_rate is not None:
            accuracy = lesson_rate
            observations = len(latest_by_lesson)
            evidence_dates = [_parse_day(x.get("date")) for x in latest_by_lesson.values()]
            evidence_dates = [x for x in evidence_dates if x]
        elif assessment_rate is not None:
            accuracy = assessment_rate
            observations = assessment_total
            evidence_dates = [assessment_date] if assessment_date else []
        else:
            accuracy = None
            observations = 0
            evidence_dates = []

        last_evidence = max(evidence_dates) if evidence_dates else None
        days_stale = (today - last_evidence).days if last_evidence else None
        max_weight = max((safe_num(m.get("weight", 0)) for m in missions), default=0)
        if profile_key == "caixa":
            if is_essay:
                weight_factor = 1.45  # eliminatory: protected recurring practice
                base_minutes = 50
            else:
                # The 15-question subject gets more study time, but weakness still controls ranking.
                weight_factor = {15: 1.75, 10: 1.42, 5: 1.0}.get(int(max_weight), 1.0)
                base_minutes = {15: 60, 10: 50, 5: 40}.get(int(max_weight), 40)
        elif profile_key == "python":
            weight_factor = 1.0
            base_minutes = 55
        else:
            weight_factor = 1.0
            base_minutes = 35

        known = accuracy is not None
        weakness = (1.0 - accuracy) if known else 0.55
        stale_factor = 1.0 if days_stale is None else (1.25 if days_stale >= 21 else 1.15 if days_stale >= 8 else 1.0)
        uncertainty_factor = 1.15 if not known else (1.08 if observations < 5 else 1.0)
        # All Caixa subject blocks are checked against the edital's 50% minimum.
        blocks = {str(m.get("block", "")) for m in missions if m.get("block")}
        block = next(iter(blocks)) if len(blocks) == 1 else ("Redação" if is_essay else "")
        score = weight_factor * (0.25 + weakness) * stale_factor * uncertainty_factor
        if profile_key == "caixa" and block in block_scores and known:
            block_scores[block].append((accuracy, max(1, int(max_weight or 5))))
        intermediate.append({
            "subject": subject, "accuracy": accuracy, "known": known,
            "observations": observations, "days_stale": days_stale,
            "weight": int(max_weight), "weight_factor": weight_factor,
            "priority_score": score, "base_minutes": base_minutes,
            "block": block, "is_essay": is_essay,
            "pending_lessons": sum(1 for m in missions if m.get("id") not in completed),
            "lesson_count": len(missions),
        })

    basics = block_scores["Conhecimentos Básicos"]
    specifics = block_scores["Conhecimentos Específicos"]
    # Estimate each block score weighted by its actual question count, not by number of
    # subjects. This matters because Banking Knowledge is worth 15 and Attendance 10.
    basic_average = (sum(rate * weight for rate, weight in basics) / sum(weight for _, weight in basics)) if basics else None
    specific_average = (sum(rate * weight for rate, weight in specifics) / sum(weight for _, weight in specifics)) if specifics else None

    for item in intermediate:
        score = item["priority_score"]
        if profile_key == "caixa":
            target = safe_num(profile.get("calendar_settings", {}).get("target_score", 0.85))
            safety_buffer = max(0.60, min(0.75, target - 0.20))
            if item["block"] == "Conhecimentos Básicos" and basic_average is not None and basic_average < safety_buffer:
                score *= 1.25
            elif item["block"] == "Conhecimentos Específicos" and specific_average is not None and specific_average < safety_buffer:
                score *= 1.25
        item["priority_score"] = round(score, 3)
        accuracy = item["accuracy"]
        target_score = max(0.50, min(1.0, safe_num(profile.get("calendar_settings", {}).get("target_score", 0.85))))
        reinforcement_floor = max(0.55, min(0.75, target_score - 0.15))
        if not item["known"]:
            item["status"] = "Diagnóstico necessário"
            item["recommendation"] = "Faça o diagnóstico para descobrir onde sua próxima hora renderá mais."
        elif accuracy < 0.55:
            item["status"] = "Ponto crítico"
            item["recommendation"] = "Reestude o fundamento e resolva questões sem consulta antes de avançar."
        elif accuracy < reinforcement_floor:
            item["status"] = "Reforço prioritário"
            item["recommendation"] = "Use recuperação ativa e exemplos variados; volte a este tema em breve."
        elif accuracy < target_score:
            item["status"] = "Consolidar"
            item["recommendation"] = f"Você ainda está abaixo da sua meta de {target_score * 100:.0f}%; intercale questões novas e revisão espaçada."
        else:
            item["status"] = "Manutenção"
            item["recommendation"] = "Meta pessoal atingida neste conjunto; mantenha o tema vivo com revisões curtas e questões intercaladas."
        # The user's target affects the booster duration too; never recommend an impossible
        # workload without the daily budget check performed by the UI.
        minute_gap = 0.55 if accuracy is None else max(0.0, target_score - accuracy)
        item["recommended_minutes"] = int(max(20, min(90, round(item["base_minutes"] * (0.8 + minute_gap)))))
        raw.append(item)

    raw.sort(key=lambda x: (x["priority_score"], x["pending_lessons"]), reverse=True)
    for rank, item in enumerate(raw, 1):
        item["rank"] = rank
    return raw


def safe_count(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def safe_num(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0



def block_readiness(metrics: list[dict[str, Any]], profile_key: str, target_score: float = 0.85) -> list[dict[str, Any]]:
    """Estimate objective block performance with exam-question weighting and coverage.

    The result is explicitly partial until every objective subject in a block has evidence.
    Essay is excluded because it is a separate eliminatory stage, not part of the 60 questions.
    """
    if profile_key != "caixa":
        return []
    specs = [
        ("Conhecimentos Básicos", 25, ["Língua Portuguesa", "Língua Inglesa", "Matemática Financeira", "Probabilidade e Estatística", "Ética e Compliance"]),
        ("Conhecimentos Específicos", 35, ["Conhecimentos Bancários", "Tecnologia da Informação e Comunicação", "Conhecimentos e Comportamentos Digitais", "Atendimento Bancário"]),
    ]
    by_subject = {str(item.get("subject")): item for item in metrics if not item.get("is_essay")}
    results = []
    for block, max_points, subjects in specs:
        known = [by_subject[name] for name in subjects if name in by_subject and by_subject[name].get("known")]
        observed_weight = sum(max(1, safe_count(item.get("weight", 5))) for item in known)
        weighted_points = sum(float(item.get("accuracy", 0.0)) * max(1, safe_count(item.get("weight", 5))) for item in known)
        accuracy = weighted_points / observed_weight if observed_weight else None
        coverage = len(known) / len(subjects)
        if accuracy is None:
            status = "Sem diagnóstico"
        elif accuracy < 0.50:
            status = "RISCO DE ELIMINAÇÃO"
        elif accuracy < 0.65:
            status = "Margem de segurança insuficiente"
        elif accuracy < target_score:
            status = "Abaixo da meta pessoal"
        else:
            status = "Meta pessoal atingida nos assuntos medidos"
        results.append({
            "block": block, "max_points": max_points, "accuracy": accuracy,
            "estimated_points": accuracy * max_points if accuracy is not None else None,
            "known_subjects": len(known), "total_subjects": len(subjects),
            "coverage": coverage, "complete_coverage": len(known) == len(subjects),
            "status": status, "elimination_threshold": 0.50,
            "safety_buffer": 0.65,
        })
    return results


def estimate_readiness(metrics: list[dict[str, Any]], profile_key: str) -> dict[str, Any]:
    known = [m for m in metrics if m.get("known") and not m.get("is_essay")]
    if not known:
        return {"known_subjects": 0, "total_subjects": sum(1 for m in metrics if not m.get("is_essay")), "weighted_accuracy": None, "label": "Calibração pendente"}
    weights = [max(1.0, safe_num(m.get("weight", 0))) if profile_key == "caixa" else 1.0 for m in known]
    total_weight = sum(weights)
    acc = sum(float(m["accuracy"]) * w for m, w in zip(known, weights)) / total_weight if total_weight else None
    label = "Base inicial" if acc is None or acc < 0.60 else "Em construção" if acc < 0.75 else "Competitivo em evolução" if acc < 0.88 else "Desempenho forte — manter" 
    return {"known_subjects": len(known), "total_subjects": sum(1 for m in metrics if not m.get("is_essay")), "weighted_accuracy": acc, "label": label}


def exam_pace(profile: dict[str, Any], profile_key: str, today: date | None = None) -> dict[str, Any] | None:
    today = today or date.today()
    cfg = profile.get("calendar_settings", {})
    exam_day = _parse_day(cfg.get("exam_date"))
    if not exam_day:
        return None
    days_left = (exam_day - today).days
    missions = sorted(profile.get("mission_data", []), key=lambda m: int(m.get("global_index", 0)))
    completed = set(profile.get("completed_missions", []))
    pending = sum(1 for m in missions if m.get("id") not in completed)
    minimum = max(1, safe_count(cfg.get("daily_minimum", 1)))
    required_daily = ceil(pending / max(1, days_left)) if days_left > 0 else (pending if pending else 0)
    estimated_minutes_left = 0
    if profile_key == "caixa":
        from schedule_system import estimated_minutes
        estimated_minutes_left = sum(estimated_minutes(m, profile_key) for m in missions if m.get("id") not in completed)
    else:
        estimated_minutes_left = pending * (55 if profile_key == "python" else 35)
    daily_minutes = max(1, safe_count(cfg.get("daily_minutes", 60)))
    time_required_per_day = ceil(estimated_minutes_left / max(1, days_left)) if days_left > 0 else estimated_minutes_left
    if days_left < 0:
        status = "Data-alvo passou"
    elif days_left == 0:
        status = "Dia da prova"
    elif pending == 0:
        status = "Trilha concluída: fase de revisão e simulados"
    elif time_required_per_day <= daily_minutes and required_daily <= minimum:
        status = "Ritmo compatível com a data-alvo"
    elif time_required_per_day <= daily_minutes:
        status = f"Ajuste o mínimo para cerca de {required_daily} tópico(s)/dia; a carga estimada cabe no tempo"
    else:
        status = "Ajuste necessário: carga acima do tempo disponível"
    return {
        "exam_date": exam_day, "days_left": days_left, "pending_lessons": pending,
        "required_daily_lessons": required_daily, "daily_minimum": minimum,
        "estimated_minutes_left": estimated_minutes_left,
        "time_required_per_day": time_required_per_day, "daily_minutes": daily_minutes,
        "status": status,
    }


def next_spacing_date(completion_day: date, stage_index: int) -> date | None:
    """Stage 1 -> 1 day; stage 2 -> 7 days; stage 3 -> 30 days; then stop."""
    if stage_index < 1 or stage_index > len(SPACED_REPETITION_DAYS):
        return None
    return completion_day + timedelta(days=SPACED_REPETITION_DAYS[stage_index - 1])


def _allocate_quotas(weights: dict[str, float], count: int) -> dict[str, int]:
    if not weights or count <= 0:
        return {key: 0 for key in weights}
    total = sum(max(0.0, value) for value in weights.values())
    if total <= 0:
        each = count // len(weights)
        out = {key: each for key in weights}
        for key in list(out)[:count - each * len(out)]:
            out[key] += 1
        return out
    raw = {key: count * max(0.0, value) / total for key, value in weights.items()}
    out = {key: floor(value) for key, value in raw.items()}
    remainder = count - sum(out.values())
    for key in sorted(raw, key=lambda k: raw[k] - out[k], reverse=True)[:remainder]:
        out[key] += 1
    return out


def build_adaptive_question_set(profile: dict[str, Any], profile_key: str, count: int = 20, rng=None) -> list[dict[str, Any]]:
    """Build a non-official practice sim weighted by subject importance and observed weakness."""
    import random
    rng = rng or random
    groups = group_missions(profile)
    metrics = {m["subject"]: m for m in subject_metrics(profile, profile_key)}
    pools: dict[str, list[dict[str, Any]]] = {}
    subject_weights: dict[str, float] = {}
    for subject, missions in groups.items():
        if profile_key == "caixa" and "redação" in subject.casefold():
            continue
        seen: set[str] = set()
        pool = []
        for mission in missions:
            for q in mission.get("quiz", []):
                question_text = str(q.get("q", "")).strip()
                if not question_text or question_text in seen:
                    continue
                seen.add(question_text)
                item = dict(q)
                item["_planner_subject"] = subject
                pool.append(item)
        if not pool:
            continue
        pools[subject] = pool
        metric = metrics.get(subject, {})
        priority = max(0.2, safe_num(metric.get("priority_score", 1.0)))
        if profile_key == "caixa":
            base_weight = OBJECTIVE_QUESTIONS.get(subject, max(1, safe_num(metric.get("weight", 5))))
            # Slightly oversample weak topics without losing the underlying exam weighting.
            subject_weights[subject] = float(base_weight) * (0.65 + min(1.0, priority / 1.8) * 0.7)
        else:
            # For Python/custom tracks, prioritize gaps while retaining broad coverage.
            subject_weights[subject] = priority
    quotas = _allocate_quotas(subject_weights, count)
    chosen: list[dict[str, Any]] = []
    chosen_text: set[str] = set()
    shortages = 0
    for subject, quota in quotas.items():
        pool = [q for q in pools.get(subject, []) if q.get("q") not in chosen_text]
        take = min(quota, len(pool))
        if take:
            selected = rng.sample(pool, take)
            chosen.extend(selected)
            chosen_text.update(q.get("q") for q in selected)
        shortages += quota - take
    if shortages:
        remaining = [q for pool in pools.values() for q in pool if q.get("q") not in chosen_text]
        take = min(shortages, len(remaining))
        if take:
            selected = rng.sample(remaining, take)
            chosen.extend(selected)
            chosen_text.update(q.get("q") for q in selected)
    # Very small/custom curricula may not contain enough unique questions. Reuse explicitly,
    # but annotate the duplicate so it is not mistaken for new material in the report.
    if len(chosen) < count:
        all_questions = [q for pool in pools.values() for q in pool]
        while all_questions and len(chosen) < count:
            item = dict(rng.choice(all_questions))
            item["_repeated_in_sim"] = True
            chosen.append(item)
    rng.shuffle(chosen)
    return chosen[:count]


def build_caixa_weighted_mock(profile: dict[str, Any], rng=None) -> list[dict[str, Any]]:
    """Build a 60-question practice test using the exact objective distribution in the
    attached 2024 TBN (non-IT) edital. Questions are app-created, not official Cesgranrio items.
    """
    import random
    if rng is None:
        rng = random
    missions_by_subject = group_missions(profile)
    pools: dict[str, list[dict[str, Any]]] = {}
    for subject in OBJECTIVE_QUESTIONS:
        seen = set()
        pool = []
        for mission in missions_by_subject.get(subject, []):
            for source in mission.get("quiz", []):
                prompt = str(source.get("q", "")).strip()
                if not prompt or prompt in seen:
                    continue
                seen.add(prompt)
                question = dict(source)
                question["_planner_subject"] = subject
                question["_exam_block"] = "Conhecimentos Básicos" if subject in {
                    "Língua Portuguesa", "Língua Inglesa", "Matemática Financeira",
                    "Probabilidade e Estatística", "Ética e Compliance"
                } else "Conhecimentos Específicos"
                pool.append(question)
        pools[subject] = pool

    chosen: list[dict[str, Any]] = []
    used_prompts: set[str] = set()
    deficits: dict[str, int] = {}
    for subject, quota in OBJECTIVE_QUESTIONS.items():
        eligible = [q for q in pools.get(subject, []) if q.get("q") not in used_prompts]
        take = min(quota, len(eligible))
        if take:
            sample = rng.sample(eligible, take)
            chosen.extend(sample)
            used_prompts.update(q.get("q") for q in sample)
        deficits[subject] = quota - take

    # The supplied curriculum has enough unique questions per subject for a full set. Keep a
    # defensive fallback so edited/customized saves still return 60 items where possible.
    for subject, deficit in list(deficits.items()):
        while deficit > 0:
            eligible = [q for q in pools.get(subject, []) if q.get("q") not in used_prompts]
            if not eligible:
                break
            question = rng.choice(eligible)
            chosen.append(question)
            used_prompts.add(question.get("q"))
            deficit -= 1
        deficits[subject] = deficit

    # If a user has edited away questions in one subject, do not silently claim an exact mock.
    if any(deficits.values()):
        missing_total = sum(deficits.values())
        fill_pool = [q for pool in pools.values() for q in pool if q.get("q") not in used_prompts]
        fill_take = min(missing_total, len(fill_pool))
        if fill_take:
            chosen.extend(rng.sample(fill_pool, fill_take))

    rng.shuffle(chosen)
    return chosen


def essay_metrics(profile: dict[str, Any]) -> tuple[float | None, int, date | None]:
    """Calculate self-assessed essay rubric only; this is not an automatic writing grade."""
    logs = profile.get("essay_practice_log", [])
    valid = [x for x in logs if isinstance(x, dict) and isinstance(x.get("rubric_score"), (int, float)) and x.get("rubric_score") >= 0]
    if not valid:
        return None, 0, None
    recent = valid[-3:]
    scores = [max(0, min(5, safe_count(x.get("rubric_score", 0)))) / 5.0 for x in recent]
    latest_day = _parse_day(valid[-1].get("date"))
    return sum(scores) / len(scores), len(valid), latest_day
