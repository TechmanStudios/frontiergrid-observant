from __future__ import annotations

import argparse
from pathlib import Path

from frontiergrid_observant.demo.dashboard import export_demo_dashboard
from frontiergrid_observant.demo.run_demo import run_demo
from frontiergrid_observant.eval.ablation_study import export_ablation_study
from frontiergrid_observant.eval.compare_substrates import export_substrate_comparison
from frontiergrid_observant.eval.evidence_summary import export_evidence_summary
from frontiergrid_observant.eval.stress_study import export_stress_study
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Export FrontierGrid-Observant demo artifacts.")
    parser.add_argument("--substrate", default="frontier_os", choices=["fallback", "frontier_os"])
    parser.add_argument("--seed", type=int, default=149)
    parser.add_argument("--ticks", type=int, default=30)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--skip-ablation", action="store_true")
    parser.add_argument("--skip-comparison", action="store_true")
    parser.add_argument("--skip-dashboard", action="store_true")
    parser.add_argument("--skip-evidence-summary", action="store_true")
    parser.add_argument("--include-stress", action="store_true")
    parser.add_argument("--stress-runs", type=int, default=5)
    args = parser.parse_args(argv)

    for scenario in sorted(SCENARIOS):
        print(f"Exporting {scenario} with {args.substrate} substrate...")
        run_demo(
            scenario=scenario,
            substrate=args.substrate,
            seed=args.seed,
            ticks=args.ticks,
            export=True,
            artifact_root=args.artifact_root,
        )

    if not args.skip_comparison:
        print("Exporting fallback/native comparison...")
        export_substrate_comparison(
            seed=args.seed,
            ticks=args.ticks,
            artifact_root=args.artifact_root,
        )

    if not args.skip_ablation:
        print("Exporting ablation study...")
        export_ablation_study(
            seed=args.seed,
            ticks=args.ticks,
            artifact_root=args.artifact_root,
        )

    if args.include_stress:
        print(f"Exporting randomized stress study over {args.stress_runs} runs...")
        export_stress_study(
            seed=args.seed,
            runs=args.stress_runs,
            ticks=args.ticks,
            artifact_root=args.artifact_root,
            progress=True,
            refresh_dashboard=not args.skip_dashboard,
        )
        if not args.skip_evidence_summary:
            print("Exporting scenario evidence summary...")
            export_evidence_summary(args.artifact_root)

    if not args.skip_dashboard:
        print("Exporting static dashboard...")
        export_demo_dashboard(args.artifact_root)

    print("Demo artifact export complete.")


if __name__ == "__main__":
    main()
