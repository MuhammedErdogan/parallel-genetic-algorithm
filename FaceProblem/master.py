import time

import face_util as util
import pickle
import socket
from threading import Thread, Lock

start = time.time()
end = time.time()

class Master(Thread):
    def __init__(self, init_ip, init_port, init_conn, index):
        Thread.__init__(self)
        self.ip = init_ip
        self.port = init_port
        self.connection = init_conn
        self.connectionIndex = index

    # Method to send data to both connected clients
    @staticmethod
    def slaves_send_data(data):
        global connected_conns  # list of connected clients
        # Serialize data
        converted_data = pickle.dumps(data)
        # Send data to both clients
        connected_conns[0].send(converted_data)
        connected_conns[1].send(converted_data)

    # Method to process received data from clients
    def process_pop(self):
        global generation  # current population of agents
        global evaluation_count  # number of iterations
        global current_best_score  # best fitness score found so far
        global foundCount  # number of times a solution has been found
        global total_evaluation_count  # total number of iterations over all tries
        global try_count  # number of tries
        global total_fitness  # total fitness score of found solutions

        # Increase iteration count
        evaluation_count += 1
        # Update population in generation object with sorted received data
        generation.set_pop(self.get_sorted_pop())

        # Check if a solution has been found
        if generation.best_agent.fitnessScore > 0.975:
            # Draw the face represented by the solution
            util.draw_face(generation.best_agent.genome)
            # Print information about the found solution
            print(
                f'{round(generation.best_agent.fitnessScore, 3)} is found in {evaluation_count}')
            # Add fitness score to total fitness score
            total_fitness += round(generation.best_agent.fitnessScore, 3)
            # Check if this is the final try
            if foundCount < try_count:
                # Increase found count
                foundCount += 1
                # Add iteration count to total iteration count
                total_evaluation_count += evaluation_count
                # Reset iteration count, generation object, and send new population to clients
                evaluation_count = 0
                generation = util.Generation(10)
                self.slaves_send_data(generation.population)
                return False
            else:
                # Print final results and exit
                print(
                    f'Found {try_count} times. The Average : {total_evaluation_count / try_count}. The Average of Fitness: {total_fitness / (try_count + 1)}')
                end = time.time()
                print(f'Time: {end - start}')
                exit()
        else:
            # If a solution has not been found, send updated population to clients
            self.slaves_send_data(generation.population)
            return False

    # Method to sort received data and return the top 10 elements
    @staticmethod
    def get_sorted_pop():
        global received_population  # list of received data from clients
        # Create a dictionary mapping indices to received data
        mergedDictionary = {}
        for j in range(len(received_population)):
            mergedDictionary[j] = received_population[j]
        # Sort the dictionary by fitness score in descending order
        sorted_population = sorted(mergedDictionary.values(), key=lambda agent: agent.calculate_fitness(), reverse=True)
        # Return the top 10 elements
        sorted_population = sorted_population[:10]
        # Clear received_population list
        received_population.clear()

        return sorted_population

    # Method to listen for data from connected clients
    def slaves_listen(self):
        global connected_conns  # list of connected clients
        global received_population  # list of received data from clients
        global thread_lock  # lock to synchronize threads
        while True:
            # Receive data from client
            data = self.connection.recv(100000)
            # If no data received, continue
            if not data:
                continue
            # Deserialize received data
            converted_data = pickle.loads(data)
            # Acquire lock
            thread_lock.acquire()
            # Add received data to received_population list
            for _ in range(len(converted_data)):
                received_population.append(converted_data[_])
            # Release lock
            thread_lock.release()
            # If 20 or more elements have been received, process data and send updated population to clients
            if len(received_population) >= 20:
                control = self.process_pop()
                if control:
                    return True

    # Method run when starting a thread
    def run(self):
        global connected_conns  # list of connected clients
        global generation  # current population of agents
        # If there are more than 1 connected clients, send initial population to clients
        if len(connected_conns) > 1:
            self.slaves_send_data(generation.population)
        # Listen for data from clients
        control = self.slaves_listen()
        if control:
            return


def standart_algo():
    try_count = 10  # number of tries
    evaluation_count = 0  # number of iterations
    total_evaluation_count = 0  # total number of iterations over all tries
    foundCount = 0  # number of times a solution has been found

    # Create initial generation of agents
    generation = util.Generation(10)

    print("Standart Algorithm Started To Work")
    start = time.time()
    currentMutationChance = 0.45
    while foundCount < try_count:
        currentMutationChance += 0.05
        while generation.best_agent.fitnessScore <= 0.975:
            generation.evolve(10, currentMutationChance)
            evaluation_count += 1

        print(
            f'{round(generation.best_agent.fitnessScore, 3)} is found in {evaluation_count} iteration. Mutation chance : %{currentMutationChance * 100}')
        total_evaluation_count += evaluation_count
        foundCount += 1
        # reset part
        evolutionCount = 0
        generation = util.Generation(10)

    print(f'Found {try_count} times. The Average : {total_evaluation_count / try_count}')
    end = time.time()
    print(f'Time : {end - start}')


if __name__ == '__main__':
    standart_algo()

    """
    try_count = 10  # number of tries
    connected_conns = []  # list of connected clients
    thread_lock = Lock()  # lock to synchronize threads
    received_population = []  # list of received data from clients
    evaluation_count = 0  # number of iterations
    total_evaluation_count = 0  # total number of iterations over all tries
    current_best_score = 0  # best fitness score found so far
    foundCount = 0  # number of times a solution has been found
    total_fitness = 0  # total fitness score of found solutions
    CONNECTION_COUNT = 2  # number of expected connections

    # Create initial generation of agents
    generation = util.Generation(10)
    
    TCP_IP = 'localhost'  # IP address of server
    TCP_PORT = 12345  # port of server
    BUFFER_SIZE = 100000  # buffer size for receiving data
    # Create a TCP socket for the server
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the specified IP and port
    tcpServer.bind((TCP_IP, TCP_PORT))
    threads = []  # list of created threads

    print("Parallel Algorithm Started")
    # Start listening for connections, allow up to CONNECTION_COUNT connections
    tcpServer.listen(CONNECTION_COUNT)
    # Accept connections from clients and create a thread for each
    for i in range(CONNECTION_COUNT):
        (conn, (ip, port)) = tcpServer.accept()
        print('A slave connected!')
        thread_lock.acquire()
        connected_conns.append(conn)
        masterThread = Master(ip, port, conn, i)
        thread_lock.release()
        masterThread.start()
        threads.append(masterThread)
    # Keep the server running until all threads have finished
    start = time.time()
    for t in threads:
        t.join()
    #"""
