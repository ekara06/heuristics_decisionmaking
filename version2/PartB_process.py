import pandas as pd
import json

# --- STEP 1: Load data ---
df_ranking_A = pd.read_csv("ranking_B.csv", sep=";")
df_direction_A = pd.read_csv("direction_B.csv", sep=";")

df_ranking_master = pd.read_csv("ranking_output.csv", sep=";")
df_direction_master = pd.read_csv("direction_output.csv", sep=";")

print("Files loaded successfully.")

# --- STEP 2: Identify the 100 target names + feature pairs ---
ranking_keys = df_ranking_A[["Feature_3 name", "Feature 1 name", "Feature 2 name"]].drop_duplicates()
direction_keys = df_direction_A[["Feature_3 name", "Feature 1 name", "Feature 2 name"]].drop_duplicates()

print(f"Ranking: {ranking_keys['Feature_3 name'].nunique()} targets")
print(f"Direction: {direction_keys['Feature_3 name'].nunique()} targets")

# --- STEP 3: Expand back, matching target name + feature pairs ---
expanded_ranking = df_ranking_master.merge(
    ranking_keys,
    left_on=["Target name", "Feature 1 name", "Feature 2 name"],
    right_on=["Feature_3 name", "Feature 1 name", "Feature 2 name"],
    how="inner"
)

expanded_direction = df_direction_master.merge(
    direction_keys,
    left_on=["Target name", "Feature 1 name", "Feature 2 name"],
    right_on=["Feature_3 name", "Feature 1 name", "Feature 2 name"],
    how="inner"
)

# drop the duplicate key col
expanded_ranking = expanded_ranking.drop(columns=["Feature_3 name"])
expanded_direction = expanded_direction.drop(columns=["Feature_3 name"])

# --- STEP 3b: Check for missing matches ---
missing_ranking = ranking_keys.merge(
    df_ranking_master,
    left_on=["Feature_3 name", "Feature 1 name", "Feature 2 name"],
    right_on=["Target name", "Feature 1 name", "Feature 2 name"],
    how="left",
    indicator=True
).query("_merge == 'left_only'")

missing_direction = direction_keys.merge(
    df_direction_master,
    left_on=["Feature_3 name", "Feature 1 name", "Feature 2 name"],
    right_on=["Target name", "Feature 1 name", "Feature 2 name"],
    how="left",
    indicator=True
).query("_merge == 'left_only'")

if not missing_ranking.empty:
    print("\n⚠️ Warning: Some Ranking targets were not found in master:")
    print(missing_ranking[["Feature_3 name", "Feature 1 name", "Feature 2 name"]])

if not missing_direction.empty:
    print("\n⚠️ Warning: Some Direction targets were not found in master:")
    print(missing_direction[["Feature_3 name", "Feature 1 name", "Feature 2 name"]])

# --- STEP 4: Assign IDs (starting from 51) ---
def assign_ids(df, start_id=51):
    targets = df["Target name"].drop_duplicates().reset_index(drop=True)
    target_map = {t: i+start_id for i, t in enumerate(targets)}
    df["task_id"] = df["Target name"].map(target_map)
    df["trial_id"] = df.groupby("task_id").cumcount() + 1
    return df

expanded_ranking = assign_ids(expanded_ranking, start_id=51)
expanded_direction = assign_ids(expanded_direction, start_id=51)

# --- STEP 5: Save CSV ---
expanded_ranking.to_csv("Extended_ranking_B.csv", index=False)
expanded_direction.to_csv("Extended_direction_B.csv", index=False)

# --- STEP 6: JSON export ---
def df_to_json(df):
    return {
        "features": [
            {
                "trial_id": str(row["trial_id"]),
                "task_id": str(row["task_id"]),
                "values": f"{row['Feature 1 value']}, {row['Feature 2 value']}",
                "target_value": row["Target value"],
                "options": [row["Feature 1 name"], row["Feature 2 name"]],
                "target": row["Target name"],
            }
            for _, row in df.iterrows()
        ]
    }

with open("final_ranking_B.json", "w") as f:
    json.dump(df_to_json(expanded_ranking), f, indent=2)

with open("final_direction_B.json", "w") as f:
    json.dump(df_to_json(expanded_direction), f, indent=2)

print("🎉 Expansion complete! CSV + JSON files created.")
