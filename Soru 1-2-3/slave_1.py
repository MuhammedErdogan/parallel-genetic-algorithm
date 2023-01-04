import socket
import face_util as util
import pickle

generation = None


class Slave:
    def __init__(self, chance):
        self.generation = util.Generation(10)
        self.mutationChance = chance
        self.name = f'Slave P : %{self.mutationChance * 100}'

    def listen(self, init_tcp):
        while True:
            data = init_tcp.recv(100000)
            if data is None:
                continue
            convertedData = pickle.loads(data)
            print(f"\nreceived data: {convertedData}")
            self.generation.set_pop(convertedData)
            evolved = self.generation.evolve(10, self.mutationChance)
            self.send(init_tcp, evolved)

    @staticmethod
    def send(tcp, data=None):
        if data is None:
            return
        convertedData = pickle.dumps(data)
        tcp.send(convertedData)

    def start(self):
        host = 'localhost'
        port = 12345

        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpServer.connect((host, port))
        self.listen(tcpServer)


if __name__ == '__main__':
    Slave(.9).start()
