import re
import numpy as np
import random
from sklearn.cluster import KMeans          # 使用Kmeans聚类的方式计算相似度
def calcu_list(Anima_info):
    dimesion_list = []
    for index in range(41):
        dimesion_list.append(0)
    tag_dict = {"原创":0,"漫画改":1,"小说改":2,"游戏改":3,"布袋戏":4,"热血":5,"奇幻":6,"战斗":7,"日常":8,"搞笑":9,
                "科幻": 10,"萌系":11,"治愈":12,"校园":13,"少儿":14,"泡面":15,"恋爱":16,"后宫":17,"猎奇":18,"少女":19,
                "魔法": 20,"历史":21,"机战":22,"致郁":23,"神魔":24,"声控":25,"运动":26,"励志":27,"音乐":28,"推理":29,
                "社团": 30,"智斗":31,"催泪":32,"美食":33,"装逼":34,"偶像":35,"乙女":36,"职场":37,"伪娘":38,"时泪":39,
                "萝莉": 40}
    for tag in Anima_info[2]:
        dimesion_list[tag_dict[tag]] += 10
    return np.array(dimesion_list)
def calcu_avg_vector(vector_list):
    SUM_vector = np.array(np.zeros(41))
    for vector in vector_list:
        SUM_vector += vector[1]
    SUM_vector /= len(vector_list)
    return SUM_vector
def calcu_date_heat(anima_info):
    Heat = 100
    Date = 20080101
    if anima_info[4] != None:
        word = "万"
        text = anima_info[4]
        patt_list = re.findall(word,text)
        if patt_list != []:
            text = text.replace("万","")
            Heat = int(float(text) * 10000)
        else:
            Heat = int(text)
    if anima_info[5] != None:
        text2 = anima_info[5]
        digitals = re.findall('\d+',text2)
        if(int(digitals[0]) > 1500):
            STR_date = digitals[0]
            if(len(digitals[1]) <= 1):
                STR_date += '0' + digitals[1]
            else:STR_date += digitals[1]
            if(len(digitals) < 3):STR_date += '01'                      #对应播放日期仅有年月的情况
            else:
                if (len(digitals[2]) <= 1):STR_date += '0' + digitals[2]
                else:STR_date += digitals[2]
            Date = int(STR_date)
    return Heat,Date

def user_judge(CHECK_id_list,user_list,like,Cut_id):
    user_list = np.array(user_list)
    judge_list = []
    recom_user = []
    index = 0
    id_set = set()
    for user in user_list:
        length = 0
        if random.randint(0,100) >= 35:
            index += 1
            continue
        for item in user:
            if item != '0' and length <= 21:
                length += 1
            else:break
        if length >= 20 or length <= 3:
            index += 1
            continue
        users = np.array(user)
        common = np.intersect1d(users,np.array(CHECK_id_list))
        common_len = len(common)
        judge_list.append((common_len,index))
        index += 1
    judge_list = sorted(judge_list,key=lambda x:x[0])
    judge_list.reverse()
    count = 0

    if like == True:
        count = 0
        for user_index in judge_list:
            if len(recom_user) >= 5:break               #如果已经收录的用户超过3名，就停止加入
            User = user_list[user_index[1]]
            for elem in User:                           #当用户中不在Cut_id中的ID数目超过5个，就认为是可加入的用户
                if elem == '0':break
                if elem not in Cut_id:
                    count += 1
            if count >= 5:
                recom_user.append(User)
            count = 0

        best_user = recom_user[random.randint(0,1)]
        best_list = []
        for ID in best_user:
            if ID == '0':break
            if ID in Cut_id:continue
            if ID in best_list:continue
            best_list.append(ID)                        #在最优用户中，不在Cut_id中可以放入推荐中，同时删去已经在列表中的元素

        for user in recom_user:
            for id in user:
                if id == '0':break
                if id in Cut_id:continue                    #由于放入集合中，不需担心重复问题
                id_set.add(id)
        return best_list,id_set
    else:
        for user_index in judge_list:
            if count >= 2: break
            recom_user.append(user_list[user_index[1]])
            count += 1
        for user in recom_user:
            for id in user:
                if id == '0':break
                id_set.add(id)
        return id_set
                                            #对于所有user_matrix需要转化为str模式
def get_user_recom(id,Cut_id,user_matrix,matrix_column):
    recom_id = []
    id_list = np.array(user_matrix[id])
    sort_list = []
    posit_dect = {}
    for index in range(len(id_list)):
        posit_dect[(id_list[index],matrix_column[index])] = index
        sort_list.append((id_list[index],matrix_column[index]))
    sort_list = sorted(sort_list,key=lambda x:x[0])
    sort_list.reverse()

    count = 0
    for item in sort_list:
        recom = item[1]

        if count >= 40:break
        if recom in Cut_id:continue                     #已经排除所有在Cut_id中的Anima ID
        if recom in recom_id:continue                   #排除所有已经在recom_id中的Anima ID
        else:
            recom_id.append(recom)
            count += 1
    POP_index = []
    POP_index.append(random.randint(2, 9))
    POP_index.append(random.randint(2, 9))
    for times in range(3):POP_index.append(random.randint(8,15-times))            #对得到的推荐ID进行随机排除
    for times in range(15):POP_index.append(random.randint(4,34-times))                                                                          #共减去20个Anima ID
    for index2 in POP_index:
        recom_id.pop(index2)
    return recom_id


                                                                                #
def get_avg_tag_recom(Anima_info,avg_vector,Cut_id,chose_set):
    index = 0
    vector_list = []
    for anima in Anima_info:
        if random.randint(0,100) >= 35:
            index += 1
            continue
        vector = calcu_list(anima)
        distance = np.linalg.norm(vector - avg_vector)
        vector_list.append((index,distance))
        index += 1
    vector_list = sorted(vector_list,key=lambda x:x[1])

    above_avg_list = set()
    for elem in vector_list:
        id = Anima_info[elem[0]][1]
        if id in Cut_id:continue                #删除所有在Cut_id中的id
        if len(chose_set) >= 60:
            if len(above_avg_list) >= 40:break
        else:
            if len(above_avg_list) + len(chose_set) >= 120:break
        if random.randint(0,100) >= 60:continue
        above_avg_list.add(id)
    return above_avg_list
def get_recommend(Anima_info,Anima_position,choose_list,LIKE,DONT):      #由已经得到接近的进行在综合比较，得到推荐
    Recom_list = set()
    if len(DONT) >= 20:
        K_mean_like = []
        K_mean_dis = []
        for like in LIKE:
            like_anima = Anima_info[Anima_position[like]]
            heat, date = calcu_date_heat(like_anima)
            date = int(date/100)
            heat = int(date/100)
            K_mean_like.append((heat, date))
        for dis in DONT:
            dis_anima = Anima_info[Anima_position[dis]]
            heat, date = calcu_date_heat(dis_anima)
            date = int(date/100)
            heat = int(date/100)
            K_mean_dis.append((heat, date))
        like_cluster = KMeans(n_clusters=1)
        dis_cluster = KMeans(n_clusters=1)

        like_data_cluster = like_cluster.fit_predict(K_mean_like)
        dis_data_cluster = dis_cluster.fit_predict(K_mean_dis)

        like_center = like_cluster.cluster_centers_[0]
        like_center = np.array(like_center)
        dis_center = dis_cluster.cluster_centers_[0]
        dis_center = np.array(dis_center)

        Distance_list = []

        for chose_id in choose_list:
            chose_info = Anima_info[Anima_position[chose_id]]
            chose_heat,chose_date = calcu_date_heat(chose_info)
            chose_date/= 100
            chose_heat/= 100

            check_vector = np.array([chose_heat,chose_date])

            like_distance = np.linalg.norm(check_vector - like_center)
            dis_distance = np.linalg.norm(check_vector - dis_center)

            if like_distance >= dis_distance:continue
            Distance_list.append((chose_id,like_distance,like_distance - dis_distance))

        Distance_list = sorted(Distance_list, key=lambda x: x[1])
        Distance_list = sorted(Distance_list, key=lambda x: x[2])

        for item in Distance_list:
            if random.randint(0,100) >= 20:continue
            if len(Recom_list) >= 3:break
            else:
                Recom_list.add(item[0])
        return Recom_list
    else:
        K_mean_like = []
        for like in LIKE:
            like_anima = Anima_info[Anima_position[like]]
            heat, date = calcu_date_heat(like_anima)
            date = int(date/100)
            heat = int(date/100)
            K_mean_like.append((heat, date))

        like_cluster = KMeans(n_clusters=1)
        like_data_cluster = like_cluster.fit_predict(K_mean_like)
        like_center = like_cluster.cluster_centers_[0]
        like_center = np.array(like_center)

        Distance_list = []

        for chose_id in choose_list:
            chose_info = Anima_info[Anima_position[chose_id]]
            chose_heat, chose_date = calcu_date_heat(chose_info)
            chose_date /= 100
            chose_heat /= 100

            check_vector = np.array([chose_heat, chose_date])

            like_distance = np.linalg.norm(check_vector - like_center)

            Distance_list.append((chose_id, like_distance))
        Distance_list = sorted(Distance_list, key=lambda x: x[1])

        for item in Distance_list:
            if random.randint(0, 100) >= 20: continue
            if len(Recom_list) >= 3:
                break
            else:
                Recom_list.add(item[0])
        return Recom_list
def random_recom(Anima_info,Anima_position,LIKE,DONT,limit,Cut_id):
    LIKE_vector = np.array(np.zeros(41))
    DONT_vector = np.array(np.zeros(41))
    for like in LIKE:
        like_anima = Anima_info[Anima_position[like]]
        like_vector = calcu_list(like_anima)
        LIKE_vector += like_vector
    for dis in DONT:
        dis_anima = Anima_info[Anima_position[dis]]
        dis_vector = calcu_list(dis_anima)
        DONT_vector += dis_vector

    zero_index = []
    likes_tag_index = []
    MAX = max(LIKE_vector)
    for index in range(len(LIKE_vector)):
        if LIKE_vector[index] == 0 and DONT_vector[index] == 0:
            zero_index.append(index)        #zero_index中含有目前未涉及到的标签
        if LIKE_vector[index] >= MAX*0.8:
            likes_tag_index.append(index)   #likes_tag_index中含有占比较高的标签
    chose_anima = []
    for anima in Anima_info:
        if anima[1] in Cut_id:continue
        if random.randint(0,100) >= 20:continue
        info = list(anima)
        if info[3] == None:
            info[3] = str(7.5)

        chose_anima.append(info)
    chose_anima = sorted(chose_anima,key = lambda x:float(x[3]))           #进行评分排序
    chose_anima.reverse()
    id_list = []
    for elem in chose_anima:
        id_list.append(elem[1])

    Recom_set = set()
    fix_list = []
                                                                            # 当Like数目少于20条时，在其中顺序遍历热门Anima
    if len(Cut_id) % 2 == 0:
        if len(LIKE) <= 20:
            for anima_id in range(random.randint(0,100),len(Anima_info),5):
                if random.randint(0,100) >= 20:continue
                if len(Recom_set) >= limit: break
                if Anima_info[anima_id][1] not in Cut_id and Anima_info[anima_id][1] not in Recom_set:
                    Recom_set.add(Anima_info[anima_id][1])
            return Recom_set

    for elem in id_list:
        distance = limit - len(Recom_set)
        continue_flag = False
        if random.randint(0,100) >= 10+distance*2:continue
        if len(Recom_set) >=limit:break

        chose_info = Anima_info[Anima_position[elem]]
        chose_vector = calcu_list(chose_info)
        for index in zero_index:
            if chose_vector[index] == 0:
                if random.randint(0,100) >= 50:continue
                Recom_set.add(elem)
                continue_flag = True
                break
        if continue_flag == True:continue           #优先挑选未出现过的标签

        fix_count = 0
        for index in likes_tag_index:
            if chose_vector[index] >= MAX*0.8:      #优先挑选出现率较高的标签
                fix_count += 1
        fix_list.append(fix_count)
        if fix_count >= max(fix_list)*0.8:
            Recom_set.add(elem)
            continue

        if random.randint(0,100) >= len(Recom_set)*2:continue

        else:Recom_set.add(elem)

    return Recom_set

def Recommend(Anima_info,Anima_position,User_name,Cut_ID,User_matrix,matrix_column,user_list):      #user_list为pandas打开文件, Cut_ID 为集合
    Recom_ID_list = []
    User_file = open('Data/User/' + User_name + ".txt",'r')
    Like_pattern = "<LIKE (\d+)>"
    Dont_pattern = "<DONT (\d+)>"
    LIKE_list = []
    DONT_list = []                      #构建用户喜欢\不喜欢列表
    User_actions = 0
    for lines in User_file:
        User_actions += 1
        Check = re.findall(Like_pattern,lines)
        if Check != []:
            LIKE_list.append(Check[0])
        else:
            Check = re.findall(Dont_pattern,lines)
            DONT_list.append(Check[0])
    Cut_ID = Cut_ID | user_judge(DONT_list,user_list,False,Cut_ID)     #利用DONT删去用户不喜欢的用户
    Cut_ID = Cut_ID | set(LIKE_list)
    Cut_ID = Cut_ID | set(DONT_list)                             #将LIKE、DONT加入需要删去集合中

    if len(LIKE_list) >= 20:            #用户喜欢Anima多于20条，计算平均向量
        LIKE_vector_list = []
        LIKE_distance_list = []
        for item in LIKE_list:
            LIKE_vector_list.append((item,calcu_list(Anima_info[Anima_position[item]])))        #以元组的形式将id和向量结合
        avg_vector = calcu_avg_vector(LIKE_vector_list)
        for item in LIKE_vector_list:
            distance = np.linalg.norm(item[1] - avg_vector)                     #得到各个LIKE中向量与平均向量的距离
            LIKE_distance_list.append((item[0],distance))
        LIKE_distance_list = sorted(LIKE_distance_list,key=lambda x:x[1])  #以距离进行排序
        ten_index_list = []
        id_index_list = []              #随机选择后得到的参与匹配的ID

        ten_index_list.append(0)
        ten_index_list.append(1)
        ten_index_list.pop(random.randint(0,1))             #从0、1选择一个参与匹配
        while True:
            if len(ten_index_list) >= 5:break
            num = random.randint(2,9)                      #从2-10中再随机选择4个作为匹配index
            if num not in ten_index_list:
                ten_index_list.append(num)

        for item in ten_index_list:
            id_index_list.append(LIKE_distance_list[item][0])        #将匹配的Anima ID导入id_index_list

        User_recom = []
        for index in range(5):
            User_recom += get_user_recom(id_index_list[index],Cut_ID,User_matrix,matrix_column)
        record = 0
        while record <= 10:
            if len(Recom_ID_list) >= 4:break                                                #将所有可能出错的进行过滤
            if User_recom[record] not in Cut_ID and User_recom[record] not in Recom_ID_list:
                Recom_ID_list.append(User_recom[record])
            if len(Recom_ID_list) >= 4: break
            if User_recom[record+20] not in Cut_ID and User_recom[record+20] not in Recom_ID_list:
                Recom_ID_list.append(User_recom[record+20])
            if len(Recom_ID_list) >= 4: break
            if User_recom[record+40] not in Cut_ID and User_recom[record+40] not in Recom_ID_list:
                Recom_ID_list.append(User_recom[record+40])
            if len(Recom_ID_list) >= 4: break
            if User_recom[record+60] not in Cut_ID and User_recom[record+60] not in Recom_ID_list:
                Recom_ID_list.append(User_recom[record+60])
            if len(Recom_ID_list) >= 4: break
            record += 1                                                                     #根据总体用户推荐
        Recom_ID_list.pop(random.randint(0,3))                          #随机删去一个
        for elem in Recom_ID_list:
            User_recom.remove(elem)
        User_recom = set(User_recom)                                    #将用户推荐转化为集合
        for item in Recom_ID_list:
            Cut_ID.add(item)                                            #在Cut_id中添加已经推荐过的


        best_set,like_set = user_judge(LIKE_list,user_list,True,Cut_ID)                 #依据最佳用户匹配得到的集合
        Check_score = []
        for elem2 in best_set:                                           #将最佳用户的ID进行评分排序，得到最高评分加入推荐中
            info = Anima_info[Anima_position[elem2]]
            if info[3] == None:score = 8.0
            else:score = float(info[3])
            Check_score.append((elem2,score))
        Check_score = sorted(Check_score,key=lambda x:x[1])
        Check_score.reverse()

        record_2 = 0
        for elem3 in Check_score:
            if random.randint(0,60+record_2*20) >= 40:continue
            Recom_ID_list.append(elem3[0])
            like_set.remove(elem3[0])                                       #在like_set中删去已经推荐的元素
            Cut_ID.add(elem3[0])                                            #向Cut_id中添加加入Recom中的元素
            record_2 += 1
            if len(Recom_ID_list) >= 5:break                              #在最佳用户中选择随机两个

        chose_recom = User_recom | like_set
        chose_recom = chose_recom | get_avg_tag_recom(Anima_info,avg_vector,Cut_ID,chose_recom)

        Recom_ID_list += get_recommend(Anima_info,Anima_position,chose_recom,LIKE_list,DONT_list)

        if len(Recom_ID_list) < 8:
            for elem4 in random_recom(Anima_info,Anima_position,LIKE_list,DONT_list,-len(Recom_ID_list),Cut_ID):
                Recom_ID_list.append(elem4)
        return Recom_ID_list
    else:
        for elem5 in random_recom(Anima_info,Anima_position,LIKE_list,DONT_list,8-len(Recom_ID_list),Cut_ID):
            Recom_ID_list.append(elem5)
        return Recom_ID_list
