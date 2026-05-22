from __future__ import annotations

from frontiergrid_observant.demo.run_demo import run_demo
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS


def main() -> None:
    for scenario in sorted(SCENARIOS):
        payload = run_demo(scenario=scenario, export=True)
        print(f"{payload['scenario_id']}: {len(payload['alerts'])} alert(s)")


if __name__ == "__main__":
    main()
