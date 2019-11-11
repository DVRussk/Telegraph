import socket
import csv


def writeTable(f, table):
    file = open(f, 'w')
    file.write('\n'.join(map(lambda d: ';'.join(d), table)))
    file.close()
    return


def readTable(f):
    file = open(f, 'r')
    data = map(lambda d: d.split(';'), file.read().split('\n'))
    file.close()
    return list(data)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9090))
users = readTable('users.txt')
client = []  # Массив где храним адреса клиентов
print('Start Server')
while 1:
    try:
        data, adress = sock.recvfrom(1024)
        print(adress[0], adress[1])
        if adress not in client:
            client.append(adress)  # Если такова клиента нету , то добавить
        for clients in client:
            # if clients == adress:
            #    continue  # Не отправлять данные клиенту который их прислал
            print(data.decode('utf-8'))
            sock.sendto(data, clients)
    except Exception as e:
        print(e)

