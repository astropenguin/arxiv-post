# dependencies
from astro_ph.search import search


# constants
CATEGORIES = ("astro-ph.GA",)
KEYWORDS = ("galaxy",)
START_DATE = "2021-01-01 in UTC"
END_DATE = "2021-01-02 in UTC"
N_ARTICLES = 4


# test functions
def test_search() -> None:
    articles = list(search(CATEGORIES, KEYWORDS, START_DATE, END_DATE))
    assert len(articles) == N_ARTICLES
