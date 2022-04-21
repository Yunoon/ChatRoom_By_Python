import hashlib
import os
import socket
import threading
import queue
import json  # json.dumps(some)打包   json.loads(some)解包
import time
import sys

# IP = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
from datetime import datetime

IP = ''
PORT = 8888
que = queue.Queue()                             # 用于存放客户端发送的信息的队列
users = []                                      # 用于存放在线用户的信息  [conn, user, addr]
lock = threading.Lock()                         # 创建锁, 防止多个线程写入数据的顺序打乱


# 将在线用户存入online列表并返回
def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online


class ChatServer(threading.Thread):
    global users, que, lock

    def __init__(self, port):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        # self.PORT = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn = None
        # self.addr = None

    def find_user(self, username):
        for i in users:
            if username == i[1]:
                return i[0]

    # 用于接收所有客户端发送信息的函数
    def tcp_connect(self, conn, addr):
        # 连接后将用户信息添加到users列表
        user = conn.recv(1024)                                    # 接收用户名
        user = user.decode()

        for i in range(len(users)):
            if user == users[i][1]:
                print('User already exist')
                user = '' + user + '_2'

        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        print("总用户：" + str(users))
        print(' 新的连接:', addr, ':', user, end='')         # 打印用户名
        d = onlines()                                          # 有新连接则刷新客户端的在线用户显示
        self.recv(d, addr)
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                self.recv(data, addr)                         # 保存信息到队列
                if "#send_file" in data:
                    print("msg: " + data.split(":;")[0])
                    self.recv_file(content=data, client=conn)
                    print("接受文件成功")
                    if data.split(":;")[2] != '【群发】':
                        print("准备发送文件给：" + data.split(":;")[2])
                        send_conn = self.find_user(username=data.split(":;")[2])
                        self.send_file(s=send_conn, data=data)

            conn.close()
        except:
            print(user + ' 断开连接')
            self.delUsers(conn, addr)                             # 将断开用户移出users
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print(' 在线用户: ', end='')         # 打印剩余在线用户(conn)
                d = onlines()
                self.recv(d, addr)
                print(d)
                break
            a += 1

    # 将接收到的信息(ip,端口以及发送的信息)存入que队列
    def recv(self, data, addr):
        lock.acquire()
        try:
            que.put((addr, data))
        finally:
            lock.release()

    def send_file(self, s, data):
        print("send ffile!!!!")
        lock.acquire()
        msg = ' ' + data.split(":;")[1] + '：' + "#recv_file"+data
        print(msg)
        s.send(msg.encode('utf-8'))
        filename = "./public/"+"new" + data.split(" ")[1].split(":;")[0].split("/")[-1]
        while True:
            if os.path.isfile(filename):  # 判断文件存在
                # 1.先发送文件大小，让客户端准备接收
                size = os.stat(filename).st_size  # 获取文件大小
                s.send(str(size).encode("utf-8"))  # 发送数据长度
                print("发送的大小：", size)

                # 2.发送文件内容
                print(datetime.now())
                s.send("准备好接收".encode("utf-8"))
                # s.recv(1024)  # 接收确认
                m = hashlib.md5()
                f = open(filename, "rb")
                for line in f:
                    s.send(line)  # 发送数据
                    m.update(line)
                f.close()

                # 3.发送md5值进行校验
                md5 = m.hexdigest()
                s.send(md5.encode("utf-8"))  # 发送md5值
                print("md5:", md5)
            lock.release()
            return


    # 接受文件
    def recv_file(self, content, client):
        lock.acquire()

        # client.send(content.encode("utf-8"))  # 传送和接收都是bytes类型

        # 1.先接收长度，建议8192
        server_response = client.recv(1024)
        file_size = int(server_response.decode("utf-8"))
        print("接收到的大小：", file_size)

        # 2.接收文件内容
        client.send("准备好接收".encode("utf-8"))  # 接收确认
        print("conten" + content)
        # 3.判断是否为文件夹路径
        if "/" in content:
            filename = "new" + content.split(" ")[1].split(":;")[0].split("/")[-1]
        else:
            filename = "new" + content.split(":;")[0]

        f = open("./public/"+filename, "wb")
        received_size = 0
        m = hashlib.md5()

        while received_size < file_size:
            size = 0  # 准确接收数据大小，解决粘包
            if file_size - received_size > 1024:  # 多次接收
                size = 1024
            else:  # 最后一次接收完毕
                size = file_size - received_size
            data = client.recv(size)  # 多次接收内容，接收大数据
            data_len = len(data)
            received_size += data_len
            print("已接收：", int(received_size / file_size * 100), "%")
            m.update(data)
            f.write(data)
        f.close()
        print("实际接收的大小:", received_size)  # 解码

        # 3.md5值校验
        md5_sever = client.recv(1024).decode("utf-8")
        md5_client = m.hexdigest()
        print("服务器发来的md5:", md5_sever)
        print("接收文件的md5:", md5_client)
        if md5_sever == md5_client:
            print("MD5值校验成功")
        else:
            print("MD5值校验失败")

        lock.release()




    # 将队列que中的消息发送给所有连接到的用户
    def sendData(self):
        while True:
            if not que.empty():
                data = ''
                reply_text = ''
                message = que.get()                               # 取出队列第一个元素


                # if " " in message[1]:
                #     if message[1].split(" ")[0] == "#send_file":
                #         for i in range(len(users)):
                #             print("recv")
                #             # self.recv_file(client=users[i][0], content=message[1])
                #     elif message[1].split(":;")[0].split(" ")[0] == "recv_file":
                #         print("recv_file")


                if isinstance(message[1], str):                   # 如果data是str则返回Ture
                    for i in range(len(users)):
                        # user[i][1]是用户名, users[i][2]是addr, 将message[0]改为用户名
                        for j in range(len(users)):
                            if message[0] == users[j][2]:
                                print(' this: message is from user[{}]'.format(j))
                                data = ' ' + users[j][1] + '：' + message[1]
                                break
                        users[i][0].send(data.encode())
                if isinstance(message[1], list):  # 同上
                    # 如果是list则打包后直接发送  
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][0].send(data.encode())
                        except:
                            pass

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(5)
        print('服务器正在运行中...')
        q = threading.Thread(target=self.sendData)
        q.start()

        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
            # c = threading.Thread(target=self.recv_file, args=(conn, addr))
            # c.start()
        self.s.close()




if __name__ == '__main__':
    cserver = ChatServer(PORT)
    cserver.start()
    while True:
        time.sleep(1)
        if not cserver.isAlive():
            print("Chat connection lost...")
            sys.exit(0)
