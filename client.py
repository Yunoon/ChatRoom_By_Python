import hashlib
import os
import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from datetime import datetime
from tkinter.scrolledtext import ScrolledText  # 导入多行文本框用到的包

from tkinter.filedialog import askdirectory, askopenfilename, askopenfile

IP = ''
PORT = ''
user = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '【群发】'  # 聊天对象, 默认为群聊

temp_file_path = ""
lock = threading.Lock()                         # 创建锁, 防止多个线程写入数据的顺序打乱


# 登陆窗口
loginRoot = tkinter.Tk()
loginRoot.title('聊天室')
loginRoot['height'] = 110
loginRoot['width'] = 270
loginRoot.resizable(0, 0)  # 限制窗口大小

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:8888')  # 默认显示的ip和端口
User = tkinter.StringVar()
User.set('')

# 服务器标签
labelIP = tkinter.Label(loginRoot, text='地址:端口')
labelIP.place(x=20, y=10, width=100, height=20)

entryIP = tkinter.Entry(loginRoot, width=80, textvariable=IP1)
entryIP.place(x=120, y=10, width=130, height=20)

# 用户名标签
labelUser = tkinter.Label(loginRoot, text='昵称')
labelUser.place(x=30, y=40, width=80, height=20)

entryUser = tkinter.Entry(loginRoot, width=80, textvariable=User)
entryUser.place(x=120, y=40, width=130, height=20)

path = tkinter.StringVar()


# 登录按钮
def login(*args):
    global IP, PORT, user
    IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    PORT = int(PORT)  # 端口号需要为int类型
    user = entryUser.get()
    if not user:
        tkinter.messagebox.showerror('温馨提示', message='请输入任意的用户名！')
    else:
        loginRoot.destroy()  # 关闭窗口


loginRoot.bind('<Return>', login)  # 回车绑定登录功能
but = tkinter.Button(loginRoot, text='登录', command=login)
but.place(x=100, y=70, width=70, height=30)

loginRoot.mainloop()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
if user:
    s.send(user.encode())  # 发送用户名
else:
    s.send('no'.encode())  # 没有输入用户名则标记no

# 如果没有用户名则将ip和端口号设置为用户名
addr = s.getsockname()  # 获取客户端ip和端口号
addr = addr[0] + ':' + str(addr[1])
if user == '':
    user = addr

# 聊天窗口
# 创建图形界面
root = tkinter.Tk()
root.title(user)  # 窗口命名为用户名
root['height'] = 400
root['width'] = 580
root.resizable(0, 0)  # 限制窗口大小

# 创建多行文本框
listbox = ScrolledText(root)
listbox.place(x=5, y=0, width=570, height=320)
# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')
listbox.insert(tkinter.END, '欢迎加入聊天室 ！', 'blue')

# 表情功能代码部分
# 四个按钮, 使用全局变量, 方便创建和销毁
b1 = ''
b2 = ''
b3 = ''
b4 = ''
# 将图片打开存入变量中
p1 = tkinter.PhotoImage(file='./emoji/facepalm.png')
p2 = tkinter.PhotoImage(file='./emoji/smirk.png')
p3 = tkinter.PhotoImage(file='./emoji/concerned.png')
p4 = tkinter.PhotoImage(file='./emoji/smart.png')
# 用字典将标记与表情图片一一对应, 用于后面接收标记判断表情贴图
dic = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4}
ee = 0  # 判断表情面板开关的标志


# 发送表情图标记的函数, 在按钮点击事件中调用


def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    mes = exp + ':;' + user + ':;' + chat
    s.send(mes.encode())
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    ee = 0


# 四个对应的函数
def bb1():
    mark('aa**')


def bb2():
    mark('bb**')


def bb3():
    mark('cc**')


def bb4():
    mark('dd**')


def express():
    global b1, b2, b3, b4, ee
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(root, command=bb1, image=p1,
                            relief=tkinter.FLAT, bd=0)
        b2 = tkinter.Button(root, command=bb2, image=p2,
                            relief=tkinter.FLAT, bd=0)
        b3 = tkinter.Button(root, command=bb3, image=p3,
                            relief=tkinter.FLAT, bd=0)
        b4 = tkinter.Button(root, command=bb4, image=p4,
                            relief=tkinter.FLAT, bd=0)

        b1.place(x=5, y=248)
        b2.place(x=75, y=248)
        b3.place(x=145, y=248)
        b4.place(x=215, y=248)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()


# 路径选择
def selectPath():
    path_ = "send " + askopenfilename()
    a.set(path_)


def selectFile():
    global temp_file_path
    file = askopenfilename()
    if os.path.isfile(file):  # 判断文件存在
        temp_file_path = file
        msg = "#send_file " + file + ':;' + user + ':;' + chat
        # a.set(msg)
        s.send(msg.encode('utf-8'))
        send_file()


# 创建表情按钮
eBut = tkinter.Button(root, text='表情', command=express)
eBut.place(x=5, y=320, width=60, height=30)

# 创建文件按钮
fBut = tkinter.Button(root, text='File', command=selectFile)
fBut.place(x=70, y=320, width=60, height=30)

# 创建多行文本框, 显示在线用户
listbox1 = tkinter.Listbox(root)
listbox1.place(x=445, y=0, width=130, height=320)


def showUsers():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        ii = 1


# 查看在线用户按钮
button1 = tkinter.Button(root, text='用户列表', command=showUsers)
button1.place(x=485, y=320, width=90, height=30)

# 创建输入文本框和关联变量
a = tkinter.StringVar()
a.set('')
entry = tkinter.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=350, width=570, height=40)


def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    users.append('【群发】')
    print(chat)
    if chat not in users:
        tkinter.messagebox.showerror('温馨提示', message='没有聊天对象!')
        return
    if chat == user:
        tkinter.messagebox.showerror('温馨提示', message='自己不能和自己进行对话!')
        return
    mes = entry.get() + ':;' + user + ':;' + chat  # 添加聊天对象标记
    s.send(mes.encode())
    a.set('')  # 发送后清空文本框


# 创建发送按钮
button = tkinter.Button(root, text='发送', command=send)
button.place(x=515, y=353, width=60, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息


# 私聊功能
def private(*args):
    global chat
    # 获取点击的索引然后得到内容(用户名)
    indexs = listbox1.curselection()
    index = indexs[0]
    if index > 0:
        chat = listbox1.get(index)
        # 修改客户端名称
        if chat == '【群发】':
            root.title(user)
            return
        ti = user + '  -->  ' + chat
        root.title(ti)


# 在显示用户列表框上设置绑定事件
listbox1.bind('<ButtonRelease-1>', private)


def send_file():
    # while True:
    global temp_file_path
    filename = temp_file_path
    while True:
        if os.path.isfile(filename):  # 判断文件存在
            # 1.先发送文件大小，让客户端准备接收
            size = os.stat(filename).st_size  # 获取文件大小
            s.send(str(size).encode("utf-8"))  # 发送数据长度
            print("发送的大小：", size)

            # 2.发送文件内容
            s.recv(1024)  # 接收确认
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
            listbox.insert(tkinter.END, "\n发送文件成功！", 'red')
        return



# 接受文件
def recv_file(content, recv_name, send_name):
    lock.acquire()

    # 1.先接收长度，建议8192
    server_response = s.recv(1024)
    file_size = int(server_response.decode("utf-8"))
    print("接收到的大小：", file_size)

    # 2.接收文件内容


    print(datetime.now())
    s.recv(1024)  # 接收确认
    # s.send("准备好接收".encode("utf-8"))  # 接收确认
    print("conten" + content)
    # 3.判断是否为文件夹路径
    if "/" in content:
        filename = "new" + content.split(" ")[1].split(":;")[0].split("/")[-1]
    else:
        filename = "new" + content.split(":;")[0]

    dir = "./" + recv_name

    if not os.path.isdir(dir):
        os.mkdir(dir)

    f = open(dir + "/" + filename, "wb")
    received_size = 0
    m = hashlib.md5()

    while received_size < file_size:
        size = 0  # 准确接收数据大小，解决粘包
        if file_size - received_size > 1024:  # 多次接收
            size = 1024
        else:  # 最后一次接收完毕
            size = file_size - received_size
        data = s.recv(size)  # 多次接收内容，接收大数据
        data_len = len(data)
        received_size += data_len
        print("已接收：", int(received_size / file_size * 100), "%")
        m.update(data)
        f.write(data)
    f.close()
    print("实际接收的大小:", received_size)  # 解码

    # 3.md5值校验
    md5_sever = s.recv(1024).decode("utf-8")
    md5_client = m.hexdigest()
    print("服务器发来的md5:", md5_sever)
    print("接收文件的md5:", md5_client)
    if md5_sever == md5_client:
        print("MD5值校验成功")
    else:
        print("MD5值校验失败")
    listbox.insert(tkinter.END, "\n接受文件成功！From："+send_name, 'red')
    lock.release()



# 用于时刻接收服务端发送的信息并打印
def recv():
    global users
    while True:
        data = s.recv(1024)
        data = data.decode()
        print(data)
        # 没有捕获到异常则表示接收到的是在线用户列表
        try:
            data = json.loads(data)
            users = data
            listbox1.delete(0, tkinter.END)  # 清空列表框
            number = ('   在线用户数: ' + str(len(data)))
            listbox1.insert(tkinter.END, number)
            listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
            listbox1.insert(tkinter.END, '【群发】')
            listbox1.itemconfig(tkinter.END, fg='green')
            for i in range(len(data)):
                listbox1.insert(tkinter.END, (data[i]))
                listbox1.itemconfig(tkinter.END, fg='green')

        except:
            if ":;" in data:
                data = data.split(':;')
                # print(data)
                data1 = data[0].strip()  # 消息
                data2 = data[1]  # 发送信息的用户名
                data3 = data[2]  # 聊天对象
                markk = data1.split('：')[1]
                # 判断是不是图片
                pic = markk.split('#')
                # 判断是不是表情
                # 如果字典里有则贴图
                if (markk in dic) or pic[0] == '``':
                    data4 = '\n' + data2 + '：'  # 例:名字-> \n名字：
                    if data3 == '【群发】':
                        if data2 == user:  # 如果是自己则将则字体变为蓝色
                            listbox.insert(tkinter.END, data4, 'blue')
                        else:
                            listbox.insert(tkinter.END, data4, 'green')  # END将信息加在最后一行
                    elif data2 == user or data3 == user:  # 显示私聊
                        listbox.insert(tkinter.END, data4, 'red')  # END将信息加在最后一行
                    listbox.image_create(tkinter.END, image=dic[markk])
                elif "#" in data1:
                    if "#recv_file" in data1:
                        recv_file(content=data1, recv_name=data3, send_name=data2)
                    else:
                        pass
                else:
                    data1 = '\n' + data1
                    if data3 == '【群发】':
                        if data2 == user:  # 如果是自己则将则字体变为蓝色
                            listbox.insert(tkinter.END, data1, 'blue')
                        else:
                            listbox.insert(tkinter.END, data1, 'green')  # END将信息加在最后一行
                        if len(data) == 4:
                            listbox.insert(tkinter.END, '\n' + data[3], 'pink')
                    elif data2 == user or data3 == user:  # 显示私聊

                        listbox.insert(tkinter.END, data1, 'red')  # END将信息加在最后一行
                listbox.see(tkinter.END)  # 显示在最后





r = threading.Thread(target=recv)
r.start()  # 开始线程接收信息

root.mainloop()
s.close()  # 关闭图形界面后关闭TCP连接
