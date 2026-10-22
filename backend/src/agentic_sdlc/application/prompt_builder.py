def build_prompt(*, instructions: str, title: str, description: str) -> str:
    return "\n\n".join(
        [
            "STAGE INSTRUCTIONS",
            instructions.strip(),
            "WORK ITEM",
            f"Title:\n{title}",
            f"Description:\n{description}",
        ]
    )
