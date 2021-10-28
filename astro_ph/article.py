from __future__ import annotations


# standard library
from dataclasses import dataclass, replace
from typing import List, Optional


# dependencies
from arxiv import Result  # type: ignore


# submodules
from .detex import detex


# constants
TITLE_SUMMARY_DIV = "+" * 16


# dataclasses
@dataclass
class Article:
    """Data class for arXiv articles."""

    title: str  #: Title of the article.
    authors: List[str]  #: Author list of the article.
    summary: str  #: Summary (abstract) of the article.
    arxiv_url: str  #: arXiv URL of the article.
    original: Optional[Article] = None  #: For translation.

    def __post_init__(self) -> None:
        self.title = detex(self.title)
        self.summary = detex(self.summary)

    @property
    def arxiv_pdf_url(self) -> str:
        return self.arxiv_url.replace("abs", "pdf")

    @classmethod
    def from_arxiv_result(cls, result: Result) -> Article:
        return Article(
            title=result.title,
            authors=[a.name for a in result.authors],  # type: ignore
            summary=result.summary,
            arxiv_url=str(result),
        )

    def replace(self, original: str, translated: str) -> Article:
        title, summary = translated.split(TITLE_SUMMARY_DIV)
        return replace(self, title=title, summary=summary, original=self)

    def __str__(self) -> str:
        return f"{self.title}\n{TITLE_SUMMARY_DIV}\n{self.summary}"
