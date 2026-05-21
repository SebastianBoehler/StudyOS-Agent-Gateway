from pathlib import Path

from study_discord_agent.diagram_tool import build_dot_command


def test_build_dot_command_targets_png_output() -> None:
    command = build_dot_command(Path("flow.dot"), Path("flow.png"), "png")

    assert command == ["dot", "-Tpng", "flow.dot", "-o", "flow.png"]
