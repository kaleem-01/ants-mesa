import numpy as np
import os
import csv
from warnings import filterwarnings
filterwarnings("ignore")

from mesa.batchrunner import batch_run
from multiprocessing import freeze_support

from ants.config import Sensitivity as S
from ants.model import AntWorld
from ants.agent import Ant, Food, Home, Predator
from ants.config import *
from tqdm import tqdm

# DATA_COLLECTORS = ["Ants 🐜",'Predators',"Food 🍯","Home 🏠", 'Carrying',"Distance", "prob_random", "max_steps_without_food", "birth_rate", "num_predators", "num_food_locs", "num_ants", "max_steps_without_ants", "reproduction_threshold", "predator_lifetime", "pheromone_ant_count"]
DATA_COLLECTORS = ["Ants 🐜",'Predators',"Food 🍯","Home 🏠", 'Carrying', "Distance",  "num_ants", "pheromone_ant_avg", "stopping_condition", "entropy_log"]



# Full list of parameters

# PARAMS = ["prob_random", 'max_steps_without_ants', 'birth_rate', 'max_steps_without_food', 'reproduction_threshold']
PARAMS = ['prob_random']

# INTEGER_PARAMS = ["num_ants"]
INTEGER_PARAMS = []  
# INTEGER_PARAMS = ["max_steps_without_ants"]  
# INTEGER_PARAMS = ["max_steps_without_ants", "max_steps_without_food", "reproduction_threshold"]  

# Data will be stored in this directory
SAVE_PATH = os.path.join('data', 'sensitivity', 'ants')

# We define our variables and bounds
PROBLEM = {
    'num_vars': 1,
    'names': PARAMS,    # TODO CHOOSE PROBLEM SPACE
    'bounds': [
            # [S.FoodParamsRange.EVAPORATE_MIN, S.FoodParamsRange.EVAPORATE_MAX],
            # [S.FoodParamsRange.DIFFUSION_MIN, S.FoodParamsRange.DIFFUSION_MAX],
            [S.AntParamsRange.P_PROB_RANDOM_MIN, S.AntParamsRange.P_PROB_RANDOM_MAX],
            # [S.AntParamsRange.NUM_ANTS_MIN, S.AntParamsRange.NUM_ANTS_MAX],
            # [S.FoodParamsRange.NUM_FOOD_LOCS_MIN, S.FoodParamsRange.NUM_FOOD_LOCS_MAX],
            # [S.PredatorParamsRange.NUM_PREDATORS_MIN, S.PredatorParamsRange.NUM_PREDATORS_MAX],
            # [S.PredatorParamsRange.PREDATOR_LIFETIME_MIN, S.PredatorParamsRange.PREDATOR_LIFETIME_MAX],
            # [S.PredatorParamsRange.MAX_STEPS_WITHOUT_ANTS_MIN, S.PredatorParamsRange.MAX_STEPS_WITHOUT_ANTS_MAX],
            # [S.AntParamsRange.P_BIRTH_MIN, S.AntParamsRange.P_BIRTH_MAX],
            # [S.AntParamsRange.MAX_STEPS_WITHOUT_FOOD_MIN, S.AntParamsRange.MAX_STEPS_WITHOUT_FOOD_MAX],
            # [S.PredatorParamsRange.REPRODUCTION_THRESHOLD_MIN, S.PredatorParamsRange.REPRODUCTION_THRESHOLD_MAX],
            # [S.AntParamsRange.INIT_ANTS_MIN, S.AntParamsRange.INIT_ANTS_MAX]
            # [0, 0.5]
        ]
}

N_ITERATIONS = 32
N_STEPS = 500
N_SAMPLES = 32

DATA = np.zeros((len(PROBLEM['names']), N_SAMPLES * N_ITERATIONS, len(DATA_COLLECTORS) + 1))

if __name__ == '__main__':
    freeze_support()
    
    for i, var in tqdm(enumerate(PROBLEM['names'])):
        # Get the bounds for this variable and get N_SAMPLES uniform samples within this space
        if var not in INTEGER_PARAMS:
            samples = np.linspace(*PROBLEM['bounds'][i], num=N_SAMPLES)
        else:
            samples = np.linspace(*PROBLEM['bounds'][i], num=N_SAMPLES, dtype=int)
        
        # print(samples)
        # print(var)
        params = {var: samples}


        # params = {"prob_random": np.linspace(S.AntParamsRange.P_PROB_RANDOM_MIN, S.AntParamsRange.P_PROB_RANDOM_MAX, N_SAMPLES),
        #             "max_steps_without_food": np.linspace(S.AntParamsRange.MAX_STEPS_WITHOUT_FOOD_MIN, S.AntParamsRange.MAX_STEPS_WITHOUT_FOOD_MAX, N_SAMPLES),
        #             "birth_rate": np.linspace(S.AntParamsRange.P_BIRTH_MIN, S.AntParamsRange.P_BIRTH_MAX, N_SAMPLES),
        #             "max_steps_without_ants": np.linspace(S.PredatorParamsRange.MAX_STEPS_WITHOUT_ANTS_MIN, S.PredatorParamsRange.MAX_STEPS_WITHOUT_ANTS_MAX, N_SAMPLES),
        #             "reproduction_threshold": np.linspace(S.PredatorParamsRange.REPRODUCTION_THRESHOLD_MIN, S.PredatorParamsRange.REPRODUCTION_THRESHOLD_MAX, N_SAMPLES)}

        results = batch_run(AntWorld, 
                parameters=params,
                number_processes=15, # CHOOSE ACCORDING TO THE NUM OF PROCESSORS YOU HAVE
                iterations=N_ITERATIONS, 
                max_steps=N_STEPS,
                display_progress=True,
                data_collection_period=-1)
        
        # print(results)

        with open("data/prob_random.csv", "w", newline="") as csvfile:
            # Get the column names from the first dictionary
            fieldnames = results[0].keys()
            results = [dict(row) for row in results]
            print(results)
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write rows
            writer.writerows(results)