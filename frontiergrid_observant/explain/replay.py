"""Replay export helpers."""

from __future__ import annotations

from pathlib import Path

from frontiergrid_observant.schemas.provenance import ReplayTrace


def write_replay_markdown(trace: ReplayTrace, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(trace.to_markdown(), encoding="utf-8")
