# standard library
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Union


# dependencies
import requests
from typing_extensions import Protocol


# submodules
from .article import Article


# type hints
Element = Dict[str, str]
Payload = Dict[str, Union[List[Element], str]]


class App(Protocol):
    def post(self, articles: Sequence[Article]) -> None:
        ...


@dataclass
class Slack:
    webhook_url: str

    def post(self, articles: Iterable[Article]) -> None:
        """Post articles to Slack."""
        for article in articles:
            requests.post(self.webhook_url, json=self.to_payload(article))

    def to_payload(self, article: Article) -> Payload:
        """Convert an article to a payload for Slack post."""
        if article.original is None:
            original = article
        else:
            original = article.original

        divider = self.divider()
        header = self.header(self.plain_text(article.title))
        title = self.section(self.mrkdwn(f"*Title:* {original.title}"))
        authors = self.section(self.mrkdwn(f"*Authors:* {', '.join(original.authors)}"))
        summary = self.section(self.mrkdwn(f"*Summary:* {article.summary}"))

        buttons = self.actions(
            elements=[
                self.button(
                    self.plain_text("View arXiv"),
                    url=original.arxiv_url,
                ),
                self.button(
                    self.plain_text("View PDF"),
                    url=original.arxiv_url.replace("abs", "pdf"),
                ),
            ]
        )

        return dict(
            text=article.title,
            blocks=[divider, header, title, authors, summary, buttons, divider],
        )

    def __getattr__(self, type: str) -> Callable[..., Element]:
        """Generate a function to create elements of Slack payload."""

        def element(text: Optional[str] = None, **params: str) -> Element:
            if text is None:
                return dict(type=type, **params)

            return dict(text=text, type=type, **params)

        return element
