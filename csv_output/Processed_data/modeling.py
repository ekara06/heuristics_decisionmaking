import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import math

def no_binarization(x):
    return XXXX

def relative_binarization(x):
    return XXXX

def absolute_binarization(x):
    return XXXX

def random(x):
    prob_F = 0.5
    
    human_choices = np.where(df_task["button_pressed"] == "F", 1, 0)

    log_likelihood = np.sum(human_choices * np.log(prob_F) + (1 - human_choices) * np.log(1 - prob_F))

    return -log_likelihood

def weighted_additive(x):
    F1, F2, J1, J2 = binarization_strategy(x)

    y_F = x[0]*F1 + x[1]*F2
    y_J = x[0]*J1 + x[1]*J2
    y_difference = x[2] * (y_F - y_J)

    prob_F = 1 / (1 + np.exp(-y_difference) + 0.00001)
    prob_F = np.clip(prob_F, 0.00001, 1-0.00001)
    
    human_choices = np.where(df_task["button_pressed"] == "F", 1, 0)

    log_likelihood = np.sum(human_choices * np.log(prob_F) + (1 - human_choices) * np.log(1 - prob_F))

    return -log_likelihood

def first_cue(x):
    F1, F2, J1, J2 = binarization_strategy(x)

    y_F = x[0]*F1 
    y_J = x[0]*J1
    y_difference = x[2] * (y_F - y_J)

    prob_F = 1 / (1 + np.exp(-y_difference) + 0.00001)
    prob_F = np.clip(prob_F, 0.00001, 1-0.00001)
    
    human_choices = np.where(df_task["button_pressed"] == "F", 1, 0)

    log_likelihood = np.sum(human_choices * np.log(prob_F) + (1 - human_choices) * np.log(1 - prob_F))

    return -log_likelihood

def second_cue(x):
    F1, F2, J1, J2 = binarization_strategy(x)

    y_F = x[0]*F2
    y_J = x[0]*J2
    y_difference = x[1] * (y_F - y_J)

    prob_F = 1 / (1 + np.exp(-y_difference) + 0.00001)
    prob_F = np.clip(prob_F, 0.00001, 1-0.00001)
    
    human_choices = np.where(df_task["button_pressed"] == "F", 1, 0)

    log_likelihood = np.sum(human_choices * np.log(prob_F) + (1 - human_choices) * np.log(1 - prob_F))

    return -log_likelihood

def equal_weighting(x):
    F1, F2, J1, J2 = binarization_strategy(x)

    y_F = x[0]*F1 + x[0]*F2
    y_J = x[0]*J1 + x[0]*J2
    y_difference = x[1] * (y_F - y_J)

    prob_F = 1 / (1 + np.exp(-y_difference) + 0.00001)
    prob_F = np.clip(prob_F, 0.00001, 1-0.00001)
    
    human_choices = np.where(df_task["button_pressed"] == "F", 1, 0)

    log_likelihood = np.sum(human_choices * np.log(prob_F) + (1 - human_choices) * np.log(1 - prob_F))

    return -log_likelihood


files = ["../../jatos_results_data_20250826/csv_output/ranking_data.csv", "../../jatos_results_data_20250826/csv_output/direction_data.csv"]
models = [weighted_additive, equal_weighting, first_cue, second_cue, random]
binarization_strategies = [no_binarization, relative_binarization, absolute_binarization] 
num_parameters = [3, 2, 2, 2, 0]

model_performances = np.zeros((len(models), len(binarization_strategies), 121+178))

for model_index, model in enumerate(models):
    for binarization_strategy_index, binarization_strategy in enumerate(binarization_strategies):
        task_index = 0
        for file in files:
            df = pd.read_csv(file)
            df["task"] = df["optionA_task_id"].astype(str) + "_" + df["optionB_task_id"].astype(str)
        
            # optional binarization:
            df['F1'] = df['optionA_value1'].astype(float)
            df['F2'] = df['optionA_value2'].astype(float)
            df['J1'] = df['optionB_value1'].astype(float)
            df['J2'] = df['optionB_value2'].astype(float)
        
            # iterate over every question
            for task in df['task'].unique():
                df_task = df[df['task'] == task]
                # normalization
                F1 = (df_task['F1'] - df_task['F1'].min()) / (df_task['F1'].max() - df_task['F1'].min())
                F2 = (df_task['F2'] - df_task['F2'].min()) / (df_task['F2'].max() - df_task['F2'].min())
                J1 = (df_task['J1'] - df_task['J1'].min()) / (df_task['J1'].max() - df_task['J1'].min())
                J2 = (df_task['J2'] - df_task['J2'].min()) / (df_task['J2'].max() - df_task['J2'].min())

                # fit model
                res = minimize(model, [1, 1, 1])
                # add goodness-of-fit to list
                model_performances[model_index, binarization_strategy_index, task_index] = num_parameters[model_index] * math.log(len(df_task)) + 2 * res.fun 
                task_index = task_index + 1

# average goodness-of-fit
print(model_performances.mean(-1))
# count how often each model wins
# TODO MAKE THIS WORK WITH 3D array
mins = np.argmin(model_performances, axis=-1)
counts = np.bincount(mins, minlength=model_performances.shape[-1])
print("Counts:", counts)

          