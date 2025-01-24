from mesa.time import BaseScheduler
from .agent import Ant, Food, Environment, Home, Predator
import random

class CustomScheduler(BaseScheduler):
    def __init__(self, model):
        super().__init__(model)
        self.all_agents = {
            Ant: {},
            Food: {},
            Environment: {},
            Home: {},
            Predator: {}
        }

        self.schedule_order = [Predator, Food, Environment, Home]

    def step(self):
        for agent_type in self.schedule_order:
            agent_type_keys = list(self.all_agents[agent_type].keys())
            random.shuffle(agent_type_keys)
            for agent_key in agent_type_keys:
                self.all_agents[agent_type][agent_key].step()

    def step_for_each(self, agent):
        agent_keys = list(self.all_agents[agent].keys())
        random.shuffle(agent_keys)
        for agent_key in agent_keys:
            self.all_agents[agent][agent_key].step()

    def get_agent_count(self, agent) -> int:
        agent_type = type(agent)
        return len(self.all_agents[agent].values())