import pandas as pd

# Load the CSV
df = pd.read_csv("comb_comparison.csv")

#Get 50 rows where known_ranking == True
known_ranking_df = df[df['known_ranking'] == True].head(50)

#Get 25 rows where known_direction == True
known_direction_df = df[df['known_direction'] == True].head(25)

#Get 25 rows where known_direction == False
known_direction_false_df = df[df['known_direction'] == False].head(25)

#combine these 100 rows into a new dataframe
known_df = pd.concat([known_ranking_df, known_direction_df, known_direction_false_df])

#save the new dataframe to a new csv file
known_df.to_csv("known_df.csv", index=False)


