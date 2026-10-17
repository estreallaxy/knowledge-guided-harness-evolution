import argparse
from clonemem.common.config import load_yaml
from clonemem.build.runners import (
    run_build_sync,
    run_qa_only_sync,
    run_postprocess_sync,
    run_trace_data_only_sync
)


def main() -> None:
    parser = argparse.ArgumentParser(prog="clonemem")
    sub = parser.add_subparsers(dest="command", required=True)

    # clonemem trace-only --config configs/build.yaml
    p_trace = sub.add_parser("trace-only", help="Generate trace data only (events + medias), no QA/benchmark")
    p_trace.add_argument("--config", required=True, help="Path to YAML config")
    p_trace.add_argument("--person-id", default=None, help="Override person.person_id")
    p_trace.add_argument("--name", default=None, help="Override person.display_name")

    # clonemem qa-only --config configs/build.yaml --person-id <person_id>
    p_qa = sub.add_parser("qa-only", help="Build QA only from an existing person in Neo4j")
    p_qa.add_argument("--config", required=True, help="Path to YAML config")
    p_qa.add_argument("--person-id", required=True, help="Person ID in Neo4j")

    # clonemem postprocess --config configs/build.yaml --person-id b2df4690-4d0e-47f3-b863-f8584bd5880c --person-name 林子昂
    p_pp = sub.add_parser("postprocess", help="QA postprocessing (verify/MCQ/translate)")
    p_pp.add_argument("--config", required=True, help="Path to YAML config")
    p_pp.add_argument("--person-id", required=True)
    p_pp.add_argument("--person-name", required=True)
    p_pp.add_argument("--output-dir", default=None, help="Base output dir (default: outputs/<run_id>/postprocess)")
    p_pp.add_argument("--model", default=None, help="LLM model for postprocessing")
    p_pp.add_argument("--validation-model", default=None, help="LLM model for verification")

    # clonemem build --config configs/build.yaml
    p_build = sub.add_parser("build", help="Build/generate CloneMem data & QA")
    p_build.add_argument("--config", required=True, help="Path to YAML config")
    p_build.add_argument("--person-id", default=None, help="Override person.person_id")
    p_build.add_argument("--name", default=None, help="Override person.display_name")

    args = parser.parse_args()

    if args.command == "postprocess":
        cfg = load_yaml(args.config)
        run_postprocess_sync(
            cfg,
            person_id=args.person_id,
            person_name=args.person_name,
            model=args.model,
            validation_model=args.validation_model,
        )
        return

    if args.command == "qa-only":
        cfg = load_yaml(args.config)
        run_qa_only_sync(cfg, args.person_id)
        return

    if args.command == "trace-only":
        cfg = load_yaml(args.config)

        if args.person_id:
            cfg.setdefault("person", {})["person_id"] = args.person_id
        if args.name:
            cfg.setdefault("person", {})["display_name"] = args.name

        person, relations, life_arcs, run_id = run_trace_data_only_sync(cfg)
        print(f"[trace-only] done. run_id={run_id}")
        print(f"[trace-only] person_id={getattr(person, 'id', None) or cfg.get('person', {}).get('person_id')}")
        print(f"[trace-only] relations={len(relations) if relations is not None else 'N/A'}")
        print(f"[trace-only] life_arcs={len(life_arcs) if life_arcs is not None else 'N/A'}")
        return

    if args.command == "build":
        cfg = load_yaml(args.config)

        if args.person_id:
            cfg.setdefault("person", {})["person_id"] = args.person_id
        if args.name:
            cfg.setdefault("person", {})["display_name"] = args.name

        run_build_sync(cfg)
        return

    raise SystemExit(f"Unknown command: {args.command}")
