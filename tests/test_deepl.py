# standard library
from typing import List, Tuple, TypeVar


# dependencies
from arxiv_post.article import Article
from arxiv_post.deepl import Translatable, translate
from pytest import mark


# type hints
TL = TypeVar("TL", bound=Translatable)


# test data
testdata: List[Tuple[Translatable, Translatable]] = [
    (
        "This is a test script.",
        "これはテストスクリプトです。",
    ),
    (
        Article("Title of the paper", [], "Summary of the paper", ""),
        Article("論文タイトル", [], "論文の概要", ""),
    ),
]


# test functions
@mark.parametrize("original, translated", testdata)
def test_translate(original: TL, translated: TL) -> None:
    assert translate([original], "ja") == [translated]
