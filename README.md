# auto-x

Automated X (Twitter) posting pipeline powered by [LangGraph](https://github.com/langchain-ai/langgraph). Fetches content from [MoltBook OpenClaw Explorers](https://www.moltbook.com/m/openclaw-explorers), uses an LLM to pick the most interesting case, generates an engaging post, and publishes it to X — all on autopilot.

👉 Follow me on [@alen_hh_x](https://x.com/alen_hh_x).

## How It Works

```
START → fetch_content → generate_x_post → post_x → END
```

1. **fetch_content** — Retrieves the OpenClaw Explorers page via [Jina Reader API](https://jina.ai/reader/) and converts it to markdown.
2. **generate_x_post** — Sends the content to an LLM (via [OpenRouter](https://openrouter.ai/)) to select the most interesting case and craft a concise X post.
3. **post_x** — Publishes the generated post to X using the Twitter API v2.

The workflow runs as a LangGraph `StateGraph`, making it easy to extend with additional nodes (e.g., image generation, multi-platform posting).

## Prerequisites

- Python 3.10+
- API keys for Jina Reader, OpenRouter, and X (Twitter)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/your-username/auto-x.git
cd auto-x

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and fill in your API keys

# Run the workflow
python workflows/openclaw-explorers.py
```

## Configuration

Copy `.env.example` to `.env` and set the following variables:

| Variable | Description |
|---|---|
| `JINA_API_KEY` | [Jina Reader](https://jina.ai/reader/) API key |
| `OPENROUTER_API_KEY` | [OpenRouter](https://openrouter.ai/) API key |
| `X_CONSUMER_KEY` | X API consumer key |
| `X_CONSUMER_SECRET` | X API consumer secret |
| `X_ACCESS_TOKEN` | X API access token |
| `X_ACCESS_TOKEN_SECRET` | X API access token secret |

## GitHub Actions

A cron workflow is included at `.github/workflows/cron-openclaw-explorers.yml` that runs the pipeline daily at 12:00 UTC. It can also be triggered manually via `workflow_dispatch`.

To use it, add all the environment variables above as **repository secrets** in your GitHub repo settings.

## Project Structure

```
auto-x/
├── workflows/
│   └── openclaw-explorers.py   # Main LangGraph workflow
├── .github/
│   └── workflows/
│       └── cron-openclaw-explorers.yml
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
└── LICENSE
```

## Dependencies

| Package | Purpose |
|---|---|
| [langgraph](https://github.com/langchain-ai/langgraph) | Workflow orchestration |
| [httpx](https://www.python-httpx.org/) | HTTP client for Jina Reader API |
| [openai](https://github.com/openai/openai-python) | LLM calls via OpenRouter |
| [tweepy](https://www.tweepy.org/) | X (Twitter) API v2 client |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable loading |

## License

This project is licensed under the [MIT License](LICENSE).
