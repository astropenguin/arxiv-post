# third-party packages
from astro_ph.arxiv import search
from typing_extensions import Final


# constants
DATE_START: Final[str] = "2021-01-01"
DATE_END: Final[str] = "2021-01-02"
KEYWORDS: Final[tuple] = ("galaxy",)
CATEGORIES: Final[tuple] = ("astro-ph.GA",)
N_ARTICLES: Final[int] = 4


# test functions
def test_search() -> None:
    articles = search(DATE_START, DATE_END, KEYWORDS, CATEGORIES)
    assert len(articles) == N_ARTICLES
