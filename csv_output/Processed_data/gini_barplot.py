import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import math

files = ["../../jatos_results_data_20250826/csv_output/ranking_data.csv", "../../jatos_results_data_20250826/csv_output/direction_data.csv"]
all_ginis = []
labels = []

for file in files:
    df = pd.read_csv(file)
    df["task"] = df["optionA_task_id"].astype(str) + "_" + df["optionB_task_id"].astype(str)

    
    # Model 2: binarize based on relatives values
    df['feature1_value_F_bin'] = (df['optionA_value1'] > df['optionB_value1']).astype(float)
    df['feature2_value_F_bin'] = (df['optionA_value2'] > df['optionB_value2']).astype(float)

    # Assuming 'J_bin' should be 0 when 'F > J', and 1 otherwise:
    df['feature1_value_J_bin'] = (df['optionA_value1'] <= df['optionB_value1']).astype(float)
    df['feature2_value_J_bin'] = (df['optionA_value2'] <= df['optionB_value2']).astype(float)
    '''
    
    # Model 3: don't binarize
    df['feature1_value_F_bin'] = df['optionA_value1'].astype(float)
    df['feature2_value_F_bin'] = df['optionA_value2'].astype(float)

    # Assuming 'J_bin' should be 0 when 'F > J', and 1 otherwise:
    df['feature1_value_J_bin'] = df['optionB_value1'].astype(float)
    df['feature2_value_J_bin'] = df['optionB_value2'].astype(float)
    

    # Model 4: binarize based on median
    df['feature1_value_F_bin'] = (df['optionA_value1'] > df['optionA_value1'].median()).astype(float)
    df['feature2_value_F_bin'] = (df['optionA_value2'] > df['optionA_value2'].median()).astype(float)

    # Assuming 'J_bin' should be 0 when 'F > J', and 1 otherwise:
    df['feature1_value_J_bin'] = (df['optionB_value1'] > df['optionB_value1'].median()).astype(float)
    df['feature2_value_J_bin'] = (df['optionB_value2'] > df['optionB_value2'].median()).astype(float)
    '''


    w1 = 1
    w2 = 1
    beta = 1

    file_ginis = []

    print(df['task'].unique())
    print(len(df['task'].unique()))
    for task in df['task'].unique():
        df_task = df[df['task'] == task]

        def neg_loglikelihood(x):
            y_F = x[0]*df_task["feature1_value_F_bin"] + x[1]*df_task["feature2_value_F_bin"]
            y_J = x[0]*df_task["feature1_value_J_bin"] + x[1]*df_task["feature2_value_J_bin"]
            y_difference = x[2] * (y_F - y_J)

            prob_F = 1 / (1 + np.exp(-y_difference) + 0.00001)
            human_choices = np.where(df_task["button_pressed"] == "F", 1, 0)

            log_likelihood = np.sum(human_choices * np.log(prob_F) + (1 - human_choices) * np.log(1 - prob_F))
            return -log_likelihood

        x0 = [w1, w2, beta]
        res = minimize(neg_loglikelihood, x0)
        print(len(df_task))
        print(-len(df_task) * math.log(0.5))
        print(res.fun)
        print(res.x)
   
        print()

        if res.success:
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

# Average Ginis per condition
mean_ginis = [np.mean(ginis) for ginis in all_ginis]

# Bar plot
plt.bar(labels, mean_ginis)
plt.ylabel("Mean Gini coefficient")
plt.title("Gini by condition")
plt.show()

