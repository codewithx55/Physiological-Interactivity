"""Evaluate baseline VAD against physiology-aware turn-taking."""

from __future__ import annotations

from dataclasses import dataclass

from src.features.physiology_features import extract_turn_features
from src.sensors.simulator import Scenario, TimelineEvent, load_scenarios
from src.turn_taking.baseline_vad_policy import BaselineVadPolicy, PolicyDecision
from src.turn_taking.physiology_aware_policy import PhysiologyAwarePolicy


@dataclass(frozen=True)
class PolicyMetrics:
    policy: str
    false_interruptions: int
    true_end_latency_ms: float
    unnecessary_wait_ms: int
    clarify_hits: int
    score: float


@dataclass(frozen=True)
class EvaluatedEvent:
    scenario_id: str
    scenario_title: str
    event: TimelineEvent
    baseline: PolicyDecision
    physiology: PolicyDecision


def evaluate_events(scenarios: list[Scenario] | None = None) -> list[EvaluatedEvent]:
    baseline_policy = BaselineVadPolicy()
    physiology_policy = PhysiologyAwarePolicy()
    rows: list[EvaluatedEvent] = []
    for scenario in scenarios or load_scenarios():
        for event in scenario.events:
            features = extract_turn_features(event)
            rows.append(
                EvaluatedEvent(
                    scenario_id=scenario.id,
                    scenario_title=scenario.title,
                    event=event,
                    baseline=baseline_policy.decide(features),
                    physiology=physiology_policy.decide(features),
                )
            )
    return rows


def _metrics_for(policy_name: str, rows: list[EvaluatedEvent]) -> PolicyMetrics:
    false_interruptions = 0
    clarify_hits = 0
    latency_values: list[int] = []
    unnecessary_wait_ms = 0

    by_scenario: dict[str, list[EvaluatedEvent]] = {}
    for row in rows:
        by_scenario.setdefault(row.scenario_id, []).append(row)

    for scenario_rows in by_scenario.values():
        first_done_ms: int | None = None
        first_response_ms: int | None = None

        for row in scenario_rows:
            decision = getattr(row, policy_name)
            event = row.event
            if event.ground_truth == "done" and first_done_ms is None:
                first_done_ms = event.at_ms
            if decision.action == "RESPOND" and first_response_ms is None:
                first_response_ms = event.at_ms
            if decision.action == "RESPOND" and event.ground_truth == "continue":
                false_interruptions += 1
            if event.ground_truth == "clarify" and decision.action == "ASK_SHORT_CLARIFYING_QUESTION":
                clarify_hits += 1
            if (
                event.ground_truth == "done"
                and first_response_ms is None
                and decision.action in {"WAIT", "LISTEN"}
            ):
                unnecessary_wait_ms += event.silence_ms

        if first_done_ms is not None:
            if first_response_ms is None or first_response_ms < first_done_ms:
                latency_values.append(1500)
            else:
                latency_values.append(first_response_ms - first_done_ms)

    true_end_latency_ms = sum(latency_values) / len(latency_values) if latency_values else 0.0
    score = 100.0
    score -= false_interruptions * 22
    score -= true_end_latency_ms / 100
    score -= unnecessary_wait_ms / 300
    score += clarify_hits * 8
    score = min(100.0, max(0.0, score))

    return PolicyMetrics(
        policy=policy_name,
        false_interruptions=false_interruptions,
        true_end_latency_ms=round(true_end_latency_ms, 1),
        unnecessary_wait_ms=unnecessary_wait_ms,
        clarify_hits=clarify_hits,
        score=round(score, 1),
    )


def evaluate() -> tuple[list[EvaluatedEvent], list[PolicyMetrics]]:
    rows = evaluate_events()
    return rows, [_metrics_for("baseline", rows), _metrics_for("physiology", rows)]


def print_report() -> None:
    rows, metrics = evaluate()
    print("Physiology-aware Turn-Taking Eval")
    print()
    print("policy,false_interruptions,true_end_latency_ms,unnecessary_wait_ms,clarify_hits,score")
    for metric in metrics:
        print(
            f"{metric.policy},{metric.false_interruptions},{metric.true_end_latency_ms},"
            f"{metric.unnecessary_wait_ms},{metric.clarify_hits},{metric.score}"
        )
    print()
    print("Key events")
    for row in rows:
        if row.event.speech_active:
            continue
        print(
            f"{row.scenario_id} t={row.event.at_ms}ms truth={row.event.ground_truth} "
            f"baseline={row.baseline.action} physiology={row.physiology.action} "
            f"breath={row.event.breath_phase} silence={row.event.silence_ms}ms"
        )


def main() -> int:
    print_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
