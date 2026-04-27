# DECISIONS.md

## Project setup decisions

**Date: 2026-04-27**

1. **Library-style project layout (uv with --package).**
   Project 2 has multiple modules with cross-dependencies (4 agents + orchestrator + tools + eval).
   A flat script layout would have made imports brittle and hidden a class of "works on my
   machine, breaks in production" bugs we hit on Project 1's deploy. Library layout forces
   installable-package discipline.

2. **uv over pip + requirements.txt.**
   Project 1's deploy broke twice on dependency conflicts (grpcio/google-api-core, then
   protobuf with Python 3.14). Root cause was using `pip freeze` — a snapshot of machine
   state — as a deployment manifest. uv separates "what I asked for" (pyproject.toml) from
   "what got resolved" (uv.lock), which is the correct shape for production.

3. **Sentiment classifier (Project 1) consumed as an importable dependency, not copied.**
   Project 2's Sentiment Analyst agent will install Project 1 from GitHub and import it.
   This forces clean interface contracts and makes the compositional reuse story
   visible in the codebase, not just narrative.

   ## Data source decisions

**Date: 2026-04-27**

4. **Three external data sources verified before any agent code written.**
   Project 1's lesson: scraped data sources don't survive deployment (yfinance hit
   rate limits on Streamlit Cloud's datacenter IPs, discovered at deploy time).
   Project 2 inverts the order: data verification at Day 0, architecture decisions
   downstream of verified data shape. The eval design now reflects what we can
   actually fetch, not what we wish we could.

5. **Twelve Data over Alpha Vantage for price history.**
   Initial recommendation was Alpha Vantage (NASDAQ-licensed, established).
   Verification revealed AV free tier is 25 requests/day vs. Twelve Data's 800/day.
   For one-time eval dataset construction (~60-120 calls), AV would have required
   3-5 days of throttled fetching. Twelve Data lets us iterate freely. Same data
   shape, no downside.

6. **Finnhub free tier scoped to EPS-surprise data only.**
   Free tier doesn't include earnings transcripts, revenue, guidance, or analyst
   estimates beyond EPS. The Researcher agent's FactSheet schema must shrink to
   match. Memo will be EPS-surprise-and-news-sentiment focused, not full
   earnings-reaction. Honest to constraints.

7. **Switched from `google.generativeai` (deprecated) to `google.genai` (current),
   and from `gemini-2.0-flash-lite` (deprecated) to `gemini-2.5-flash`.**
   Caught at verify step. Same cost tier, supported library, removed 15 transitive
   dependencies (incl. grpcio and protobuf — the same packages that broke
   Project 1's deploy).
   
   ## Scope decisions

**Date: 2026-04-27**

8. **Press-release LLM extraction over paying for Finnhub Personal.**
   Finnhub free gives EPS surprise only. Two ways to fill the revenue/guidance gap:
   pay $10/mo, or build an LLM-based structured extraction layer over public press
   releases. Picked extraction because it surfaces a richer AI-PM problem
   (per-agent eval for extraction accuracy, contamination of downstream agents
   when extraction is wrong) — and the project's purpose is to demonstrate
   capability, not minimize friction.

9. **Project timeline extended from 4 to 5 weeks.**
   Press-release extraction adds a per-agent eval layer (extraction accuracy
   on hand-labeled releases) and 3-5 days of integration. Held the sentiment
   integration in scope rather than cutting it because that integration is the
   narrative spine — the line in interviews that ties Project 1 capability into
   Project 2 architecture.

10. **Researcher agent gets dedicated extraction eval layer.**
    Per-agent eval is what most multi-agent demos skip. We need it specifically
    for the Researcher because errors in extracted financials contaminate every
    downstream agent (Skeptic challenges wrong numbers, Synthesizer cites wrong
    numbers). Eval layer 1 = extraction accuracy by field, hand-labeled gold set
    of 15-20 releases.

11. **Week 1 has a decision gate.**
    If by end of Week 1 we cannot reliably fetch press release text from at least
    5 of our seed earnings events, the project falls back to the shrunk-memo
    scope without further investment. Forces an early reality check on the
    feasibility of the extraction layer before committing weeks of agent
    architecture to it.