from __future__ import annotations


# standard library
import re
from dataclasses import dataclass, replace
from typing import Pattern, Optional, Sequence, Union


# third-party packages
from typing_extensions import Final


# constants
SEPARATOR: Final[str] = "++++++++++"


# data classes
@dataclass
class Article:
    """Article class for storing article information."""

    title: str  #: Title of an article.
    authors: Sequence[str]  #: Author(s) of an article.
    summary: str  #: Summary of an article.
    arxiv_url: str  #: arXiv URL of an article.

    def __post_init__(self) -> None:
        self.title = detex(self.title)
        self.summary = detex(self.summary)

    def replace(self, text: str, translated: str) -> Article:
        """Method necessary to become translatable."""
        title, summary = translated.split(SEPARATOR)
        return replace(self, title=title, summary=summary)

    def __str__(self) -> str:
        """Method necessary to become translatable."""
        return f"{self.title}\n{SEPARATOR}\n{self.summary}"


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


# utility functions
default_rules = [
    Rule(r"\\text(bb|bf|it|gt|mc|md|rm|sc|sf|sl|tt|up){(.+?)}", r"\2"),
    Rule(r"{\\text(bb|bf|it|gt|mc|md|rm|sc|sf|sl|tt|up) (.+?)}", r"\2"),
    Rule(r"{\\(bf|em|it|rm|sc|sf|sl|tt) (.+?)}", r"\2"),
    Rule(r"\\emph{(.+?)}", r"\1"),
    Rule(r"(\n+\s*|\n*\s+)", " "),
]


def detex(text: str, rules: Optional[Sequence[Rule]] = None) -> str:
    """Remove TeX's control commands from text."""
    if rules is None:
        rules = default_rules

    for rule in rules:
        text = rule.apply(text)

    return text
