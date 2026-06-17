# HW5 Results — Failure Transition Heat-Map

96 pre-labeled agent traces. Each one succeeds through some state, then breaks at
the next. I counted every (last-success → first-failure) pair into a 10×10 matrix
and read where the pipeline actually dies.

Two views in `results/`:
- `failure_transition_heatmap.png` — the bare matrix
- `failure_transition_heatmap_margins.png` — same matrix with column and row totals
  in the margins (the column totals are the part that matters, more below)

## 1. Where it breaks

Read the matrix by **column**. A column is a first-failure state, so the column
total is how often that state is where things *first* go wrong. That's the root
cause, because the labeling records only the first failure in each trace. Whatever
breaks downstream of it never gets counted. So a tall column isn't "this state
looks bad sometimes." It's "this state is the origin."

| first-failure state | count |
|---------------------|-------|
| **GetRecipes** | **32** |
| **GenRecipeArgs** | **20** |
| GetCustomerProfile | 13 |
| GenWebArgs | 8 |
| GenCustomerArgs | 7 |
| GetWebInfo / ComposeResponse / DeliverResponse | 5 each |
| PlanToolCalls | 1 |

Don't read it by row. The biggest row total is PlanToolCalls at 31, and it's a
trap. Those 31 don't fail *at* Plan. They were last *healthy* at Plan and then
scattered into seven different failure columns. Big row, no single fix. Big column,
one place to look. Triage by column.

## 2. The recipe leg is the whole story

The two recipe-search states sit next to each other and together own **52 of 96
failures, 54%**:

- `GenRecipeArgs` (20) — the LLM builds the recipe-search arguments
- `GetRecipes` (32) — the tool runs the search

Everything else is a rounding error by comparison:

| pipeline leg | failures |
|--------------|----------|
| **recipe (args + fetch)** | **52** |
| customer (args + fetch) | 20 |
| web (args + fetch) | 13 |
| compose + deliver | 10 |

The web leg and the compose/deliver tail are quiet, but quiet here is ambiguous.
It could mean those steps are robust. It could also mean almost nothing survives
far enough to reach them. The right-margin totals say it's the second one. By the
time a trace gets past recipe search, most of the population is already gone. You
can't read a low column as "this step is safe" when the step barely runs.

## 3. The notable cells

The single darkest cell is `PlanToolCalls → GenRecipeArgs` (10). The agent planned
its tools fine, then broke the instant it tried to write recipe arguments, skipping
any customer lookup. The heavy feeds into the GetRecipes column are
`GetCustomerProfile → GetRecipes` (9) and `GenCustomerArgs → GetRecipes` (8). Those
ones did pull customer context first, then still died at the search.

Same crash site, two routes in. One fetched the customer, one didn't. If the fix
lives in recipe-arg construction, the route in shouldn't matter and both should
drain together. If it doesn't, they're separate bugs. The matrix can't tell me
which.

## 4. What the matrix couldn't answer, and what reading the traces did

The matrix gave me two stories for the GetRecipes-32 and no way to choose. Story A:
bad args in disguise. The label says GenRecipeArgs "succeeded," but "succeeded" only
means the step emitted a valid-looking argument object, not that the args were good.
A clean query that returns nothing still gets labeled GenRecipeArgs-success,
GetRecipes-failure. If that's the cause, the fix is upstream in the arg-generation
prompt. Story B: the args were fine and the search itself came up empty. If that's
the cause, the fix is in the tool or the data, not the prompt. The matrix is blind
to *why* a step failed, so it can't tell A from B. It's a triage map, not a
diagnosis. So I opened the 32 traces and read them.

It's Story B. The failing requests are almost all the same three prompts repeated:
gluten-free dinner for four, vegetarian high-protein, healthy oatmeal breakfast.
These aren't weird queries. They're the most normal recipe requests a user could
make. If the LLM were writing bad args, the failures would scatter across varied,
random queries. Instead a tiny fixed set of reasonable requests fails every single
time. That's the fingerprint of a catalog gap, not a reasoning bug. The recipe
catalog almost certainly doesn't hold good matches for these, and the tool returns
empty. The fix is data, not prompt.

The error wording splits two ways, "unable to retrieve ... at this time" versus "no
recipes found matching criteria." Same failure, two narrations. The agent has no
stable way to report an empty tool result. Worth one caution: if you ever
auto-classify these failures by string-matching the error text, those two phrasings
would split one root cause into two buckets and send the fix to the wrong place.

## 5. The bug the heat-map can't see: graceful failure

Reading the traces surfaced something the matrix never could. After the recipe
search returns empty, the agent doesn't retry, doesn't relax the constraints, and
doesn't fall back to web search. It asks the user a smooth, plausible follow-up
question ("any ingredients to include or avoid?") and the conversation moves on. The
user answers, stays happy, and never complains. In none of the 32 traces does the
user push back on the post-error message.

That looks like good recovery. It isn't. The user asked for a recipe and never got
one. The agent papered over a retrieval failure with a fluent redirect, and the
original goal quietly died. This is the most dangerous failure mode in the whole
set, precisely because it's pleasant. If you measured this agent by user sentiment,
it passes. By "did the user get the recipe they asked for," it fails all 32.

The lesson: you could not find this bug by watching user reactions. Even a
thumbs-down wouldn't catch it, because the user wasn't unhappy, they were redirected.
The only signal that catches a graceful failure is an explicit goal-completion check
run on the trace itself, "was a recipe actually delivered for the request that was
made?" That check is exactly what reading the 32 traces by hand amounted to. The
heat-map pointed me to the right column. Reading the traces told me what was wrong.
Neither one, alone, was enough.

## 6. What I'd do with this

Stop looking anywhere but the recipe leg. 54% of the failures live there and nothing
else clears double digits. Two fixes, in order. First, the data: fill the catalog
gaps for the common requests that return empty, since that's the root cause of the
GetRecipes-32. Second, the recovery: when recipe search comes back empty, the agent
should retry with relaxed constraints or fall back to web search, not silently
redirect. And going forward, instrument a goal-completion eval so a graceful failure
trips an alarm instead of sliding by on a friendly tone.

## 7. The goal-completion eval, sketched

`analysis/goal_completion_eval.py` is a reference design for that eval. Two layers,
cheapest first.

Layer 1 is a code check, free and deterministic: did the trace reach DeliverResponse
with a recipe? If it died at or before GetRecipes, no recipe ever reached the user,
auto-fail. No LLM, no user signal. On these 96 traces it returns a goal-completion
rate of **0/96**. Every trace failed to deliver, including the pleasant ones. Graded
on sentiment this agent looks fine. Graded on the job, it's at zero. Same traces,
opposite verdict.

Layer 2 is an LLM judge, and it only runs on traces that pass Layer 1, so no judge
call is wasted on a trace code already condemned. It reads the delivered recipe
against the request and rules whether intent was met. It's the HW3 dietary judge
re-aimed, and like that judge it has to be validated on hand-labeled traces (TPR/TNR)
before its number means anything. I shipped it as a wired stub, unvalidated, on
purpose.

The load-bearing decision is in the goal extraction: it anchors on the **original**
request, the first user turn, and the judge is told to ignore later goalpost-moving.
That's the whole defense against graceful failure. Anchor on the latest turn instead
and the agent's smooth redirect scores as success, because the redirected question
did get resolved. Original-intent anchoring is the one line that makes the eval work.

## Files
- `analysis/transition_heatmaps.py` — builds the matrix, renders both PNGs
- `analysis/goal_completion_eval.py` — two-layer goal-completion eval (code + LLM judge)
- `results/failure_transition_heatmap.png` — bare matrix
- `results/failure_transition_heatmap_margins.png` — matrix + marginal totals
- `results/getrecipes_failures.html` — self-contained viewer for the 32 GetRecipes failures
- `results/getrecipes_failures.jsonl` — those 32 traces, extracted
