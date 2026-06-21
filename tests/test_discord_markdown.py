from study_discord_agent.discord_markdown import discord_safe_markdown


def test_discord_safe_markdown_converts_pipe_table_to_bullets() -> None:
    text = "\n".join(
        [
            "Priority",
            "| Rank | Issue | Why |",
            "|---|---|---|",
            "| 1 | #55 Add eval harness | Beta-critical |",
            "| 2 | #50 Data validation | Builds trust |",
            "",
            "Done.",
        ],
    )

    assert discord_safe_markdown(text) == "\n".join(
        [
            "Priority",
            "- Rank: 1; Issue: #55 Add eval harness; Why: Beta-critical",
            "- Rank: 2; Issue: #50 Data validation; Why: Builds trust",
            "",
            "Done.",
        ],
    )


def test_discord_safe_markdown_leaves_regular_pipes_alone() -> None:
    text = "Use `a | b` in a shell pipeline, then continue."

    assert discord_safe_markdown(text) == text
