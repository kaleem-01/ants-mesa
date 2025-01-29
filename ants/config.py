WIDTH = 50
HEIGHT = 50
EVAPORATE = 0.25
DIFFUSION = 0.1
INITDROP = 1000
LOWERBOUND = 0.01
PROB_RANDOM = 0.3
DROP_RATE = 0.7
DECAY_RATE = 0
MAX_STEPS_WITHOUT_FOOD = 100
BIRTH_RATE = 0.0001
CONSUMPTION_RATE = 0.001
CARRYING_CAPACITY = 1
NUM_PREDATORS = 3
NUM_FOOD_LOCS = 3
NUM_ANTS = 300
MAX_STEPS_WITHOUT_ANTS = 5
REPRODUCTION_THRESHOLD = 20
PREDATOR_LIFETIME = 20
FOV = 3



# prob_random=PROB_RANDOM, 
# max_steps_without_food=MAX_STEPS_WITHOUT_FOOD, 
# birth_rate=BIRTH_RATE, 
# num_predators=NUM_PREDATORS, 
# num_food_locs=NUM_FOOD_LOCS,
# num_ants=NUM_ANTS, 
# max_steps_git without_ants=MAX_STEPS_WITHOUT_ANTS 
# predator_lifetime=PREDATOR_LIFETIME

class Sensitivity:

    class AntParamsRange:

        NUM_ANTS_MIN, NUM_ANTS_MAX = 1, 75 
        P_PROB_RANDOM_MIN, P_PROB_RANDOM_MAX = 0, 1
        P_BIRTH_MIN, P_BIRTH_MAX = 0.0, 0.001
        MAX_STEPS_WITHOUT_FOOD_MIN,MAX_STEPS_WITHOUT_FOOD_MAX = 100, 300
        

    class FoodParamsRange:
        
        NUM_FOOD_LOCS_MIN, NUM_FOOD_LOCS_MAX = 1, 5
        EVAPORATE_MIN, EVAPORATE_MAX = 0.1, 0.9
        DIFFUSION_MIN, DIFFUSION_MAX = 0.1, 0.9



    class PredatorParamsRange:
        
        NUM_PREDATORS_MIN, NUM_PREDATORS_MAX = 1, 10
        PREDATOR_LIFETIME_MIN, PREDATOR_LIFETIME_MAX = 100, 300
        MAX_STEPS_WITHOUT_ANTS_MIN, MAX_STEPS_WITHOUT_ANTS_MAX = 100, 300
        REPRODUCTION_THRESHOLD_MIN, REPRODUCTION_THRESHOLD_MAX = 100, 300


class AntWorldConfig:
    def __init__(self, **kwargs):


        self.prob_random = kwargs.get('prob_random', PROB_RANDOM)
        self.max_steps_without_food = kwargs.get('max_steps_without_food', MAX_STEPS_WITHOUT_FOOD)
        self.birth_rate = kwargs.get('birth_rate', BIRTH_RATE)
        # self.num_predators = kwargs.get('num_predators', NUM_PREDATORS)
        # self.num_food_locs = kwargs.get('num_food_locs', NUM_FOOD_LOCS)
        # self.num_ants = kwargs.get('num_ants', NUM_ANTS)
        self.max_steps_without_ants = kwargs.get('max_steps_without_ants', MAX_STEPS_WITHOUT_ANTS)
        self.reproduction_threshold = kwargs.get('reproduction_threshold')
        # self.predator_lifetime = kwargs.get('predator_lifetime', PREDATOR_LIFETIME)
        # self.fov = kwargs.get('fov', FOV)
        # self.evaporate = kwargs.get('evaporate', EVAPORATE)
        # self.diffusion = kwargs.get('diffusion', DIFFUSION)
        # self.initdrop = kwargs.get('initdrop', INITDROP)
        # self.lowerbound = kwargs.get('lowerbound', LOWER
        

