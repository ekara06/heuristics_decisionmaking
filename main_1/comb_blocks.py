import pandas as pd
import numpy as np

# Load your original files
known_df = pd.read_csv("known_df.csv")
qwen_unknown = pd.read_csv("qwen_unknown.csv")
qwen_direction = pd.read_csv("qwen_direction.csv")

# Get the list of relevant Feature_3 names from known_df
feature_3_list = known_df["Feature_3 name"].unique()

# Get all rows from qwen_unknown and qwen_direction where Feature_3 name is in known_df
ordered_qwen_unknown = qwen_unknown[qwen_unknown["Feature 3 name"].isin(feature_3_list)]
ordered_qwen_direction = qwen_direction[qwen_direction["Feature 3 name"].isin(feature_3_list)]

# Combine both datasets (each has original 10 rows per feature)
ordered_combined = pd.concat([ordered_qwen_unknown, ordered_qwen_direction], ignore_index=True)

# Sort so all rows for the same Feature_3 name appear together
ordered_combined_sorted = ordered_combined.sort_values(by="Feature 3 name").reset_index(drop=True)

# Add initial trial_id and task_id (10 rows per task before expansion)
trials_per_task = 10
n_rows = len(ordered_combined_sorted)
n_tasks = n_rows // trials_per_task

# Generate task_id and trial_id
task_ids = np.repeat(np.arange(n_tasks), trials_per_task)
trial_ids = np.tile(np.arange(1, trials_per_task + 1), n_tasks)

# Assign to dataframe
ordered_combined_sorted["task_id"] = task_ids
ordered_combined_sorted["trial_id"] = trial_ids

# Reorder columns
final_df = ordered_combined_sorted[["trial_id", "task_id"] + 
                                   [col for col in ordered_combined_sorted.columns if col not in ["trial_id", "task_id"]]]

# Now expand: split each row into two — one for Object 1, one for Object 2
expanded_rows = []

for _, row in final_df.iterrows():
    shared = {
        "task_id": row["task_id"]
    }

    # Object 1 row
    row_obj1 = {
        **shared,
        "trial_id": None,  # will be filled later
        "Feature 1 name": row["Feature 1 name"],
        "Feature 2 name": row["Feature 2 name"],
        "Feature 3 name": row["Feature 3 name"],
        "Feature 1 value": row["Object 1 Feature 1 value"],
        "Feature 2 value": row["Object 1 Feature 2 value"],
        "Feature 3 value": row["Object 1 Feature 3 value"]
    }

    # Object 2 row
    row_obj2 = {
        **shared,
        "trial_id": None,
        "Feature 1 name": row["Feature 1 name"],
        "Feature 2 name": row["Feature 2 name"],
        "Feature 3 name": row["Feature 3 name"],
        "Feature 1 value": row["Object 2 Feature 1 value"],
        "Feature 2 value": row["Object 2 Feature 2 value"],
        "Feature 3 value": row["Object 2 Feature 3 value"]
    }

    expanded_rows.extend([row_obj1, row_obj2])

# Create DataFrame and assign new trial_ids (1 to 20 per task)
expanded_df = pd.DataFrame(expanded_rows)
expanded_df["trial_id"] = expanded_df.groupby("task_id").cumcount() + 1

# Reorder columns
final_expanded_df = expanded_df[[
    "trial_id", "task_id",
    "Feature 1 name", "Feature 1 value",
    "Feature 2 name", "Feature 2 value",
    "Feature 3 name", "Feature 3 value"
]]

# Save final expanded format
final_expanded_df.to_csv("comb_blocks.csv", index=False)
