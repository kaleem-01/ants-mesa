from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
from .agent import Environment, Ant, Food, Home, Predator

from .config import *
import math
import numpy as np

# derived from ConwaysGameOfLife
class AntWorld(Model):
    """
    Represents the ants foraging for food.
    """


    def __init__(self,  **kwargs):
        """
        Create a new playing area of (height, width) cells.
        """
        # print("Making World")
        super().__init__()

        height=HEIGHT
        width=WIDTH

        self.prob_random = kwargs.get('prob_random', PROB_RANDOM)
        self.max_steps_without_food = kwargs.get('max_steps_without_food', MAX_STEPS_WITHOUT_FOOD)
        self.max_steps_without_ants = kwargs.get('max_steps_without_ants', MAX_STEPS_WITHOUT_ANTS)
        self.birth_rate = kwargs.get('birth_rate', BIRTH_RATE)
        self.reproduction_threshold = kwargs.get('reproduction_threshold', REPRODUCTION_THRESHOLD)
        self.num_ants = kwargs.get('num_ants', NUM_ANTS)
        self.num_predators = kwargs.get('num_predators', NUM_PREDATORS)
        self.evaporate = kwargs.get('evaporate', EVAPORATE)
        self.diffusion = kwargs.get('diffusion', DIFFUSION)
        self.initdrop = kwargs.get('initdrop', INITDROP)
        self.lowerbound = kwargs.get('lowerbound', LOWERBOUND)
        self.drop_rate = kwargs.get('drop_rate', DROP_RATE)
        self.decay_rate = kwargs.get('decay_rate', DECAY_RATE)
        self.consumption_rate = kwargs.get('consumption_rate', CONSUMPTION_RATE)
        self.carrying_capacity = kwargs.get('carrying_capacity', CARRYING_CAPACITY)
        # self.num_food_locs = kwargs.get('num_food_locs', NUM_FOOD_LOCS)
        
            
        self.num_food_locs = NUM_FOOD_LOCS
        self.state_counts_over_time = []
        self.predator_lifetime = PREDATOR_LIFETIME
        self.fov = FOV

        self.stopping_condition = None

        self.pheromone_ant_count = 0
        self.pheromone_ant_avg = 0
        self.pher_count_list = []

        self.occupied_cells = []
        self.entropy_log = []



        self.all_predators = []
        self.all_ants = []
        self.pheromone_ant_count = 0
        self.pher_count_list = []

        # Set up the grid and schedule.

        # Use SimultaneousActivation which simulates all the cells
        # computing their next state simultaneously.  This needs to
        # be done because each cell's next state depends on the current
        # state of all its neighbors -- before they've changed.
        self.schedule = SimultaneousActivation(self)

        # Use a simple grid, where edges wrap around.
        self.grid = MultiGrid(height, width, torus=True)

        # Define pos for the initial home and food locations
        homeloc = (25, 25)

        # Setup the datacollector
        self.setup_datacollector() 


        self.home = Home(self.next_id(), homeloc, self)
        self.grid.place_agent(self.home, homeloc)
        self.schedule.add(self.home)

        if self.num_predators > 0:
            predator = Predator(self.next_id(), self)
            self.grid.place_agent(predator, homeloc)
            self.schedule.add(predator)

            for _ in range(self.num_predators-1):
                predator_loc = (random.randint(0, height - 1), random.randint(0, width - 1))
                predator = Predator(self.next_id(), self)
                self.grid.place_agent(predator, predator_loc)
                self.schedule.add(predator)

        # Add in the ants
        # Need to do this first, or it won't affect the cells, consequence of SimultaneousActivation
        for i in range(self.num_ants):
            ant = Ant(self.next_id(), self.home, self)
            self.grid.place_agent(ant, self.home.pos)
            self.schedule.add(ant)

        food_locs = ((40,40), (35,10), (5,33))
        # Add the food locations
        for each_food_site in food_locs:
            food = Food(self.next_id(), self)
            food.add(100)
            self.grid.place_agent(food, each_food_site)
            # self.grid.place_agent(food, loc)
            self.schedule.add(food)

        # Place an environment cell at each location
        for contents, (x, y) in self.grid.coord_iter():
            cell = Environment(self.next_id(), (x, y), self)
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)

        self.running = True

    def setup_datacollector(self):

        def get_ants(model):
            return sum(1 for agent in model.schedule.agents if isinstance(agent, Ant))
        
        def get_predators(model):
            return sum(1 for agent in model.schedule.agents if isinstance(agent, Predator))
        
        def get_food(model):
            return sum(food.amount for food in model.schedule.agents if isinstance(food, Food))
        
        def get_home(model):
            return model.home.amount
            
        def get_carrying(model):
            return sum(ant.carrying for ant in model.schedule.agents if isinstance(ant, Ant))
        
        def get_entropy(model):
            return model.entropy_log

        def get_distance(pos_1, pos_2):
            """ Get the distance between two points """          
            x1, y1 = pos_1
            x2, y2 = pos_2
            dx = x1 - x2
            dy = y1 - y2
            return math.sqrt(dx**2 + dy**2)
        
        def get_pheromone_avg(model):
            pherom_avg =  model.pheromone_ant_count / get_ants(model)
            # print(pherom_avg)
            return pherom_avg
        
        def avg_dist_food_nest(self):
            """
            Calculate the average distance of food from the nest
            """
            food = [food for food in self.schedule.agents if isinstance(food, Food)]
            return sum(get_distance(food.pos, self.home.pos) for food in food) / len(food)

        
        model_reporters = {
            'Ants 🐜': lambda mod: get_ants(mod),
            'Predators': lambda mod: get_predators(mod),
            'Food 🍯': lambda mod: get_food(mod),
            'Home 🏠': lambda mod: get_home(mod),
            'Carrying': lambda mod: get_carrying(mod),
            "Distance": lambda mod: avg_dist_food_nest(mod),
            "prob_random": lambda mod: mod.prob_random,
            "max_steps_without_food": lambda mod: mod.max_steps_without_food,
            "birth_rate": lambda mod: mod.birth_rate,
            "max_steps_without_ants": lambda mod: mod.max_steps_without_ants,            
            "reproduction_threshold": lambda mod: mod.reproduction_threshold,
            "pheromone_ant_avg": lambda mod: get_pheromone_avg(mod),
            "entropy_log": lambda mod: get_entropy(mod),
            "state_counts": lambda mod: mod.stopping_condition
        }

        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters={}
        )

    def step(self):
        """
        Have the scheduler advance each cell by one step
        """
        self.datacollector.collect(self)
        
        self.pheromone_ant_count = 0

        self.occupied_cells = []
        self.schedule.step()

        # Stop if all ants are gone
        if not any(isinstance(agent, Ant) for agent in self.schedule.agents):
            self.stopping_condition = "No ants left"
            self.running = False


        # stop when no food remains to collect
        if sum(food.amount for food in self.schedule.agents if isinstance(food, Food)) == 0:
            self.stopping_condition = "No food left"
            self.running = False

        
        # Record in datacollector


        num_ants = sum(1 for agent in self.schedule.agents if isinstance(agent, Ant))
        for i in range(max(int(self.birth_rate * num_ants), 0)):
            ant = Ant(self.next_id(), self.home, self)
            self.grid.place_agent(ant, self.home.pos)
            self.schedule.add(ant)
        
        # self.pheromone_ant_avg = self.pheromone_ant_count / self.num_ants
        # self.pher_count_list.append(self.pheromone_ant_avg)
        # print(self.pheromone_ant_avg)
        
        unique_occupied_cells, occupied_cells_count = np.unique(self.occupied_cells, axis=0, return_counts=True)
        occupied_cell_probs = occupied_cells_count.astype(float) / num_ants
        
        entropy = float(-np.sum(occupied_cell_probs * np.log(occupied_cell_probs)))
        self.entropy_log.append(entropy)

        # Stop simulation if all ants are dead
        if num_ants == 0:
            self.running = False
            self.stopping_condition = "No ants left"
            # print("Stopping: No ants left")
        
        # Stop simulation if all predators are dead
        if self.num_predators > 0 and not any(isinstance(agent, Predator) for agent in self.schedule.agents):
            self.running = False
            self.stopping_condition = "No predators left"
            # print("Stopping: No predators left")

        # self.remove_empty_food()
        # self.make_food()

        # print(self.pheromone_ant_avg)
        # self.pheromone_ant_count = 0
        # self.pheromone_ant_avg = 0

        

    def run_model_for_steps(self, n):
        for _ in range(n):
            self.step()
        

    def remove_empty_food(self):
        """
        Remove all food objects with no food left
        """
        for food in [food for food in self.schedule.agents if isinstance(food, Food)]:
            if food.amount < self.carrying_capacity + 1:
                self.grid.remove_agent(food)
                self.schedule.remove(food)

    def make_food(self, amount=100):
        """
        Create a new food object
        """
        food_locs = sum(1 for food in self.schedule.agents if isinstance(food, Food))
        if food_locs < self.num_food_locs:
            food = Food(self.next_id(), self)
            food.add(amount)
            self.grid.place_agent(food, (random.randint(0, self.grid.width - 1), random.randint(0, self.grid.height - 1)))
            self.schedule.add(food)

