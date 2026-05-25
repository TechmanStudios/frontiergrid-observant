import argparse
from frontiergrid_observant.demo.run_demo import run_demo
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all synthetic scenarios.")
    parser.add_argument("--substrate", default="frontier_os", choices=["fallback", "frontier_os"])
    args = parser.parse_args()

    for scenario in sorted(SCENARIOS):
        payload = run_demo(scenario=scenario, substrate=args.substrate, export=True)
        print(f"{payload['scenario_id']} on {args.substrate}: {len(payload['alerts'])} alert(s)")


if __name__ == "__main__":
    main()

