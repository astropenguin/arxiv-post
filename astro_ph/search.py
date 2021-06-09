from dataclasses import dataclass, field
from datetime import timezone
from typing import Generator, Sequence

from arxiv import Search as _Search  # type: ignore
from dateparser import parse

from .article import Article


@dataclass
class Search:
    """Class for searching for articles in arXiv."""

    categories: Sequence[str] = field(default_factory=list)
    keywords: Sequence[str] = field(default_factory=list)
    start_date: str = "3 days ago at midnight in UTC"
    end_date: str = "2 days ago at midnight in UTC"

    def run(self) -> Generator[Article, None, None]:
        for result in _Search(self.query).get():
            yield Article.from_arxiv_result(result)

    @property
    def query(self) -> str:
        start_date = format_date(self.start_date)
        end_date = format_date(self.end_date)

        query = f"submittedDate:[{start_date} TO {end_date}]"

        if self.categories:
            sub = " OR ".join(f"cat:{cat}" for cat in self.categories)
            query += f" AND ({sub})"

        if self.keywords:
            sub = " OR ".join(f'abs:"{kwd}"' for kwd in self.keywords)
            query += f" AND ({sub})"

        return query


def format_date(date_like: str) -> str:
    """Parse and format (YYYYmmddHHMMSS) date-like string."""
    dt = parse(date_like)

    if dt is None:
        raise ValueError(f"Could not parse: {date_like}")

    return dt.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
