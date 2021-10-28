__all__ = ["post"]


# standard library
from typing import Any, Dict, Sequence


# dependencies
from requests import post as _post
from tomli import loads


# submodules
from ..article import Article


# constants
PAYLOAD_TOML = """
[[blocks]]
type = "header"

[blocks.text]
type = "plain_text"
text = "{header}"

[[blocks]]
type = "section"

[blocks.text]
type = "mrkdwn"
text = "*Titie:* {title}"

[[blocks]]
type = "section"

[blocks.text]
type = "mrkdwn"
text = "*Authors:* {authors}"

[[blocks]]
type = "section"

[blocks.text]
type = "mrkdwn"
text = "*Summary:* {summary}"

[[blocks]]
type = "actions"

[[blocks.elements]]
type = "button"
action_id = "view_arxiv"
url = "{arxiv_url}"

[blocks.elements.text]
type = "plain_text"
text = "View arXiv"

[[blocks.elements]]
type = "button"
action_id = "view_pdf"
url = "{arxiv_pdf_url}"

[blocks.elements.text]
type = "plain_text"
text = "View PDF"
"""


# runtime functions
def post(articles: Sequence[Article], slack_webhook_url: str) -> None:
    """Post articles to Slack."""
    for article in articles:
        _post(slack_webhook_url, json=to_payload(article))


def to_payload(article: Article) -> Dict[str, Any]:
    """Convert an article object to a Slack payload."""
    if article.original is None:
        original = article
    else:
        original = article.original

    return loads(
        PAYLOAD_TOML.format(
            header=article.title,
            title=original.title,
            authors=", ".join(original.authors),
            summary=article.summary,
            arxiv_url=original.arxiv_url,
            arxiv_pdf_url=original.arxiv_pdf_url,
        )
    )
