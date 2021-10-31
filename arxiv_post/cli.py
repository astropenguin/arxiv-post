# standard library
from logging import DEBUG, basicConfig, getLogger
from typing import Sequence


# dependencies
from fire import Fire


# submodules
from .apps import slack
from .constants import (
    CATEGORIES,
    KEYWORDS,
    START_DATE,
    END_DATE,
    LANGUAGE_FROM,
    LANGUAGE_TO,
    N_CONCURRENT,
    TIMEOUT,
)
from .search import search
from .translate import translate


# logger
logger = getLogger(__name__)


# runtime functions
def configure_logging(debug: bool = False) -> None:
    """Configure logging format and level for CLI."""
    if debug:
        getLogger("arxiv_post").setLevel(DEBUG)

    basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s %(name)s %(levelname)s]: %(message)s",
    )


def cmd_slack(
    categories: Sequence[str] = CATEGORIES,
    keywords: Sequence[str] = KEYWORDS,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
    language_from: str = LANGUAGE_FROM,
    language_to: str = LANGUAGE_TO,
    n_concurrent: int = N_CONCURRENT,
    timeout: float = TIMEOUT,
    webhook_url: str = "",
    dry_run: bool = False,
    debug: bool = False,
) -> None:
    """Translate and post articles to Slack.

    Args:
        categories: Comma-separated arXiv categories.
        keywords: Comma-separated keywords for a search.
        start_date: Start date for a search (inclusive).
        end_date: End date for a search (exclusive).
        language_from: Language of original text in articles.
        language_to: Language for translated text in articles.
        n_concurrent: Number of simultaneous execution.
        timeout: Timeout for each post execution (in seconds).
        webhook_url: URL of Slack incoming webhook.
        dry_run: If True, articles are not posted to Slack.
        debug: If True, debug-level log messages are shown.

    Returns:
        This command does not return anything.

    """
    configure_logging(debug)

    if isinstance(categories, str):
        categories = categories.split(",")

    if isinstance(keywords, str):
        keywords = keywords.split(",")

    for name, value in locals().items():
        logger.debug(f"{name}: {value!r}")

    articles = search(
        categories=categories,
        keywords=keywords,
        start_date=start_date,
        end_date=end_date,
    )
    translated = translate(
        articles,
        language_from=language_from,
        language_to=language_to,
        n_concurrent=n_concurrent,
        timeout=timeout,
    )

    return slack.post(translated, webhook_url, dry_run)


def main() -> None:
    """Entry point of command line interface."""
    Fire(dict(slack=cmd_slack))
