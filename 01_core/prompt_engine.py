def expand_prompt(name: str, variables: dict[str, str]) -> str:
    text = name
    for key, value in variables.items():
        text = text.replace("{" + key + "}", value)
    return text
