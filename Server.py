import random
import socket


def write_users(table):
    file = open('users.txt', 'w')
    file.write('\n'.join(map(lambda y: ';'.join(y), table)))
    file.close()
    return


def read_users():
    file = open('users.txt', 'r')
    data = list(map(lambda d: d.split(';'), file.read().split('\n')))
    file.close()
    return list(data)


def read_chats():
    file = open('chats.txt', 'r')
    data = list(map(lambda d: d.split(';'), file.read().split('\n')))
    file.close()
    data2 = []
    for i in data:
        data2.append([i[0], i[1], i[2:]])
    return list(data2)


def write_chats(table):
    file = open('chats.txt', 'w')
    table = table.copy()
    table = map(lambda y: [y[0], y[1]] + y[2], table)
    file.write('\n'.join(map(lambda y: ';'.join(y), table)))
    file.close()
    return


def decode_text_message(message):
    message_out = {}
    loglen = int(message[1])
    message_out['login'] = message[2:2 + loglen]
    message_out['chat_id'] = message[2 + loglen:2 + loglen + 9]
    message_out['message_id'] = message[2 + loglen + 9:2 + loglen + 9 + 9]
    message_out['text'] = message[2 + loglen + 9 + 9:]
    message_out['to_send'] = message
    return message_out


def write_message(message, chat):
    f = open(chat[1] + '.txt', 'a')
    f.write('\n' + message['to_send'])
    f.close()


def decode_create_message(message):
    message_out = {}
    loglen = int(message[1])
    message_out['login'] = message[2:2 + loglen]
    message_out['chat_name'] = message[2 + loglen:]
    return message_out


def key_gen(n):
    return str(random.randint(10 ** (n - 1), (10 ** n) - 1))


def gen_full_mes(unfull_mes):
    fullmes = unfull_mes.copy()
    fullmes['to_send'] = '0' + str(len(fullmes['login'])) + fullmes['login'] + fullmes['chat_id'] + fullmes[
        'message_id'] + fullmes['text']
    return fullmes


def create_chat(message, chats, online_users):
    while True:
        chat_id = key_gen(9)
        chat = list(filter(lambda x: x[1] == chats, chats))
        if len(chat) == 0:
            break
    if message['login'] in online_users:
        chats.append((message['chat_name'], chat_id, [message['login']]))
        for i in online_users[message['login']]:
            sock.sendto(('2' + chat_id + message['chat_name']).encode('utf-8'), i)
            unrecieved_messages(i, message['login'], chat)
        write_chats(chats)
        f = open(chat_id + '.txt', 'w')
        f.write(gen_full_mes(
            {'login': message['login'], 'chat_id': chat_id, 'message_id': key_gen(9), 'text': 'Chat was created',
             'adress': message['adress']})['to_send'])
        f.close()


def decode_invite_message(message):
    message_out = {}
    loglen = int(message[1])
    message_out['login'] = message[2:2 + loglen]
    message_out['chat_id'] = message[2 + loglen:2 + loglen + 9]
    message_out['invited_login'] = message[2 + loglen + 9:]
    return message_out


def invite_to_chat(message, chats, online_users):
    chat = list(filter(lambda x: x[1] == message['chat_id'], chats))
    if len(chat) == 0:
        return
    chat = chat[0]
    if message['login'] in chat[2] and message['invited_login'] not in chat:
        chat[2].append(message['invited_login'])
        if message['invited_login'] in online_users:
            for i in online_users[message['invited_login']]:
                sock.sendto(('2' + str(message['chat_id']) + chat[0]).encode('utf-8'), i)
                unrecieved_messages(i, message['invited_login'], [chat])
        sock.sendto(('1' + str(len('Server')) + 'ServerUser was successfully invited').encode('utf-8'),
                    message['adress'])
        write_chats(chats)


def send_to_chat(message, chats):
    chat = list(filter(lambda x: x[1] == message['chat_id'], chats))
    if len(chat) == 0:
        return
    chat = chat[0]
    if message['login'] in chat[2]:
        write_message(message, chat)
        for i in chat[2]:
            if i in online_users:
                for j in online_users[i]:
                    sock.sendto(message['to_send'].encode('utf-8'), j)
    else:
        sock.sendto(('1' + str(len('Server')) + 'ServerYou have no permission').encode('utf-8'), message['adress'])


def unrecieved_messages(adress, log, chats):
    active_chats = []
    for i in chats:
        if log in i[2]:
            active_chats.append(i[1])
    for i in active_chats:
        f = open(i + '.txt', 'r')
        messages = f.read()
        f.close()
        messages = messages.split('\n')
        for j in messages:
            sock.sendto(j.encode('utf-8'), adress)


def configure_message(adress, log, chats):
    active_chats = []
    for i in chats:
        if log in i[2]:
            active_chats.append(i[1] + i[0])
    sock.sendto(('2' + ';'.join(active_chats)).encode('utf-8'), adress)


VERSION = '0.9'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 9090))
print('Server version ' + VERSION)
print(socket.gethostbyname(socket.getfqdn()))
all_users = read_users()
online_users = {}
chats = read_chats()
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
#     3 - invite to chat
#     4 - create chat
while 1:
    try:
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
                    configure_message(adress, log, chats)
                else:
                    online_users[log] = [adress]
                    configure_message(adress, log, chats)
                unrecieved_messages(adress, log, chats)
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
                write_users(all_users)
                print('Ok')
            else:
                sock.sendto((str(len('Server')) + 'ServerLogin is not available').encode('utf-8'), adress)
                print('Error')
        elif de_data[0] == '3' and adress in clients:
            message = decode_invite_message(de_data)
            message['adress'] = adress
            if adress in online_users[message['login']]:
                invite_to_chat(message, chats, online_users)
        elif de_data[0] == '4' and adress in clients:
            message = decode_create_message(de_data)
            message['adress'] = adress
            if adress in online_users[message['login']]:
                create_chat(message, chats, online_users)
        else:
            sock.sendto((str(len('Server')) + 'ServerUnknown request').encode('utf-8'), adress)
    except Exception as e:
        print(e)
