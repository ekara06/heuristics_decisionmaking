import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt


df = pd.read_csv("chatgpt_ranking_problems.csv")
df_ranking = pd.read_csv("main_centaur_chatgpt_ranking.csv")
print(df)

#loop over task_id and select the rows with the same task_id
w1 = 1
w2 = 2
beta = 0.5

all_gini=[]
all_neg_entropy=[]

for participant in df_ranking['participant'].unique():
    df_task =df[df['trial'] == participant]
    print(len(df_task))

    df_ranking_task =df_ranking[df_ranking['trial'] == trial]

    def neg_loglikelihood(x):
        y_F= x[0]*df_task["feature1_value_F"]+x[1]*df_task["feature2_value_F"]
        y_J= x[0]*df_task["feature1_value_J"]+x[1]*df_task["feature2_value_J"]
        y_difference = x[2]+(y_F - y_J)

        #sigmoid function of y_difference
        prob_F = 1/(1+np.exp(-y_difference)) 
        #print(y_difference)
        #map answer column from F to 1 and J to 0
        human_choices = np.where(df_task["answer"]=="F",1,0)

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
    all_neg_entropy.append(df_ranking_task["neg_entropy"].item())

print(all_gini)
print(all_neg_entropy)
plt.scatter(all_neg_entropy, all_gini)
plt.ylabel("Gini coefficient")
plt.xlabel("Negative entropy")
plt.show()
