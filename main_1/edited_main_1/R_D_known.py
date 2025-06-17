import pandas as pd

# Load the CSV
df = pd.read_csv("comb_comparison.csv")

# Get 50 rows where known_ranking == True
known_ranking_df = df[df['known_ranking'] == True].head(50)

# Save to CSV
known_ranking_df.to_csv("known_ranking.csv", index=False)

# Get 25 rows where known_direction == True
known_direction_true_df = df[df['known_direction'] == True].head(25)

# Get 25 rows where known_direction == False
known_direction_false_df = df[df['known_direction'] == False].head(25)

# Combine these 50 rows into one dataframe for known_direction
known_direction_df = pd.concat([known_direction_true_df, known_direction_false_df])

# Save to CSV
known_direction_df.to_csv("known_direction.csv", index=False)
