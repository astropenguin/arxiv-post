__all__ = []


# standard library
from logging import DEBUG, basicConfig, getLogger
from typing import Sequence


# dependencies
from fire import Fire


# submodules
from .apps import slack
from .arxiv import search
from .consts import (
    CATEGORIES,
    KEYWORDS,
    START_DATE,
    END_DATE,
    SOURCE_LANG,
    TARGET_LANG,
    DEEPL_MODE,
    N_CONCURRENT,
    TIMEOUT,
    DeepLMode,
)
from .deepl import translate


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
    source_lang: str = SOURCE_LANG,
    target_lang: str = TARGET_LANG,
    deepl_mode: DeepLMode = DEEPL_MODE,
    deepl_api_key: str = "",
    n_concurrent: int = N_CONCURRENT,
    timeout: float = TIMEOUT,
    slack_webhook_url: str = "",
    dry_run: bool = False,
    debug: bool = False,
) -> None:
    """Translate and post articles to Slack.

    Args:
        categories: Comma-separated arXiv categories.
        keywords: Comma-separated keywords for a search.
        start_date: Start date for a search (inclusive).
        end_date: End date for a search (exclusive).
        source_lang: Language of original text in articles.
        target_lang: Language of translated text in articles.
        deepl_mode: Translation mode (auto, api, browser) of DeepL.
        deepl_api_key: Authentication Key for DeepL API (api-mode only).
        n_concurrent: Number of concurrent translation (browser-mode only).
        timeout: Timeout for translation in seconds (browser-mode only).
        slack_webhook_url: URL of Slack incoming webhook.
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
        source_lang=source_lang,
        target_lang=target_lang,
        deepl_mode=deepl_mode,
        deepl_api_key=deepl_api_key,
        n_concurrent=n_concurrent,
        timeout=timeout,
    )

    return slack.post(translated, slack_webhook_url, dry_run)


def main() -> None:
    """Entry point of command line interface."""
    Fire(dict(slack=cmd_slack))
