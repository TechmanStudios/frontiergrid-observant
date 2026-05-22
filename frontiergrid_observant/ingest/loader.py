"""JSONL event loading utilities."""

from __future__ import annotations

import json
from pathlib import Path

from frontiergrid_observant.schemas.events import ObservantEvent


def read_jsonl(path: Path) -> list[ObservantEvent]:
    events: list[ObservantEvent] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                events.append(ObservantEvent.model_validate(json.loads(line)))
    return events


def write_jsonl(events: list[ObservantEvent], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(event.model_dump_json() + "\n")
