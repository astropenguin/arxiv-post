# arxiv-post

[![Release](https://img.shields.io/pypi/v/arxiv-post?label=Release&color=cornflowerblue&style=flat-square)](https://pypi.org/project/arxiv-post/)
[![Python](https://img.shields.io/pypi/pyversions/arxiv-post?label=Python&color=cornflowerblue&style=flat-square)](https://pypi.org/project/arxiv-post/)
[![Downloads](https://img.shields.io/pypi/dm/arxiv-post?label=Downloads&color=cornflowerblue&style=flat-square)](https://pepy.tech/project/arxiv-post)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.5633924-cornflowerblue?style=flat-square)](https://doi.org/10.5281/zenodo.5633924)
[![Tests](https://img.shields.io/github/actions/workflow/status/astropenguin/arxiv-post/tests.yml?label=Tests&style=flat-square)](https://github.com/astropenguin/arxiv-post/actions)

Translate and post arXiv articles to Slack and various apps

## Installation

```shell
$ pip install arxiv-post
$ playwright install chromium
```

## Usage

Command line interface `arxiv-post` is available after installation, with which you can translate and post arXiv articles to various apps.
Note that only `slack` app is currently available.
You need to [create a custom Slack app to get an URL of incoming webhook](https://slack.com/help/articles/115005265063-Incoming-webhooks-for-Slack).

```shell
$ arxiv-post slack --keywords deshima \
                   --categories astro-ph.IM \
                   --target_lang ja \
                   --slack_webhook_url <Slack webhook URL>
```

The posted article looks like this.

![arxiv-post-slack.png](https://raw.githubusercontent.com/astropenguin/arxiv-post/master/docs/_static/arxiv-post-slack.png)

For detailed information, see the built-in help by the following command.

```shell
$ arxiv-post slack --help
```

## Example

It would be nice to regularly run the command by some automation tools such as GitHub Actions.
Here is a live example where daily arXiv articles in [astro-ph.GA](https://arxiv.org/list/astro-ph.GA/new), [astro-ph.IM](https://arxiv.org/list/astro-ph.IM/new), and [astro-ph.HE](https://arxiv.org/list/astro-ph.HE/new) are posted to different channels of a Slack workspace.

- [a-lab-nagoya/astro-ph-slack: Translate and post arXiv articles to Slack](https://github.com/a-lab-nagoya/astro-ph-slack)

## References

- [fkubota/Carrier-Owl: arxiv--> DeepL --> Slack](https://github.com/fkubota/Carrier-Owl): The arxiv-post package is highly inspired by their work.
