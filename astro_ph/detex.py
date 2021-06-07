import re
from dataclasses import dataclass


@dataclass
class ReplaceRule:
    pattern: str
    replacement: str

    def __post_init__(self):
        self._pattern = re.compile(self.pattern)

    def apply(self, text: str) -> str:
        return self._pattern.sub(self.replacement, text)


DETEX_RULES = [
    ReplaceRule(r"\\text(bb|bf|it|gt|mc|md|rm|sc|sf|sl|tt|up){(.+?)}", r"\2"),
    ReplaceRule(r"{\\text(bb|bf|it|gt|mc|md|rm|sc|sf|sl|tt|up) (.+?)}", r"\2"),
    ReplaceRule(r"{\\(bf|em|it|rm|sc|sf|sl|tt) (.+?)}", r"\2"),
    ReplaceRule(r"\\emph{(.+?)}", r"\1"),
    ReplaceRule(r"(\n+\s*|\n*\s+)", " "),
]


def detex(text: str) -> str:
    """Remove TeX's control commands from text."""
    for rule in DETEX_RULES:
        text = rule.apply(text)

    return text
