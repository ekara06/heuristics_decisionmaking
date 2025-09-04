import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

files = ["/Users/elifkara/Desktop/jatos_results_data_20250826/csv_output/Processed_data/ranking_data.csv", "/Users/elifkara/Desktop/jatos_results_data_20250826/csv_output/Processed_data/direction_data.csv"]
all_ginis = []
labels = []

for file in files:
    df = pd.read_csv(file)
    df["trial"] = df["optionA_trial_id"].astype(str) + "_" + df["optionB_trial_id"].astype(str)

    # Vectorized binary comparison
    df['feature1_value_F_bin'] = (df['optionA_value1'] > df['optionA_value2']).astype(float)
    df['feature2_value_F_bin'] = (df['optionB_value1'] > df['optionB_value2']).astype(float)

    # Assuming 'J_bin' should be 0 when 'F > J', and 1 otherwise:
    df['feature1_value_J_bin'] = (df['optionA_value1'] <= df['optionA_value2']).astype(float)
    df['feature2_value_J_bin'] = (df['optionB_value1'] <= df['optionB_value2']).astype(float)

    w1 = 1
    w2 = 1
    beta = 1

    file_ginis = []

    for trial in df['trial'].unique():
        df_task = df[df['trial'] == trial]

        def neg_loglikelihood(x):
            y_F = x[0]*df_task["feature1_value_F_bin"] + x[1]*df_task["feature2_value_F_bin"]
            y_J = x[0]*df_task["feature1_value_J_bin"] + x[1]*df_task["feature2_value_J_bin"]
            y_difference = x[2] + (y_F - y_J)

            prob_F = 1 / (1 + np.exp(-y_difference))
            human_choices = np.where(df_task["button_pressed"] == "F", 1, 0)

            log_likelihood = np.sum(human_choices * np.log(prob_F) + (1 - human_choices) * np.log(1 - prob_F))
            return -log_likelihood

        x0 = [w1, w2, beta]
        res = minimize(neg_loglikelihood, x0)
        w = res.x[:2]

        def gini(x):
            mad = np.abs(np.subtract.outer(x, x)).mean()
            rmad = mad / np.mean(x)
            g = 0.5 * rmad
            return g

        gini_coefficient = gini(np.abs(w))
        file_ginis.append(gini_coefficient)

    all_ginis.append(file_ginis)

    # label 
    if "ranking" in file:
        labels.append("ranking")
    elif "direction" in file:
        labels.append("direction")

# Box plot
plt.boxplot(all_ginis, labels=labels, showmeans=True)
plt.ylabel("Gini coefficient")
plt.title("Gini by condition")
plt.show()
