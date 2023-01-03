import random
from math import *

prices = [[1, 3, 3, 2, 10], [4, 8, 12, 6, 5], [
    6, 2, 3, 10, 12], [4, 5, 5, 2, 6], [4, 15, 5, 4, 3]]


class Agent:
    def __init__(self, individual, score):
        self.individual = individual
        self.score = score

    def calculate_fitness(self):
        return self.score


def print_individual(population):
    for i in range(5):
        print(population[i])


def f(a): return int((abs(a) + a) / 2)


class Generation:
    def __init__(self):
        self.population = []
        for i in range(10):
            self.population.append(self.generate_individual())

        self.best_agent = None
        self.evolve(1)

    def set_pop(self, pop):
        for i in range(len(pop)):
            self.population[i] = pop[i]
        self.find_best()

    def find_best(self):
        self.best_agent = Agent(self.population[0], self.calculate_fitness(self.population[0]))

    @staticmethod
    def generate_individual():
        individual = [[], [], [], [], []]
        stock = [30, 40, 20, 40, 20]

        for i in range(4):
            for j in range(5):
                random_num = random.randint(0, stock[j])
                individual[i].append(random_num)
                stock[j] = stock[j] - random_num

        for j in range(5):
            individual[4].append(stock[j])

        return individual

    @staticmethod
    def calculate_fitness(sales):
        global prices
        # bir malın hangi şehre ne kadar verildiği
        receives = [[], [], [], [], []]
        percentages_b2 = []
        # bir şehrin toplam ne kadar mal aldığı
        itemcount = [0, 0, 0, 0, 0]
        profits = [0, 0, 0, 0, 0]

        bonus1 = 0
        bonus2 = 0

        for city in sales:
            if city.count(0) < 5:
                bonus1 += 1

            for i in range(5):
                receives[i].append(city[i])
                itemcount[sales.index(city)] += city[i]

            percentages_b2.append(f(20 - (max(city) - min(city))))

        percentage_b3 = (f(20 - (max(itemcount) - min(itemcount))))

        for i in range(5):
            for j in range(5):
                profits[i] += receives[j][i] * prices[i][j]
            bonus2 += profits[i] * (percentages_b2[i] / 100)

        bonus3 = (percentage_b3 / 100) * sum(profits)

        if bonus1 == 5:
            bonus1 = 100

        score = sum(profits) + bonus1 + bonus2 + bonus3
        return score

    def evolve(self, mut_prob):
        global prices
        newPopulation = []
        selectionChance = []
        allFitnessScores = []
        selectedCouples = [[], [], [], [], []]
        agentList = {}

        for i in range(10):
            allFitnessScores.append(self.calculate_fitness(self.population[i]))

        for i in range(10):
            if i == 0:
                selectionChance.append(
                    allFitnessScores[i] / sum(allFitnessScores))
            else:
                selectionChance.append(
                    (selectionChance[i - 1] + (allFitnessScores[i] / sum(allFitnessScores))))

        for j in range(10):
            randomint = random.random()
            for i in range(9):
                if 0 < randomint <= selectionChance[0]:
                    selectedCouples[floor(j / 2)].append(self.population[0])
                    # selectedCouples[floor(j / 2)].append(0)
                    break
                elif selectionChance[i] < randomint <= selectionChance[i + 1]:
                    selectedCouples[floor(
                        j / 2)].append(self.population[i + 1])
                    # selectedCouples[floor(j / 2)].append(i+1)

        # crossover
        for i in range(5):
            if random.random() < 0.5:
                columNumb1 = random.randint(0, 4)
                columNumb2 = random.randint(0, 4)

                for j in range(5):
                    tempColomn1 = selectedCouples[i][0][j][columNumb1]
                    selectedCouples[i][0][j][columNumb1] = selectedCouples[i][1][j][columNumb1]
                    selectedCouples[i][1][j][columNumb1] = tempColomn1

                    tempColomn2 = selectedCouples[i][0][j][columNumb2]
                    selectedCouples[i][0][j][columNumb2] = selectedCouples[i][1][j][columNumb2]
                    selectedCouples[i][1][j][columNumb2] = tempColomn2

            else:
                columNumb1 = random.randint(0, 4)

                for j in range(5):
                    tempColomn1 = selectedCouples[i][0][j][columNumb1]
                    selectedCouples[i][0][j][columNumb1] = selectedCouples[i][1][j][columNumb1]
                    selectedCouples[i][1][j][columNumb1] = tempColomn1

        # mutation
        for i in range(5):
            if random.random() < mut_prob:
                if random.random() < 0.5:
                    columNumb1 = random.randint(0, 4)
                    city1 = random.randint(0, 4)
                    city2 = random.randint(0, 4)
                    # print(f"mutation1 : {printIndv(selectedCouples[i][1])} ")
                    mutatiomValue = random.randint(floor(selectedCouples[i][1][city1][columNumb1] / 2),
                                                   selectedCouples[i][1][city1][columNumb1])

                    if (selectedCouples[i][1][city1][columNumb1] - mutatiomValue) > 0:
                        selectedCouples[i][1][city1][columNumb1] = selectedCouples[i][1][city1][
                                                                       columNumb1] - mutatiomValue
                        selectedCouples[i][1][city2][columNumb1] = selectedCouples[i][1][city2][
                                                                       columNumb1] + mutatiomValue
                else:
                    columNumb1 = random.randint(0, 4)
                    city1 = random.randint(0, 4)
                    city2 = random.randint(0, 4)
                    # print(f"mutation2 : {printIndv(selectedCouples[i][0])}")
                    mutatiomValue = random.randint(floor(selectedCouples[i][0][city1][columNumb1] / 2),
                                                   selectedCouples[i][0][city1][columNumb1])

                    if (selectedCouples[i][0][city1][columNumb1] - mutatiomValue) > 0:
                        selectedCouples[i][0][city1][columNumb1] = selectedCouples[i][0][city1][
                                                                       columNumb1] - mutatiomValue
                        selectedCouples[i][0][city2][columNumb1] = selectedCouples[i][0][city2][
                                                                       columNumb1] + mutatiomValue

        for i in range(5):
            for j in range(2):
                currrentIndv = selectedCouples[i][j]

                agentList[2 * i + j] = Agent(currrentIndv,
                                             self.calculate_fitness(currrentIndv))

        agentList = sorted(
            agentList.values(), key=lambda agent: agent.score, reverse=True)

        self.set_pop(newPopulation)

        self.best_agent = agentList[0]

        return agentList


generation = Generation()
generation.evolve(0.3)
