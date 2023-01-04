import util as util
import pickle
import socket
from threading import Thread, Lock

try_count = 10
connected_conns = []
thread_lock = Lock()
received_population = []
generation = None
evaluation_count = 0
total_evaluation_count = 0
current_best_score = 0
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
        global connected_conns
        converted_data = pickle.dumps(data)
        connected_conns[0].send(converted_data)
        connected_conns[1].send(converted_data)

    def process_pop(self):
        global generation
        global evaluation_count
        global current_best_score
        global foundCount
        global total_evaluation_count
        global try_count

        evaluation_count += 1
        generation.set_pop(self.get_sorted_pop())

        util.draw_face(generation.best_agent.genome)
        if generation.best_agent.fitnessScore >= 0.95:
            print(
                f'{round(generation.best_agent.fitnessScore, 3)} is found in {evaluation_count} iteration with 2 '
                f'different mutation chance')
            if foundCount < try_count:
                foundCount += 1
                total_evaluation_count += evaluation_count
                # reset part
                evaluation_count = 0
                generation = util.Generation(10)
                self.slaves_send_data(generation.population)
            else:
                print(
                    f'Found {try_count} times. The Average : {total_evaluation_count / try_count}. iteration with 2 '
                    f'different mutation chance')
                exit()
        else:
            self.slaves_send_data(generation.population)

    @staticmethod
    def get_sorted_pop():
        global received_population
        mergedDictionary = {}
        for j in range(len(received_population)):
            mergedDictionary[j] = received_population[j]

        sorted_population = sorted(mergedDictionary.values(), key=lambda agent: agent.calculate_fitness(), reverse=True)
        sorted_population = sorted_population[:10]
        received_population.clear()

        return sorted_population

    def slaves_listen(self):
        global connected_conns
        global received_population
        global thread_lock
        while True:
            data = self.connection.recv(100000)
            if not data:
                continue
            converted_data = pickle.loads(data)
            thread_lock.acquire()
            for _ in range(len(converted_data)):
                received_population.append(converted_data[_])
            thread_lock.release()
            if len(received_population) >= 20:
                self.process_pop()

    def run(self):
        global connected_conns
        global generation
        if len(connected_conns) > 1:
            self.slaves_send_data(generation.population)
        self.slaves_listen()


if __name__ == '__main__':
    generation = util.Generation(10)
    TCP_IP = 'localhost'
    TCP_PORT = 2004
    BUFFER_SIZE = 100000
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpServer.bind((TCP_IP, TCP_PORT))
    threads = []

    print("Paralel Algorithm Started")
    tcpServer.listen(2)
    for i in range(2):
        (conn, (ip, port)) = tcpServer.accept()
        print('A slave connected!')
        thread_lock.acquire()
        connected_conns.append(conn)
        masterThread = Master(ip, port, conn, i)
        thread_lock.release()
        masterThread.start()
        threads.append(masterThread)

    for t in threads:
        t.join()
