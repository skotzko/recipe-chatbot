#!/usr/bin/env python3
"""Generate diverse 3-tuple combinations for recipe queries."""

import random
import csv
from itertools import combinations, product

# Define dimensions
dimensions = {
    'dietary_restriction': ['gluten free', 'dairy free', 'keto', 'low carb', 'vegetarian', 'vegan', 'pescatarian'],
    'dish_type': ['appetizer', 'main', 'dessert', 'side', 'salad'],
    'time_available': ['15 min', '30 min', '45 min', '1 hour', '2 hour', '>2 hours'],
    'number_of_people': ['1', '2', '3', '4', '6', '8'],
    'number_of_dishes': ['1', '2', '3', '4', '5'],
    'meal': ['breakfast', 'lunch', 'dinner', 'snack'],
    'equipment_available': ['microwave only', 'stove only', 'stove and oven', 'no microwave', 'sous vide', 'air fryer']
}

# Define common dimension groupings that make sense together
dimension_groups = [
    ['dietary_restriction', 'dish_type', 'time_available'],
    ['dietary_restriction', 'meal', 'number_of_people'],
    ['dish_type', 'time_available', 'equipment_available'],
    ['meal', 'number_of_people', 'dietary_restriction'],
    ['dish_type', 'number_of_people', 'time_available'],
    ['dietary_restriction', 'equipment_available', 'time_available'],
    ['meal', 'dish_type', 'number_of_people'],
    ['number_of_dishes', 'meal', 'number_of_people'],
    ['dietary_restriction', 'dish_type', 'equipment_available'],
    ['meal', 'time_available', 'equipment_available'],
    ['dish_type', 'meal', 'time_available'],
    ['number_of_dishes', 'dietary_restriction', 'meal'],
    ['equipment_available', 'number_of_people', 'meal'],
]

def generate_combinations(target_count=50):
    """Generate diverse 3-tuple combinations (values only)."""
    value_tuples = []
    seen = set()

    # Generate combinations from each dimension group
    for group in dimension_groups:
        # Get all possible value combinations for this dimension group
        values = [dimensions[dim] for dim in group]
        all_combos = list(product(*values))

        # Sample some combinations from this group
        sample_size = min(target_count // len(dimension_groups) + 2, len(all_combos))
        sampled = random.sample(all_combos, sample_size)

        for value_tuple in sampled:
            if value_tuple not in seen:
                seen.add(value_tuple)
                value_tuples.append({
                    'dimensions': group,
                    'values': value_tuple
                })

    # Shuffle and trim to target count
    random.shuffle(value_tuples)
    return value_tuples[:target_count]

def format_output(combinations):
    """Format combinations as readable output."""
    output = []
    for i, combo in enumerate(combinations, 1):
        # Format as just the value tuple
        value_str = str(combo['values'])
        output.append(f"{i}. {value_str}")
    return '\n'.join(output)

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    combos = generate_combinations(50)
    print(format_output(combos))

    # Also save as CSV
    output_file = "/Users/andrew/projects/recipe-chatbot/query_combinations.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['combination_id', 'value1', 'value2', 'value3', 'dim1_name', 'dim2_name', 'dim3_name'])

        for i, combo in enumerate(combos, 1):
            row = [i]
            row.extend(combo['values'])  # Add the three values
            row.extend(combo['dimensions'])  # Add dimension names for reference
            writer.writerow(row)

    print(f"\n✓ Saved to {output_file}")
