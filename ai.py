import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")

# Order of attempts: (provider, model)
CHAIN = []
if GROQ_KEY:
    CHAIN += [("groq", "openai/gpt-oss-120b"), ("groq", "qwen/qwen3-32b")]
CHAIN += [("gemini", "gemini-3.5-flash")]

_groq_client = None
_gemini_client = None


def _clean(text):
    """Remove <think> blocks and code fences some models add."""
    if not text:
        return ""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return text.strip()


def _call_groq(model, prompt, json_mode):
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_KEY)

    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    if "gpt-oss" in model:
        kwargs["reasoning_effort"] = "low"
        kwargs["max_completion_tokens"] = 4000

    resp = _groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    )
    return resp.choices[0].message.content


def _call_gemini(model, prompt, json_mode):
    global _gemini_client
    from google import genai
    from google.genai import types

    if _gemini_client is None:
        _gemini_client = genai.Client()

    config = None
    if json_mode:
        config = types.GenerateContentConfig(response_mime_type="application/json")
    resp = _gemini_client.models.generate_content(
        model=model, contents=prompt, config=config
    )
    return resp.text


def generate(prompt, json_mode=False):
    """Call the AI, trying each model in the chain, with retries."""
    if json_mode:
        prompt += "\n\nReturn ONLY valid JSON. No explanations, no markdown."

    for provider, model in CHAIN:
        for attempt in range(2):
            try:
                if provider == "groq":
                    text = _call_groq(model, prompt, json_mode)
                else:
                    text = _call_gemini(model, prompt, json_mode)

                text = _clean(text)
                if not text:
                    raise ValueError("empty reply from model")
                return text
            except Exception as e:
                print(f"[{provider}/{model}] try {attempt + 1} failed: {str(e)[:90]}")
                time.sleep(2)

    raise RuntimeError("All AI models failed. Check your keys or try again in a few minutes.")


def ask_ai(prompt):
    return generate(prompt)