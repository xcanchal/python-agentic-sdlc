from agentic_sdlc.application.prompt_builder import build_prompt


def test_build_prompt() -> None:
    prompt = build_prompt(
        instructions="Agent instructions line 1\nline 2",
        title="Prompt title",
        description="Prompt description",
    )

    assert prompt == (
        "STAGE INSTRUCTIONS\n"
        "\n"
        "Agent instructions line 1\n"
        "line 2\n"
        "\n"
        "WORK ITEM\n"
        "\n"
        "Title:\n"
        "Prompt title\n"
        "\n"
        "Description:\n"
        "Prompt description"
    )
