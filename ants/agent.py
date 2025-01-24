from mesa import Agent
import math
import random

# from Sugarscape_cg
def get_distance(pos_1, pos_2):
    """ Get the distance between two point

    Args:
        pos_1, pos_2: Coordinate tuples for both points.

    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)

class Environment(Agent):
    """
    A cell representing the Environment that will hold the chemical being
    disbursed, and then reduce that amount through diffusion and evaporation.
    """

    def __init__(self, unique_id, pos, model):
        """
        Create a new cell.
        Args:
            unique_id: a unique value to distinguish the agent
            pos: The cell's coordinates on the grid.
            model: standard model reference for agent.
        """
        super().__init__(unique_id, model)
        #self.pos = pos
        self.amount = 0.0
        self._nextAmount = 0.0

    def step(self):
        """
        Find the sum of chemical in the neighboring environment, including this
        cell, then set this cell to be the diffused and evaporated amount.
        """
        all_p = self.amount
        neighbors = [n for n in self.model.grid.get_neighbors(self.pos, True) if type(n) is Environment]
        for n in neighbors:
            all_p += n.amount
        ave_p = all_p / (len(neighbors) + 1)

        self._nextAmount = (1 - self.model.evaporate) * \
            (self.amount + (self.model.diffusion * \
                                (ave_p - self.amount)))

        if self._nextAmount < self.model.lowerbound:
            self._nextAmount = 0.0

    def advance(self):
        """
        Set the state to the new computed state -- computed in step().
        """
        self.amount = self._nextAmount

    def add(self, amount):
        """
        Add the amount to the cell's amount
        """
        self.amount += amount

    def get_pos(self):
        return self.pos

class Home(Agent):
    """
    The home of the ants, recording how much food has been harvested.
    """
    def __init__(self, unique_id, pos, model):
        """
        Records the unique_id with the super, and saves the pos.
        Initializes the food amount to 0.
        """
        super().__init__(unique_id, model)
        #self.pos = pos
        self.amount = 0

    def add(self, amount):
        """
        Add the amount to the home amount
        """
        self.amount += amount

class Food(Agent):
    """
    A food cache for the ants, recording how much food is available.
    """
    def __init__(self, unique_id, model):
        """
        Records the unique_id with the super.
        Initializes the food amount to 0.
        """
        super().__init__(unique_id, model)
        self.amount = 0

    def add(self, amount):
        """
        Add the amount to the food amount
        """
        self.amount += amount
    
    def decay(self):
        decay_rate = self.model.decay_rate
        self.amount -= self.amount * decay_rate
        if self.amount < 1:
            self.amount = 0

    # def eaten(self):
    #     """
    #     Removes one food if there are any available
    #     """
    #     if self.any_food():
    #         self.amount -= 1

    def any_food(self):
        """
        Returns a bool to show if there is food available
        """
        return self.amount > 1
    
    def step(self):
        """
        Each step, decay the food amount based on the decay rate.
        """
        self.decay()

class Ant(Agent):
    """
    The ants wander around the world in search of food. Upon finding food,
    they drop a pheromone trail while heading home to store the food. When
    wandering, they either follow the strongest gradient of pheromone, or move randomly.
    """
    def __init__(self, unique_id, home, model, moore=True):
        super().__init__(unique_id, model)
        #self.pos = home.pos
        self.state = "FORAGING"
        self.drop = 0
        self.home = home
        self.moore = moore
        self.steps_without_food = 0
        self.carrying = 0

    # derived from Sugarscape get_sugar()
    # def get_item(self, item):
    #     """
    #     Finds the Agent of type item at this location in the Grid
    #     """
    #     this_cell = self.model.grid.get_cell_list_contents([self.pos])
    #     for agent in this_cell:
    #         if type(agent) is item:
    #             return agent
            
    def get_item(self, item, radius=1):
        neighbors = self.model.grid.get_neighbors(self.pos, self.moore, True, radius=radius)
        for neighbor in neighbors:
            if isinstance(neighbor, item):
                return neighbor
            

    
    # def consume_food(self):
    #     """
    #     Consume food from the available food
    #     """
    #     self.carrying -= self.model.consumption_rate


    def step(self):
        """
        Ants will either be FORAGING for food or HOMING in on the home location.
        If a FORAGING ant finds food, they eat it and begin HOMING, otherwise they
        wander either randomly or following the pheromone gradient.
        If a HOMING agent is home, they deposit their food and return FORAGING,
        otherwise they drop pheromone and take one step closer to home.
        """

        if self.pos is None:
            return  # Skip step if the ant has been removed

        self.steps_without_food += 1
        if self.steps_without_food > self.model.max_steps_without_food:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            return

        if self.state == "FORAGING":
            # Look for Food
            food = self.get_item(Food,radius=3)


            if food is not None and food.any_food(): # Eat the food and then head home
                self.steps_without_food = 0
                food.amount -= self.model.carrying_capacity
                self.carrying += self.model.carrying_capacity
                self.state = "HOMING"
                self.drop = self.model.initdrop

            else: # Not on food, move (up gradient or wander)
                if self.random.random() < self.model.prob_random:
                    self.random_move()
                else:
                    self.gradient_move()


        else: #HOMING
            # If Home, then go back to FORAGING
            if self.pos == self.home.pos:
                home = self.get_item(Home)
                if self.carrying > 0:
                    home.add(self.carrying)
                    self.carrying = 0
                self.state = "FORAGING"
                self.drop = 0
            else: #drop pheromone, and move toward home
                self.drop_pheromone()
                self.home_move()
            
        # self.consume_food()

    def drop_pheromone(self):
        """
        Leave pheromone in the Environment and reduce the pheromone drop
        """
        env = self.get_item(Environment)
        env.add(self.drop)
        self.drop *= self.model.drop_rate

    # from wolf_sheep RandomWalker
    def random_move(self):
        """
        Step one cell in any allowable direction.
        """
        # Pick the next cell from the adjacent cells.
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = self.random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)

    # adapted from Sugarscape
    def home_move(self):
        """
        Step one cell toward self.home.pos.
        """
        # Get neighborhood within vision
        neighbors = [n.get_pos() for n in self.model.grid.get_neighbors(self.pos, self.moore) if type(n) is Environment]

        # Narrow down to the nearest ones to home
        min_dist = min([get_distance(self.home.pos, pos) for pos in neighbors])
        final_candidates = [
            pos for pos in neighbors if get_distance(self.home.pos, pos) == min_dist
        ]
        self.random.shuffle(final_candidates)
        self.model.grid.move_agent(self, final_candidates[0])

    def gradient_move(self):
        """
        Step one cell to the pheromone gradient in the Environment
        """
        # Find the neighbor Environment cell that has the highest pheromone amount
        where = (0, 0)
        maxp = self.model.lowerbound
        neighbors = [n for n in self.model.grid.get_neighbors(self.pos, self.moore) if type(n) is Environment]
        for n in neighbors:
            if n.amount > maxp:
                maxp = n.amount
                where = n.get_pos()

        # When something looks interesting, move there, otherwise randomly move
        if maxp > self.model.lowerbound:
            self.model.grid.move_agent(self, where)
        else:
            self.random_move()

class Predator(Agent):
    """
    Predators hunt and eat ants in their neighborhood. If no ants are nearby,
    they move randomly within the grid. Each predator keeps track of the number
    of ants it has eaten.
    """
    def __init__(self, unique_id, model, moore=True):
        """
        Initialize the predator with its unique ID and behavior.
        """
        super().__init__(unique_id, model)
        #self.pos = (30, 30)
        self.moore = moore  # Determines movement style (Moore or Von Neumann neighborhood)
        self.ants_eaten = 0
        self.catch_streak = 0
        self.meal_sizes = []

    def hunt(self):
        """
        The predator will hunt for ants in its neighborhood.
        """
        neighbors = self.model.grid.get_neighbors(self.pos, self.moore, include_center=False)
        ants = [n for n in neighbors if isinstance(n, Ant)]

        if ants:
            # If there are ants nearby, choose one randomly and move there
            target_ant = self.random.choice(ants)
            if target_ant is None:
                random.move()
            else:
                self.model.grid.move_agent(self, target_ant.pos)
                self.catch(target_ant)
        else:
            # Otherwise, move randomly
            self.meal_sizes.append(self.catch_streak)
            self.catch_streak = 0
            self.random_move()

    def catch(self, ant):
        """
        Catch and 'eat' the given ant, removing it from the model.
        """
        self.model.grid.remove_agent(ant)
        self.model.schedule.remove(ant)  # Also remove it from the schedule
        self.ants_eaten += 1
        self.catch_streak += 1
    
    def random_move(self):
        """
        Step one cell in any allowable direction.
        """
        # Pick the next cell from the adjacent cells.
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        next_move = self.random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)

    def step(self):
        """
        Execute one step of the predator's behavior.
        """
        self.hunt()