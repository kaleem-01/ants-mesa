from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
from .agent import Environment, Ant, Food, Home, Predator

from .config import WIDTH, HEIGHT, EVAPORATE, DIFFUSION, INITDROP, LOWERBOUND, PROB_RANDOM, DROP_RATE, DECAY_RATE, MAX_STEPS_WITHOUT_FOOD, BIRTH_RATE, CONSUMPTION_RATE, CARRYING_CAPACITY, NUM_PREDATORS, NUM_FOOD_LOCS, NUM_ANTS
import math

# derived from ConwaysGameOfLife
class AntWorld(Model):
    """
    Represents the ants foraging for food.
    """

    def __init__(self, height=HEIGHT, width=WIDTH, evaporate=EVAPORATE, diffusion=DIFFUSION, initdrop=INITDROP, lowerbound=LOWERBOUND, prob_random=PROB_RANDOM, drop_rate=DROP_RATE, decay_rate=DECAY_RATE, max_steps_without_food=MAX_STEPS_WITHOUT_FOOD, birth_rate=BIRTH_RATE, consumption_rate=CONSUMPTION_RATE, carrying_capacity=CARRYING_CAPACITY, num_predators=NUM_PREDATORS, num_food_locs=NUM_FOOD_LOCS, num_ants=NUM_ANTS):
        """
        Create a new playing area of (height, width) cells.
        """
        print("Making World")
        super().__init__()
        self.evaporate = evaporate
        self.diffusion = diffusion
        self.initdrop = initdrop
        self.lowerbound = lowerbound
        self.prob_random = prob_random
        self.drop_rate = drop_rate
        self.decay_rate = decay_rate
        self.max_steps_without_food = max_steps_without_food
        self.birth_rate = birth_rate
        self.consumption_rate = consumption_rate
        self.carrying_capacity = carrying_capacity
        self.num_predators = num_predators
        self.num_food_locs = num_food_locs
        self.num_ants = num_ants

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
        food_locs = ((22, 11), (35, 8), (18, 33))

        # Setup the datacollector
        self.setup_datacollector() 


        self.home = Home(self.next_id(), homeloc, self)
        self.grid.place_agent(self.home, homeloc)
        self.schedule.add(self.home)

        for _ in range(self.num_predators):
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

        # Add the food locations
        for each_food_site in range(self.num_food_locs):
            food = Food(self.next_id(), self)
            food.add(100)
            self.grid.place_agent(food, (random.randint(0, self.grid.width - 1), random.randint(0, self.grid.height - 1)))
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
        
        def get_food(model):
            return sum(food.amount for food in model.schedule.agents if isinstance(food, Food))
        
        def get_home(model):
            return model.home.amount
            
        def get_carrying(model):
            return sum(ant.carrying for ant in model.schedule.agents if isinstance(ant, Ant))
        
        def get_distance(pos_1, pos_2):
            """ Get the distance between two points """          
            x1, y1 = pos_1
            x2, y2 = pos_2
            dx = x1 - x2
            dy = y1 - y2
            return math.sqrt(dx**2 + dy**2)

        def avg_dist_food_nest(self):
            """
            Calculate the average distance of food from the nest
            """
            food = [food for food in self.schedule.agents if isinstance(food, Food)]
            return sum(get_distance(food.pos, self.home.pos) for food in food) / len(food)

        
        model_reporters = {
            'Ants 🐜': lambda mod: get_ants(mod),
            'Food 🍯': lambda mod: get_food(mod),
            'Home 🏠': lambda mod: get_home(mod),
            'Carrying': lambda mod: get_carrying(mod),
            "Distance": lambda mod: avg_dist_food_nest(mod)
        }

        self.datacollector = DataCollector(
            model_reporters=model_reporters,
            agent_reporters={}
        )

    def step(self):
        """
        Have the scheduler advance each cell by one step
        """
        self.schedule.step()

        # Stop if all ants are gone
        if not any(isinstance(agent, Ant) for agent in self.schedule.agents):
            self.running = False

        # stop when no food remains to collect
        if sum(food.amount for food in self.schedule.agents if isinstance(food, Food)) == 0:
            self.running = False

        # Record in datacollector
        self.datacollector.collect(self)

        #birth of new ants

        num_ants = sum(1 for agent in self.schedule.agents if isinstance(agent, Ant))
        for i in range(int(self.birth_rate * num_ants)):
            ant = Ant(self.next_id(), self.home, self)
            self.grid.place_agent(ant, self.home.pos)
            self.schedule.add(ant)
        
        # Stop simulation if all ants are dead
        if num_ants == 0:
            self.running = False

        self.remove_empty_food()
        self.make_food()


    def run_model_for_steps(self, n):
        for _ in range(n):
            self.step()
        

    def remove_empty_food(self):
        """
        Remove all food objects with no food left
        """
        for food in [food for food in self.schedule.agents if isinstance(food, Food)]:
            if food.amount == 0:
                self.grid.remove_agent(food)
                self.schedule.remove(food)

    def make_food(self):
        """
        Create a new food object
        """
        food_locs = sum(1 for food in self.schedule.agents if isinstance(food, Food))
        if food_locs < self.num_food_locs:
            food = Food(self.next_id(), self)
            food.add(100)
            self.grid.place_agent(food, (random.randint(0, self.grid.width - 1), random.randint(0, self.grid.height - 1)))
            self.schedule.add(food)

