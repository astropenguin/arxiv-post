# arxiv-post

[![PyPI](https://img.shields.io/pypi/v/arxiv-post.svg?label=PyPI&style=flat-square)](https://pypi.org/project/arxiv-post/)
[![Python](https://img.shields.io/pypi/pyversions/arxiv-post.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/project/arxiv-post/)
[![Test](https://img.shields.io/github/workflow/status/astropenguin/arxiv-post/Test?logo=github&label=Test&style=flat-square)](https://github.com/astropenguin/arxiv-post/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat-square)](LICENSE)

Translate and post arXiv articles to various apps

## Installation

Use pip or other package manager to install the Python package.

```shell
$ pip install arxiv-post
```

## Usage

After installation, command line interface, `arxiv-post`, is available, with which you can translate and post arXiv articles to various apps.
Note that only `slack` app is currently available.
In this case, you need to [create a custom Slack app to get an URL of incoming webhook](https://slack.com/help/articles/115005265063-Incoming-webhooks-for-Slack).

```shell
$ arxiv-post slack --keywords galaxy,galaxies \
                 --categories astro-ph.GA,astro-ph.IM \
                 --language_to ja \
                 --webhook_url https://hooks.slack.com/services/***/***
```

The posted article looks like this.

![arxiv-post-slack.png](https://raw.githubusercontent.com/astropenguin/arxiv-post/master/docs/_static/arxiv-post-slack.png)

For detailed information, see the built-in help by the following command.

```shell
$ arxiv-post slack --help
```

## Example

It would be nice to regularly run the command by GitHub Actions.
Here is a live example in which daily (2 days ago) arXiv articles in [astro-ph.GA](https://arxiv.org/list/astro-ph.GA/new) and [astro-ph.IM](https://arxiv.org/list/astro-ph.IM/new) are posted to different channels of a Slack workspace.

- [a-lab-nagoya/astro-ph-slack: Translate and post arXiv articles to Slack](https://github.com/a-lab-nagoya/astro-ph-slack)

## References

- [fkubota/Carrier-Owl: arxiv--> DeepL --> Slack](https://github.com/fkubota/Carrier-Owl)
    - The arxiv-post package is highly inspired by their work
- [a-lab-nagoya/astro-ph-slack: Translate and post arXiv articles to Slack](https://github.com/a-lab-nagoya/astro-ph-slack)
    - A live example using the arxiv-post package
- [pyppeteer/pyppeteer: Headless chrome/chromium automation library (unofficial port of puppeteer)](https://github.com/pyppeteer/pyppeteer)
    - Used for async Chromium operation
- [aio-libs/aiohttp: Asynchronous HTTP client/server framework for asyncio and Python](https://github.com/aio-libs/aiohttp)
    - Used for async article posts to Slack
- [google/python-fire: Python Fire is a library for automatically generating command line interfaces (CLIs) from absolutely any Python object.](https://github.com/google/python-fire)
    - Used for creating command line interface
