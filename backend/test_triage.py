from types import SimpleNamespace

import httpx2
import pytest
from fastapi.testclient import TestClient
from mistralai.client.errors import MistralError

from main import app

GOOD = {
    "category": "billing",
    "urgency": "high",
    "summary": "Charged twice.",
    "suggested_reply": "Sorry, we will refund you.",
}


class FakeMistral:
    """Stands in for the Mistral client: returns a fixed reply or raises, and records calls."""

    def __init__(self, parsed=None, error=None):
        self.parsed = parsed
        self.error = error
        self.calls = []
        self.chat = SimpleNamespace(parse_async=self.parse_async)

    async def parse_async(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        message = SimpleNamespace(parsed=self.parsed)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def make_client(fake):
    # No `with`, so the real lifespan (and the real Mistral client) never runs
    app.state.mistral = fake
    return TestClient(app, raise_server_exceptions=False)


def upstream_error(status):
    return MistralError("boom", httpx2.Response(status, text="boom"))


def test_success_returns_four_fields_and_sends_the_email():
    fake = FakeMistral(parsed=GOOD)
    res = make_client(fake).post("/api/triage", json={"text": "I was charged twice"})

    assert res.status_code == 200
    assert res.json() == GOOD
    assert fake.calls[0]["messages"][-1] == {"role": "user", "content": "I was charged twice"}


def test_missing_text_is_rejected_without_calling_mistral():
    fake = FakeMistral(parsed=GOOD)
    res = make_client(fake).post("/api/triage", json={})

    assert res.status_code == 422
    assert fake.calls == []


def test_category_outside_the_list_is_never_returned_as_200():
    fake = FakeMistral(parsed={**GOOD, "category": "spam"})
    res = make_client(fake).post("/api/triage", json={"text": "hi"})

    assert res.status_code == 500


def test_timeout_maps_to_504():
    fake = FakeMistral(error=httpx2.ReadTimeout("slow"))
    res = make_client(fake).post("/api/triage", json={"text": "hi"})

    assert res.status_code == 504
    assert "too long" in res.json()["detail"]


@pytest.mark.parametrize("upstream, expected", [(429, 429), (401, 502), (503, 502)])
def test_upstream_errors_are_mapped(upstream, expected):
    fake = FakeMistral(error=upstream_error(upstream))
    res = make_client(fake).post("/api/triage", json={"text": "hi"})

    assert res.status_code == expected
