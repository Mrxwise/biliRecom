import re
from selenium import webdriver
import requests
import os
import time

            #muti_get_id函数中，Thread_job_list记录当前线程爬虫需要访问页面
            #Thread_job_id用于保存已经获取的id
            #Alread_set为已经存在的id的集合，用于排除已经存在的id
            #detect为检测到的AnimaGUI绑定显示量IntVar()
            #new为新检测到的AnimaGUI绑定显示量IntVar()
def muti_get_id(Thread_job_list,Thread_job_id,Alread_set,detect,new,signal,stop_flag,Anima_id_dict,show_flag):
    Driver_path = os.getcwd() + "/bin/chromedriver.exe"
    Chrome_options = webdriver.ChromeOptions()
    Chrome_options.add_argument('--incognito')
    if show_flag == True:
        Chrome_options.add_argument("--headless")
    Chrome_options.add_argument("--disable-gpu")  #将跳出的chrome进行隐藏
    Broswer = webdriver.Chrome(Driver_path, chrome_options=Chrome_options)
    Base_url = "https://www.bilibili.com/anime/index/?spm_id_from=666.4.primary_menu.13#season_version=-1&area=-1&is_finish=-1&copyright=-1&season_status=-1&season_month=-1&pub_date=-1&style_id=-1&order=3&st=1&sort=0&page="
    for page in Thread_job_list:
        try:
            Combine_url = Base_url + str(page)
            Broswer.get(Combine_url)
            Broswer.implicitly_wait(5)
            Current_page_anima_url_list = []
            Item_list = []
            Try_flag = True
            Broswer.refresh()               #将页面刷新
            for times in range(5):
                try:
                    Item_list = Broswer.find_elements_by_xpath('//ul//li[@class="bangumi-item"]')
                    break           #成功退出，否则刷新暂停几秒
                except:
                    if times == 1:
                        Broswer.refresh()  # 在发生错误后refresh， 即并非加载错误，而是页面未更新错误。
                    time.sleep(0.5)
                    if times == 4:
                        Try_flag = False        #连续5次全部失败
            if Try_flag == False:continue#break正式时调整为continue

            #检测外部是否关闭页面
            if (stop_flag.get() == 0):  # 外部已经关闭页面
                Broswer.close()
                return

            for item in Item_list:
                Current_page_anima_url_list.append(item.find_element_by_class_name("cover-wrapper").get_attribute("href"))
            for anima_url in Current_page_anima_url_list:
                if (stop_flag.get() == 0):  # 外部已经关闭页面
                    Broswer.close()
                    return
                signal.acquire()
                detect.set(detect.get() + 1)
                signal.release()

                Page_reponse = requests.get(anima_url)
                Page_content = Page_reponse.content
                Page_html = str(Page_content, encoding='utf-8')
                Id_pattern = "md(\d+)"
                Pattern_id_list = re.findall(Id_pattern, Page_html)
                if Pattern_id_list:
                    ID = Pattern_id_list[0]
                    if ID not in Alread_set:        #新找到的Anima
                        signal.acquire()
                        new.set(new.get()+1)
                        signal.release()
                        Thread_job_id.append(ID)

                        Orin_pattern = "ss(\d+)"        #将ID-序号对导入字典。
                        Number = re.findall(Orin_pattern, anima_url)
                        if Number:
                            Pattern_num = Number[0]
                            Anima_id_dict[Pattern_num] = ID

                else:
                    #在当前页面没有找到 ID号，则跳过当前页面
                    continue
                        #完成当前页面的ID搜寻后先跳到空页面,其url为data:,
            Broswer.get("data:,")
        except:
            continue            #当前页面出现错误，跳到下一个页面
    Broswer.close()
    return
