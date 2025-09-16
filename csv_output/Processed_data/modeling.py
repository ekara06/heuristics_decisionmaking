import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import math

def no_binarization(x, F1, F2, J1, J2):
    return F1, F2, J1, J2

def relative_binarization(x, F1, F2, J1, J2):
    F1 = (F1 > J1).astype(float)
    F2 = (F2 > J2).astype(float)
    J1 = (J1 > F1).astype(float)
    J2 = (J2 > F2).astype(float)
    return F1, F2, J1, J2

def absolute_binarization(x, F1, F2, J1, J2):
    F1 = (F1 > x[3]).astype(float)
    F2 = (F2 > x[4]).astype(float)
    J1 = (J1 > x[3]).astype(float)
    J2 = (J2 > x[4]).astype(float)
    return F1, F2, J1, J2

def random(x, F1, F2, J1, J2):
    return 0.5

def weighted_additive(x, F1, F2, J1, J2):

    y_F = x[0]*F1 + x[1]*F2
    y_J = x[0]*J1 + x[1]*J2
    y_difference = x[2] * (y_F - y_J)

    prob_F = 1 / (1 + np.exp(-y_difference) + 0.00001)
    
    return prob_F 

def first_cue(x, F1, F2, J1, J2):

    y_F = x[0]*F1 
    y_J = x[0]*J1
    y_difference = x[2] * (y_F - y_J)

    prob_F = 1 / (1 + np.exp(-y_difference) + 0.00001)
    
    return prob_F

def second_cue(x, F1, F2, J1, J2):

    y_F = x[0]*F2
    y_J = x[0]*J2
    y_difference = x[1] * (y_F - y_J)

    prob_F = 1 / (1 + np.exp(-y_difference) + 0.00001)
    
    return prob_F

def equal_weighting(x, F1, F2, J1, J2):

    y_F = x[0]*F1 + x[0]*F2
    y_J = x[0]*J1 + x[0]*J2
    y_difference = x[1] * (y_F - y_J)

    prob_F = 1 / (1 + np.exp(-y_difference) + 0.00001)
    
    return prob_F


files = ["../../jatos_results_data_20250826/csv_output/ranking_data.csv", "../../jatos_results_data_20250826/csv_output/direction_data.csv"]
models = [random, weighted_additive, equal_weighting, first_cue, second_cue]
binarization_strategies = [no_binarization, relative_binarization, absolute_binarization] 
num_parameters = [0, 3, 2, 2, 2]

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

                def negative_loglikelihood(x):
                    # normalization
                    F1 = 2 * ((df_task['optionA_value1'] - df_task['optionA_value1'].min()) / (df_task['optionA_value1'].max() - df_task['optionA_value1'].min())) - 1 
                    F2 = 2 * ((df_task['optionA_value2'] - df_task['optionA_value2'].min()) / (df_task['optionA_value2'].max() - df_task['optionA_value2'].min())) - 1 
                    J1 = 2 * ((df_task['optionB_value1'] - df_task['optionB_value1'].min()) / (df_task['optionB_value1'].max() - df_task['optionB_value1'].min())) - 1 
                    J2 = 2 * ((df_task['optionB_value2'] - df_task['optionB_value2'].min()) / (df_task['optionB_value2'].max() - df_task['optionB_value2'].min())) - 1

                    # binarization
                    F1, F2, J1, J2 = binarization_strategy(x, F1, F2, J1, J2)

                    # model
                    prob_F = model(x, F1, F2, J1, J2)
                    prob_F = np.clip(prob_F, 0.00001, 1-0.00001)

                    # log likelihood
                    human_choices = np.where(df_task["button_pressed"] == "F", 1, 0)
                    log_likelihood = np.sum(human_choices * np.log(prob_F) + (1 - human_choices) * np.log(1 - prob_F))
                    return -log_likelihood

                # fit model
                res = minimize(negative_loglikelihood, [1, 1, 1, 0, 0])
                # add goodness-of-fit to list
                bonus_parameters = 0
                if binarization_strategy_index == 2:
                    if model_index >= 3:
                        bonus_parameters += 1
                    else:
                        bonus_parameters += 2
                        
                model_performances[model_index, binarization_strategy_index, task_index] = (num_parameters[model_index] + bonus_parameters) * math.log(len(df_task)) + 2 * res.fun 
                task_index = task_index + 1

# average goodness-of-fit
print(model_performances.mean(-1))
# count how often each model wins
# TODO MAKE THIS WORK WITH 3D array
#mins = np.argmin(model_performances, axis=-1)
#counts = np.bincount(mins, minlength=model_performances.shape[-1])
#print("Counts:", counts)

winning_models = np.zeros(len(models))
winning_binarization_strategies = np.zeros(len(binarization_strategies))
          
for task_index in range(model_performances.shape[-1]):
    row, col = np.unravel_index(model_performances[:, :, task_index].argmin(), model_performances[:, :, task_index].shape)
    winning_models[row] += 1
    winning_binarization_strategies[col] += 1
    print(row, col)

print(winning_models)
print(winning_binarization_strategies)