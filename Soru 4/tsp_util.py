import random

import numpy as np

CITY_COUNT = 5
STOCKS = [30, 40, 20, 40, 20]
CITY_PRICES = [
    [1, 4, 6, 4, 4],
    [3, 8, 2, 5, 15],
    [3, 12, 3, 5, 5],
    [2, 6, 10, 2, 4],
    [10, 5, 12, 6, 3]
]

# GENETIC SEARCH CONFIGURATION #
POP_SIZE = 10
TRY_TO_MUTATE_COUNT = 200000

# ADDITIONAL CONFIGURATION #
ALLOW_RATE = 0.01
ALLOW_SAME_INDIVIDUALS = True


class Agent:
    def __init__(self, chromosome, generation_num):
        self.chromosome = chromosome
        self.fitness = self.fitness_func()
        self.generation_number = generation_num

    def f_base_by_city(self, city_index):
        income_by_city = 0
        for stock_index in range(len(STOCKS)):
            income_by_city += self.chromosome[stock_index][city_index] * CITY_PRICES[stock_index][city_index]
        return income_by_city

    def f_base(self):
        if self.chromosome.count([]) != 0:
            return 0

        income = 0
        for city_index in range(CITY_COUNT):
            income += self.f_base_by_city(city_index)
        return income

    def f1(self):
        if self.chromosome.count([]) != 0:
            return 0

        is_visited_count = 0
        for city_index in range(CITY_COUNT):
            for stock_index in range(len(STOCKS)):
                if self.chromosome[stock_index][city_index] == 0:
                    continue

                is_visited_count += 1
                break

        if is_visited_count == CITY_COUNT:
            return 100

        return 0

    def f2(self):
        if self.chromosome.count([]) != 0:
            return 0

        income = 0
        for city_index in range(CITY_COUNT):
            min_sold_stock = max(STOCKS)
            max_sold_stock = 0
            for stock_index in range(len(STOCKS)):
                max_sold_stock = max(self.chromosome[stock_index][city_index], max_sold_stock)
                min_sold_stock = min(self.chromosome[stock_index][city_index], min_sold_stock)

            income += self.f_base_by_city(city_index) * max(20 - (max_sold_stock - min_sold_stock), 0) / 100
        return income

    def f3(self):
        if self.chromosome.count([]) != 0:
            return 0

        sold_stock_count = []
        for city_index in range(CITY_COUNT):
            sold_stock_count_by_city = 0
            for stock_index in range(len(STOCKS)):
                sold_stock_count_by_city += self.chromosome[stock_index][city_index]
            sold_stock_count.append(sold_stock_count_by_city)

        return self.f_base() * (max((20 - (max(sold_stock_count) - min(sold_stock_count))), 0) / 100)

    def fitness_func(self):
        return self.f_base() + self.f1() + self.f2() + self.f3()

    def __str__(self):
        return f'Chromosome: {self.chromosome}, Fitness: {self.fitness}, Generation Number: {self.generation_number}'


class Generation:
    def __init__(self, generation_number):
        self.population = []
        self.generation_number = generation_number

    def print_population(self):
        print("\nInitial population: \nSTATE\t\t\tFITNESS VALUE\n")
        for individual in self.population:
            for i in range(len(STOCKS)):
                for j in range(CITY_COUNT):
                    print(individual.chromosome[i][j], end=" ")
                if i == 0:
                    print("\t\t\t", individual.fitness, end=" ")
                print("\n", end="")
            print("\n", end="")
        print()

    def set_population(self, population):
        self.population = population

    @staticmethod
    def copy_matrix(matrix):
        new_matrix = []
        for i in range(len(matrix)):
            new_matrix.append(matrix[i].copy())
        return new_matrix

    def mutated_chromosome(self, chromosome):
        will_be_mutated_chromosome = self.copy_matrix(chromosome)

        for stock_index in range(len(STOCKS)):
            while True:
                rand_index_1 = random.randint(0, len(STOCKS) - 1)
                rand_index_2 = random.randint(0, len(STOCKS) - 1)
                if rand_index_2 != rand_index_1:
                    total_stock_2_city = will_be_mutated_chromosome[stock_index][rand_index_1] + \
                                         will_be_mutated_chromosome[stock_index][rand_index_2]
                    if total_stock_2_city == 0:
                        break
                    will_be_mutated_chromosome[stock_index][rand_index_2] = random.randint(0, total_stock_2_city)
                    will_be_mutated_chromosome[stock_index][rand_index_1] = total_stock_2_city - \
                                                                            will_be_mutated_chromosome[stock_index][
                                                                                rand_index_2]
                    break

        return will_be_mutated_chromosome

    @staticmethod
    def create_chromosome():
        chromosome = [[0] * 5, [0] * 5, [0] * 5, [0] * 5, [0] * 5]
        copied_stocks = STOCKS.copy()

        while sum(copied_stocks) != 0:
            copied_stocks = STOCKS.copy()
            for stock_index in range(len(STOCKS)):
                for city_index in range(CITY_COUNT):
                    chromosome[stock_index][city_index] = random.randint(0, copied_stocks[stock_index])
                    copied_stocks[stock_index] -= chromosome[stock_index][city_index]

        return chromosome

    def crossover(self, chromosome1, chromosome2):
        copied_chromosome = self.copy_matrix(chromosome1)
        cross_point = random.randint(0, len(STOCKS) - 1)
        for i in range(len(STOCKS)):
            if i >= cross_point:
                copied_chromosome[i] = chromosome2[i]
        return copied_chromosome

    def crossover_for_pop(self):
        next_generation = []
        total_fitness = sum([individual.fitness for individual in self.population])
        weighted_selection = [individual.fitness / total_fitness for individual in self.population]
        for _ in range(0, POP_SIZE):
            draw2 = np.random.choice(self.population, 2, p=weighted_selection)
            next_generation.append(Agent(self.crossover(draw2[0].chromosome, draw2[1].chromosome), 0))
        return next_generation

    def population_best(self):
        best = self.population[0]
        for individual in self.population:
            if individual.fitness > best.fitness:
                best = individual
        return best

    def evolve(self, mutation_chance):
        best_chromosome = Agent([[], [], [], [], []], 0)

        for _ in range(POP_SIZE):
            current_individual = Agent(self.create_chromosome(), 0)
            self.population.append(current_individual)

        # self.print_population()

        for i in range(self.generation_number):
            if all([individual.fitness == self.population[0].fitness for individual in self.population]):
                canBeMutatedFurther = False
                for _ in range(TRY_TO_MUTATE_COUNT):
                    temp = Agent(self.mutated_chromosome(self.population[0].chromosome), self.population[0].generation_number)
                    if self.population[0].fitness < temp.fitness:
                        canBeMutatedFurther = True
                        self.population[0].chromosome = self.copy_matrix(temp.chromosome)
                        self.population[0].fitness = temp.fitness
                        break
                if not canBeMutatedFurther:
                    break

            next_pop = []
            crossover_pop = self.crossover_for_pop().copy()
            crossover_pop.sort(key=lambda x: x.fitness, reverse=False)

            for k in range(POP_SIZE):
                current = self.population[k]
                next_chromosome = crossover_pop[k]
                next_chromosome.generation_number = current.generation_number + 1

                while True:
                    if random.random() < mutation_chance:
                        next_chromosome.chromosome = self.mutated_chromosome(next_chromosome.chromosome)
                        next_chromosome.fitness = next_chromosome.fitness_func()

                    if next_chromosome.fitness > current.fitness:
                        next_pop.append(next_chromosome)
                        break
                    else:
                        if random.random() < ALLOW_RATE:
                            next_pop.append(next_chromosome)
                            break
                        elif ALLOW_SAME_INDIVIDUALS:
                            next_pop.append(current)
                            break

            self.population = next_pop.copy()
            self.population.sort(key=lambda x: x.fitness, reverse=True)

            population_best = self.population_best()
            print(population_best)

            if best_chromosome.fitness <= population_best.fitness:
                best_chromosome.chromosome = self.copy_matrix(population_best.chromosome)
                best_chromosome.fitness = population_best.fitness
                best_chromosome.generation_number = population_best.generation_number

        return self.population
