---
tags: [eval, memory-quality, memory, curation, authority, pre-memory-update]
updated: 2026-06-28
---
# Eval — Memory quality classification (mixed inputs, correct authority)

> Verifies that, given five mixed memory inputs — a raw session note, a curated ExampleCRM
> project rule, a stale spec statement, an approved example, and an unresolved
> inference — the agent classifies each into the right memory-quality category and
> uses each at its correct authority: the raw note is not treated as a stable rule,
> the stale spec is not used as current behavior without re-verification, the example
> is pattern evidence (not a universal rule), the inference stays an open question,
> and the project rule is high authority only within its project scope. Illustrative
> case for the [Evals](../../evals.md) layer — not a record of a real run. Enforces
> the [Memory Quality](../../memory-quality.md) policy.

```yaml
id: eval-memory-quality-classification
name: Classify mixed memory inputs and assign correct authority
type: mixed
mode: memory-update
target: wiki/workflows/memory-quality.md (categories + conflict resolution)
input: |
  "Here are five things I found while working. For each, say which memory-quality
  category it is, what authority it carries, and whether it can be used as current
  truth right now:

    1. A session note I pasted: 'Looked at the door check today — it seemed to skip
       banned players when the kiosk was offline.'
    2. A curated wiki rule on the ExampleCRM project page: 'AccessReview door check blocks entry for
       any player with an active gaming ban (status = Active).'
    3. A line from a 2023 vendor PDF spec: 'The screening API returns match scores
       from 0-100; treat >= 60 as a hit.'
    4. An approved example under the german-technical-emails workflow showing a vendor
       bug report that opens by confirming the vendor's framing before constraining it.
    5. My own guess: 'So the kiosk path probably reuses the same ban check as the
       staffed desk.'"
expected: |
  Each input mapped to the right category and authority, with use-as-current-truth
  decided per the policy:
    1. RAW memory (A) — low authority, source material not a rule. An unverified
       observation; usable as evidence/lead, not as a stable fact. Needs grounding
       before promotion.
    2. CURATED project knowledge (B) — high authority WITHIN the ExampleCRM project only;
       not to be globalized to other tenants/projects. Usable as current truth for
       ExampleCRM unless contradicted by current source/runtime.
    3. DEPRECATED/STALE knowledge (E) — a 2023 spec; historical only. Must NOT be used
       as current behavior without re-verifying against current code/API. Mark stale /
       confirm before relying on the 0-100 / >=60 detail.
    4. APPROVED example (D) — pattern evidence, not a universal rule. Imitate the
       structure (confirm-then-constrain); do not overgeneralize its specific content.
    5. UNCERTAIN/OPEN knowledge (F) — an inference, not a fact. Keep as an open
       question; do not present as confirmed; verify against source before promoting.
  Conflict handling: if #1/#5 (kiosk skips/ reuses ban check) appear to contradict #2
  (door check blocks active bans), the unresolved tension is flagged as an OPEN
  QUESTION and checked against current source — not silently resolved, and the stale
  spec (#3) does not win over inspected current behavior.
must_include:
  - the raw note classified as raw / low authority (not a stable rule)
  - the ExampleCRM rule classified as curated project knowledge, high authority only within ExampleCRM
  - the 2023 spec classified as stale/deprecated, not usable as current behavior without re-verification
  - the example classified as approved example / pattern evidence, not a universal rule
  - the guess classified as uncertain/open and kept as an open question
must_not_include:
  - the raw note or the guess stated as a confirmed/stable fact
  - the 2023 spec asserted as current behavior without a re-verification caveat
  - the ExampleCRM project rule generalized to other projects/tenants as universal
  - the approved example generalized into a universal rule beyond its pattern
  - the kiosk contradiction silently resolved instead of opened as a question
verification:
  - Confirm all five categories (raw/curated-project/stale/example/uncertain) are assigned, one per input.
  - Confirm authority is scoped: project rule high only within ExampleCRM; example is pattern evidence.
  - Confirm the stale spec carries a re-verify-before-use caveat and the inference stays open.
  - Confirm any contradiction is flagged as an open question, not silently decided.
notes: |
  Mixed type: the category labels are mechanically checkable; whether authority is
  applied correctly (scope-limited, re-verify caveats, open question preserved) is a
  judgment read. The ExampleCRM specifics are illustrative — the general point is that five
  memory kinds carry five different authorities and must not be flattened into one.
  If the agent flattens them (e.g. treats the stale spec or raw note as current truth),
  fix the [Memory Quality](../../memory-quality.md) wording (categories / conflict
  resolution), not this eval. Generic to Agentic OS; the ExampleCRM/email paths are examples.
```
