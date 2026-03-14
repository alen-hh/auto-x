import os
from typing import TypedDict, NotRequired

import httpx
import tweepy
from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()

TARGET_URL = "https://www.moltbook.com/m/openclaw-explorers"


class State(TypedDict):
    url: str
    page_content: NotRequired[str]
    x_post: NotRequired[str]


def fetch_content(state: State) -> dict:
    """Fetch page text from the target URL via Jina Reader API."""
    jina_api_key = os.environ["JINA_API_KEY"]
    url = state["url"]

    print(f"  Fetching: {url} ...")
    response = httpx.get(
        f"https://r.jina.ai/{url}",
        headers={
            "Authorization": f"Bearer {jina_api_key}",
            "X-Retain-Images": "none",
            "X-Return-Format": "markdown",
            "X-Target-Selector": "body > div.flex-1 > div > main > div.space-y-3",
        },
        timeout=60,
    )
    response.raise_for_status()
    print(f"  Done ({len(response.text)} chars)")

    return {"page_content": response.text}


def generate_x_post(state: State) -> dict:
    """Pick the most interesting OpenClaw case and craft an X post under 240 chars."""
    openrouter_api_key = os.environ["OPENROUTER_API_KEY"]
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )

    prompt = (
        "You are an AI product manager who is active on X (Twitter). "
        "From the following web page contents, pick the single most interesting, "
        "novel, or surprising case or idea about OpenClaw improving personal "
        "productivity or enterprise efficiency.\n\n"
        "Write a concise, engaging X post in English in a sharing tone, as if you've discovered this from someone else's case and are now sharing it to X. "
        "The post body MUST NOT exceed 220 characters (this is a hard limit — count carefully). "
        "Do NOT use any hashtags. Do NOT include any quotes or markdown formatting. "
        "Use emojis appropriately to make the post more engaging. "
        "Just output the post text, nothing else.\n\n"
        f"Web page contents:\n{state['page_content']}"
    )

    print("  Generating X post ...")
    response = client.chat.completions.create(
        model="stepfun/step-3.5-flash:free",
        messages=[{"role": "user", "content": prompt}],
    )

    suffix = "\n\nshared by AI from #MoltBook #OpenClaw"
    x_post = response.choices[0].message.content.strip() + suffix

    print("=" * 60)
    print(f"  X Post ({len(x_post)} chars)")
    print("=" * 60)
    print(x_post)
    print("=" * 60)

    return {"x_post": x_post}


def post_x(state: State) -> dict:
    """Post the generated text to X (Twitter) via API v2."""
    client = tweepy.Client(
        consumer_key=os.environ["X_CONSUMER_KEY"],
        consumer_secret=os.environ["X_CONSUMER_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    print("  Posting to X ...")
    response = client.create_tweet(text=state["x_post"])
    tweet_id = response.data["id"]
    print(f"  Posted! https://x.com/i/status/{tweet_id}")

    return {}


def build_graph():
    builder = StateGraph(State)

    builder.add_node("fetch_content", fetch_content)
    builder.add_node("generate_x_post", generate_x_post)
    builder.add_node("post_x", post_x)

    builder.add_edge(START, "fetch_content")
    builder.add_edge("fetch_content", "generate_x_post")
    builder.add_edge("generate_x_post", "post_x")
    builder.add_edge("post_x", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    graph.invoke({"url": TARGET_URL})
