# dependencies
import arxiv_post


# constants
AUTHOR = "Akio Taniguchi"
VERSION = "0.4.0"


# test functions
def test_author() -> None:
    assert arxiv_post.__author__ == AUTHOR


def test_version() -> None:
    assert arxiv_post.__version__ == VERSION
