## Task and criterion
Evaluate if the agent's response matches the dietary restrictions/guidelines in the user's query.

The given dietary restriction ALWAYS applies, even if the user's query does not explicitly repeat it. Evaluate the recipe against the provided restriction regardless of how the request is phrased. (e.g. restriction=vegetarian + a recipe containing chicken → FAIL, even if the user only asked for "comfort food.")

Here is a short definition of common dietary restrictions:
- Vegan: No animal products (meat, dairy, eggs, honey, etc.)
- Vegetarian: No meat or fish, but dairy and eggs are allowed
- Gluten-free: No wheat, barley, rye, or other gluten-containing grains
- Dairy-free: No milk, cheese, butter, yogurt, or other dairy products
- Keto: Very low carb (typically <20g net carbs), high fat, moderate protein
- Paleo: No grains, legumes, dairy, refined sugar, or processed foods
- Pescatarian: No meat except fish and seafood
- Kosher: Follows Jewish dietary laws (no pork, shellfish, mixing meat/dairy)
- Halal: Follows Islamic dietary laws (no pork, alcohol, proper slaughter)
- Nut-free: No tree nuts or peanuts
- Low-carb: Significantly reduced carbohydrates (typically <50g per day)
- Sugar-free: No added sugars or high-sugar ingredients (including honey)
- Raw vegan: Vegan foods not heated above 118°F (48°C)
- Whole30: No grains, dairy, legumes, sugar, alcohol, or processed foods
- Diabetic-friendly: Low glycemic index, controlled carbohydrates
- Low-sodium: Reduced sodium content for heart health

Evaluate every ingredient against the restriction's intent, not just exact-name matches. Sweeteners like honey, agave, maple syrup, and fruit concentrates all count as sugar. Apply the same generalization to every restriction.

## Pass/Fail definitions

FAIL IF: The response partially or completely ignores the user's dietary restrictions. Partial adherence fails, as does ignoring the restriction.

FAIL IF: the recipe includes a non-compliant ingredient — even as an option or alternative — UNLESS the user explicitly permitted that ingredient in their query. A compliant alternative being also offered does NOT excuse it. (e.g. "honey or stevia" for a sugar-free user who gave no waiver → FAIL; optional cheese for a user who said "cheese is okay" → PASS.)

PASS IF: The response fully (100%) adheres to the dietary restrictions present in the user query.


## Examples
<!-- 2-3 few-shot examples from your Train set with input, output, reasoning, and pass/fail label -->

### Example 1: ambiguous query
<example>
<query>Gluten-light recipe - I'm not celiac just sensitive</query>
<dietary_restriction>gluten-free</dietary_restriction>
<output>
Absolutely! Here's a delicious **Garlic Herb Quinoa Salad** that is light on gluten but full of flavor, perfect for a satisfying lunch or dinner for two.

### Garlic Herb Quinoa Salad (Serves 2)

#### Ingredients:
- ¾ cup quinoa
- 1 ½ cups water
- 2 tbsp olive oil
- 3 garlic cloves, minced
- 1 cup cherry tomatoes, halved
- 1 small cucumber, diced
- ¼ cup fresh parsley, chopped
- 2 tbsp fresh lemon juice
- Salt and freshly ground black pepper, to taste
- Optional: crumbled feta cheese or sliced olives for extra flavor

#### Instructions:

1. **Rinse the Quinoa:**
   Place the quinoa in a fine-mesh sieve and rinse thoroughly under cold running water. This removes any bitterness and ensures fluffiness.

2. **Cook the Quinoa:**
   In a medium saucepan, combine the rinsed quinoa and water. Bring to a boil over medium-high heat. Once boiling, reduce the heat to low, cover, and let simmer for about 15 minutes, or until the water is absorbed and the quinoa is fluffy. Remove from heat, and let it sit covered for 5 minutes to finish steaming. Fluff with a fork.

3. **Prepare the Dressing & Vegetables:**
   While the quinoa is cooking, heat 1 tablespoon of olive oil in a small skillet over medium heat. Add minced garlic and sauté for 1-2 minutes until fragrant, taking care not to burn it.

4. **Combine Ingredients:**
   In a large mixing bowl, add the cooked quinoa. Pour over the sautéed garlic and olive oil. Add cherry tomatoes, diced cucumber, chopped parsley, lemon juice, salt, and pepper. Toss gently until well combined.

5. **Taste & Adjust:**
   Adjust seasoning as needed, adding more lemon juice, salt, or pepper according to your preference. For added richness, sprinkle with feta or olives if desired.

6. **Serve:**
   Divide the salad into two bowls or plates. Serve immediately for a fresh experience or chill in the fridge for 30 minutes to enhance flavors.

Enjoy your gluten-light, flavorful quinoa salad! It’s refreshing, healthy, and easy to prepare.
</output>
<reasoning>
The recipe provided is for a Garlic Herb Quinoa Salad, which uses quinoa as the main grain. Quinoa is naturally gluten-free, making it suitable for a gluten-free diet. The other ingredients listed, such as olive oil, garlic, cherry tomatoes, cucumber, parsley, lemon juice, salt, and pepper, are also gluten-free. The optional ingredients, feta cheese and olives, are typically gluten-free as well. However, the recipe is described as 'gluten-light' rather than 'gluten-free,' which may imply that it is not strictly adhering to a gluten-free standard. Since the dietary restriction specified is 'gluten-free,' the recipe should be strictly free of gluten. The description of the recipe as 'gluten-light' suggests a potential misunderstanding of the dietary restriction, even though the ingredients themselves are gluten-free. Therefore, while the ingredients are appropriate, the labeling and description do not align with a strict gluten-free requirement.
</reasoning>
<answer>FAIL</answer>
</example>

### Example 2: pass
<example>
<query>My kid needs a nut-free cookie recipe for school but she's super picky and only likes chocolate</query>
<dietary_restriction>nut-free</dietary_restriction>
<output>
Absolutely! Here's a delicious and kid-friendly nut-free chocolate cookie recipe that should satisfy even the pickiest eater. These cookies are soft, chewy, and rich in chocolate flavor — perfect for school!

**Nut-Free Double Chocolate Cookies (Makes about 12 cookies)**

---

### Ingredients:
- 1/2 cup (115g) unsalted butter, softened
- 1/2 cup (100g) granulated sugar
- 1/2 cup (100g) packed light brown sugar
- 1 large egg
- 1 teaspoon vanilla extract
- 1 cup (125g) all-purpose flour
- 1/4 cup (25g) unsweetened cocoa powder
- 1/2 teaspoon baking soda
- 1/4 teaspoon salt
- 1 cup (180g) semi-sweet chocolate chips

---

### Instructions:

1. **Preheat your oven** to 350°F (175°C). Line a baking sheet with parchment paper for easy cleanup.

2. **Cream the butter and sugars**: In a large mixing bowl, cut the softened butter into pieces. Use a hand or stand mixer to beat the butter, granulated sugar, and brown sugar together until the mixture is light and fluffy, about 2-3 minutes.

3. **Add the egg and vanilla**: Crack the egg into the mixture and beat until well combined. Then stir in the vanilla extract.

4. **Mix dry ingredients**: In a separate bowl, whisk together the flour, cocoa powder, baking soda, and salt.

5. **Combine wet and dry**: Gradually add the dry ingredients to the wet ingredients, mixing on low speed or stirring with a spoon, until just combined. Be careful not to overmix — stop once everything is well incorporated.

6. **Fold in the chocolate chips**: Using a spatula, gently fold in the chocolate chips until evenly dispersed throughout the dough.

7. **Shape the cookies**: Using a tablespoon or cookie scoop, portion the dough onto the prepared baking sheet, spacing each cookie about 2 inches apart. Gently press down on each cookie with the back of a spoon or your fingers to slightly flatten them.

8. **Bake**: Place in the oven and bake for 10-12 minutes. The cookies will look soft but should be set around the edges.

9. **Cool**: Remove from the oven and let the cookies cool on the baking sheet for about 5 minutes. Then transfer them to a wire rack to cool completely.

---

### Serving:
Enjoy these cookies with a glass of milk or just as they are! They are best eaten fresh but can be stored in an airtight container for up to 3 days.

---

Would you like a variation with added ingredients or different flavors?
</output>
<reasoning>
The recipe for Nut-Free Double Chocolate Cookies adheres to the nut-free dietary restriction. The ingredients listed do not include any tree nuts or peanuts, which are the primary concern for a nut-free diet. The recipe uses common baking ingredients such as butter, sugar, flour, cocoa powder, and chocolate chips, none of which typically contain nuts. Additionally, the preparation method does not introduce any risk of cross-contamination with nuts, assuming that all ingredients are sourced from nut-free facilities. Therefore, the recipe is suitable for someone with a nut-free dietary requirement.
</reasoning>
<answer>PASS</answer>
</example>

### Example 3: fail
<example>
<query>I avoid processed foods but I'm lazy</query>
<dietary_restriction>paleo</dietary_restriction>
<output>
Let's go for a quick and nutritious Meal: **Garlic Lemon Chickpea Salad**. It’s super simple, packed with protein, and requires minimal prep, suitable for a lazy day with basic ingredients. Serves 2.

### Ingredients:
- 1 can (15 oz) chickpeas, drained and rinsed
- 1-2 cloves garlic, minced
- 1 lemon (for juice and zest)
- 2 tbsp olive oil
- Salt and black pepper to taste
- Optional: fresh herbs like parsley or cilantro, chopped

### Steps:

1. **Prepare the chickpeas:** Drain and rinse the chickpeas thoroughly under cold water. Set aside in a mixing bowl.

2. **Make the dressing:** In a small bowl or jar, combine the juice of 1 lemon, 2 tablespoons of olive oil, and the minced garlic. Add a pinch of salt and black pepper to taste. Whisk everything together until well combined. If you like, add some lemon zest for extra zing.

3. **Assemble the salad:** Pour the dressing over the chickpeas and toss gently to coat all the beans evenly.

4. **Add herbs (optional):** If you have fresh parsley or cilantro, sprinkle some on top for added flavor and color.

5. **Serve:** Divide the salad into two bowls. It can be enjoyed immediately or chilled for 10-15 minutes for a more refreshing taste.

### Tip:
Eat as-is for a quick, healthy snack or side dish. For extra nutritional punch, serve with a slice of whole grain bread or over a bed of greens if you have them.

Enjoy your no-fuss, nourishing meal!
</output>
<reasoning>
The recipe for Garlic Lemon Chickpea Salad includes chickpeas, which are legumes. The paleo diet restricts the consumption of legumes, as they are not considered part of the diet that mimics what was presumably eaten during the Paleolithic era. Additionally, the use of canned chickpeas could be considered a processed food, which is also not aligned with the paleo dietary restriction. Therefore, the recipe does not adhere to the paleo guidelines.
</reasoning>
<answer>FAIL</answer>
</example>


## Expected output format (JSON with reasoning and Pass/Fail)
Respond in JSON:

```json
{"reasoning": "<your brief explanation>", "answer": "<Pass or Fail>"}
```