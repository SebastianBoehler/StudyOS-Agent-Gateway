import argparse
import shutil
import subprocess
from pathlib import Path


def build_dot_command(input_path: Path, output_path: Path, output_format: str) -> list[str]:
    return ["dot", f"-T{output_format}", str(input_path), "-o", str(output_path)]


def render_graphviz(input_path: Path, output_path: Path, output_format: str = "png") -> None:
    if shutil.which("dot") is None:
        raise RuntimeError("Graphviz 'dot' is required to render diagrams")
    if not input_path.exists():
        raise RuntimeError(f"Diagram source does not exist: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_dot_command(input_path, output_path, output_format)
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        error = completed.stderr.strip() or "unknown Graphviz error"
        raise RuntimeError(f"Diagram render failed: {error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Graphviz DOT diagrams for Discord upload")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--format", default="png", choices=["png", "svg", "pdf"])
    args = parser.parse_args()
    try:
        render_graphviz(args.input, args.output, args.format)
    except RuntimeError as exc:
        raise SystemExit(f"studyos-render-diagram failed: {exc}") from exc


if __name__ == "__main__":
    main()
