# standard library
import asyncio
from datetime import date, datetime, time, timedelta
from logging import basicConfig, DEBUG, getLogger
from typing import Union


# third-party packages
from fire import Fire
from typing_extensions import Final
from .apps import Slack
from .search import Search
from .translate import DeepL


# constants
CATEGORIES: Final[str] = (
    "astro-ph.CO,"
    "astro-ph.EP,"
    "astro-ph.GA,"
    "astro-ph.HE,"
    "astro-ph.IM,"
    "astro-ph.SR"
)
KEYWORDS: Final[str] = ""
LANG_FROM: Final[str] = "en"
LANG_TO: Final[str] = "auto"
N_CONCURRENT: Final[int] = 10
TIMEOUT: Final[int] = 60


# module-level logger
logger = getLogger(__name__)


# helper functions
def n_days_ago(n: int) -> str:
    """Return string of date n days ago in YYYY-mm-dd."""
    today = datetime.combine(date.today(), time())
    return (today - timedelta(days=n)).strftime("%Y-%m-%d")


def parse_multiple(obj: Union[list, tuple, str], sep: str = ",") -> list:
    """Parse comma-separated multiple values correctly."""

    def remove_empty(strings: list) -> list:
        return [s for s in strings if s != ""]

    if isinstance(obj, str):
        return remove_empty(obj.split(sep))

    if isinstance(obj, (list, tuple)):
        return remove_empty(sep.join(obj).split(sep))

    raise ValueError(f"Invalid value: {obj:!r}")


def configure_logging(debug: bool = False) -> None:
    """Configure logging format and level for CLI."""
    basicConfig(
        datefmt="%Y-%m%d %H:%M:%S",
        format="[{asctime} {name} {levelname}]: {message}",
        style="{",
    )

    if debug:
        getLogger("astro_ph").setLevel(DEBUG)


# subcommand functions
def slack(
    date_start: str = n_days_ago(2),
    date_end: str = n_days_ago(1),
    keywords: str = KEYWORDS,
    categories: str = CATEGORIES,
    lang_from: str = LANG_FROM,
    lang_to: str = LANG_TO,
    timeout: int = TIMEOUT,
    n_concurrent: int = N_CONCURRENT,
    webhook_url: str = "",
    debug: bool = False,
) -> None:
    """Translate and post articles to Slack.

    Args:
        date_start: Start date for a search in YYYY-mm-dd (inclusive).
        date_end: End date for a search in YYYY-mm-dd (exclusive).
        keywords: Comma-separated keywords for a search.
        categories: Comma-separated arXiv categories.
        lang_from: Language of original text in articles.
        lang_to: Language for translated text in articles.
        timeout: Timeout for each post execution (in seconds).
        n_concurrent: Number of simultaneous execution.
        webhook_url: URL of Slack incoming webhook.
        debug: If True, debug-level log messages are shown.

    Returns:
        This command does not return anything.

    """
    configure_logging(debug)

    if not webhook_url:
        raise ValueError("Webhook URL must be specified.")

    keywords = parse_multiple(keywords)
    categories = parse_multiple(categories)

    articles = Search(date_start, date_end, keywords, categories)
    translator = DeepL(lang_from, lang_to)
    app = Slack(translator, n_concurrent, timeout, webhook_url)

    logger.debug(articles)
    logger.debug(translator)
    logger.debug(app)

    asyncio.run(app.post(articles))


# command line interface
def cli() -> None:
    """Entry point of command line interface."""
    Fire(dict(slack=slack))
