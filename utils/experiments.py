import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
from warnings import filterwarnings
filterwarnings("ignore")

from ants.model import AntWorld

def run_experiment(steps=500, runs=5, params={}):
    """
    Runs multiple simulations of the AntWorld model and collects data on emergent properties.
    """
    results = {
        "ants": [],
        "predators": [],
        "food_collected": [],
        "entropy": []
    }
    
    
    for run in tqdm(range(runs)):
        model = AntWorld(**params)  # Initialize model with given parameters
        ants_over_time = []
        predators_over_time = []
        food_over_time = []
        entropy_over_time = []
        
        for step in tqdm(range(steps)):
            model.step()
            data = model.datacollector.get_model_vars_dataframe().iloc[-1]  # Get last recorded step
            
            ants_over_time.append(data['Ants 🐜'])
            predators_over_time.append(data['Predators'])
            food_over_time.append(data['Home 🏠'])  # Amount of food collected
            entropy_over_time.append(data['entropy_log'][-1] if len(data['entropy_log']) > 0 else None)

            if not model.running:
                break
        
        results["ants"].append(ants_over_time)
        results["predators"].append(predators_over_time)
        results["food_collected"].append(food_over_time)
        results["entropy"].append(entropy_over_time)

    return results


def plot_results(results, steps=500):
    """
    Plots the collected data from multiple runs.
    """
    time = np.arange(steps)

    # print(results)
    def plot_metric(metric, ylabel, title, color):
        mean_values = np.mean(results[metric], axis=0)
        std_values = np.std(results[metric], axis=0)
        plt.figure(figsize=(8, 4))
        plt.fill_between(time, mean_values - std_values, mean_values + std_values, alpha=0.2, color=color)
        plt.plot(time, mean_values, label=title, color=color)
        plt.xlabel("Time Steps")
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.show()

    plot_metric("ants", "Ant Population", "Ant Population Over Time", "green")
    plot_metric("predators", "Predator Population", "Predator Population Over Time", "red")
    plot_metric("food_collected", "Food Collected", "Food Collected Over Time", "blue")
    plot_metric("entropy", "Entropy", "Entropy Over Time", "purple")

if __name__ == "__main__":
    import powerlaw
    from plots import *
    params = {
        # "height": 50,
        # "width": 50,
        # "evaporate": 0.4,
        # "diffusion": 0.1,
        # "initdrop": 100,
        # "prob_random": 0.3,
        # "drop_rate": 0.1,
        # "decay_rate": 0,
        # "max_steps_without_food": 100,
        # "birth_rate": 0.01,
        # "num_predators": 3,
        # "num_food_locs": 3,
        # "num_ants": 200,
        # "max_steps_without_ants": 50,
        # "reproduction_threshold": 5,
        # "predator_lifetime": 40,
        # "init_ants": 50
    }
    # params = {}
    steps = 300
    runs = 5

    results = run_experiment(steps=steps, runs=runs, params=params)
    # plt.savefig("results.png")    
    

    results = pd.read_csv("data/results_max_steps_500.csv")
    # results.head()
    # results = load_and_prepare_data("data/results_max_steps_500.csv")
    plot_results(results, steps=steps)
    # plt.show()
    plot_powerlaw(np.array(results["food_collected"]).flatten())
    plt.savefig("powerlaw food_collected.png")

    # plt.hist(np.array(results["food_collected"]).flatten(), bins=50)
    # plot_mean_std(results, column="Home 🏠")

    # plt.show()
    # results = pd.DataFrame(results)
    # results.to_csv(f"data/results_max_steps_500.csv", index=False)
