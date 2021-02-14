from __future__ import annotations


# standard library
from dataclasses import dataclass, replace
from typing import Sequence


# third-party packages
from typing_extensions import Final
from .detex import detex


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


