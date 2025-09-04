import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

files = ["/Users/elifkara/Desktop/jatos_results_data_20250826/csv_output/Processed_data/ranking_data.csv", "/Users/elifkara/Desktop/jatos_results_data_20250826/csv_output/Processed_data/direction_data.csv"]
for file in files:

    df = pd.read_csv(file)

    df["trial"] = df["optionA_trial_id"].astype(str) + "_" + df["optionB_trial_id"].astype(str)

    w1 = 1
    w2 = 2
    beta = 0.5

    all_gini = []


    for trial in df['trial'].unique():
        df_task =df[df['trial'] == trial]

        def neg_loglikelihood(x):
            y_F= x[0]*df_task["optionA_value1"]+x[1]*df_task["optionB_value1"]
            y_J= x[0]*df_task["optionA_value2"]+x[1]*df_task["optionB_value2"]
            y_difference = x[2]+(y_F - y_J)

            #sigmoid function of y_difference
            prob_F = 1/(1+np.exp(-y_difference)) 
            #print(y_difference)
            #map answer column from F to 1 and J to 0
            human_choices = np.where(df_task["button_pressed"]=="F",1,0)

            #calculate the log likelihood
            log_likelihood = np.sum(human_choices*np.log(prob_F)+(1-human_choices)*np.log(1-prob_F))
            #print(log_likelihood)
            return -log_likelihood
        
        #optimize parameters w1, w2, beta with scipy.optimize.minimize
        x0 = [w1, w2, beta]
        res = minimize(neg_loglikelihood, x0)
        w=res.x[:2]

        #compute Gini coefficient of w 
        def gini(x):
            # https://stackoverflow.com/questions/39512260/calculating-gini-coefficient-in-python-numpy
            # (Warning: This is a concise implementation, but it is O(n**2)
            # in time and memory, where n = len(x).  *Don't* pass in huge
            # samples!)
            # Mean absolute difference
            mad = np.abs(np.subtract.outer(x, x)).mean()
            # Relative mean absolute difference
            rmad = mad/np.mean(x)
            # Gini coefficient
            g = 0.5 * rmad
            return g
        
        gini_coefficient = gini(np.abs(w))
        all_gini.append(gini_coefficient)

    print(np.mean(all_gini))


    #higher single cue, lower EW - inranking gini high, in direction gini low

result = getattr(ufunc, method)(*inputs, **kwargs)
0.162045427157435