import numpy as np
import matplotlib.pyplot as plt
from groupBMC import GroupBMC
import seaborn as sns

fig, axs = plt.subplots(2,2, figsize=(7.2, 6))

for i, condition in enumerate(['ranking', 'direction']):
    # load
    model_performances = np.load(condition + '_all.npy')
    # get performance of random guessing
    random_performance = model_performances[0, 0]

    # remove all random guessing models
    model_performances = model_performances[1:, :]

    # flatten
    flat_model_performances = model_performances.reshape(model_performances.shape[0]*model_performances.shape[1], model_performances.shape[2])

    # remove random problems
    flat_model_performances = flat_model_performances[:, flat_model_performances.min(0) < random_performance]
    print(flat_model_performances.shape)

    # average goodness-of-fit
    print(flat_model_performances.mean(-1))

    # groupBMC
    result = GroupBMC(-flat_model_performances).get_result() # TODO WE WANT TO REMOVE ALL RANDOM
    print(result.frequency_mean.reshape(model_performances.shape[0], model_performances.shape[1]))
    frequency_mean = result.frequency_mean.reshape(model_performances.shape[0], model_performances.shape[1]).sum(0)
    protected_exceedance_probability = result.protected_exceedance_probability.reshape(model_performances.shape[0], model_performances.shape[1]).sum(0)

    frequency_mean = [frequency_mean[0], frequency_mean[1], frequency_mean[2]]
    protected_exceedance_probability = [protected_exceedance_probability[0], protected_exceedance_probability[1], protected_exceedance_probability[2]]

    print(frequency_mean)
    print(protected_exceedance_probability)

    axs[0, i].bar(['no\nbinarization', 'relative\nbinarization', 'absolute\nbinarization'], frequency_mean)
    axs[1, i].bar(['no\nbinarization', 'relative\nbinarization', 'absolute\nbinarization'], protected_exceedance_probability)
    axs[0, i].set_ylabel('model frequency')
    axs[1, i].set_ylabel('protected exceedance probability')
    axs[0, i].set_ylim(0, 1)
    axs[1, i].set_ylim(0, 1)

axs[0, 0].set_title('ranking condition')
axs[0, 1].set_title('direction condition')

sns.despine()
plt.tight_layout()
plt.show()
