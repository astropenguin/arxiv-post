__all__ = ["Article"]


# standard library
from dataclasses import dataclass, field, replace
from typing import List, Optional


# dependencies
import re
from arxiv import Result
from pylatexenc.latex2text import LatexNodes2Text


# dataclasses
@dataclass
class Article:
    """Dataclass for arXiv articles."""

    title: str
    """Title of the article."""

    authors: List[str]
    """Author list of the article."""

    summary: str
    """Summary of the article."""

    arxiv_url: str
    """arXiv URL of the article."""

    original: Optional["Article"] = field(default=None, compare=False)
    """Original article before translation (if any)."""

    @property
    def arxiv_pdf_url(self) -> str:
        """arXiv PDF URL of the article."""
        return self.arxiv_url.replace("abs", "pdf")

    @classmethod
    def from_arxiv_result(cls, result: Result) -> "Article":
        """Create an article from an arXiv query result."""
        return Article(
            title=result.title,
            authors=[a.name for a in result.authors],
            summary=result.summary,
            arxiv_url=str(result),
        )

    def replace(self, original: str, translated: str) -> "Article":
        """Text replacement method for translation."""
        title, summary = translated.split("\n", 1)
        return replace(self, title=title, summary=summary, original=self)

    def __str__(self) -> str:
        """Text output method for translation."""
        return f"{self.title}\n{self.summary}"

    def __post_init__(self) -> None:
        """Remove TeX's control commands from texts."""
        self.title = detex(self.title)
        self.summary = detex(self.summary)


# runtime functions
def detex(text: str) -> str:
    """Remove TeX's control commands from a text."""
    text = re.sub(r"(\n+\s*|\n*\s+)", " ", text)
    return LatexNodes2Text(keep_comments=True).latex_to_text(text)
