# Persona Discovery

Discover 2-3 customer personas from the ad data. This runs in parallel with business context questions — it uses only the data already pulled in Phase 1.

## Data Sources for Persona Construction

| Source | What it reveals | Where it lives in the audit dataset |
|--------|----------------|---------------|
| Search terms | What customers actually search for — their language, pain points, urgency | `search_term_view` rows |
| Converting keywords | What they buy — terms that lead to conversions reveal purchase intent | `keyword_view` rows filtered to `metrics.conversions > 0` |
| Ad-group themes | How the business segments services — each theme may serve a different persona | `ad_group.name` distribution |
| Landing page URLs | Where they land — different pages suggest different customer journeys | `ad_group_ad.ad.final_urls` |
| Geographic data | Where they are — metro vs rural, specific cities | `campaign_criterion` LOCATION + PROXIMITY rows |
| Device split | How they search — mobile-heavy suggests on-the-go / urgent need | Segment any `metrics.*` query by `segments.device` |
| Time-of-day patterns | When they search — business hours vs. evenings vs. weekends | Segment by `segments.day_of_week` and `segments.hour` |

## Persona Template

Use this full template for the persisted JSON file. In the **report output**, personas appear as a compact 3-column table (name, example searches, value). The JSON file has the full detail for downstream skills like `/ads-copy`:

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Descriptive label capturing their defining trait | "The Emergency Caller" |
| **Demographics** | Role, context, location type | Homeowner, suburban, dual-income household |
| **Primary goal** | What they're trying to accomplish RIGHT NOW | Fix a burst pipe before it damages the floor |
| **Pain points** | What's driving them to search | Can't wait for regular business hours. Worried about cost. Doesn't know who to trust |
| **Search language** | Actual search terms from the data that this persona uses | "emergency plumber near me", "plumber open now", "burst pipe repair cost" |
| **Decision trigger** | What makes them click the ad and convert | Seeing "24/7" and "Same Day" in the headline. Phone number in the ad. Reviews mentioned |
| **Value to business** | Estimated revenue or conversion value | High urgency = willing to pay premium. Avg ticket $350-800 |

## Derivation Rules

- Each persona MUST be grounded in actual search term clusters from the data. If you can't point to 5+ search terms that this persona would use, the persona is speculative — drop it
- If all search terms look the same (single-intent account), identify 1-2 personas max. Don't force 3
- Name personas by their dominant behavior, not demographics: "The Comparison Shopper" is more useful than "Female 35-44"
- Include the actual search terms from the data that map to each persona — this directly informs ad copy decisions

## Persist Personas

Save to `{data_dir}/personas/{accountId}.json`:

```json
{
  "account_id": "1234567890",
  "saved_at": "2024-01-15T10:30:00Z",
  "personas": [
    {
      "name": "The Emergency Caller",
      "demographics": "Homeowner, suburban, any age",
      "primary_goal": "Fix an urgent problem right now",
      "pain_points": ["Can't wait", "Worried about cost", "Doesn't know who's reliable"],
      "search_terms": ["emergency plumber near me", "plumber open now", "burst pipe repair"],
      "decision_trigger": "24/7 availability, phone number visible, reviews",
      "value": "High — willing to pay premium for urgency"
    }
  ]
}
```

These personas feed directly into `/ads-copy` for headline generation and `/ads` for keyword strategy.
