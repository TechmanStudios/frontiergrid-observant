"""Runtime configuration helpers for FrontierGrid-Observant."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_root: Path = Path("data")
    artifact_root: Path = Path("artifacts/demo")
    frontier_os_root: Path | None = None
    frontier_os_node_count: int = 1024
    frontier_os_tau_threshold: float = 1.0
    sol_root: Path | None = None


def _workspace_default(path_parts: tuple[str, ...]) -> Path | None:
    workspace_root = Path(__file__).resolve().parents[2]
    candidate = workspace_root.joinpath(*path_parts)
    return candidate if candidate.exists() else None


def load_settings() -> Settings:
    frontier_os_root = os.getenv("FRONTIER_OS_ROOT")
    sol_root = os.getenv("SOL_ROOT")
    return Settings(
        data_root=Path(os.getenv("FRONTIERGRID_DATA_ROOT", "data")),
        artifact_root=Path(os.getenv("FRONTIERGRID_ARTIFACT_ROOT", "artifacts/demo")),
        frontier_os_root=Path(frontier_os_root)
        if frontier_os_root
        else _workspace_default(("Frontier_OS-main", "Frontier_OS-main", "Exciton-MoA")),
        frontier_os_node_count=int(os.getenv("FRONTIER_OS_NODE_COUNT", "1024")),
        frontier_os_tau_threshold=float(os.getenv("FRONTIER_OS_TAU_THRESHOLD", "1.0")),
        sol_root=Path(sol_root) if sol_root else _workspace_default(("sol-main", "sol-main")),
    )
