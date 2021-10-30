# dependencies
from arxiv_post.detex import detex
from pytest import mark


# test data
test_header = "original, detexed"
test_data = [
    ("This is \\textbf{a bold text}.", "This is a bold text."),
    ("This is {\\textbf a bold text}.", "This is a bold text."),
    ("This is \\emph{emphasized}.", "This is emphasized."),
    ("This is {\\em emphasized}.", "This is emphasized."),
    ("This has   \n irregular\nbreaks.", "This has irregular breaks."),
]


# test functions
@mark.parametrize(test_header, test_data)
def test_detex(original: str, detexed: str) -> None:
    assert detex(original) == detexed
