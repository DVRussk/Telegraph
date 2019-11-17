import socket


# def writeUsers(table):
#     file = open('users.txt', 'w')
#     file.write('\n'.join(map(lambda y: ';'.join(y), map(lambda x: (x[0], x[1], ';'.join(x[2])), table))))
#     file.close()
#     return
#
#
# def readUsers():
#     file = open('users.txt', 'r')
#     data = list(map(lambda d: d.split(';'), file.read().split('\n')))
#     file.close()
#     data2 = []
#     for i in data:
#         data2.append([i[0], i[1], i[2:]])
#     return list(data2)

def writeUsers(table):
    file = open('users.txt', 'w')
    file.write('\n'.join(map(lambda y: ';'.join(y), table)))
    file.close()
    return


def readUsers():
    file = open('users.txt', 'r')
    data = list(map(lambda d: d.split(';'), file.read().split('\n')))
    file.close()
    return list(data)


def readChats():
    file = open('chats.txt', 'r')
    data = list(map(lambda d: d.split(';'), file.read().split('\n')))
    file.close()
    data2 = []
    for i in data:
        data2.append([i[0], i[1], i[2:]])
    return list(data2)


def massSend(mes, clients):
    for client in clients:
        sock.sendto(mes, client)


def decode_text_message(message):
    message_out = {}
    loglen = int(message[1])
    message_out['login'] = message[2:2 + loglen]
    message_out['chat_id'] = message[2 + loglen:2 + loglen + 9]
    message_out['message_id'] = message[2 + loglen + 9:2 + loglen + 9 + 9]
    message_out['text'] = message[2 + loglen + 9 + 9:]
    message_out['to_send'] = message
    return message_out


def send_to_chat(message, chats):
    chat = list(filter(lambda x: x[1] == message['chat_id'], chats))
    if len(chat) == 0:
        return
    chat = chat[0]
    if message['login'] in chat[2]:
        for i in chat[2]:
            if i in online_users:
                for j in online_users[i]:
                    sock.sendto(message['to_send'].encode('utf-8'), j)
    else:
        sock.sendto(('1' + str(len('Server')) + 'ServerYou have no permission').encode('utf-8'), message['adress'])


def configure_message(adress, log, chats):
    active_chats = []
    for i in chats:
        if log in i[2]:
            active_chats.append(i[1])
    sock.sendto(('2'+';'.join(active_chats)).encode('utf-8'), adress)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9090))
all_users = readUsers()
online_users = {}
chats = readChats()
logins = list(map(lambda x: x[0], all_users))

clients = []
print('Start Server')

# Structure of message after decode:
#     1 char - message code
#       if message code is 0:
#           2 char is login length N
#           next N chars login
#           next 9 chars are chat id
#           next 9 chars are personal message id
#           other chars are text message
#       if message code is 1 or 2:
#           2 char is login length N
#           next N chars are login
#           2+N char is pass length N'
#           next N' chars are pass
#       if message code is 3:
#           todo
#
# Message codes:
#     0 - text Message
#     1 - try to log in
#     2 - try to log up
#     3 - join to the chat
#     4 - request for unreceived messages
while 1:
    #    try:
    data, adress = sock.recvfrom(1024)
    de_data = data.decode('utf-8')
    print(de_data)
    if de_data[0] == '0' and adress in clients:
        message = decode_text_message(de_data)
        message['adress'] = adress
        if adress in online_users[message['login']]:
            send_to_chat(message, chats)
    elif de_data[0] == '1':
        loglen = int(de_data[1])
        passlen = int(de_data[2 + loglen])
        log = de_data[2:2 + loglen]
        pas = de_data[3 + loglen: 3 + loglen + passlen]
        print(log, pas)
        print(all_users)
        if [log, pas] in all_users:
            clients.append(adress)
            if log in online_users:
                online_users[log].append(adress)
            else:
                online_users[log] = [adress]
                configure_message(adress, log, chats)
            print('Ok')
        else:
            sock.sendto((str(len('Server')) + 'ServerInvalid login or password').encode('utf-8'), adress)
            print('Error')
    elif de_data[0] == '2':
        loglen = int(de_data[1])
        passlen = int(de_data[2 + loglen])
        log = de_data[2:2 + loglen]
        pas = de_data[3 + loglen: 3 + loglen + passlen]
        print(log, pas)
        print(all_users)
        if log not in logins:
            clients.append(adress)
            configure_message(adress, log, chats)
            all_users.append([log, pas])
            if log in online_users:
                online_users[log].append(adress)
            else:
                online_users[log] = [adress]
            logins.append(log)
            writeUsers(all_users)
            print('Ok')
        else:
            sock.sendto((str(len('Server')) + 'ServerLogin is not available').encode('utf-8'), adress)
            print('Error')
#    except Exception as e:
#        print(e)
