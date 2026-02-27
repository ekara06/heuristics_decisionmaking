import numpy as np
import matplotlib.pyplot as plt
from groupBMC import GroupBMC
import seaborn as sns

fig, axs = plt.subplots(2,2, figsize=(7.2, 6))

for i, condition in enumerate(['ranking', 'direction']):
    # load
    model_performances = np.load(condition + '_all.npy')
    model_performances = model_performances[:, 0, :]

    # remove random problems
    model_performances = model_performances[:, model_performances.argmin(0) != 0]
    print(model_performances.shape)

    # average goodness-of-fit
    print(model_performances.mean(-1))

    # groupBMC
    result = GroupBMC(-model_performances[1:]).get_result()
    frequency_mean = [result.frequency_mean[0], result.frequency_mean[1], result.frequency_mean[2] + result.frequency_mean[3]]
    frequency_var = [result.frequency_var[0], result.frequency_var[1], result.frequency_var[2] + result.frequency_var[3]]
    protected_exceedance_probability = [result.protected_exceedance_probability[0], result.protected_exceedance_probability[1], result.protected_exceedance_probability[2] + result.protected_exceedance_probability[3]]
    
    

    print(frequency_mean)
    print(protected_exceedance_probability)

    axs[0, i].bar(['weighted\nadditive', 'equal\nweighting', 'single\ncue'], frequency_mean, yerr=np.sqrt(frequency_var))
    axs[1, i].bar(['weighted\nadditive', 'equal\nweighting', 'single\ncue'], protected_exceedance_probability)
    axs[0, i].set_ylabel('model frequency')
    axs[1, i].set_ylabel('protected exceedance probability')
    axs[0, i].set_ylim(0, 1)
    axs[1, i].set_ylim(0, 1)

axs[0, 0].set_title('ranking condition')
axs[0, 1].set_title('direction condition')

sns.despine()
plt.tight_layout()
plt.show()
