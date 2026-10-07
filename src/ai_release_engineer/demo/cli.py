"""Command-line interface for the reproducible Phase 1 MVP demo."""

import argparse
import json
from pathlib import Path

from ai_release_engineer.demo.runner import run_demo
from ai_release_engineer.demo.scenarios import DemoScenario, get_demo_scenario
from ai_release_engineer.runner import DockerCommandRunner


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the AI Release Engineer Phase 1 MVP demonstration.",
    )
    parser.add_argument(
        "--scenario",
        choices=[scenario.value for scenario in DemoScenario],
        default=DemoScenario.SUCCESS.value,
        help="Run the passing scenario or the intentionally failing validation scenario.",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("examples/mvp_demo/target_repo"),
        help="Path to the demo target repository.",
    )
    parser.add_argument(
        "--image",
        default="ai-release-engineer-demo:local",
        help="Docker image containing the validation tools.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".demo-output"),
        help="Directory for the generated evidence JSON.",
    )
    return parser


def main() -> int:
    """Run the selected scenario and print a concise evidence summary."""
    args = _parser().parse_args()
    scenario_name = DemoScenario(args.scenario)
    scenario = get_demo_scenario(scenario_name)
    source_root = args.source_root.expanduser().resolve()

    result = run_demo(
        scenario=scenario,
        source_root=source_root,
        runner=DockerCommandRunner(image=args.image),
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = args.output_dir / f"mvp-{scenario_name.value}.json"
    evidence_path.write_text(
        result.evidence.model_dump_json(indent=2),
        encoding="utf-8",
    )

    summary = {
        "scenario": scenario_name.value,
        "run_id": str(result.evidence.run_id),
        "status": result.evidence.status.value,
        "validation_gate_passed": result.validation_gate_passed,
        "expected_to_pass": result.expected_to_pass,
        "files_changed": result.evidence.change_summary.files_changed,
        "additions": result.evidence.change_summary.additions,
        "deletions": result.evidence.change_summary.deletions,
        "evidence_file": str(evidence_path),
    }
    print(json.dumps(summary, indent=2))

    if result.validation_gate_passed != result.expected_to_pass:
        return 3
    return 0 if result.validation_gate_passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
