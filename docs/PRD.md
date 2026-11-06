# PRD: Email / ticket triage

## Goal

Paste an email or ticket and get back structured triage: `{ category, urgency, summary, suggested_reply }`.

## User

A support agent who wants to sort and answer incoming emails quickly.

## Core flow

1. User pastes an email into a textarea and clicks "Triage".
2. Frontend POSTs `{ text }` to `/api/triage` (through the Vite proxy).
3. Backend asks Mistral for structured JSON (async call, shared client).
4. Backend validates it with Pydantic and returns the JSON.
5. Frontend shows the four fields (loading, error and empty states included).

## Out of scope

Database, auth, Docker, tests, styling, history of past triages, streaming, batch or file upload, email inbox integration, multiple languages, editing the reply.

## Endpoints and data (in memory, nothing stored)

- `POST /api/triage`
  - Request: `{ text: str }`
  - Response: `{ category: str, urgency: "low"|"medium"|"high", summary: str, suggested_reply: str }`
- `POST /api/triage/batch` (Step 2)
  - Request: `{ emails: list[str] }` (max 5)
  - Response: `{ results: list[TriageResponse] }`, same order as the input
- `GET /api/health` (exists)
- Categories: fixed list (see open questions).

## Milestones

- [x] **M1: Thin slice.** `POST /api/triage` returns a hardcoded stub; the textarea and button show it. _Done when:_ clicking Triage shows the stub fields on the page.
- [x] **M2: Real Mistral call.** Shared async client in the lifespan, structured output into a Pydantic model. _Done when:_ the `curl` returns valid JSON for a sample email.
- [x] **M3: UI states.** Loading, error and empty states in the frontend. _Done when:_ each state shows when I trigger it (empty input, backend stopped).
- [x] **M4: Hardening.** Timeout, SDK retry on 429/5xx, error mapping (429 passthrough, 502/504 otherwise). _Done when:_ a bad API key or forced timeout returns a clear error in the UI.

### Step 2: response schema, labelled fields, several emails

Already done: `TriageResponse` is a Pydantic model and the UI shows labelled fields (M1, M2, styling). M5 only tightens the schema; the labelled display is reused for each result in M8.

- [ ] **M5: Documented schema.** Add `Field(description=...)` to each `TriageResponse` field, so one model drives Mistral's output and the API docs. *Done when:* `localhost:8000/docs` shows a description for each response field and the `curl` still returns valid JSON.
- [ ] **M6: Batch endpoint.** `POST /api/triage/batch` takes up to 5 emails, triages them concurrently with `asyncio.gather`, and returns the results in input order. *Done when:* a `curl` with 3 emails returns 3 results in order, and 6 emails returns 422.
- [ ] **M7: Several emails in the UI.** One textarea; emails are separated by a line with `---`. The button sends them to the batch endpoint. *Done when:* pasting 2 emails and clicking Triage shows 2 raw results (loading and error states reused).
- [ ] **M8: One result card set per email.** Render each result with the labelled fields (badges, summary, reply) under a small "Email 1 / Email 2" heading. *Done when:* each email's result is clearly separate and readable.

## Open questions

1. **Category list:** fixed list or free text? **I decide.** Default: fixed list `billing, bug, feature_request, account, other`.
2. **Urgency scale:** `low/medium/high` or 1–5? **I decide.** Default: `low/medium/high`.
3. **Reply language and tone:** match the email's language, polite and short? **Ask.** Default: same language as the email, short and polite.

### Step 2 open questions
4. **How to enter several emails:** one box with a `---` separator, or one box per email? **I decide.** Default: one box, separated by a line with `---`.
5. **If one email fails in a batch:** fail the whole batch, or return the others? **Ask.** Default: fail the whole batch with the existing error mapping (simplest to explain). Per-email errors can come later.
