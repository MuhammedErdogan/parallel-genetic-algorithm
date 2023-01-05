from _ast import Constant

import tsp_util as tutil
import pickle
import socket
from threading import Thread, Lock

tryCount = 10
connectedConns = []
threadLock = Lock()
receivedPopulation = []
generation = None
evolutionCount = 0
totalEvolutionCount = 0
currentBestScore = 0
foundCount = 0

CONNECTION_COUNT = 2


class Master(Thread):
    def __init__(self, ip, port, conn, index):
        Thread.__init__(self)
        self.ip, self.port = ip, port
        self.connection = conn
        self.connectionIndex = index

    @staticmethod
    def slaves_send(data):
        global connectedConns
        convertedData = pickle.dumps(data)
        connectedConns[0].send(convertedData)
        connectedConns[1].send(convertedData)

    def process_pop(self):
        global generation
        global evolutionCount
        global currentBestScore
        global foundCount
        global totalEvolutionCount
        global tryCount

        evolutionCount += 1
        generation.set_population(self.get_sorted_pop())

        if generation.population_best().fitness >= 1700:
            print(
                f'{round(generation.population_best().fitness, 3)} is found in {evolutionCount} iteration with 2 '
                f'different mutation chances')
            if foundCount < tryCount:
                foundCount += 1
                totalEvolutionCount += evolutionCount
                # reset part
                evolutionCount = 0
                generation = tutil.Generation(10)
                self.slaves_send(generation.population)
            else:
                print(
                    f'Found {tryCount} times. The Average : {totalEvolutionCount/tryCount}. iteration with 2 '
                    f'different mutation chances')
                exit()
        else:
            self.slaves_send(generation.population)

    @staticmethod
    def get_sorted_pop():
        global receivedPopulation
        mergedDictionary = {}
        for _ in range(len(receivedPopulation)):
            mergedDictionary[_] = receivedPopulation[_]

        sorted_population = sorted(mergedDictionary.values(), key=lambda agent: agent.fitness, reverse=True)
        sorted_population = sorted_population[:10]
        receivedPopulation.clear()

        populationList = []
        for element in sorted_population:
            populationList.append(element)
        return populationList

    def slaves_listen(self):
        global connectedConns
        global receivedPopulation
        global threadLock
        while True:
            data = self.connection.recv(100000)
            if not data:
                continue
            convertedData = pickle.loads(data)
            threadLock.acquire()
            for _ in range(len(convertedData)):
                receivedPopulation.append(convertedData[_])
            threadLock.release()
            if len(receivedPopulation) >= 20:
                self.process_pop()

    def run(self):
        global connectedConns
        global generation
        if len(connectedConns) > 1:
            self.slaves_send(generation.population)
        self.slaves_listen()


if __name__ == '__main__':
    generation = tutil.Generation(10)

    """
    print("Standart Algorithm Started To Work")
    currentMutationChance = 0.1
    evolved = generation.evolve(currentMutationChance)
    evolutionCount += 1
    while foundCount < tryCount:
        while evolved[0].fitness <= 1700:
            evolved = generation.evolve(currentMutationChance)
            evolutionCount += 1

        print(
            f'{round(evolved[0].fitness, 3)} is found in {evolutionCount} iteration. Mutation chance : %{currentMutationChance * 100}')
        totalEvolutionCount += evolutionCount
        foundCount += 1
        # reset part
        evolutionCount = 0
        generation = tutil.Generation(10)

    print(f'Found {tryCount} times. The Average : {totalEvolutionCount / tryCount}')
    
    """
    TCP_IP = 'localhost'
    TCP_PORT = 12345
    BUFFER_SIZE = 100000
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServer.bind((TCP_IP, TCP_PORT))
    threads = []

    print("Parallel Algorithm Started To Work")
    tcpServer.listen(CONNECTION_COUNT)
    for i in range(CONNECTION_COUNT):
        (conn, (ip, port)) = tcpServer.accept()
        print('A slave connected!')
        threadLock.acquire()
        connectedConns.append(conn)
        masterThread = Master(ip, port, conn, i)
        threadLock.release()
        masterThread.start()
        threads.append(masterThread)

    for t in threads:
        t.join()
    #"""