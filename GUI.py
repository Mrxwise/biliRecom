import tkinter as tk
from selenium import webdriver
import random
from tkinter import messagebox as mbox
import threading
import re
import os
import Client
import pandas as pd
import AnimaGrab as ani
from urllib.request import urlopen
from PIL import Image,ImageTk
import io
import PIL
import Recommend as recom
import time
class Login_Win:
    def __init__(self):
        self.Root = tk.Tk()
        self.Root.geometry('500x300')
        self.Root.title("ARS")
        self.User = tk.StringVar()
        self.Exit_program = False
        self.User_name = ""
    def Create_window(self):
        Title_label = tk.Label(self.Root, text="<----------------------------欢迎来到推荐系统!---------------------------->")
        Title_label.pack(ipady=20)
        Window_frame = tk.Frame(self.Root)
        Window_frame.pack(expand=tk.YES)
        User_label = tk.Label(Window_frame, text="用户名:")  # 添加标签
        User_text = tk.Entry(Window_frame, textvariable=self.User)  # 添加文本框
        User_label.grid(row=0,column=0)
        User_text.grid(row=0,column=1)
        Button_login = tk.Button(Window_frame, text="登陆", command=self.Login, height=1, width=10)
        Button_exit = tk.Button(Window_frame, text="退出", command=self.Exit, height=1, width=10)  # 按钮可以直接加入命令
        Button_login.grid(row=2, column=0, sticky=tk.W, padx=5, pady=40)
        Button_exit.grid(row=2, column=1, sticky=tk.E, padx=5, pady=40)
    def Exit(self):
        self.Root.destroy()
        self.Exit_program = True
    def Login(self):
        self.Exit_program = False
        if(self.User.get() == ""):
            Message_box1 = mbox.showinfo("输入无效","用户名不能为空！重新输入")
            return
        else:
            self.User_name = self.User.get()
            User_create = open(os.getcwd() + "\\Data\\User\\" + self.User_name + ".txt","w")
            self.Root.destroy()

class Select_Win:
    def __init__(self,User_name):
        self.Root = tk.Tk()
        self.Root.geometry('500x500+200+150')
        self.Root.title("ARS")
        self.User_name = User_name
        self.Anima_info = []
        self.Last_recom = []
        self.Last_simple = []
        self.Anima_position = {}
        self.Anima_id_set = set()
        self.Anima_image_url = {}
        self.Anima_description = {}

        self.Graber_detect = tk.IntVar()
        self.Thread_input = tk.IntVar()
        self.Graber_Local = tk.IntVar()
        self.Graber_new = tk.IntVar()
        self.Graber_detect.set(0)
        self.Graber_Local.set(0)
        self.Graber_new.set(0)
        self.Button_limit = 0
        self.Thread_tip = 0
        self.clear = False
        self.Update_win = None
        self.Broswer_hide = False
        self.Update_large = False
        self.Anima_page_id = None
        self.loading_string = tk.StringVar()
        self.Update_begin = tk.IntVar()
        self.Graber_stop_flag = tk.IntVar()         #使用flag放在线程中，当线程中函数发现stop_flag已经暂停时就return，结束线程
        self.Update_end = tk.IntVar()
        self.show_broswer = True
        self.Graber_thread = None
        self.Show_broswer = None
        self.ProExit = False
        self.Anima_page = None
        self.Safe_write = False
        self.Anima_user_write = []
        self.Anima_user_rewrite = []
        self.Count_time_thread = None                          #用于在程序开始时计时，当到安全时间时直接写入
        self.User_cut_list = []
        self.User_show_page = None

        self.init_program = False
        self.user_matrix = None
        self.recom_list = []
        self.user_list = None
        self.recom_anima_window = None
        self.recom_anima_tag_list = []
        self.recom_anima_image_list = []
        self.recom_anima_page = None
        self.recom_anima_image_url_list = []
        self.recom_anima_wrong_image = []
        self.recom_anima_anima_info = []
        self.first_page_complete = False
        self.second_page_complete = False
        self.user_rewrite = False


        Local_file = open("Data/Anima_list.txt",'r',encoding='utf-8')        #初始化类中的信息，将本地中所有的已知信息进行完善。
        Image_file = open("Data/Image_url.txt",'r')
        Desc_file = open("Data/Description.txt",'r',encoding='utf-8')

        Anima_pattern = "<(.+?)\|\|(.+?)\|\|(.+?)\|\|(.+?)\|\|(.+?)\|\|(.+?)>"
        for anima in Local_file.readlines():
            Detailed_list = []
            anima = anima.strip()
            Anima_info_list = re.findall(Anima_pattern,anima)[0]
            Detailed_list.append(Anima_info_list[0])
            Detailed_list.append(Anima_info_list[1])

            if Anima_info_list[2] == "-":Detailed_list.append([])
            else:
                LIST = []
                tag_list = Anima_info_list[2].split('-')
                for tag in tag_list:LIST.append(tag)
                Detailed_list.append(LIST)
            if Anima_info_list[3] == "-":Detailed_list.append(None)
            else:Detailed_list.append(Anima_info_list[3])
            if Anima_info_list[4] == "-":Detailed_list.append(None)
            else:Detailed_list.append(Anima_info_list[4])
            if Anima_info_list[5] == "-":Detailed_list.append(None)
            else:Detailed_list.append(Anima_info_list[5])
            self.Anima_info.append(Detailed_list)
        index = 0
        for image in Image_file.readlines():
            image = image.strip()
            ID = re.findall("(\d+)===>",image)[0]
            URL = re.findall("===>(.+)",image)[0]
            self.Anima_image_url[ID] = URL
            self.Anima_position[ID] = index
            self.Anima_id_set.add(ID)
            index += 1              #           #
        self.Graber_Local.set(index)
        for desc in Desc_file.readlines():
            desc = desc.strip()
            ID = re.findall("(\d+)===>", desc)[0]
            DESC = re.findall("===>(.+)",desc)
            self.Anima_description[ID] = DESC

        self.Count_time_thread = threading.Thread(target=self.Count_thread)
        self.Count_time_thread.setDaemon(True)
        self.Count_time_thread.start()

    def Count_thread(self):
        #for times in range(2):                  #等待n秒后将安全标志置为True
        #    time.sleep(1)
        self.user_matrix = pd.read_csv('bin/MATRIX.csv',dtype=int)       #将读取Matrix作为安全时间，同时初始化推荐。
        self.user_list = pd.read_csv('bin/USER.csv')
        self.recom_list = self.user_matrix.columns.values.tolist()
        self.user_list = self.user_list.drop_duplicates()               #对用户列表进行去重，填空处理，同时将元素化为int再化为str来减去float
        self.user_list = self.user_list.fillna(0).astype(int)
        self.user_list = self.user_list.astype(str)                                    #对用户矩阵同样需要转化float
        self.user_matrix = pd.DataFrame(self.user_matrix)
        self.user_list = pd.DataFrame(self.user_list)
        self.recom_list.pop(0)
        self.init_program = True                                #初始化成功
        if self.Anima_user_rewrite != []:
            User_file = open("Data/User/" + self.User_name + '.txt','w')
            for lines in self.Anima_user_rewrite:
                User_file.write(lines + '\n')
            User_file.close()
        self.Anima_user_rewrite.clear()
        if self.user_rewrite == True:
            User_file = open("Data/User/" + self.User_name + '.txt','a')
            for lines in self.Anima_user_write:
                User_file.write(lines + '\n')
                if self.ProExit == True:
                    return
            User_file.close()
        self.Anima_user_write.clear()
        self.Safe_write = True
        return

    def Create_window(self):
        Title_label = tk.Label(self.Root, text="欢迎! " + self.User_name)
        Title_label.pack(ipady=20)
        Window_frame = tk.Frame(self.Root, width=560, height=600)  # 向当前窗口中添加容器
        Window_frame.pack(expand=tk.YES)  # 将容器添加到窗口中

        Button_frame = tk.Frame(Window_frame)
        Button_frame.grid(row=0, column=0, sticky="nswe")

        Deco_image = tk.PhotoImage(file=os.getcwd()+ "/bin/Deco.gif")      #需要加file来表示图片0
        Deco_Label = tk.Label(Window_frame, width=240, height=320,image=Deco_image)
        Deco_Label.image = Deco_image
        Deco_Label.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        loading_text = tk.Label(Button_frame,textvariable=self.loading_string)

        Button_Lucky = tk.Button(Button_frame, text="手气不错！", width=8, command=self.Try_luck)
        Button_Recommend = tk.Button(Button_frame, text="推荐", width=8, command=self.Recommend)
        Button_Update = tk.Button(Button_frame, text="升级数据", width=8, command=self.Update)

        Button_input_user = tk.Button(Button_frame,text='关于',width=8,command=self.About)
        Button_show_user = tk.Button(Button_frame, text='查看用户', width=8, command=self.Show_user)
        Button_About = tk.Button(Button_frame, text="清除用户", width=8,command=self.Clear)  # 使用窗口.destroy可以正确关闭窗口，使用quit无法正确关闭窗口
        Button_Exit = tk.Button(Button_frame, text="退出", width=8, command=self.Exit)  # 主菜单按钮实例

        Button_Lucky.grid(row=0,column=0,sticky="nsew",padx=15,pady=30,columnspan=2)                            #对于grid布局方式，要想合并单元格，不能让第一个防入单元格的组件过大
        Button_Recommend.grid(row=1,column=0,sticky="nsew",padx=15,pady=10,columnspan=2)
        loading_text.grid(row=2,column=0)
        Button_Update.grid(row=3,column=0,sticky="nsew",padx=15,pady=10,columnspan=2)
        Button_input_user.grid(row=4,column=0,sticky='nsew',padx=5,pady=10)
        Button_show_user.grid(row=4, column=1, sticky='nsew', padx=5, pady=10)
        Button_About.grid(row=6,column=0,padx=5,pady=15)
        Button_Exit.grid(row=6,column=1,padx=5,pady=15)

    def Create_update_window(self):
        self.Update_win = tk.Toplevel()
        #Top_window = tk.Toplevel()
        self.Update_win.geometry('400x300+400+300')
        update_frame = tk.Frame(self.Update_win, width=400, height=500)
        update_frame.pack(expand=tk.YES)

        Thread_label = tk.Label(update_frame,text="运行线程数(最好别超6个):")
        Thread_Entry = tk.Entry(update_frame,textvariable=self.Thread_input)

        Detect_label = tk.Label(update_frame, text="检测到的动漫数:")
        Detect_count = tk.Label(update_frame,textvariable=self.Graber_detect)
        New_label = tk.Label(update_frame, text="检测到的本地没有的动漫数:")
        New_count = tk.Label(update_frame,textvariable=self.Graber_new)
        Local_label = tk.Label(update_frame,text="本地已有的动漫数:")
        Local_count = tk.Label(update_frame,textvariable=self.Graber_Local)

        Deep_Text = tk.Label(update_frame, text="重新读取所有动漫(耗时极长)")
        Deep_check = tk.Checkbutton(update_frame,command=self.Deep_click)

        Show_broswer = tk.Label(update_frame,text="查看搜索浏览器状态：")
        Show_check = tk.Checkbutton(update_frame,command=self.Show_click)

        Begin_button = tk.Button(update_frame, text="开始", command=self.Update_start, width=10, height=1)
        Exit_button = tk.Button(update_frame, text="退出", command=self.Update_exit, width=10, height=1)

        Thread_label.grid(row=0,column=0,padx=5,pady=10)
        Thread_Entry.grid(row=0,column=2,columnspan=2)

        Deep_Text.grid(row=1,column=0,padx=5,pady=10)
        Deep_check.grid(row=1,column=1)
        Show_broswer.grid(row=1,column=2,padx=5)
        Show_check.grid(row=1,column=3,padx=5)

        Detect_label.grid(row=2,column=0,padx=5)
        Detect_count.grid(row=2,column=2,columnspan=2)

        New_label.grid(row=3,column=0,padx=5)
        New_count.grid(row=3,column=2,columnspan=2)

        Local_label.grid(row=4,column=0,padx=5)
        Local_count.grid(row=4,column=2,columnspan=2)

        Begin_button.grid(row=5,column=0,pady=15)
        Exit_button.grid(row=5,column=2,columnspan=2)

        self.Update_win.title("Update")
        self.Update_win.mainloop()

        #self.Graber_thread = StopThread(target=ani.Update,args=(0,2,self.Graber_detect,self.Graber_new,self.Graber_Local,4,self.Anima_id_set))
    def Deep_click(self):
        if self.Update_large == False:
            self.Update_large = True
        elif self.Update_large == True:
            self.Update_large = False
    def Show_click(self):
        if self.show_broswer == False:
            self.show_broswer = True
        else:
            self.show_broswer = False
    def Update_start(self):
        try:
            Thread_input = self.Thread_input.get()
        except:
            Messbox2 = mbox.showinfo(">_<","输入线程数目错误！")
            return
        if Thread_input > 6:
            Messbox3 = mbox.showinfo("提示","过多线程可能导致未知错误！你确定吗?<_<\n或者开启查看浏览器状态，防止程序暂停<_<")
            self.Thread_tip -= 1
        elif Thread_input <= 0:
            Messbox4 = mbox.showinfo("错误>_<","你输入的线程数目无效>_<")
            return
        if self.Button_limit == 1:
            self.Button_limit -= 1
            self.Graber_detect.set(0)
            self.Graber_new.set(0)
            if self.Update_large == False:
                self.Graber_thread = threading.Thread(target=ani.Update, args=(1, 20, self.Graber_detect, self.Graber_new, self.Graber_Local, Thread_input, self.Anima_id_set,self.Graber_stop_flag,self.show_broswer))
            elif self.Update_large == True:
                self.Graber_thread = threading.Thread(target=ani.Update,args=(1, 155,self.Graber_detect,self.Graber_new,self.Graber_Local,Thread_input,self.Anima_id_set,self.Graber_stop_flag,self.show_broswer))
            self.Graber_thread.setDaemon(True)
            self.Graber_thread.start()
    def Update_exit(self):
        self.Graber_stop_flag.set(0)
        self.Update_win.destroy()           #若更新信息超过10条，就自动更新内存信息。
        if self.Graber_new.get() >= 10:
            Local_file = open("Data/Anima_list.txt", 'r',encoding='utf-8')  # 初始化类中的信息，将本地中所有的已知信息进行完善。
            Image_file = open("Data/Image_url.txt", 'r')
            Desc_file = open("Data/Description.txt", 'r', encoding='utf-8')

            Anima_pattern = "<(.+?)\|\|(.+?)\|\|(.+?)\|\|(.+?)\|\|(.+?)\|\|(.+?)>"
            for anima in Local_file.readlines():
                Detailed_list = []
                anima = anima.strip()
                Anima_info_list = re.findall(Anima_pattern, anima)[0]
                Detailed_list.append(Anima_info_list[0])
                Detailed_list.append(Anima_info_list[1])

                if Anima_info_list[2] == "-":
                    Detailed_list.append([])
                else:
                    LIST = []
                    tag_list = Anima_info_list[2].split('-')
                    for tag in tag_list: LIST.append(tag)
                    Detailed_list.append(LIST)
                if Anima_info_list[3] == "-":
                    Detailed_list.append(None)
                else:
                    Detailed_list.append(Anima_info_list[3])
                if Anima_info_list[4] == "-":
                    Detailed_list.append(None)
                else:
                    Detailed_list.append(Anima_info_list[4])
                if Anima_info_list[5] == "-":
                    Detailed_list.append(None)
                else:
                    Detailed_list.append(Anima_info_list[5])
                self.Anima_info.append(Detailed_list)
            index = 0
            for image in Image_file.readlines():
                image = image.strip()
                ID = re.findall("(\d+)===>", image)[0]
                URL = re.findall("===>(.+)", image)[0]
                self.Anima_image_url[ID] = URL
                self.Anima_position[ID] = index
                self.Anima_id_set.add(ID)
                index += 1  # #
            self.Graber_Local.set(index)
            for desc in Desc_file.readlines():
                desc = desc.strip()
                ID = re.findall("(\d+)===>", desc)[0]
                DESC = re.findall("===>(.+)", desc)
                self.Anima_description[ID] = DESC

    def Check_close(self):
        while True:
            try:
                A = self.Show_broswer.current_url
            except:
                self.Show_broswer.quit()
                return
    def Show_Anima(self,Anima_id):
        self.Anima_page_id = Anima_id
        self.Anima_page = tk.Toplevel()
        self.Anima_page.title("详情")
        self.Anima_page.geometry('+300+50')
        if len(self.Last_simple) > 20:
            self.Last_simple.pop(0)
        self.Last_simple.append(Anima_id)

        Detailed_info = self.Anima_info[self.Anima_position[Anima_id]]
        Image_url = self.Anima_image_url[Anima_id]
        Anima_desc = self.Anima_description[Anima_id]


        if len(Anima_desc[0]) <= 200:width = 200
        elif len(Anima_desc[0]) <= 300:width = 250
        elif len(Anima_desc[0]) <= 400:width = 320
        else:width = 400


        Name = Detailed_info[0]
        Tag_list = Detailed_info[2]
        Score = Detailed_info[3]
        Heat = Detailed_info[4]
        Time = Detailed_info[5]
        Time.replace("年",".")
        Time.replace("月", ".")
        Time.replace("日", ".")

        Tag = ""
        if Tag_list != []:
            for tag in Tag_list:Tag += tag + " "
        else:Tag = "-"
        if Score == None:Score = "-"
        if Heat == None: Heat = "-"
        if Time == None: Time = "-"

        try:
            Image_bytes = urlopen(Image_url).read()
            data_stream = io.BytesIO(Image_bytes)
            Anima_image = Image.open(data_stream)
        except:
            Anima_image = Image.open("bin/Neterror.JPG")

        ImageX = 240
        ImageY = 320
        Resize_image = Anima_image.resize((ImageX,ImageY),PIL.Image.ANTIALIAS)

        Anima_frame = tk.Frame(self.Anima_page)
        Button_frame = tk.Frame(self.Anima_page)
        Anima_frame.pack()
        Button_frame.pack()

        Desc_frame = tk.Frame(Anima_frame)
        Imag_frame = tk.Frame(Anima_frame, width=240, height=320)
        Desc_frame.grid(row=0, column=1)
        Imag_frame.grid(row=0, column=0)

        Title_label = tk.Label(Desc_frame, text=Name, wraplength=150,pady=15)
        Tag_label = tk.Label(Desc_frame, text="标签:" + Tag, wraplength=150)
        Score_label = tk.Label(Desc_frame, text="评分:" + Score)
        Heat_label = tk.Label(Desc_frame, text="热度:" + Heat)
        Time_label = tk.Label(Desc_frame, text="开播时间:" + Time)
        Description_label = tk.Label(Desc_frame, text=Anima_desc, wraplength=width)
        Image_show = ImageTk.PhotoImage(Resize_image)
        Image_label = tk.Label(Imag_frame, image=Image_show)

        Title_label.grid(row=0, column=0, columnspan=2)
        Tag_label.grid(row=1, column=0, columnspan=2)
        Score_label.grid(row=2, column=0, columnspan=2)
        Time_label.grid(row=3,column=0,columnspan=2)
        Heat_label.grid(row=4,column=0,columnspan=2)
        Image_label.pack(padx=15, pady=15)
        Description_label.grid(row=5, column=0, columnspan=2, pady=15,padx=10)

        Button_copy = tk.Button(Button_frame, text="详细情况", command=self.Copy_net, width=10)
        Button_fav = tk.Button(Button_frame, text="喜欢", command=self.Fav, width=8)
        Button_like = tk.Button(Button_frame, text="一般", command=self.Like, width=8)
        Button_look = tk.Button(Button_frame, text="没兴趣", command=self.Dont, width=8)
        Button_exit = tk.Button(Button_frame, text="不知道", command=self.Show_exit, width=8)
        Hide_label = tk.Label(Button_frame,text='无痕浏览')
        Check_label = tk.Checkbutton(Button_frame,variable=True,command=self.Broswer_set)
        Button_copy.grid(row=0,column=0 , padx=30)
        Button_fav.grid(row=0, column=1, padx=10, columnspan = 2)
        Button_like.grid(row=0, column=4, padx=10,columnspan = 2)
        Button_look.grid(row=0, column=6, padx=10,columnspan = 2)
        Button_exit.grid(row=0, column=9, padx=10,columnspan = 2)
        Hide_label.grid(row=1,column=0)
        Check_label.grid(row=1,column=1,pady = 15)
        self.Anima_page.mainloop()
    def Broswer_set(self):
        if self.Broswer_hide == True:
            self.Broswer_hide = False
        else:self.Broswer_hide = True
    def Copy_net(self):
        URL = "https://www.bilibili.com/bangumi/media/md"
        URL += self.Anima_page_id
        Driver = os.path.abspath("bin/chromedriver.exe")
        Chrome_opt = webdriver.ChromeOptions()
        if self.Broswer_hide == True:Chrome_opt.add_argument('--incognito')
        Chrome_opt.add_argument('disable-infobars')
        try:
            self.Show_broswer = webdriver.Chrome(chrome_options=Chrome_opt,executable_path=Driver)
            self.Show_broswer.get(URL)
            new_thread = threading.Thread(target=self.Check_close)
            new_thread.start()
        except:
            self.Show_broswer.quit()


    def Show_exit(self):
        self.Anima_page.destroy()
        if self.Show_broswer != None:
            CloseThread = threading.Thread(target=self.Show_broswer.quit)
            CloseThread.setDaemon(True)
            CloseThread.start()
        return
    def Like(self):
        Write_in = "<LIKE "
        Write_in += self.Anima_page_id
        Write_in += ">"
        self.Anima_page.destroy()
        if self.Safe_write == True:
            User_file = open("Data/User/" + self.User_name + ".txt",'a')
            User_file.write(Write_in + '\n')
            User_file.close()
        else:self.Anima_user_write.append(Write_in)
    def Dont(self):
        Write_in = "<DONT "
        Write_in += self.Anima_page_id
        Write_in += ">"
        self.Anima_page.destroy()
        if self.Safe_write == True:
            User_file = open("Data/User/" + self.User_name + ".txt",'a')
            User_file.write(Write_in + '\n')
            User_file.close()
        else:self.Anima_user_write.append(Write_in)
    def Fav(self):
        Write_in = "<LIKE "
        Write_in += self.Anima_page_id
        Write_in += ">"
        self.Anima_page.destroy()
        if self.Safe_write == True:
            User_file = open("Data/User/" + self.User_name + ".txt", 'a')
            User_file.write(Write_in + '\n')
            User_file.write(Write_in + '\n')
            User_file.write(Write_in + '\n')                    #对于Favourite的Anima一次性写入三次
            User_file.close()
        else:
            self.Anima_user_write.append(Write_in)
            self.Anima_user_write.append(Write_in)
            self.Anima_user_write.append(Write_in)

    def Create_show_user(self):
        self.user_rewrite = False
        self.Anima_user_rewrite.clear()
        self.User_show_page = tk.Toplevel()
        self.User_show_page.title("用户详情")
        self.User_show_page.geometry('+200+200')
        Text_Frame = tk.Frame(self.User_show_page,width=250,height=400,padx=40,pady=20)
        Button_Frame = tk.Frame(self.User_show_page,padx=40,pady=20)
        Text_Frame.pack()
        Button_Frame.pack()
        self.User_show_list = tk.Listbox(Text_Frame,width=40,height=20)
        self.User_show_list.pack()
        Like_pattern = "<LIKE (\d+)>"
        Dont_pattern = "<DONT (\d+)>"
        User_file = open("Data/User/" + self.User_name + ".txt",'r')            #以只读的方式打开并不会影响多线程，多线程中打开可以分别处理
        for lines in User_file.readlines():
            lines = lines.strip()
            if lines == "":continue
            Check = re.findall(Like_pattern, lines)
            if Check != []:
                Show_line = "%-20s \t %-20s" % ("LIKE ID:"+ self.Anima_info[self.Anima_position[Check[0]]][1],"NAME:" +  self.Anima_info[self.Anima_position[Check[0]]][0])
                self.User_show_list.insert(tk.END,Show_line)
            else:
                Check = re.findall(Dont_pattern, lines)
                Show_line = "%-20s%-20s" % ("DONT ID:"+ self.Anima_info[self.Anima_position[Check[0]]][1],"NAME:" +  self.Anima_info[self.Anima_position[Check[0]]][0])
                self.User_show_list.insert(tk.END,Show_line)
        Button_Save = tk.Button(Button_Frame,text="保存并返回",command=self.save_exit)
        Button_Remove = tk.Button(Button_Frame,text="删除条目",command=self.click_delete)

        Button_Save.grid(row=0,column=2,padx=10,pady=10)
        Button_Remove.grid(row=0,column=0)

        self.User_show_page.mainloop()
    def save_exit(self):
        Write_tuple = self.User_show_list.get(0,tk.END)
        self.user_rewrite = True
        if self.Safe_write == True:
            User_file = open("Data/User/" + self.User_name + ".txt", 'w')
        for item in Write_tuple:
            Like_pattern = "LIKE ID:(\d+)"
            Dont_pattern = "DONT ID:(\d+)"
            Check = re.findall(Like_pattern, item)
            if Check != []:
                Write = "<LIKE " + Check[0] + ">"
                if self.Safe_write == True:
                    User_file.write(Write + '\n')
                else:
                    self.Anima_user_rewrite.append(Write)
            else:
                Check = re.findall(Dont_pattern, item)
                Write = "<DONT " + Check[0] + ">"
                if self.Safe_write == True:
                    User_file.write(Write + '\n')
                else:
                    self.Anima_user_rewrite.append(Write)
        if self.Safe_write == True:
            User_file.close()
        self.User_show_page.destroy()
    def click_delete(self):
        self.User_show_list.delete(tk.ACTIVE)       #tk.ACTIVE表示当前选定的值

    def Create_recommend_win(self,recommend_list):
        self.recom_anima_window = tk.Toplevel()
        self.recom_anima_window.geometry('750x650+200+20')

        for id in recommend_list:
            self.recom_anima_image_url_list.append(self.Anima_image_url[id])
            self.recom_anima_anima_info.append(list(self.Anima_info[self.Anima_position[id]]))
            anima = self.Anima_info[self.Anima_position[id]]
            if anima[2] == []:
                tag = "-"
            else:
                tag = ""
                for text in anima[2]:
                    tag += text +" "
            self.recom_anima_tag_list.append(tag)
        for index in range(len(self.recom_anima_anima_info)):
            if self.recom_anima_anima_info[index][3] == None:
                self.recom_anima_anima_info[index][3] = '-'

        self.recom_anima_page = tk.Frame(self.recom_anima_window)
        Button_frame = tk.Frame(self.recom_anima_window)
        self.recom_anima_page.grid(row=0,column=0)

        Button_frame.grid(row=1,column=0)

        self.page_first()                           #开始时载入第一页
        Button_first = tk.Button(Button_frame,text="第一页",command=self.page_first,width=7)
        Button_second = tk.Button(Button_frame, text="第二页", command=self.page_second, width=7)
        Button_exit = tk.Button(Button_frame, text="退出", command=self.recom_exit, width=10)

        self.loading_string.set("")
        Button_first.grid(row=0, column=1, padx=5)
        Button_second.grid(row=0, column=2, padx=5)
        Button_exit.grid(row=0, column=3, padx=15, pady=20)

        self.recom_anima_window.title("推荐")
        self.recom_anima_window.mainloop()
    def get_image(self,image_url,index):
        try:
            Image_bytes = urlopen(image_url).read()
            data_stream = io.BytesIO(Image_bytes)
            Anima_image = Image.open(data_stream)
            if index in self.recom_anima_wrong_image:
                self.recom_anima_wrong_image.remove(index)
            return Anima_image
        except:
            Anima_image = Image.open("bin/" + "Neterror.JPG")
            if index not in self.recom_anima_wrong_image:
                self.recom_anima_wrong_image.append(index)
            return Anima_image
    def page_first(self):
        if self.recom_anima_page != None:
            self.recom_anima_page.destroy()
        self.recom_anima_page = tk.Frame(self.recom_anima_window)
        self.recom_anima_page.grid(row=0,column=0)

        if self.first_page_complete == False:
            for index in range(4):
                self.recom_anima_image_list.append(self.get_image(self.recom_anima_image_url_list[index],index))
                self.recom_anima_image_list[index] = self.recom_anima_image_list[index].resize((120,160),PIL.Image.ANTIALIAS)
                self.recom_anima_image_list[index] = ImageTk.PhotoImage(self.recom_anima_image_list[index])
            self.first_page_complete = True
        if self.recom_anima_wrong_image != []:
            for index in self.recom_anima_wrong_image:
                self.recom_anima_image_list[index] = self.get_image(self.recom_anima_image_url_list[index],index)
                self.recom_anima_image_list[index] = self.recom_anima_image_list[index].resize((120, 160),PIL.Image.ANTIALIAS)
                self.recom_anima_image_list[index] = ImageTk.PhotoImage(self.recom_anima_image_list[index])

        Image1_frame = tk.Frame(self.recom_anima_page)
        Image2_frame = tk.Frame(self.recom_anima_page)
        Image3_frame = tk.Frame(self.recom_anima_page)
        Image4_frame = tk.Frame(self.recom_anima_page)

        Image1_frame.grid(row=0, column=0, padx=80, pady=60)
        Image2_frame.grid(row=0, column=1, padx=60, pady=60)
        Image3_frame.grid(row=1, column=0, padx=80, pady=60)
        Image4_frame.grid(row=1, column=1, padx=60, pady=60)

        Image_label1 = tk.Label(Image1_frame, image=self.recom_anima_image_list[0])
        Image_label2 = tk.Label(Image2_frame, image=self.recom_anima_image_list[1])
        Image_label3 = tk.Label(Image3_frame, image=self.recom_anima_image_list[2])
        Image_label4 = tk.Label(Image4_frame, image=self.recom_anima_image_list[3])

        First_button = tk.Button(Image1_frame, text="详细", command=self.First, height=1)
        Second_button = tk.Button(Image2_frame, text="详细", command=self.Second, height=1)
        Third_button = tk.Button(Image3_frame, text="详细", command=self.Third, height=1)
        Fourth_button = tk.Button(Image4_frame, text="详细", command=self.Forth, height=1)

        First_title_label = tk.Label(Image1_frame, text=self.recom_anima_anima_info[0][0], wraplength=100)
        First_tag_label = tk.Label(Image1_frame, text="标签: " + self.recom_anima_tag_list[0], wraplength=100)
        First_score_table = tk.Label(Image1_frame, text="评分: " + self.recom_anima_anima_info[0][3])

        Second_title_label = tk.Label(Image2_frame, text=self.recom_anima_anima_info[1][0], wraplength=100)
        Second_tag_label = tk.Label(Image2_frame, text="标签: " + self.recom_anima_tag_list[1], wraplength=100)
        Second_score_table = tk.Label(Image2_frame, text="评分: " + self.recom_anima_anima_info[1][3])

        Third_title_label = tk.Label(Image3_frame, text=self.recom_anima_anima_info[2][0], wraplength=100)
        Third_tag_label = tk.Label(Image3_frame, text="标签: " + self.recom_anima_tag_list[2], wraplength=100)
        Third_score_table = tk.Label(Image3_frame, text="评分: " + self.recom_anima_anima_info[2][3])

        Fourth_title_label = tk.Label(Image4_frame, text=self.recom_anima_anima_info[3][0], wraplength=100)
        Fourth_tag_label = tk.Label(Image4_frame, text="标签: " + self.recom_anima_tag_list[3], wraplength=100)
        Fourth_score_table = tk.Label(Image4_frame, text="评分: " + self.recom_anima_anima_info[3][3])

        Image_label1.grid(row=0, column=0, rowspan=5)
        First_title_label.grid(row=0, column=1)
        First_tag_label.grid(row=1, column=1)
        First_score_table.grid(row=2, column=1)
        First_button.grid(row=3, column=1)

        Image_label2.grid(row=0, column=0, rowspan=5)
        Second_title_label.grid(row=0, column=1)
        Second_tag_label.grid(row=1, column=1)
        Second_score_table.grid(row=2, column=1)
        Second_button.grid(row=3, column=1)

        Image_label3.grid(row=0, column=0, rowspan=5)
        Third_title_label.grid(row=0, column=1)
        Third_tag_label.grid(row=1, column=1)
        Third_score_table.grid(row=2, column=1)
        Third_button.grid(row=3, column=1)

        Image_label4.grid(row=0, column=0, rowspan=5)
        Fourth_title_label.grid(row=0, column=1)
        Fourth_tag_label.grid(row=1, column=1)
        Fourth_score_table.grid(row=2, column=1)
        Fourth_button.grid(row=3, column=1)

        self.recom_anima_page.grid(row=0, column=0)
    def page_second(self):

        if self.recom_anima_page != None:
            self.recom_anima_page.destroy()
        self.recom_anima_page = tk.Frame(self.recom_anima_window)
        self.recom_anima_page.grid(row=0,column=0)

        if self.second_page_complete == False:
            for index in range(4,8):
                self.recom_anima_image_list.append(self.get_image(self.recom_anima_image_url_list[index],index))
                self.recom_anima_image_list[index] = self.recom_anima_image_list[index].resize((120,160),PIL.Image.ANTIALIAS)
                self.recom_anima_image_list[index] = ImageTk.PhotoImage(self.recom_anima_image_list[index])
                self.second_page_complete = True
        if self.recom_anima_wrong_image != []:
            for index in self.recom_anima_wrong_image:
                self.recom_anima_image_list[index] = self.get_image(self.recom_anima_image_url_list[index],index)
                self.recom_anima_image_list[index] = self.recom_anima_image_list[index].resize((120, 160),PIL.Image.ANTIALIAS)
                self.recom_anima_image_list[index] = ImageTk.PhotoImage(self.recom_anima_image_list[index])

        Image1_frame = tk.Frame(self.recom_anima_page)
        Image2_frame = tk.Frame(self.recom_anima_page)
        Image3_frame = tk.Frame(self.recom_anima_page)
        Image4_frame = tk.Frame(self.recom_anima_page)

        Image1_frame.grid(row=0, column=0, padx=80, pady=60)
        Image2_frame.grid(row=0, column=1, padx=60, pady=60)
        Image3_frame.grid(row=1, column=0, padx=80, pady=60)
        Image4_frame.grid(row=1, column=1, padx=60, pady=60)

        Image_label1 = tk.Label(Image1_frame, image=self.recom_anima_image_list[4])
        Image_label2 = tk.Label(Image2_frame, image=self.recom_anima_image_list[5])
        Image_label3 = tk.Label(Image3_frame, image=self.recom_anima_image_list[6])
        Image_label4 = tk.Label(Image4_frame, image=self.recom_anima_image_list[7])

        First_button = tk.Button(Image1_frame, text="详细", command=self.Fifth, height=1)
        Second_button = tk.Button(Image2_frame, text="详细", command=self.Sixth, height=1)
        Third_button = tk.Button(Image3_frame, text="详细", command=self.Seventh, height=1)
        Fourth_button = tk.Button(Image4_frame, text="详细", command=self.Eight, height=1)

        First_title_label = tk.Label(Image1_frame, text=self.recom_anima_anima_info[4][0], wraplength=100)
        First_tag_label = tk.Label(Image1_frame, text="标签: " + self.recom_anima_tag_list[4], wraplength=100)
        First_score_table = tk.Label(Image1_frame, text="评分: " + self.recom_anima_anima_info[4][3])

        Second_title_label = tk.Label(Image2_frame, text=self.recom_anima_anima_info[5][0], wraplength=100)
        Second_tag_label = tk.Label(Image2_frame, text="标签: " + self.recom_anima_tag_list[5], wraplength=100)
        Second_score_table = tk.Label(Image2_frame, text="评分: " + self.recom_anima_anima_info[5][3])

        Third_title_label = tk.Label(Image3_frame, text=self.recom_anima_anima_info[6][0], wraplength=100)
        Third_tag_label = tk.Label(Image3_frame, text="标签: " + self.recom_anima_tag_list[6], wraplength=100)
        Third_score_table = tk.Label(Image3_frame, text="评分: " + self.recom_anima_anima_info[6][3])

        Fourth_title_label = tk.Label(Image4_frame, text=self.recom_anima_anima_info[7][0], wraplength=100)
        Fourth_tag_label = tk.Label(Image4_frame, text="标签: " + self.recom_anima_tag_list[7], wraplength=100)
        Fourth_score_table = tk.Label(Image4_frame, text="评分: " + self.recom_anima_anima_info[7][3])

        Image_label1.grid(row=0, column=0, rowspan=5)
        First_title_label.grid(row=0, column=1)
        First_tag_label.grid(row=1, column=1)
        First_score_table.grid(row=2, column=1)
        First_button.grid(row=3, column=1)

        Image_label2.grid(row=0, column=0, rowspan=5)
        Second_title_label.grid(row=0, column=1)
        Second_tag_label.grid(row=1, column=1)
        Second_score_table.grid(row=2, column=1)
        Second_button.grid(row=3, column=1)

        Image_label3.grid(row=0, column=0, rowspan=5)
        Third_title_label.grid(row=0, column=1)
        Third_tag_label.grid(row=1, column=1)
        Third_score_table.grid(row=2, column=1)
        Third_button.grid(row=3, column=1)

        Image_label4.grid(row=0, column=0, rowspan=5)
        Fourth_title_label.grid(row=0, column=1)
        Fourth_tag_label.grid(row=1, column=1)
        Fourth_score_table.grid(row=2, column=1)
        Fourth_button.grid(row=3, column=1)

        self.recom_anima_page.grid(row=0, column=0)
    def recom_exit(self):
        self.recom_anima_window.destroy()

    def First(self):
        self.Show_Anima(self.recom_anima_anima_info[0][1])
    def Second(self):
        self.Show_Anima(self.recom_anima_anima_info[1][1])
    def Third(self):
        self.Show_Anima(self.recom_anima_anima_info[2][1])
    def Forth(self):
        self.Show_Anima(self.recom_anima_anima_info[3][1])
    def Fifth(self):
        self.Show_Anima(self.recom_anima_anima_info[4][1])
    def Sixth(self):
        self.Show_Anima(self.recom_anima_anima_info[5][1])
    def Seventh(self):
        self.Show_Anima(self.recom_anima_anima_info[6][1])
    def Eight(self):
        self.Show_Anima(self.recom_anima_anima_info[7][1])


    def Try_luck(self):
        if len(self.Anima_id_set) <= 200:
            Messbox4 = mbox.showinfo("警告","本地保存的Animation数量过少！")
            return
        if self.init_program == False:
            Messbox5 = mbox.showinfo("Please Wait","正在初始化请等几秒┑(￣Д ￣)┍")
            return
        Anima_recom_list = recom.Recommend(self.Anima_info,self.Anima_position,self.User_name,set(self.Last_simple),self.user_matrix,self.recom_list,self.user_list)
        try:
            Anima_ID = Anima_recom_list[random.randint(0,5)]
        except:
            Messbox6 = mbox.showinfo("Warning", "已经找不到可以推荐的动漫了，请删除用户重新开始┑(￣Д ￣)┍")
            return
        self.Show_Anima(Anima_ID)
    def Recommend(self):
        if len(self.Anima_id_set) <= 200:
            Messbox4 = mbox.showinfo("警告","本地保存的Animation数量过少！")
            return
        if self.init_program == False:
            Messbox5 = mbox.showinfo("Please Wait","正在初始化请等几秒┑(￣Д ￣)┍")
            return
        Anima_recom_list = recom.Recommend(self.Anima_info,self.Anima_position,self.User_name,set(self.Last_recom),self.user_matrix,self.recom_list,self.user_list)
        if len(Anima_recom_list) <= 7:
            Messbox7 = mbox.showinfo("Warning", "已经找不到可以推荐的动漫了，请删除用户重新开始┑(￣Д ￣)┍")
            return
        self.loading_string.set("加载中...")
        self.recom_anima_tag_list.clear()           #清空已经保存的信息
        self.recom_anima_image_list.clear()
        self.recom_anima_page = None
        self.recom_anima_image_url_list.clear()
        self.recom_anima_anima_info.clear()
        self.first_page_complete = False
        self.second_page_complete = False

        self.Create_recommend_win(Anima_recom_list)

        #需要调整位置------------------
        if(len(self.Last_recom)) > 40:
            for i in range(8):self.Last_recom.pop(0)
        self.Last_recom += Anima_recom_list
        #--------------------------------------------------------
    def Update(self):#https://www.jianshu.com/p/7b6a80faf33f，在Update中，使用一个线程调用Update函数，注意该线程应该设置为可关闭的线程。
        self.Button_limit = 1
        self.Thread_tip = 1
        self.Thread_input.set(2)
        self.Graber_detect.set(0)
        self.Graber_new.set(0)
        self.Graber_stop_flag.set(1)
        self.Create_update_window()
    def Show_user(self):
        self.Create_show_user()
    def About(self):
        self.User_input_page = tk.Toplevel()
        self.User_input_page.title("关于")
        self.User_input_page.geometry('400x200+200+200')
        Text_frame = tk.Frame(self.User_input_page)
        Button_frame = tk.Frame(self.User_input_page)
        Text_frame.pack()
        Button_frame.pack()
        Hit_label = tk.Label(Text_frame,text="欢迎使用！本程序用于获取B站动漫信息，并进行推荐>_<\n如果有BUG请发邮件到mvpgenius@qq.com>_<", wraplength=200)
        Text_label = tk.Label(Text_frame,text="Writer:(*_*)")
        Hit_label.grid(row=0,column=0,columnspan=2)
        Text_label.grid(row=1,column=0,pady=25)
        Exit_button = tk.Button(Button_frame,text="返回",command=self.User_input_page.destroy)
        Exit_button.pack()
        self.User_input_page.mainloop()
    def Clear(self):
        self.Exit()
        self.Count_time_thread.join()
        for times in range(5):
            try:
                os.remove('Data/User/' + self.User_name + '.txt')
                break
            except:
                time.sleep(1)
                if times == 4:self.clear = True
    def Exit(self):
        self.Root.destroy()
        self.ProExit = True
        if self.Anima_user_write != []:
            User_file = open("Data/User/" + self.User_name + '.txt','a')
            for lines in self.Anima_user_write:
                User_file.write(lines + '\n')
            User_file.close()
        if self.Anima_user_rewrite != []:
            User_file = open("Data/User/" + self.User_name + '.txt','w')
            for lines in self.Anima_user_rewrite:
                User_file.write(lines + '\n')
            User_file.close()
        return

def Create_root_window():
    Windows = Login_Win()
    Windows.Create_window()
    Windows.Root.mainloop()
    if(Windows.Exit_program != True):
                                #<<--------选择窗口
        Select_windows = Select_Win(Windows.User_name)
        Select_windows.Create_window()
        Select_windows.Root.mainloop()
    else:
        return

def Send_Client(Nickname):
    lines = 0
    File_open = open(os.getcwd()+"/Data/User/" + Nickname + ".txt",'r')
    for line in File_open.readlines():
        lines += 1
    if lines >= 10:
        Client.CreateClient(Nickname,os.getcwd()+"/Data/User/" + Nickname + ".txt")
        pass
def Create_root():
    #程序进程的判断变量
    #创建所有需要的数据文件
    if os.path.exists("Data/Anima_id_dect.txt") == False:
        File = open("Data/Anima_id_dect.txt",'w')
        File.close()
    if os.path.exists("Data/Anima_list.txt") == False:
        Local_file = open("Data/Anima_list.txt", 'w')
        Image_file = open("Data/Image_url.txt", 'w')
        Desc_file = open("Data/Description.txt", 'w')
        Local_file.close()
        Image_file.close()
        Desc_file.close()
    if(os.path.exists(os.getcwd() + "/Data") == False):
        os.mkdir(os.getcwd() + "/Data/")
    if (os.path.exists(os.getcwd() + "/Data/User") == False):
        os.mkdir(os.getcwd() + "/Data/User")
        Create_root_window()
    else:
        User_list = os.listdir(os.getcwd() + "/Data/User/")
    #先判断是否存在已知用户，如果有直接跳过Login阶段
        if(User_list == []):
            Create_root_window()
        else:
            User_name = re.findall("(.+?)\.txt",User_list[0])
            Trans_thread = threading.Thread(target=Send_Client,args=User_name)
            Trans_thread.start()
                                            # <<--------选择窗口
            Select_windows = Select_Win(str(User_name[0]))
            Select_windows.Create_window()
            Select_windows.Root.mainloop()

            if Select_windows.clear == True:
                Trans_thread.join()
                try:
                    os.remove('Data/User/' + Select_windows.User_name + '.txt')
                except:pass

            if Select_windows.clear == True and os.path.exists('Data/User/' + Select_windows.User_name + '.txt') == True:
                show_mess = mbox.showinfo("Fail","删除用户失败，可以手动删除>_<")

    return



#
# 得到当前系统Chrome目录
#  if os.path.exists("Data/Broswer_path.txt") == False:
#         File = open("Data/Broswer_path.txt",'w')
#         Driver_path = os.getcwd() + "/Data/chromedriver.exe"
#         Chrome_options = webdriver.ChromeOptions()
#         Chrome_options.add_argument("--disable-gpu")  # 将跳出的chrome进行隐藏
#         Broswer = webdriver.Chrome(Driver_path, chrome_options=Chrome_options)
#         Broswer.get("chrome://version")
#         Page_text = Broswer.page_source
#         Broswer.close()
#         Path_pattern = 'id="executable_path">(.+?)</td>'
#         File.write(re.findall(Path_pattern, Page_text)[0])
#         File.close()
