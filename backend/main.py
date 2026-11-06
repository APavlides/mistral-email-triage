import os
from contextlib import asynccontextmanager
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from httpx2 import RequestError, TimeoutException
from mistralai.client import Mistral
from mistralai.client.errors import MistralError
from mistralai.client.utils import BackoffStrategy, RetryConfig
from pydantic import BaseModel

load_dotenv()

MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")
TIMEOUT_MS = 20_000

SYSTEM_PROMPT = (
    "You triage support emails. Pick the category and urgency, write a one or two "
    "sentence summary, and draft a short, polite reply in the same language as the email."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # One shared Mistral client for the whole app
    # Timeout per call; the SDK retries only 429/5xx and connection errors, with backoff + jitter
    async with Mistral(
        api_key=os.environ["MISTRAL_API_KEY"],
        timeout_ms=TIMEOUT_MS,
        retry_config=RetryConfig(
            "backoff",
            BackoffStrategy(500, 4000, 2.0, 15_000, jitter_ms=250),
            True,
            ["429", "500", "502", "503", "504"],
        ),
    ) as client:
        app.state.mistral = client
        yield


app = FastAPI(lifespan=lifespan)


class TriageRequest(BaseModel):
    text: str


class TriageResponse(BaseModel):
    category: Literal["billing", "bug", "feature_request", "account", "other"]
    urgency: Literal["low", "medium", "high"]
    summary: str
    suggested_reply: str


@app.post("/api/triage", response_model=TriageResponse)
async def triage(req: TriageRequest, request: Request):
    try:
        res = await request.app.state.mistral.chat.parse_async(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": req.text},
            ],
            response_format=TriageResponse,
        )
    except TimeoutException:
        raise HTTPException(504, "Mistral took too long to answer. Try again.")
    except MistralError as e:
        if e.status_code == 429:
            raise HTTPException(429, "Rate limit reached. Wait a few seconds and retry.")
        raise HTTPException(502, f"Mistral request failed (upstream status {e.status_code}).")
    except RequestError:
        raise HTTPException(502, "Could not reach Mistral.")
    return res.choices[0].message.parsed


@app.get("/api/health")
def health():
    return {"status": "ok"}
