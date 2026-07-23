"""콤마로 구분된 키워드 문자열을 리스트로 변환하는 함수."""


def parse_keywords(raw: str) -> list[str]:
    if not raw.strip():
        return []
    return [kw.strip() for kw in raw.split(",") if kw.strip()]
