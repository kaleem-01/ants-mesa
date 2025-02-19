from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization import Slider
from mesa.visualization import ChartModule

from .model import AntWorld
from .agent import Environment, Ant, Food, Home, Predator
import math

from .config import *

def log_norm(value, lower, upper):
    """
    Finds the log normalized value between the lower and upper bounds,
    useful for plotting on a log scale. Out-of-bounds values are set to
    the lower or upper bound, whichever is closer. Similar in spirit to
    https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.colors.LogNorm.html

    Args:
        value: The value to be calibrated.
        lower: The lower bound of the range
        upper: The upper bound of the range

    """
    value = min(value, upper)
    value = max(value, lower)
    lower_log = math.log(lower)
    upper_log = math.log(upper)
    value_log = math.log(value)
    return (value_log - lower_log) / (upper_log - lower_log)

def diffusion_portrayal(agent):
    if agent is None:
        return

    # derived from sugarscape and schelling
    portrayal = {}
    if type(agent) is Ant:
        portrayal["Shape"] = "ants/resources/ant.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
    elif type(agent) is Food:
        portrayal["Shape"] = "circle"
        portrayal["r"] = math.log(1 + agent.amount)
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 2
        portrayal["Color"] = "#00FF00BB"
        portrayal["text"] = round(agent.amount)
        portrayal["text_color"] = "black"
    elif type(agent) is Home:
        portrayal["Shape"] = "circle"
        portrayal["r"] = 2
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 3
        portrayal["Color"] = "#964B00BB"
        portrayal["text"] = agent.amount
        portrayal["text_color"] = "white"
    elif type(agent) is Environment:
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

        # Calculate the amount of red we want
        red = int(log_norm(agent.amount, agent.model.lowerbound, agent.model.initdrop) * 255)

        # Scale this between red and white
        # cite https://stackoverflow.com/questions/3380726/converting-a-rgb-color-tuple-to-a-six-digit-code-in-python
        portrayal["Color"] = '#FF%02x%02x' % (255 - red, 255 - red)
    
    elif type(agent) is Predator:
        portrayal["Shape"] = "circle"
        portrayal["r"] = 2
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 4
        portrayal["Color"] = "red"

    return portrayal

# dervied from ConwaysGameOfLife
# Make a world that is 50x50, on a 500x500 display.
canvas_element = CanvasGrid(diffusion_portrayal, 50, 50, 500, 500)

# derived from schelling
model_params = {
    "height": HEIGHT,
    "width": WIDTH,
    "evaporate": Slider("Pheromone Evaporation Rate", EVAPORATE, 0.01, 0.50, 0.01),
    "diffusion": Slider("Pheromone Diffusion Rate", DIFFUSION, 0.0, 1.0, 0.1),
    "initdrop": Slider("Initial Drop", INITDROP, 100, 1000, 50),
    "prob_random": Slider("Random Move Probability", PROB_RANDOM, 0.0, 1, 0.05),
    "drop_rate": Slider("Drop Decay Rate", DROP_RATE, 0, 1, 0.01),
    "decay_rate": Slider("Food Decay Rate", DECAY_RATE, 0.0, 0.1, 0.001),
    "max_steps_without_food": Slider("Max steps without food", MAX_STEPS_WITHOUT_FOOD, 0, 100, 10),
    "birth_rate": Slider("Birth rate", BIRTH_RATE, 0.0, 0.2, 0.0001),
    "num_predators": Slider("Number of Predators", NUM_PREDATORS, 0, 30, 1),
    "num_food_locs": Slider("Number of Food Locations", NUM_FOOD_LOCS, 1, 10, 1),
    "num_ants": Slider("Number of Ants", NUM_ANTS, 1, 2000, 10),
    "max_steps_without_ants": Slider("Max steps without ants", MAX_STEPS_WITHOUT_ANTS, 0, 100, 10),
    "reproduction_threshold": Slider("Reproduction threshold predators", REPRODUCTION_THRESHOLD, 0, 100, 10),
    "predator_lifetime": Slider("Predator Lifetime", PREDATOR_LIFETIME, 0, 1000, 10),
    "init_ants": Slider("Initial Ants", INIT_ANTS, 1, 100, 1),
}   

ant_num_plot = ChartModule([{"Label": "Ants 🐜", "Color": "green"},
                            {"Label": "Predators", "Color": "red"},
                            {"Label": "ants_eaten", "Color":"black"}])

food_num_plot = ChartModule([{"Label": "Home 🏠", "Color": "red"}, # [{"Label": "Food 🍯", "Color": "blue"},
                             {"Label": "Carrying", "Color": "purple"}])

ants_eaten_plot = ChartModule([{"Label": "Ants eaten", "Color": "red"}])

dist_plot = ChartModule([{"Label": "Distance", "Color": "black"}])

server = ModularServer(
    model_cls = AntWorld, 
    visualization_elements=[canvas_element, ant_num_plot, food_num_plot, dist_plot, ants_eaten_plot], 
    name="Ants", 
    model_params=model_params
)

server.port = 8234