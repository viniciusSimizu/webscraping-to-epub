import re


def is_heading(text: str) -> bool:
    return bool(re.search(r'^PARTE\W+\d+$', text, re.IGNORECASE))


def strip_string(text: str) -> str:
    return re.sub('[\xa0\n]+', '', text).strip()
