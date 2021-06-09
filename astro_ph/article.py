from __future__ import annotations

from dataclasses import dataclass, replace
from typing import cast, ClassVar, Sequence

from arxiv import Result  # type: ignore

from .detex import detex


@dataclass
class Article:
    title: str  #: Title of the article.
    authors: Sequence[str]  #: Author list of the article.
    summary: str  #: Summary (abstract) of the article.
    arxiv_url: str  #: arXiv URL of the article.

    _SEPARATOR: ClassVar[str] = "++++++++++++"

    def __post_init__(self) -> None:
        self.title = detex(self.title)
        self.summary = detex(self.summary)

    @property
    def arxiv_pdf_url(self) -> str:
        return self.arxiv_url.replace("abs", "pdf")

    @classmethod
    def from_arxiv_result(cls, result: Result) -> Article:
        authors = [cast(str, a.name) for a in result.authors]  # type: ignore

        return Article(
            title=result.title,
            authors=authors,
            summary=result.summary,
            arxiv_url=str(result),
        )

    def replace(self, original: str, translated: str) -> Article:
        title, summary = translated.split(self._SEPARATOR)
        return replace(self, title=title, summary=summary)

    def __str__(self) -> str:
        return f"{self.title}\n{self._SEPARATOR}\n{self.summary}"
