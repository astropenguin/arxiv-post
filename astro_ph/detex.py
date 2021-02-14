# standard library
import re
from dataclasses import dataclass
from typing import Pattern, Optional, Sequence, Union


# third-party packages
from typing_extensions import Final


# data classes
@dataclass
class Rule:
    """Rule class for replacing one string with another."""

    pattern: Union[Pattern, str]  #: Text or pattern for search.
    replacement: str  #: Text or pattern for replacement.

    def __post_init__(self):
        if isinstance(self.pattern, str):
            self.pattern = re.compile(self.pattern)

    def apply(self, text: str) -> str:
        """Apply the rule to text."""
        return self.pattern.sub(self.replacement, text)


# constants
DEFAULT_RULES: Final[Sequence[Rule]] = (
    Rule(r"\\text(bb|bf|it|gt|mc|md|rm|sc|sf|sl|tt|up){(.+?)}", r"\2"),
    Rule(r"{\\text(bb|bf|it|gt|mc|md|rm|sc|sf|sl|tt|up) (.+?)}", r"\2"),
    Rule(r"{\\(bf|em|it|rm|sc|sf|sl|tt) (.+?)}", r"\2"),
    Rule(r"\\emph{(.+?)}", r"\1"),
    Rule(r"(\n+\s*|\n*\s+)", " "),
)


# utility functions
def detex(text: str, rules: Optional[Sequence[Rule]] = None) -> str:
    """Remove TeX's control commands from text."""
    if rules is None:
        rules = DEFAULT_RULES

    for rule in rules:
        text = rule.apply(text)

    return text
