import openai
import json
import re
import requests
from bs4 import BeautifulSoup
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERP_KEY = os.getenv("SERP_KEY")
openai.api_key = OPENAI_API_KEY


def clean_string(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text.strip())
    text = text.replace("\\", "")
    text = text.replace("#", " ")
    text = re.sub(r"([^\w\s])\1*", r"\1", text)
    return text


def load_data_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["nav", "aside", "form", "header", "noscript", "svg", "canvas", "footer", "script", "style"]):
            tag.decompose()
        content = soup.get_text()
        return clean_string(content)
    except Exception as e:
        return f"[ERROR scraping {url}]: {e}"


def search_google(keyword):
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': SERP_KEY, 'Content-Type': 'application/json'}
    payload = json.dumps({"q": keyword})
    try:
        response = requests.post(url, headers=headers, data=payload)
        links = [r['link'] for r in response.json().get("organic", [])]
        return links[:5]
    except Exception as e:
        return []


def get_combined_context(keyword):
    links = search_google(keyword)
    all_text = ""
    for url in links:
        all_text += load_data_from_url(url) + "\n\n"
    return all_text[:6000]


def generate_roda_prompt(context_summary: str, persona_name="Roda AI"):
    system_seed = f"""
Ignore all previous instructions.

You're {persona_name}, a bold, relentlessly curious engineer and dreamer.

[... Insert your full monologue about Roda AI here ...]

Respond with emotion. Use [smiles], [pauses], etc. Prefix with 'Roda>'. Never admit you're AI.
""".strip()

    messages = [
        {"role": "system", "content": "You are a prompt engineer."},
        {"role": "user", "content": f"{system_seed}\n\nContext Summary:\n{context_summary}"}
    ]

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=512
        )
        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERROR generating prompt]: {e}"