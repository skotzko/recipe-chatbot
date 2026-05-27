<!-- HW 2 Part 2 — my failure mode taxonomy (recipe bot). 8 modes, axially coded from 20 open-coded traces in open_coding_sample_mybot.md. Trace IDs in examples refer to the 50-trace results set (results/results_20260516_115750.json). -->

# Failure Mode Taxonomy — My Recipe Bot

Derived from open coding 20 of 50 traces produced by my HW1 system prompt against `synthetic_queries_expanded.csv`. The loud mode (missing structural sections) was saturated by trace 6; the others emerged across traces 2–20. Modes with only N=1 in the open coding were dropped unless explicitly retained.

## Failure Mode 1: Missing Required Structural Sections

*   **Definition**: Response omits structural sections that the system prompt requires for every recipe — specifically, an **equipment-needed** section, a **timing/prep guidance** section, and a **prep-vs-cooking instruction split**. Tracked as one mode with three named variants because they co-occur and share the same root cause (system prompt under-specifies required structure).
*   **Variants**: `equipment-missing`, `timing-missing`, `prep-cook-split-missing`
*   **Illustrative Examples**:
    1.  *User Query (trace 1)*: "Give me a vegan snack recipe. for 2 people."
        *Bot Response Summary*: Recipe for Crispy Chickpea Snack listed ingredients and instructions but no separate equipment section (baking sheet, parchment paper, bowl, oven were all needed but never listed up front), no timing section, and no prep-vs-cook split.
    2.  *User Query (trace 6)*: "Give me a pescatarian lunch recipe. For 2 people."
        *Bot Response Summary*: Same gaps — no equipment section, no timing section, instructions not divided into prep vs. cook. By this trace the pattern was systemic ("pattern across all — fix in system prompt").

## Failure Mode 2: Shopping List Omits Items from Ingredients

*   **Definition**: Shopping list omits items that appear in the recipe or ingredient list, including optional/recommended additions.
*   **Illustrative Examples**:
    1.  *User Query (trace 2)*: "Help me make a vegan dessert. In about 30 minutes."
        *Bot Response Summary*: Recipe included multiple optional toppings beyond berries, but the shopping list only listed berries.
    2.  *User Query (trace 9)*: "Looking for a pescatarian main. In around an hour."
        *Bot Response Summary*: Cherry tomatoes were recommended as an optional addition in the recipe but missing from the shopping list.

## Failure Mode 3: Ambiguous Quantities and Measurements

*   **Definition**: Recipe uses imprecise terms ("a pinch", "thinly sliced", or unspecified amounts) instead of the precise measurements the system prompt mandates ("no vague terms").
*   **Illustrative Examples**:
    1.  *User Query (trace 11)*: "I need a keto salad — i have a stove and oven."
        *Bot Response Summary*: Recipe instructed "thinly sliced" without specifying thickness (mm/inches or a reference).
    2.  *User Query (trace 18)*: "Help me make a snack dessert. For 2 people."
        *Bot Response Summary*: Instruction read "stir in vanilla extract and a pinch of salt" — neither quantity given; should have been e.g. "stir in 1/2 tsp vanilla extract and a pinch of salt".

## Failure Mode 4: Missing Serving Size

*   **Definition**: Response doesn't state how many people the dish serves, despite the system prompt requiring this at the top of every recipe.
*   **Illustrative Examples**:
    1.  *User Query (trace 10)*: "Looking for a salad. i only have a stove (no oven) and in about 30 minutes."
        *Bot Response Summary*: Recipe provided no serving-size header; you flagged this as a general gap ("all recipes should say that").
    2.  *User Query (trace 9)*: "Looking for a pescatarian main. In around an hour."
        *Bot Response Summary*: Implicitly missing — ingredients were given without a serving-size anchor.

## Failure Mode 5: Missing Cross-Dish Sequencing in Multi-Dish Responses

*   **Definition**: When the user requests multiple dishes, instructions are isolated per dish without timing or equipment coordination across them.
*   **Illustrative Examples**:
    1.  *User Query (trace 17)*: "What's a good dinner? I need 4 dishes. For 8 people."
        *Bot Response Summary*: Four dishes each had their own self-contained instructions, but no guidance on inter-dish sequencing (what to start first, equipment timesharing, when to bring everything together).
    2.  *User Query (trace 20)*: "What's a good low carb breakfast? I need 4 dishes."
        *Bot Response Summary*: Same gap — multiple dishes given as parallel recipes without cross-dish timing.

## Failure Mode 6: Inconsistent Recipe-vs-Questions Behavior

*   **Definition**: Bot inconsistently handles recipe queries with similar shape — sometimes returning a recipe directly, sometimes asking clarifying questions — without an obvious trigger. This is a cross-trace consistency failure rather than a per-trace defect.
*   **Illustrative Examples**:
    1.  *User Query (trace 15)*: "Help me make a snack side — for 4 people."
        *Bot Response Summary*: Bot replied with clarifying questions instead of a recipe, despite earlier snack queries getting recipes directly. The questions themselves were useful (asking for serving count) but the inconsistency is the failure.
    2.  *User Query (trace 16)*: "Help me make a dinner. I only have a stove (no oven). I've got a couple hours."
        *Bot Response Summary*: Same pattern — clarifying questions instead of a recipe, contrasting with other queries that got direct recipes.

## Failure Mode 7: Implicit / Missing Prerequisite Steps

*   **Definition**: An instruction step assumes a prep action was already performed (or a decision was made) that the recipe never explicitly stated.
*   **Illustrative Examples**:
    1.  *User Query (trace 1)*: "Give me a vegan snack recipe. for 2 people."
        *Bot Response Summary*: Step 2 instructed actions on rinsed chickpeas, but the recipe never instructed the user to rinse the chickpeas first.
    2.  *User Query (trace 14)*: "What's a good gluten free snack? For 6 people."
        *Bot Response Summary*: Step 3 said to add spices to chickpeas but didn't specify whether to pre-mix the spices first or just dump them all in together — the user can't tell which the bot meant.
    3.  *User Query (trace 5)*: "What's a good breakfast? I have an air fryer. In around an hour."
        *Bot Response Summary*: Tips section mentioned adding cooked sausage but didn't specify whether to cook the sausage separately or alongside the hash in the air fryer.

## Failure Mode 8: Time Constraint Misinterpretation (Cook vs. Total)

*   **Definition**: Bot treats a user-stated time limit as cook time only, not total time including prep. The user's "I have 15 minutes" should mean 15 minutes end-to-end, not 15 minutes of active cooking on top of unspecified prep.
*   **Illustrative Examples**:
    1.  *User Query (trace 19)*: "Help me make a low carb recipe. in 15 minutes or less and i only have a stove (no oven)."
        *Bot Response Summary*: Recipe's stated cook time was within budget, but factoring prep (chopping, measuring, heating the pan) pushed the realistic total past the user's 15-minute limit. The system prompt needs to be explicit that user time = total time.

## Modes Considered and Excluded

- **Unrequested categorical labels** (trace 9: "shouldn't say 'dinner' since user only requested a main") — N=1, dropped. Watch in round 2.
- **Over-constraining on user-stated equipment** (trace 11: "most salads are cold and don't require a stove or oven") — N=1, dropped. Watch in round 2.
- **Verbose / awkward step wording** (trace 1: "step 3 should just say 'Toss the chickpeas...'") — folded into Mode 3 (Ambiguous Quantities and Measurements) since both stem from imprecise language.
- **Reading-comprehension ambiguity** (trace 10: "is this supposed to be a warm, wilted salad?") — not codable as a per-trace failure; would be captured by acceptable/unacceptable column if used.

## Round-2 candidates (if expanding coding past 20 traces)

- Confirm N=1 candidates above.
- Test the hypothesis flagged in trace 5: programmatically compare shopping-list items to ingredient-list items across all 50 traces (this would convert Mode 2 from a sampled observation into a measured rate).
- Watch for safety/correctness failures (trace 5's "don't know if cooking eggs like this is actually a thing people do") — only one such suspicion in this batch, but the course explicitly warns these are often the highest-cost failure types.
