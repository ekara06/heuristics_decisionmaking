import pandas as pd
import numpy as np

# Load both CSV files into different variables
df_ranking = pd.read_csv("new_new_qwen_ranking.csv")
df_direction = pd.read_csv("new_new_qwen_direction.csv")

# Function to convert one row into two reshaped rows
def reshape_row(row):
    feature_1 = row['Feature 1 name']
    feature_2 = row['Feature 2 name']
    target_name = row['Feature 3 name']
    
    object_1 = {
        'Feature 1 name': feature_1,
        'Feature 1 value': row['Object 1 Feature 1 value'],
        'Feature 2 name': feature_2,
        'Feature 2 value': row['Object 1 Feature 2 value'],
        'Target name': target_name,
        'Target value': row['Object 1 Feature 3 value']
    }
    
    object_2 = {
        'Feature 1 name': feature_1,
        'Feature 1 value': row['Object 2 Feature 1 value'],
        'Feature 2 name': feature_2,
        'Feature 2 value': row['Object 2 Feature 2 value'],
        'Target name': target_name,
        'Target value': row['Object 2 Feature 3 value']
    }
    
    return pd.DataFrame([object_1, object_2])

# Apply transformation separately to each file
reshaped_ranking = pd.concat([reshape_row(row) for _, row in df_ranking.iterrows()], ignore_index=True)
reshaped_direction = pd.concat([reshape_row(row) for _, row in df_direction.iterrows()], ignore_index=True)

# Save results
reshaped_ranking.to_csv("ranking_output.csv", index=False)
reshaped_direction.to_csv("direction_output.csv", index=False)

import pandas as pd
import numpy as np

### STEP 1 — CORRELATION ANALYSIS ###
# Load your input data
df_direction = pd.read_csv("new_new_qwen_direction.csv")
df_direction['condition'] = 'direction'

df_ranking = pd.read_csv("new_new_qwen_ranking.csv")
df_ranking['condition'] = 'ranking'

cols_to_convert = [
    'Object 1 Feature 1 value', 'Object 1 Feature 2 value', 'Object 1 Feature 3 value',
    'Object 2 Feature 1 value', 'Object 2 Feature 2 value', 'Object 2 Feature 3 value'
]

for col in cols_to_convert:
    df_direction[col] = pd.to_numeric(df_direction[col], errors='coerce')
    df_ranking[col] = pd.to_numeric(df_ranking[col], errors='coerce')
 
# Combine both
df = pd.concat([df_direction, df_ranking], ignore_index=True)

# Run correlations per unique (feature1, feature2, feature3) triplet
results = []
for feature1, feature2, feature3, condition in df[['Feature 1 name', 'Feature 2 name', 'Feature 3 name', 'condition']].drop_duplicates().itertuples(index=False):
    subset = df[
        (df['Feature 1 name'] == feature1) &
        (df['Feature 2 name'] == feature2) &
        (df['Feature 3 name'] == feature3) &
        (df['condition'] == condition)
    ]

    if len(subset) == 10:
        combined_feature1 = np.concatenate([subset['Object 1 Feature 1 value'], subset['Object 2 Feature 1 value']])
        combined_feature2 = np.concatenate([subset['Object 1 Feature 2 value'], subset['Object 2 Feature 2 value']])
        combined_feature3 = np.concatenate([subset['Object 1 Feature 3 value'], subset['Object 2 Feature 3 value']])

        corr_1_3 = np.corrcoef(combined_feature1, combined_feature3)[0, 1]
        corr_2_3 = np.corrcoef(combined_feature2, combined_feature3)[0, 1]

        results.append({
            'Feature_3 name': feature3,
            'Feature_1 name': feature1,
            'Feature_2 name': feature2,
            'condition': condition,
            'corr_1_3': corr_1_3,
            'corr_2_3': corr_2_3
        })

result_df = pd.DataFrame(results).round(2)
result_df.to_csv("new_combined_correlations.csv", index=False)

### STEP 2 — ANNOTATE WITH KNOWN RANKING/DIRECTION ###
df = result_df.copy()
df["known_ranking"] = df["corr_1_3"].abs() > df["corr_2_3"].abs()
df["known_direction"] = (df["corr_1_3"] > 0) & (df["corr_2_3"] > 0)

df.to_csv("comb_comparison.csv", index=False)

### STEP 3 — EXTRACT 50 + 50 KNOWN TRIALS ###
#known_ranking_df = df[(df["known_ranking"]) & (~df["known_direction"])].head(50)
#known_direction_df = df[(~df["known_ranking"]) & (df["known_direction"])].head(50)

known_ranking_df = df[(df["condition"] == "ranking") & (df["known_ranking"]) & (~df["known_direction"])]
known_direction_df = df[(df["condition"] == "direction") & (~df["known_ranking"]) & (df["known_direction"])]

known_ranking_df.to_csv("new_new_known_ranking.csv", index=False)
known_direction_df.to_csv("new_new_known_direction.csv", index=False)


# DATA EXPANSION WITH TRIAL/TASK IDs
df_known_direction = pd.read_csv("new_new_known_direction.csv")
df_direction_output = pd.read_csv("direction_output.csv")

df_known_ranking = pd.read_csv("new_new_known_ranking.csv")
df_ranking_output = pd.read_csv("ranking_output.csv")

merged_direction_df = df_direction_output.merge(
    df_known_direction,
    left_on=["Target name", "Feature 1 name", "Feature 2 name"],
    right_on=["Feature_3 name", "Feature_1 name", "Feature_2 name"],
    how="inner"
)

merged_ranking_df = df_ranking_output.merge(
    df_known_ranking,
    left_on=["Target name", "Feature 1 name", "Feature 2 name"],
    right_on=["Feature_3 name", "Feature_1 name", "Feature_2 name"],
    how="inner"
)

### ASSIGN trial_id and task_id FUNCTION ###
def assign_ids(df):
    # Identify unique task groups by triplets
    triplets = df[['Feature 1 name', 'Feature 2 name', 'Target name']].drop_duplicates().reset_index(drop=True)
    triplets['task_id'] = triplets.index + 1

    # Merge task_id back into the main DataFrame
    df = df.merge(triplets, on=['Feature 1 name', 'Feature 2 name', 'Target name'], how='left')

    # Assign trial_id from 1 to 20 within each task_id group
    df['trial_id'] = df.groupby('task_id').cumcount() + 1
    return df

merged_direction_df = assign_ids(merged_direction_df)
merged_ranking_df = assign_ids(merged_ranking_df)

merged_direction_df.to_csv("final_extended_known_direction.csv", index=False)
merged_ranking_df.to_csv("final_extended_known_ranking.csv", index=False)

#JSON file 
import json

def df_to_json(df):
    return {
        "features": [
            {
                "trial_id": str(row["trial_id"]),
                "task_id": str(row["task_id"]),
                "values": f"{row['Feature 1 value']}, {row['Feature 2 value']}",
                "options": [row["Feature 1 name"], row["Feature 2 name"]],
                "target": row["Target name"]
            }
            for _, row in df.iterrows()
        ]
    }

# Convert to JSON
json_direction = df_to_json(merged_direction_df)
json_ranking = df_to_json(merged_ranking_df)

# Save
with open("final_known_direction.json", "w") as f:
    json.dump(json_direction, f, indent=2)

with open("final_known_ranking.json", "w") as f:
    json.dump(json_ranking, f, indent=2)

