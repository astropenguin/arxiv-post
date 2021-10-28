__all__ = ["detex"]


# standard library
import re
from dataclasses import dataclass
from typing import Pattern, Union


# constants
@dataclass
class ReplaceRule:
    """Class for replacing rules of texts."""

    pattern: Union[Pattern[str], str]
    replacement: str

    def apply(self, text: str) -> str:
        if isinstance(self.pattern, str):
            self.pattern = re.compile(self.pattern)

        return self.pattern.sub(self.replacement, text)


DETEX_RULES = [
    ReplaceRule(r"\\text(bb|bf|it|gt|mc|md|rm|sc|sf|sl|tt|up){(.+?)}", r"\2"),
    ReplaceRule(r"{\\text(bb|bf|it|gt|mc|md|rm|sc|sf|sl|tt|up) (.+?)}", r"\2"),
    ReplaceRule(r"{\\(bf|em|it|rm|sc|sf|sl|tt) (.+?)}", r"\2"),
    ReplaceRule(r"\\emph{(.+?)}", r"\1"),
    ReplaceRule(r"(\n+\s*|\n*\s+)", " "),
]


# runtime functions
def detex(text: str) -> str:
    """Remove TeX's control commands from a text."""
    for rule in DETEX_RULES:
        text = rule.apply(text)

    return text
