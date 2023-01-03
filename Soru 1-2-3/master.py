import util as util
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


class Master(Thread):
    def __init__(self, init_ip, init_port, init_conn, index):
        Thread.__init__(self)
        self.ip = init_ip
        self.port = init_port
        self.connection = init_conn
        self.connectionIndex = index

    @staticmethod
    def slaves_send_data(data):
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
        generation.set_pop(self.get_sorted_pop())

        if generation.best_agent.fitnessScore >= 0.95:
            print(
                f'{round(generation.best_agent.fitnessScore, 3)} is found in {evolutionCount} iteration with 2 '
                f'different mutation chance')
            if foundCount < tryCount:
                foundCount += 1
                totalEvolutionCount += evolutionCount
                # reset part
                evolutionCount = 0
                generation = util.Generation(10)
                self.slaves_send_data(generation.population)
                # util.DrawFace(generation.best_agent.genome)
            else:
                print(
                    f'Found {tryCount} times. The Average : {totalEvolutionCount / tryCount}. iteration with 2 '
                    f'different mutation chance')
                exit()
        else:
            self.slaves_send_data(generation.population)

    @staticmethod
    def get_sorted_pop():
        global receivedPopulation
        mergedDictionary = {}
        for i in range(len(receivedPopulation)):
            mergedDictionary[i] = receivedPopulation[i]

        sorted_population = sorted(mergedDictionary.values(), key=lambda agent: agent.calculate_fitness(), reverse=True)
        sorted_population = sorted_population[:10]
        receivedPopulation.clear()

        return sorted_population

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
            self.slaves_send_data(generation.population)
        self.slaves_listen()


if __name__ == '__main__':
    # To draw the current best, print util.DrawFace(generation.best_agent.genome)
    # If bottom line is commented, it will use parallel algorithm, otherwise it will use normal algorithm
    """
    #Normal Version

    generation = util.Generation(10)
    currentMutationChance = 0.9
    #standart algorithm 
    print("Standart Algorithm Started To Work")
    while foundCount < tryCount:
        while generation.best_agent.fitnessScore <= 0.95:
            evolved = generation.Evolve(10,currentMutationChance)
            evolutionCount += 1
            
            
        print(f'{round(generation.best_agent.fitnessScore,3)} is found in {evolutionCount} iteration. Mutation chance : %{currentMutationChance * 100}')
        totalEvolutionCount += evolutionCount
        foundCount+=1
        #reset part
        evolutionCount = 0
        generation = util.Generation(10)
    
    print(f'Found {tryCount} times. The Average : {totalEvolutionCount/tryCount}')

    """
    # Paralel versiyon
    generation = util.Generation(10)
    TCP_IP = 'localhost'
    TCP_PORT = 2004
    BUFFER_SIZE = 100000
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServer.bind((TCP_IP, TCP_PORT))
    threads = []

    print("Paralel Algorithm Started To Work")
    tcpServer.listen(2)
    for i in range(2):
        (conn, (ip, port)) = tcpServer.accept()
        # print('A slave connected!')
        threadLock.acquire()
        connectedConns.append(conn)
        masterThread = Master(ip, port, conn, i)
        threadLock.release()
        masterThread.start()
        threads.append(masterThread)

    for t in threads:
        t.join()
# """
