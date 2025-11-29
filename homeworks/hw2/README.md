# Homework 2: Recipe Bot Error Analysis

## 📝 Note

**We have provided our solutions in this repository as reference material, but we strongly encourage you to work through the exercise on your own first.** Attempting the assignment independently will help you better understand the error analysis process and develop your own insights about chatbot failure modes.

This assignment focuses on performing an error analysis for your Recipe Bot.

## Part 1: Define Dimensions & Generate Initial Queries

1. **Identify Key Dimensions:** (i.e., key aspects or variables of user inputs you'll use to generate diverse test queries, such as `cuisine_type`, `dietary_restriction`, or `meal_type` for your recipe bot)

   * Identify 3-4 key dimensions relevant to your Recipe Bot's functionality and potential user inputs.
   * For each dimension, list at least 3 example values.
1. **Generate Unique Combinations (Tuples):**

   * Write a prompt for a Large Language Model (LLM) to generate 15-20 unique combinations (tuples) of these dimension values.
1. **Generate Natural Language User Queries:**

   * Write a second prompt for an LLM to take 5-7 of the generated tuples and create a natural language user query for your Recipe Bot for each selected tuple.
   * Review these generated queries to ensure they are realistic and representative of how a user might interact with your bot.

   **Alternative for Query Generation:** If you prefer to skip the LLM-based query generation (steps 2 and 3 above), you may use the pre-existing queries and bot responses found in `homeworks/hw2/results_20250518_215844.csv` as the basis for your error analysis in Part 2. You can then proceed directly to the "Open Coding" step using this data.

### Step 1: key dimensions

Dimensions:

- `dietary_restriction`: gluten free, dairy free, keto, low carb, vegetarian, vegan, pescatarian
- `dish_type`: appetizer, main, dessert, side, salad
- `time_available`: 15 min, 30 min, 45 min, 1 hour, 2 hour, >2 hours
- `number_of_people`: 1, 2, 3, 4, 6, 8
- `number_of_dishes`: 1, 2, 3, 4, 5
- `meal`: breakfast, lunch, dinner, snack
- `equipment_available`: microwave only, stove only, stove and oven, no microwave, sous vide, air fryer

### Step 2: unique tuple combos

PROMPT:

> Taking the below dimensions + example values, generate ~50 unique 3-tuple combinations of the values.
>
> Output 3-tuples where each tuple is only values (don't include dimension names in the tuple). Here are the dimensions and values:
>
> - `dietary_restriction`: gluten free, dairy free, keto, low carb, vegetarian, vegan, pescatarian
> - `dish_type`: appetizer, main, dessert, side, salad
> - `time_available`: 15 min, 30 min, 45 min, 1 hour, 2 hour, >2 hours
> - `number_of_people`: 1, 2, 3, 4, 6, 8
> - `number_of_dishes`: 1, 2, 3, 4, 5
> - `meal`: breakfast, lunch, dinner, snack
> - `equipment_available`: microwave only, stove only, stove and oven, no microwave, sous vide, air fryer
>
> Select a unique combination of 3 dimensions from the list of 8 dimensions (e.g. dish_type, meal, number_of_people), then select a value from each of those dimensions to make a unique 3-tuple, with each position in the tuple representing a value selected from the set for each dimension selected.
>
> Example 1: you could select the dimensions `dish_type`, `meal`,and `number_of_people` for the tuple, and then select the a value from each dimension to make the unique 3-tuple, e.g. (main, breakfast, 2).
>
> Example 2: could select dimensions `dietary_restriction`, `meal`, and `number_of_dishes` and create a unique 3-tuple with values from each dimension, e.g. (dairy free, dinner, 2).
>
> Each 3-tuple of values should be unique within the overall list of tuples.

OUTPUT

(vegan, snack, 2)

(vegan, dessert, 30 min)

(low carb, air fryer, 30 min)

(breakfast, appetizer, 1)

(breakfast, 1 hour, air fryer)

(lunch, 2, pescatarian)

(2, gluten free, snack)

(breakfast, 2 hour, stove and oven)

(pescatarian, main, 1 hour)

(salad, 30 min, stove only)

(keto, salad, stove and oven)

(side, 8, >2 hours)

(lunch, appetizer, 8)

(snack, 6, gluten free)

(snack, side, 4)

(dinner, 2 hour, stove only)

(4, dinner, 8)

(snack, dessert, 2)

(low carb, stove only, 15 min)

(4, low carb, breakfast)

(5, pescatarian, lunch)

(gluten free, main, 15 min)

(stove and oven, 1, lunch)

(side, 15 min, microwave only)

(1, snack, 3)

(dairy free, no microwave, 45 min)

(dairy free, lunch, 8)

(gluten free, salad, 2 hour)

(5, lunch, 2)

(salad, dinner, 15 min)

(keto, air fryer, >2 hours)

(appetizer, 2, 15 min)

(5, dairy free, lunch)

(pescatarian, dessert, no microwave)

(main, lunch, 1 hour)

(main, snack, 45 min)

(2, snack, 2)

(breakfast, 4, keto)

(snack, main, 2)

(breakfast, 2 hour, microwave only)

(3, lunch, 1)

(keto, main, 2 hour)

(dairy free, main, no microwave)

(side, breakfast, >2 hours)

(no microwave, 1, snack)

(appetizer, 30 min, stove and oven)

(main, 3, 45 min)

(microwave only, 8, breakfast)

(appetizer, 1 hour, sous vide)

(salad, 4, 2 hour)

### Step 3: Generate Natural Language User Queries

#### PROMPT

Role & instructions: generate realistic user queries that a user might input to a recipe chatbot. Select 5-7 tuples from the <sample_data> below (each element in the tuple is a value within the dimensions in the <dimensions>). For each tuple, generate a user query in natural language that a user might put into the recipe chatbot. You can see some examples of actual user queries in `data/sample_queries.csv`.

<dimensions>

- `dietary_restriction`: gluten free, dairy free, keto, low carb, vegetarian, vegan, pescatarian
- `dish_type`: appetizer, main, dessert, side, salad
- `time_available`: 15 min, 30 min, 45 min, 1 hour, 2 hour, >2 hours
- `number_of_people`: 1, 2, 3, 4, 6, 8
- `number_of_dishes`: 1, 2, 3, 4, 5
- `meal`: breakfast, lunch, dinner, snack
- `equipment_available`: microwave only, stove only, stove and oven, no microwave, sous vide, air fryer

</dimensions>

<sample_data>

(vegan, snack, 2)

(vegan, dessert, 30 min)

(low carb, air fryer, 30 min)

(breakfast, appetizer, 1)

(breakfast, 1 hour, air fryer)

(lunch, 2, pescatarian)

(2, gluten free, snack)

(breakfast, 2 hour, stove and oven)

(pescatarian, main, 1 hour)

(salad, 30 min, stove only)

(keto, salad, stove and oven)

(side, 8, >2 hours)

(lunch, appetizer, 8)

(snack, 6, gluten free)

(snack, side, 4)

(dinner, 2 hour, stove only)

(4, dinner, 8)

(snack, dessert, 2)

(low carb, stove only, 15 min)

(4, low carb, breakfast)

(5, pescatarian, lunch)

(gluten free, main, 15 min)

(stove and oven, 1, lunch)

(side, 15 min, microwave only)

(1, snack, 3)

(dairy free, no microwave, 45 min)

(dairy free, lunch, 8)

(gluten free, salad, 2 hour)

(5, lunch, 2)

(salad, dinner, 15 min)

(keto, air fryer, >2 hours)

(appetizer, 2, 15 min)

(5, dairy free, lunch)

(pescatarian, dessert, no microwave)

(main, lunch, 1 hour)

(main, snack, 45 min)

(2, snack, 2)

(breakfast, 4, keto)

(snack, main, 2)

(breakfast, 2 hour, microwave only)

(3, lunch, 1)

(keto, main, 2 hour)

(dairy free, main, no microwave)

(side, breakfast, >2 hours)

(no microwave, 1, snack)

(appetizer, 30 min, stove and oven)

(main, 3, 45 min)

(microwave only, 8, breakfast)

(appetizer, 1 hour, sous vide)

(salad, 4, 2 hour)

</sample_data>

#### OUTPUT

(vegan, dessert, 30 min) "I need a quick vegan dessert I can make in 30 minutes or less"

(low carb, air fryer, 30 min) "What's a good low carb recipe I can make in my air fryer? Need something quick, maybe 30 min"

(pescatarian, main, 1 hour) "Give me a pescatarian main dish recipe that I can make in about an hour"

(lunch, appetizer, 8) "I'm hosting a lunch for 8 people and need some good appetizer ideas"

(keto, salad, stove and oven) "Looking for a keto-friendly salad recipe. I have access to stove and oven if I need to roast anything"

(dairy free, lunch, 8) "Need to make dairy free lunch for 8 people. What would you suggest?"

(main, 3, 45 min) "Help me with a main dish for 3 people that I can get done in 45 minutes max"

**Without leading tuples:**

I need a quick vegan dessert I can make in 30 minutes or less

What's a good low carb recipe I can make in my air fryer? Need something quick, maybe 30 min

Give me a pescatarian main dish recipe that I can make in about an hour

I'm hosting a lunch for 8 people and need some good appetizer ideas

Looking for a keto-friendly salad recipe. I have access to stove and oven if I need to roast anything

Need to make dairy free lunch for 8 people. What would you suggest?

Help me with a main dish for 3 people that I can get done in 45 minutes max

## Part 2: Initial Error Analysis (Ref Sec 3.2, 3.3, 3.4 of relevant course material)

1. **Run Bot on Synthetic Queries:**

   * Execute your Recipe Bot using the synthetic queries generated in Part 1.
   * Record the full interaction traces for each query.
1. **Open Coding:** (an initial analysis step where you review interaction traces, assigning descriptive labels/notes to identify patterns and potential errors without preconceived categories, as detailed in Sec 3.2 of the provided chapter)

   * Review the recorded traces.
   * Perform open coding to identify initial themes, patterns, and potential errors or areas for improvement in the bot's responses.
1. **Axial Coding & Taxonomy Definition:** (a follow-up step where you group the initial open codes into broader, structured categories or 'failure modes' to build an error taxonomy, as described in Sec 3.3 of the provided chapter)

   * Group the observations from open coding into broader categories or failure modes.
   * For each identified failure mode, create a clear and concise taxonomy. This should include:
       - **A clear Title** for the failure mode.
       - **A concise one-sentence Definition** explaining the failure mode.
       - **1-2 Illustrative Examples** taken directly from your bot's behavior during the tests. If a failure mode is plausible but not directly observed, you can provide a well-reasoned hypothetical example.
1. **[Optional] Spreadsheet for Analysis:**

   * Create a spreadsheet to systematically track your error analysis.
   * Include the following columns:
       - `Trace_ID` (a unique identifier for each interaction)
       - `User_Query` (the query given to the bot)
       - `Full_Bot_Trace_Summary` (a summary of the bot's full response and behavior)
       - `Open_Code_Notes` (your notes and observations from the open coding process)
       - A column for each of your 3-5 defined `Failure_Mode_Title`s (use 0 or 1 to indicate the presence or absence of that failure mode in the trace).

#### STEP 1: GET TRACES

> Execute your Recipe Bot using the synthetic queries generated in Part 1.

Q: am I missing some automated tool for this? or is this manually run them?

How many of these to do, just 5-7? or like 100+ per the general guideline?

I ran them in bulk using the bulk script and got output which is in `/Users/andrew/projects/recipe-chatbot/results/results_20251128_190135.csv`.

Q: how do I record the full traces? → I see it happens automatically (saved in `/annotation/traces`) when I manually enter a query, but not when I run the bulk script. I could update that.

TODO: update bulk script to record traces like happens manually / automatically.



> Record the full interaction traces for each query.

Q: am I missing some automated tool for this? or is this manually run them?

#### STEP 2: OPEN CODING

#### STEP 3: AXIAL CODING + TAXONOMY DEFINITION

#### STEP 4: ANALYSIS SPREADSHEET

See `hw2_error_analysis.csv`.

---

**Note:** You have the flexibility to edit, create, or modify any files within the assignment structure as needed to fulfill the requirements of this homework. This includes, but is not limited to, the `failure_mode_taxonomy.md` file, scripts for running your bot, or any spreadsheets you create for analysis.