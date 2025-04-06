import pandas as pd
import itertools
import math

# Read dataset from the specified Windows path
df = pd.read_csv(level3_data.csv)

# Standardize column names: remove extra spaces, lowercase, replace spaces with underscores
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Expected columns: weight, height, grip_strength, speed
# Drop participants missing weight or height (needed for BMI calculation)
df = df.dropna(subset=["weight", "height"])

# Calculate BMI = weight / (height^2)
df["bmi"] = df["weight"] / (df["height"] ** 2)

# Filter based on BMI and grip strength criteria:
df_filtered = df[(df["bmi"] >= 18) & (df["bmi"] <= 30) & (df["grip_strength"] >= 30)]

# If no one remains after filtering, raise an error.
if df_filtered.empty:
    raise ValueError("No participants remain after filtering by BMI and grip strength.")

# For ease of partitioning, work with the filtered DataFrame's index
indices = list(df_filtered.index)
n = len(indices)

# Create dictionaries for quick lookup of the needed metrics
weights = df_filtered["weight"].to_dict()          # participant weight
grips = df_filtered["grip_strength"].to_dict()       # participant grip strength
speeds = df_filtered["speed"].to_dict()              # participant speed

# - Team total weights must be within 5% of each other.
#    max(team_A_weight, team_B_weight) <= 1.05 * min(team_A_weight, team_B_weight))
# - Among valid splits, we choose the one minimizing the difference in average grip strength.
#   If there is a tie, we choose the one with the smallest difference in average speed.
best_partition = None
best_grip_diff = float('inf')
best_speed_diff = float('inf')

# To avoid double-counting mirror splits, force the first participant into team A.
for r in range(0, len(indices) - 1):
    for subset in itertools.combinations(indices[1:], r):
        team_A = set((indices[0],) + subset)
        team_B = set(indices) - team_A

        # Skip if team_B is empty (both teams must have at least one participant)
        if not team_B:
            continue

        # Compute total weights for each team
        weight_A = sum(weights[i] for i in team_A)
        weight_B = sum(weights[i] for i in team_B)

        # Check the 5% weight balance condition:
        if min(weight_A, weight_B) == 0:
            continue
        if max(weight_A, weight_B) > 1.05 * min(weight_A, weight_B):
            continue

        # Compute average grip strength for each team
        grip_A = sum(grips[i] for i in team_A) / len(team_A)
        grip_B = sum(grips[i] for i in team_B) / len(team_B)
        grip_diff = abs(grip_A - grip_B)

        # Compute average speed for each team
        speed_A = sum(speeds[i] for i in team_A) / len(team_A)
        speed_B = sum(speeds[i] for i in team_B) / len(team_B)
        speed_diff = abs(speed_A - speed_B)

        # Update best partition based on grip strength balance, then average speed balance
        if (grip_diff < best_grip_diff) or (math.isclose(grip_diff, best_grip_diff, rel_tol=1e-9) and speed_diff < best_speed_diff):
            best_partition = (team_A, team_B)
            best_grip_diff = grip_diff
            best_speed_diff = speed_diff

# If no valid partition is found, raise an error.
if best_partition is None:
    raise ValueError("No valid partition found that meets the weight difference criteria.")

# Assign team labels based on the best partition found.
# Here, best_partition[0] will be labeled as Team "A" and best_partition[1] as Team "B".
df_filtered["Team"] = df_filtered.index.map(lambda x: "A" if x in best_partition[0] else "B")

# Output the final assignment to a CSV file in the same directory
output_path = final_teams.csv
df_filtered.to_csv(output_path, index=False)
print(f"Final team assignments saved to {output_path}")
