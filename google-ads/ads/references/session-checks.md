# Session Start Checks

Run these checks when the user's request is analysis-oriented (performance reviews, optimization, "how are my ads", "show me", audits) OR when the user explicitly asks to review their changes ("check my changes", "did my changes work"). Skip them for direct action commands like "pause keyword X", "rename campaign Y", "add negative keyword Z".

## Check for pending change reviews

Read `{data_dir}/change-log.json`. Find entries where `reviewed` is `false`.

**If unreviewed changes exist but `reviewAfter` has NOT passed yet:**

> **Changes still maturing:**
>
> _[Date]: [summary]_
> Google Ads needs time to accumulate enough data for a reliable before/after comparison. Ready for review on [reviewAfter date] ([reviewWindow] review window per `change-tracking.md`).

Do NOT pull metrics or attempt to assess impact early — small sample sizes lead to misleading conclusions.

**If unreviewed changes exist AND `reviewAfter` has passed:**

1. Pull current metrics for affected campaigns using `listCampaigns` and `getCampaignPerformance` (7-day window). Use the `beforeSnapshot` from the change log as baseline — only fall back to `getCampaignPerformance` for the pre-change period if `beforeSnapshot.metrics` is null. Do this in parallel with the user's actual request. Save the `listCampaigns` result for reuse in anomaly detection.

2. Compute deltas: percentage change for spend, conversions, CPA, CTR.

3. Present briefly BEFORE the user's request:

> **Follow-up on recent changes:**
>
> _[Date]: [summary]_
> Result after [7/14] days: CPA went from $X -> $Y ([+/-Z%]). Conversions [increased/decreased] from X -> Y. [One sentence assessment]

4. Mark as `reviewed: true` with `reviewResult`:
```json
{
  "reviewed": true,
  "reviewedAt": "<ISO 8601>",
  "reviewResult": {
    "afterSnapshot": { "spend7d": 0, "conversions7d": 0, "cpa7d": 0, "ctr7d": 0 },
    "assessment": "positive|negative|inconclusive",
    "note": "<one line summary>"
  }
}
```

5. If `negative` (CPA increased >20% or conversions dropped >20%): suggest undoing.

## Check account baseline for anomalies

Read `{data_dir}/account-baseline.json`. If it exists AND was last updated >24 hours ago:

1. Compare each campaign's 7-day metrics to the `rolling30d` baseline.
2. Flag campaigns where CPA is >1.5x average, conversions dropped >40%, spend rate >1.5x average, or CTR dropped >30%.
3. Mention anomalies briefly if found.
4. Update the baseline (see Account Baseline section in SKILL.md).

If `account-baseline.json` doesn't exist, skip — it will be created at session end.
