import numpy as np
import matplotlib.pyplot as plt

eyes = [2.25, 3.75, 5, 5, 4]
nose = [3, 3, 6]
mouth = [2.5, 3, 3.5, 1.15, 1, 1.15, 8]

TARGETED_GENE = np.array(eyes + nose + mouth)


def draw_face(target=TARGETED_GENE, small=False):
    eye_size, nose_size = 10, 10
    if small:
        eye_size, nose_size = 8, 3
    plt.figure()
    plt.plot([target[0], target[1]], [target[2], target[3]], 'go', markersize=target[4] * eye_size)
    plt.plot(target[5], target[6], 'r^', markersize=target[7] * nose_size)
    plt.plot([target[8], target[9], target[10]], [target[11], target[12], target[13]], 'b', linewidth=target[14])
    plt.tight_layout()
    plt.show()


class Agent:
    def __init__(self, init_id, init_genome_size=15):
        self.fitnessScore = 0
        self.id = init_id
        self.genome_size = init_genome_size
        self.genome = self.create_gene()

    def create_gene(self):
        return np.random.rand(self.genome_size) * 10

    def calculate_fitness(self):
        error = (TARGETED_GENE - self.genome)
        self.fitnessScore = 1 / (1 + np.dot(error, error))
        return self.fitnessScore


class Generation:
    def __init__(self, init_agent_number):
        self.mutationChance = 0.0
        self.best_agent = None
        self.reproduction_probability = None
        self.success = None
        self.agentNumber = init_agent_number
        self.population = {}
        for i in range(init_agent_number):
            self.population[i] = Agent(i)
        self.calculate_prob()
        self.evolve(1)

    def set_pop(self, pop):
        for i in range(len(pop)):
            self.population[i] = pop[i]
        self.calculate_prob()
        self.find_best()

    def calculate_prob(self):
        self.success = {}
        for i in range(self.agentNumber):
            self.success[i] = self.population[i].calculate_fitness()
        total_success = sum(self.success.values())

        self.reproduction_probability = {}
        for i in range(self.agentNumber):
            self.reproduction_probability[i] = self.success[i] / total_success

    def selection(self):
        return np.random.choice(self.agentNumber, 2, replace=False, p=[self.reproduction_probability[i] for i in range(self.agentNumber)])

    @staticmethod
    def crossover(selected_genome_1, selected_genome_2):
        crossover_point = np.random.randint(20)
        return np.hstack((selected_genome_1[:crossover_point], selected_genome_2[crossover_point:]))

    def mutation(self, child_gene):
        if np.random.rand() < self.mutationChance:
            mutation_point = np.random.randint(len(child_gene))
            child_gene[mutation_point] = np.random.rand() * 10
        return child_gene

    def child_creation(self):
        parents = self.selection()
        child_gene = self.crossover(self.population[parents[0]].genome, self.population[parents[0]].genome)
        child_gene = self.mutation(child_gene)
        return child_gene

    def pop_creation(self):
        sorted_by_success = sorted(self.success.items(), key=lambda item: item[1])
        self.best_agent = self.population[sorted_by_success[-1][0]]

        for i in range(self.agentNumber // 2):
            agent_id = sorted_by_success[i][0]
            self.population[agent_id].genome = self.child_creation()

        self.calculate_prob()

    def find_best(self):
        sorted_by_success = sorted(self.success.items(), key=lambda item: item[1])
        self.best_agent = self.population[sorted_by_success[-1][0]]

    def evolve(self, evolve_count=10, mut_prob=0.25):
        self.mutationChance = mut_prob
        for i in range(evolve_count):
            self.pop_creation()
        return self.population