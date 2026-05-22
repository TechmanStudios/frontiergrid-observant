"""Minimal deterministic context graph for Phase I fallback reasoning."""

from __future__ import annotations

from collections import defaultdict

from frontiergrid_observant.schemas.events import ObservantEvent


class ContextGraph:
    def __init__(self) -> None:
        self.events: dict[str, ObservantEvent] = {}
        self.entity_events: dict[str, list[str]] = defaultdict(list)
        self.risk_events: dict[str, list[str]] = defaultdict(list)

    def add_event(self, event: ObservantEvent) -> None:
        self.events[event.event_id] = event
        for entity_id in event.entity_refs:
            self.link_entity_event(entity_id, event.event_id)
        self.risk_events[event.risk_type].append(event.event_id)

    def link_entity_event(self, entity_id: str, event_id: str) -> None:
        if event_id not in self.entity_events[entity_id]:
            self.entity_events[entity_id].append(event_id)

    def get_entity_timeline(self, entity_id: str) -> list[ObservantEvent]:
        return [self.events[event_id] for event_id in self.entity_events.get(entity_id, [])]

    def find_supporting_events(self, alert_type: str, tick: int, window: int = 6) -> list[str]:
        candidates = []
        for event_id in self.risk_events.get(alert_type, []):
            event = self.events[event_id]
            if event.is_anomaly and 0 <= tick - event.tick <= window:
                candidates.append(event_id)
        return candidates[-5:]

    def find_contradicting_events(self, alert_type: str, tick: int, window: int = 6) -> list[str]:
        contradictions = []
        for event in self.events.values():
            if (
                event.risk_type == "nominal"
                and 0 <= tick - event.tick <= window
                and any(
                    value in event.attributes.values() for value in ["routine_transit", "stable"]
                )
            ):
                contradictions.append(event.event_id)
        return contradictions[-3:]

    def latest_tick(self) -> int:
        return max((event.tick for event in self.events.values()), default=0)

    def latest_events(self, limit: int = 5) -> list[ObservantEvent]:
        return sorted(self.events.values(), key=lambda event: event.tick)[-limit:]
