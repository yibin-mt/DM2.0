import re
import sys
import time
import datetime
from KF_skills.fund import *
from KF_skills.dayoff import *
from DH_skills.ticket import *
from DH_skills.task import Task
from NER import time_extract
import ahocorasick

fund_list = ['公积金', '计算', '缴纳', '交', '扣除', '算一下']
dayoff_list = ['我要','帮我','替我','请假', '请病假', '居家办公', '请产假', '请婚假', '申请', '带薪病假', '年假', '使用', '在家办公','休假']
ticket_list = ['机票','订', '买']

guess_list = ['不对','不正确','答案','错误', '重新', '想想', '错啦', '笨蛋', '答错', '再猜猜']
sucess_list = ['真棒', '谢谢', '厉害', '不错', '聪明', '辛苦','是的','答对','正确']
stop_list = ['别猜','算了','停','傻瓜','笨','蠢']

KF_skill_word_list = [fund_list, dayoff_list, guess_list]
DH_skill_word_list = [ticket_list, guess_list]

KF_slots = [fund_slots, dayoff_slots]
DH_slots = [ticket_slots]
KF_skills = [response_fund, response_dayoff]
DH_skills = [response_ticket]

#构建任务
def build_skill(task_id, skill_type):
    if task_id < 0:
        return Task([])
    if skill_type == 'DH':
        task = Task(DH_slots[task_id])
        response = DH_skills[task_id]
    else:
        task = Task(KF_slots[task_id])
        response = KF_skills[task_id]
    setattr(task, "response", response)
    return task
    

def build_actree(wordlist):
    actree = ahocorasick.Automaton()
    for index, word in enumerate(wordlist):
        actree.add_word(word, (index, word))
    actree.make_automaton()
    return actree

def If_Skill(query, intent, task_id, skill_type):
    if skill_type == 'DH':
        skill_word_list = DH_skill_word_list
    else:
        skill_word_list = KF_skill_word_list
    for i in range(len(skill_word_list)):
        actree = build_actree(wordlist=skill_word_list[i])
        cnt = sum(1 for _ in actree.iter(query))
        if cnt>=2:
            return True, i
        elif cnt>=1 and (intent!=[] and intent[-1]=='DocQa'):
            return True, -1
    return False, -1

def guess_stop(query):
    actree = build_actree(wordlist=sucess_list)
    cnt = sum(1 for _ in actree.iter(query))
    actree2 = build_actree(wordlist=stop_list)
    cnt2 = sum(1 for _ in actree2.iter(query))
    if cnt>=1:
        return True, 'guess_sucess'
    elif cnt2>=1:
        return True, 'guess_stop'
    else:
        return False, '_'


def verify_date_str_lawyer(datetime_str):
    try:        
    	datetime.datetime.strptime(datetime_str, '%Y-%m-%d')        
    	return True    
    except ValueError:        
    	return False
    
def check(query, label):
    if label =='base':
        res = re.findall(r"\d+\.?\d*",query)
        if res==[]:
            return False, ''
        else:
            return True, res[0]

    elif label =='city':
        city_list = ['深圳','广州','北京','上海','成都','西安','合肥','杭州','青岛','乌鲁木齐','重庆','苏州']
        actree = build_actree(wordlist=city_list)
        cnt = sum(1 for _ in actree.iter(query))
        if cnt>=1:
            return True, query
        else:
            return False, ''
    
    elif label == 'kind':
        if 1<=int(query)<=8 or query in ['年假','带薪病假','育儿假','居家办公','事假','病假','婚假','产假']:
            return True, query
        else:
            return False, ''
        
    elif label == 'lay_time':
        start, end = query.split('｜')
        start_date, start_half= start.split(' ')
        end_date, end_half= end.split(' ')
        if verify_date_str_lawyer(start_date) and verify_date_str_lawyer(end_date):
            #判断日期是否合法,并得到日期之差
            
            date1 = datetime.datetime.strptime(start_date, '%Y-%m-%d') 
            date2 = datetime.datetime.strptime(end_date, '%Y-%m-%d') 
            
            days = (date2-date1).days
            if days==0 and start_half=='下午' and end_half=='上午':
                return False, ''
            else:
                if start_half==end_half:
                    days+=0.5
                elif start_half=='上午' and end_half=='下午':
                    days+=1
                return True, query+', 共%s天'%format(days)
        else:
            return False, ''
        
    elif label == 'season':
        pattern = re.compile(u'[\u4e00-\u9fa5]')
        if pattern.search(query):
            return True, query
        else:
            return False, ''

    elif label == 'confirm':
        if query in ['yes','y','确定']:
            return True, query
        elif query in ['no','n', '否']:
            return False, query
        else:
            return False, ''
        
    elif label == 'time':
        parse_time = time_extract(query)
        if parse_time:
            return True, parse_time[0]
        else:
            return False, ''
    
    elif label == 'meal':
        return True, query
    
    else:
        return True, query