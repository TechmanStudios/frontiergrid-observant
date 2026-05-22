from __future__ import annotations

import argparse
from pathlib import Path

from frontiergrid_observant.ingest.loader import write_jsonl
from frontiergrid_observant.ingest.synthetic_generator import (
    SCENARIOS,
    generate_all,
    generate_scenario,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create unclassified synthetic scenario JSONL files."
    )
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="scenario_01")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--seed", type=int, default=149)
    parser.add_argument("--ticks", type=int, default=30)
    parser.add_argument("--out", type=Path, default=Path("data/synthetic"))
    args = parser.parse_args()
    if args.all:
        for scenario_id, events in generate_all(seed=args.seed, ticks=args.ticks).items():
            write_jsonl(events, args.out / f"{scenario_id}.jsonl")
        return
    events = generate_scenario(args.scenario, seed=args.seed, ticks=args.ticks)
    write_jsonl(events, args.out / f"{events[0].scenario_id}.jsonl")


if __name__ == "__main__":
    main()
