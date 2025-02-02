# Ant Colony Simulation

## Overview
This repository contains a simulation model of ant colonies, exploring their foraging behaviors, population dynamics, and interactions with predators. The project was done as part of the Complex System Simulation course at University of Amsterdam. We investigated key questions related to self-organization and phase transitions.

## Authors
Group 2:
- Arran Bolger  
- Kaleem Ullah  
- Gašper Kreft  
- Kattelijn Bouma  

## Research Questions & Hypotheses
- **Initial Conditions:** What initial conditions lead to the propagation of the ant colony?
- **Exploration vs Exploitation:** Is there a critical level of exploration that maximizes foraging efficiency and/or colony survival?
- **Phase Transition:** Is there a critical number of ants that results in an organized society?
- **Self-Organized Criticality:** Does self-organized criticality emerge when predators are introduced?

## Model Components
### Agents
- **Ants**: The main agents in the simulation, responsible for foraging and communication.
- **Home**: The central location where ants return with food.
- **Food**: Resources scattered across the environment.
- **Pheromones**: Chemical trails used by ants for navigation.
- **Predators**: Entities that consume ants based on defined movement rules.

### Mechanisms
- **Birth & Death**
  - Ants are born periodically.
  - Ants die from starvation or predation.
- **Foraging Behavior**
  - Ants explore their environment for food.
  - They eat and transport food back to their home.
- **Communication & Environment**
  - Ants deposit pheromones that diffuse and evaporate over time.

## Key Findings
- **No Phase Transitions between Exploration and Exploitation:** Varying the inclination of following a trail does not result in a phase transition in colony's survival.
- **No Phase Transitions in Organization:** Exploration variation does not result in phase transitions in the colony’s structure.
- **Predator-Driven Criticality:** Predators introduce power-law behavior, hinting at self-organized criticality.

## Predator Dynamics
Predators follow these rules:
1. Spawn at a random location.
2. Move to the cell with the maximum number of ants.
3. Eat one ant per step.
4. Repeat until no more ants are within range.

A power-law distribution emerges in predator meal sizes, indicating self-organized criticality. Removing food sources disrupts this pattern, suggesting that food availability is key to self-organization.

## Summary of Key Results
- **Initial conditions play a crucial role in system dynamics.**
- **No phase transitions in colony organization.**
- **Predator interactions drive self-organized criticality.**
- **Exploration levels do not result in significant phase transitions.**

## References
- Hills, Thomas T. et al. (2015). *Exploration versus exploitation in space, mind, and society.* Trends in Cognitive Sciences.
- Zoe Cook, Daniel W. Franks, Elva J.H. Robinson (2013). *Exploration versus exploitation in polydomous ant colonies.* Journal of Theoretical Biology.
- Wilensky, U. (1997). *NetLogo Ants model.* Northwestern University.
- Beekman, Sumpter, & Ratnieks (2001). *Phase transition between disordered and ordered foraging in Pharaoh’s ants.* Proc. Natl. Acad. Sci. U. S. A.
- Mark Goadrich (2020). *ants-mesa* (GitHub repository).

## Getting Started
### Prerequisites
- Python 3.8+
- Required Libraries: `mesa`, `numpy`, `matplotlib`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/kaleem-01/ants-mesa.git
   ```
2. Navigate to the project directory:
   ```bash
   cd ants-mesa
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the simulation:
   ```bash
   python run.py
   ```

## Contributions
Contributions are welcome! Feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

