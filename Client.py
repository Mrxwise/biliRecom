import socket
import time
import threading
# -*- coding:utf-8 -*-

#接受已decode数据
def ReceiveMessage(Input_Socket):
    Message_Buff_size = 16
    Server_data,Server_address = Input_Socket.recvfrom(Message_Buff_size)
    Data_decode = Server_data.decode()
    return Data_decode

def CreateClient(UserName,path):
    #UserName += "_1"
    times = 0
    Client_socket = socket.socket()
    Client_socket.settimeout(2)                 #设置timeout
    Server_address = ("106.13.64.200",8887)   #创建client 10.70.87.66   207.246.81.52
    User_file = open(path,'r')
    Trans_list = []
    for line in User_file.readlines():
        Trans_list.append(line)
    User_file.close()
    try:
        Client_socket.connect(Server_address)
        while(times < 5):                   #尝试连接5次，之后放弃
                try:
                    Reponse = ReceiveMessage(Client_socket)
                    if Reponse != 'OK':  # 接受到OK表示连接已经建立
                        raise ConnectionError
                except:
                    Client_socket.sendall(("again").encode())
                    times += 1
                    continue
                else:
                    try:                        #正常发送
                        Client_socket.sendall(("begin").encode())

                        for lines in Trans_list:#发送数据
                            Client_socket.sendall(lines.encode())
                            time.sleep(0.01)
                        Client_socket.sendall(("over").encode()) #文件发送完成
                        Complete_signal = ReceiveMessage(Client_socket)
                        Client_socket.sendall(UserName.encode())#发送用户名
                        #print("send success")
                        return
                    except:
                        #print("trans fail")                    #发送出现问题，就直接跳过
                        break
    except:
        pass
                
                
#CreateClient("USER2","Test.txt")
                    
                
                



        
