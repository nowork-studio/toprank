# Change Tracking

After every successful write operation, log the change to `{data_dir}/change-log.json`.

## Change log entry format

Append to the `changes` array:

```json
{
  "id": "chg_<unix_timestamp_ms>",
  "timestamp": "<ISO 8601>",
  "action": "<action_type>",
  "summary": "<specific one-liner, e.g. 'Paused 5 non-converting keywords in Pet Daycare - Seattle saving ~$340/month'>",
  "details": {
    "campaignId": "<if applicable>",
    "campaignName": "<if applicable>",
    "affectedEntities": ["<IDs>"],
    "entityNames": ["<keyword text or campaign names>"]
  },
  "beforeSnapshot": {
    "metrics": { "spend30d": 0, "clicks30d": 0, "conversions30d": 0, "cpa30d": 0, "ctr30d": 0 },
    "note": "Metrics for affected entities at time of change"
  },
  "changeIds": ["<changeId(s) returned by write tool>"],
  "reviewAfter": "<ISO 8601 -- 7d for bid/keyword changes, 14d for structural>",
  "reviewWindow": "<7d or 14d>",
  "reviewed": false,
  "reviewResult": null
}
```

## Rules

- **Capture before-metrics** from data already in context. If none available: `"beforeSnapshot": { "metrics": null, "note": "No pre-change metrics" }`.
- **Review windows:** Bid/keyword/negative/budget changes: 7 days. Campaign creates/pauses/restructures/ad copy: 14 days.
- **Tell the user:** "Change logged. Google Ads changes typically take **7 days minimum** to show reliable results (14 days for structural changes like new campaigns or ad copy). I'll check the impact after [reviewAfter date] — you can also ask 'check my changes' anytime."
- **Max 200 entries** (remove oldest reviewed first).
- **Group related writes** in one session as a single entry.
