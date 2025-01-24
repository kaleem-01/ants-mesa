from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
from .agent import Environment, Ant, Food, Home, Predator

# derived from ConwaysGameOfLife
class AntWorld(Model):
    """
    Represents the ants foraging for food.
    """

    def __init__(self, height=50, width=50, evaporate=0.5, diffusion=1, initdrop=100, lowerbound=0.01, prob_random=0.1, 
                 drop_rate=0.9, decay_rate=0.01, max_steps_without_food=500, birth_rate=0.001, consumption_rate=0.001,
                 carrying_capacity=1, num_predators=1):
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
        for i in range(100):
            ant = Ant(self.next_id(), self.home, self)
            self.grid.place_agent(ant, self.home.pos)
            self.schedule.add(ant)

        # Add the food locations
        for loc in food_locs:
            food = Food(self.next_id(), self)
            food.add(100)
            self.grid.place_agent(food, loc)
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
        
        model_reporters = {
            'Ants 🐜': lambda mod: get_ants(mod),
            'Food 🍯': lambda mod: get_food(mod),
            'Home 🏠': lambda mod: get_home(mod),
            'Carrying': lambda mod: get_carrying(mod)
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