import socket
import tsp_util as tutil
import pickle

generation = None


class Slave:
    def __init__(self, chance):
        self.mutationChance = chance
        self.name = f'Slave P : %{self.mutationChance * 100}'

    def listen(self, tcp):
        global generation
        while True:
            data = tcp.recv(100000)
            if data is None:
                continue
            convertedData = pickle.loads(data)
            generation.set_pop(convertedData)
            evolved = generation.evolve(self.mutationChance)
            self.send(tcp, evolved)

    @staticmethod
    def send(tcp, data=None):
        if data is None:
            return
        convertedData = pickle.dumps(data)
        tcp.send(convertedData)

    def start(self):
        host = 'localhost'
        port = 2004

        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpServer.connect((host, port))
        self.listen(tcpServer)


if __name__ == '__main__':
    mutationChance = float(input("What is mutation chance? : "))
    generation = tutil.Generation()
    c1 = Slave(mutationChance)
    c1.start()
