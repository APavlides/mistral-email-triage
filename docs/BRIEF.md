Email or ticket triage (structured output)
  - Basic version: paste an email and get back { category, urgency, summary, suggested_reply } as JSON.

## Step 2
I now need to add a Pydantic schema for the response, showing the result as labelled fields, then several emails at once.
