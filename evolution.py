import numpy as np
from matplotlib import pyplot as plt

from agent import Agent


class Evolution:
    def __init__(self, N=10, possible_genes=None):

        self.N = N
        self.possible_genes = ['up', 'right', 'left'] if possible_genes is None else possible_genes

        self.population = [Agent() for i in range(N)]
        self.fitness_values = [self.population[i].fitness() for i in range(N)]

        total_fitness = sum(self.fitness_values)
        self.reproduction_probability = [val / total_fitness for val in self.fitness_values]

        self.best_agent = self.population[np.argmax(self.fitness_values)]

    def selection(self):
        parents = np.random.choice(self.N, size=2, p=self.reproduction_probability)
        return parents

    def crossover(self, parent0, parent1):
        cutoff = np.random.randint(len(parent0.genome))
        child = np.concatenate((parent0.genome[:cutoff], parent1.genome[cutoff:]))
        return child

    def mutation(self, child):
        mutation_point = np.random.randint(len(child.genome))
        child.genome[mutation_point] = np.random.choice(self.possible_genes)

    def create_offspring(self):
        parents = self.selection()
        P0, P1 = self.population[parents[0]], self.population[parents[1]]

        child_agent = Agent()
        child_genome = self.crossover(parent0=P0, parent1=P1)
        child_agent.set_gene(child_genome)
        self.mutation(child_agent)
        child_agent.phenotype()

        return child_agent

    def create_new_population(self):
        new_population = [self.create_offspring() for i in range(self.N - 1)] + [self.best_agent]
        self.population = new_population

        self.fitness_values = [self.population[i].fitness() for i in range(self.N)]
        total_fitness = sum(self.fitness_values)
        self.reproduction_probability = [val / total_fitness for val in self.fitness_values]
        self.best_agent = self.population[np.argmax(self.fitness_values)]

    def evolve(self, G=10):
        for i in range(G):
            self.create_new_population()
        return self.best_agent


world = Evolution()
for a in world.population:
    a.draw(verbose = False)
plt.grid()