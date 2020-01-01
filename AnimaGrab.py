import re
import requests
from tkinter import messagebox as mbox
import threading
import Graber as grab
import time

def Html_produce(html):

    error_pattern = "出错啦!"
    if re.findall(error_pattern,html):
        return None,None,None,None,None,None,None
    name_pattern = "<img alt=\"(.+?)\" src=\"\">"
    tag_pattern = "<span class=\"media-tag\">(.+?)</span>"
    score_pattern = "<div class=\"media-info-score-content\"><div>([0-9.]+)</div>"
    heat_pattern = "<span class=\"media-info-label\">[追收][番藏]人数</span> <em>(.+?)</em>"
    time_pattern = "<div class=\"media-info-time\"><span>(.+?) 开播</span>"
    description_pattern = "evaluate\":\"(.+)\",\"long_review\""
    img_pattern = "<meta property=\"og:image\" content=\"(.+?)\">"
    if re.findall(name_pattern,html): Anima_name = re.findall(name_pattern,html)[0]
    else:Anima_name = None
    if re.findall(tag_pattern, html): Anima_taglist = re.findall(tag_pattern,html)
    else:Anima_taglist= None
    if re.findall(heat_pattern, html): Anima_heat = re.findall(heat_pattern,html)[0]
    else:Anima_heat = None
    if re.findall(score_pattern, html): Anima_score = re.findall(score_pattern,html)[0]
    else:Anima_score = None
    if re.findall(time_pattern, html): Anima_time = re.findall(time_pattern,html)[0]
    else:Anima_time = None
    if re.findall(description_pattern, html): Anima_description = re.findall(description_pattern,html)[0]
    else:Anima_description = None
    if re.findall(img_pattern, html): Anima_img_url = re.findall(img_pattern,html)[0]
    else:Anima_img_url = None
    return Anima_name, Anima_taglist, Anima_score, Anima_heat, Anima_time, Anima_description, Anima_img_url

def muti_get_anima(List_id_list,Result_list,Image_list,Description_list,down,signal,stop_flag):
    Base_url = "https://www.bilibili.com/bangumi/media/md"
    for Anima_id in List_id_list:
        try:
            if stop_flag.get() == 0:
                return
            Page_url = Base_url + Anima_id
            Page_reponse = requests.get(Page_url)
            Page_content = Page_reponse.content
            Page_html = str(Page_content, encoding='utf-8')
            signal.acquire()                                #在多线程中，将信号量减一以保证down量正确。
            down.set(down.get()+1)                          #将绑定量加1
            signal.release()
            Anima_name, Anima_taglist, Anima_score, Anima_heat, Anima_time, Anima_description, Anima_img_url = Html_produce(Page_html)
            if Anima_name == None:
                time.sleep(0.5)
                Anima_name, Anima_taglist, Anima_score, Anima_heat, Anima_time, Anima_description, Anima_img_url = Html_produce(Page_html)  #第二次机会
            if Anima_name == None:
                raise ConnectionError

            Anima= (Anima_name,Anima_id, Anima_taglist, Anima_score, Anima_heat, Anima_time)
            Anima_image = (Anima_id,Anima_img_url)          #将数据存在相应的数组中
            Anima_desc = (Anima_id,Anima_description)


            Result_list.append(Anima)                       #将数据存在外部数组中
            Image_list.append(Anima_image)
            Description_list.append(Anima_desc)
        except:
            signal.acquire()
            down.set(down.get() + 1)
            signal.release()
            List_id_list.remove(Anima_id)
            continue                    #存在问题同时在原数组中，删除该ID，防止写入出现问题
                                        #存在一个页面获取失败，直接继续下一个
    return

def Update(begin,end,detect,new,down,threads,Alread_set,stop_flag,show_flag):

    Thread_job_list = []                    #给多线程分配页数任务
    Thread_job_id = []                      #Thread_job_id为id线程运行结果
    Anima_id_dict = {}
    for index in range(threads):
        Thread_job_list.append([])
        Thread_job_id.append([])
    for index in range(begin,end+1):
        Thread_job_list[index % threads].append(index)

    Thread_1_list = []                  #第一个多线程任务，用于获取Anima的id。线程数为threads
    signal_1 = threading.Semaphore(1)
    #try:
    for index in range(threads):                                #参数需要进行调整，为正确对new、detect进行改变，需要加入信号量进行限制。
            Thread = threading.Thread(target=grab.muti_get_id,args=(Thread_job_list[index],Thread_job_id[index],Alread_set,detect,new,signal_1,stop_flag,Anima_id_dict,show_flag))
            Thread_1_list.append(Thread)
    for index in range(threads):
            Thread_1_list[index].setDaemon(True)
            Thread_1_list[index].start()
    for index in range(threads):
            Thread_1_list[index].join()
    if stop_flag.get() == 0:
        return                      #外部页面已经关闭
    #except:
        #Messbox1 = mbox.showinfo("错误","搜索线程运行失败！别问我为什么，我不知道!你不能降低线程数吗?")
        #return

    Thread_job_anima = []
    Thread_job_image_url = []
    Thread_job_desc = []


    for i in range(threads):
        Thread_job_anima.append([])
        Thread_job_image_url.append([])
        Thread_job_desc.append([])

    Thread_2_list = []                  #第二个多线程任务，用于保存Anima的内容。线程数为threads
    signal_2 = threading.Semaphore(1)
    #try:
    for index in range(threads):
        Thread = threading.Thread(target=muti_get_anima,args=(Thread_job_id[index],Thread_job_anima[index],Thread_job_image_url[index],Thread_job_desc[index],down,signal_2,stop_flag))
        Thread_2_list.append(Thread)
    for index in range(threads):
        Thread_2_list[index].setDaemon(True)
        Thread_2_list[index].start()
    for index in range(threads):
        Thread_2_list[index].join()
    #except:
        #Messbox1 = mbox.showinfo(">_<", "下载线程运行失败！别问我为什么，我不知道!你不能降低线程数吗?")
        #return
    if stop_flag.get() == 0:            #外部页面已经关闭，当已经完成读取则直接等待任务完成
        return

    Anima_image_url = []
    Anima_description = []
    Anima_list = []

    for index in range(threads):                            #将所有的线程结果合并到一个数组中，在线程中进行文件操作过于缓慢
        Anima_list += Thread_job_anima[index]
        Anima_description += Thread_job_desc[index]
        Anima_image_url += Thread_job_image_url[index]

    Anima_file = open("Data/Anima_list.txt","a",encoding='utf-8')       #a标志位可以正确处理是否存在的问题。
    Image_url_file = open("Data/Image_url.txt","a")
    Description_file = open("Data/Description.txt","a",encoding='utf-8')

    for anima in Anima_list:  # 向Anima_list中添加anima信息
        line = "<"
        if anima[0] != None:line += anima[0] + "||"
        else:line += '-' + "||"
        if anima[1] != None:line += anima[1] + "||"
        else:line += '-' + "||"
        if anima[2] != None:
            line += anima[2][0]
            for index in range(1, len(anima[2])):
                line += '-' + anima[2][index]
            line += "||"
        else:line += '-' + "||"
        if anima[3] != None:line += anima[3] + "||"
        else:line += '-' + "||"
        if anima[4] != None:line += anima[4] + "||"
        else:line += '-' + "||"
        if anima[5] != None:line += anima[5]
        else:line += '-'
        line += ">\n"
        Anima_file.write(line)
        # (Anima_name,Anima_id, Anima_taglist, Anima_score, Anima_heat, Anima_time)
    Anima_file.close()
    for url in Anima_image_url:
        line = url[0]
        line += "===>"
        line += url[1] + '\n'
        Image_url_file.write(line)
    Image_url_file.close()
    for desc in Anima_description:
        line = desc[0]
        line += "===>"
        line += desc[1] + '\n'
        Description_file.write(line)
    Description_file.close()

    Dict_id_file = open("Data/Anima_id_dect.txt",'a')
    for elem in Anima_id_dict:
        Dict_id_file.write(elem + " - " + Anima_id_dict[elem] + '\n')
    Dict_id_file.close()





    Finish_tip = mbox.showinfo("完成","数据更新已经完成！")
    return
