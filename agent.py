import numpy as np
import matplotlib.pyplot as plt


class Agent:
    def __init__(self,
                 m=25,
                 start_x=0,
                 start_y=2,
                 target_x=5,
                 target_y=22,
                 possible_genes=None,
                 ):

        self.possible_genes = ['up', 'right', 'left'] if possible_genes is None else possible_genes
        self.genome = None
        self.start_x, self.start_y = start_x, start_y
        self.x, self.y = self.start_x, self.start_y
        self.target_x, self.target_y = target_x, target_y
        self.pathx, self.pathy = [self.start_x], [self.start_y]

        self.take_action = {'up': self.go_up,
                            'left': self.go_left,
                            'right': self.go_right}

        self.m = m
        self.create_genotype()
        self.phenotype()

    def go_up(self):
        self.y = self.y + 1

    def go_left(self):
        self.x = self.x - 1

    def go_right(self):
        self.x = self.x + 1

    def create_genotype(self):
        self.genome = np.random.choice(self.possible_genes, size=self.m)

    def set_gene(self, new_gene):
        ## self.genome = new_gene ---WRONG---
        self.genome = new_gene.copy()
        self.phenotype()

    def phenotype(self):
        self.pathx, self.pathy = [self.start_x], [self.start_y]
        self.x, self.y = self.start_x, self.start_y
        for gene in self.genome:
            self.take_action[gene]()

            self.pathx.append(self.x)
            self.pathy.append(self.y)

    def fitness(self):
        error_x = (self.target_x - self.pathx[-1])
        error_y = (self.target_y - self.pathy[-1])
        return 1 / (1 + np.sqrt(error_x ** 2 + error_y ** 2))

    def draw(self, verbose=True):
        if verbose: print(self.genome)
        plt.plot(self.target_x, self.target_y, 'g*', markersize=30)
        plt.plot(self.pathx[-1], self.pathy[-1], 'r^', markersize=25)
        plt.plot(self.pathx, self.pathy)
        plt.axis((-2, self.target_x + 2, 0, self.target_y + 2))
        plt.grid()
