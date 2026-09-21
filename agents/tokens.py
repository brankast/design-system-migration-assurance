from __future__ import annotations

STOPWORDS = frozenset(
    {
        "event",
        "value",
        "values",
        "name",
        "type",
        "class",
        "data",
        "id",
        "true",
        "false",
        "null",
        "string",
        "number",
        "boolean",
        "input",
        "output",
        "model",
        "instead",
    }
)


def api_score(symbol: str) -> int:
    token = symbol.strip()
    if not token or token.lower() in STOPWORDS or len(token) < 4:
        return 0
    score = 1
    if "." in token:
        score += 5
    if token.startswith(("Mat", "Cdk", "CDK", "MAT_", "CDK_")):
        score += 4
    if any(char.isupper() for char in token[1:]):
        score += 2
    if len(token) >= 8:
        score += 1
    return score


def pick_affected_api(symbols: list[str]) -> str | None:
    ranked = sorted((item.strip() for item in symbols), key=api_score, reverse=True)
    for token in ranked:
        if api_score(token) > 0:
            return token
    return None


def is_distinctive_token(token: str) -> bool:
    return api_score(token) >= 2
