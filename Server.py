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


def massSend(mes, clients):
    for client in clients:
        sock.sendto(mes, client)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9090))
users = readTable('users.txt')
clients = []  # Массив где храним адреса клиентов
print('Start Server')
while 1:
    try:
        data, adress = sock.recvfrom(1024)
        de_data = data.decode('utf-8')
        print(de_data)
        if de_data[0] == '0' and adress in clients:
            print(de_data)
            massSend(de_data[1:].encode('utf-8'), clients)
        elif de_data[0] == '1':
            loglen = int(de_data[1])
            passlen = int(de_data[2 + loglen])
            log = de_data[2:2 + loglen]
            pas = de_data[3 + loglen: 3 + loglen + passlen]
            print(log, pas)
            print(users)
            if [log, pas] in users:
                clients.append(adress)
                massSend((str(len(log)) + log + 'connected to server').encode('utf-8'), clients)
                print('Ok')
            else:
                sock.sendto((str(len('Server'))+'ServerInvalid login or password').encode('utf-8'), adress)
                print('Error')
    except Exception as e:
        print(e)
