import pandas as pd

# Load the CSV
df = pd.read_csv("comb_comparison.csv")

# Get 50 rows where known_ranking == True
#known1_ranking_df = df[(df['known_ranking'] == True)& (df['known_direction'] == True)].head(25)
known2_ranking_df = df[(df['known_ranking'] == True)& (df['known_direction'] == False)].head(50)

# Save to CSV (concate)
#known_ranking_df = pd.concat([known1_ranking_df, known2_ranking_df])
known2_ranking_df.to_csv("known_ranking.csv", index=False)

# Get 50 rows where known_direction == True
#known1_direction_df = df[(df['known_ranking'] == True)& (df['known_direction'] == True)].head(25)
known2_direction_df = df[(df['known_ranking'] == False)& (df['known_direction'] == True)].head(50)

# Combine these 50 rows into one dataframe for known_direction (concate)
#known_direction_df = pd.concat([known1_direction_df, known2_direction_df])

# Save to CSV
known2_direction_df.to_csv("known_direction.csv", index=False)
