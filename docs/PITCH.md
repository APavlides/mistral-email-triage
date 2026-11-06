# Pitch: Ticket triage

About 5 minutes of talk, then about 5 minutes of questions. Slides are in `docs/slides.html`. Everything below that I claim is in the app today; the rest is marked as a next step.

## Opening question (ask before slide 1)
"How many customer emails come in per week, and how long does someone spend reading and sorting each one?"
Write down their answer and reuse it on slides 2 and 5. If they don't know, use the placeholders `[their volume]` and `[minutes per email]`.

## 1. Title (10 seconds)
"This is a small tool that reads a customer email and tells your team what it is, how urgent it is, and what to reply."

## 2. The problem (45 seconds)
- Say: "Today someone reads every email, decides what kind it is, decides if it can wait, and writes a reply."
- "At `[their volume]` emails and `[minutes per email]` minutes each, that is `[hours per week]` of sorting before any real work starts."
- Cost of doing nothing: urgent emails wait in the same queue as easy ones, and two people label the same email differently.

## 3. What we built (30 seconds)
"A tool that reads a customer email and returns its category, urgency, a short summary and a draft reply, so your agent can respond faster and more consistently."
Value in business terms: faster first response, the same labels every time, and the agent still decides what to send.

## 4. Live demo (about 90 seconds)
Open http://localhost:5173 with the backend running.
1. **Click the empty box, then Triage.** Say: "If nobody pastes anything, it tells you instead of failing." (red message: "Paste an email first.")
2. **Paste this and click Triage:** "Hi, I was charged twice for my subscription this month and I need a refund today please. Thanks, Maria". Say: "The button shows it is working while the AI reads it."
3. **Point at the badges.** "Category: billing. Urgency: high, in red, so it jumps out of the queue."
4. **Point at the two cards.** "A one-sentence summary, and a draft reply in the customer's own language. The agent edits it and sends it."
Optional 5th click: paste a short feature request to show a green or amber urgency.
Backup if the AI is slow or down: the page shows a clear error message instead of freezing. Say so, retry once, and move on.

## 5. How it works (45 seconds)
"You paste an email into the web page. The page sends it to our own server. The server asks Mistral's AI to read it and answer in a fixed format with exactly four fields. The server checks the answer before showing it."
- **Where the AI fits:** only one step, reading and judging the email.
- **What stays under your control:** the list of categories and urgency levels is fixed by us; the AI cannot invent a new one. The API key stays on the server, never in the browser. Nothing is stored.
- Safety nets that exist today: a 20-second time limit, automatic retries for temporary Mistral problems, and clear errors for rate limits and timeouts.

## 6. Honest limitations (30 seconds)
- One email at a time. Several at once is planned but not built.
- The AI can misjudge urgency or tone, so a person should read the draft reply before it goes out.
- No login, no history, no connection to your inbox or helpdesk yet.
- Not yet measured on your real emails, so I cannot quote an accuracy figure today.
- Automated tests cover the server's behaviour with a stand-in for the AI. They do not measure answer quality.

## 7. Next steps and the ask (30 seconds)
A 2 to 4 week pilot:
1. Run it on a sample of your real emails and measure how often the category and urgency match what your team would choose.
2. Connect it to your inbox or helpdesk.
3. Add what production needs: login, data handling that fits your rules, monitoring and cost limits.

**Close:** "It turns a pile of unread email into a sorted queue with drafts ready. Can we start a pilot on `[their volume]` of your real emails?"

## Likely questions

**What does it cost?**
Each email is one call to Mistral's `mistral-small-latest` model, which is a small, low-cost model. I don't have a per-email figure to quote yet; in a pilot we'd measure it on your real volume and set a spending limit.

**Is our customers' data safe?**
Today the email text goes from our server to Mistral for processing, and we store nothing. We do not log the API key or the email text. Before real customer data, we would check Mistral's data terms against your policy, and add login and access controls.

**What if the AI is wrong?**
It can be. The output is restricted to our fixed lists, so it can't invent a category, but it can pick the wrong one or misjudge urgency. That's why the reply is a draft and a person sends it. The pilot would measure how often it is wrong on your emails.

**Will it handle our volume?**
The demo handles one email at a time and has not been load-tested. The design has no database to slow it down, and processing several emails at once is the next feature. Volume limits would be tested in the pilot.

**How long until we can use it?**
The core works now. A pilot on your real emails is 2 to 4 weeks, including connecting it to your inbox or helpdesk and the safety work above.

## If something goes wrong in the demo
- Page says "Backend: unreachable": the backend server isn't running. Say "let me restart that" and restart it.
- "Error: Rate limit reached": wait a few seconds and click again.
- "Error: Mistral took too long": click again once; if it repeats, describe the result you would have shown.
