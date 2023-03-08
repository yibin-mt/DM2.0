import re
import sys
import os
import time
import jieba
jieba.add_word('你知道',100000)
import fasttext
import logging
import argparse 
from NER import ner
from faq_infer import Faq_inference
from faq_chat import Faq_Chat_inference
from qr_infer import IUR_inference
from chat_infer import Chat_inference
from docqa_infer import DocQAInference
from emotion_infer import Emotion_inference
from collections import defaultdict
from utils import If_Skill, check, build_skill, guess_stop
from google.protobuf.json_format import MessageToJson


id_2_intent = {0:'Faq', 1:'Chat', 2:'DocQa', 3:'Mutil-Turn'}
intent_2_id = {'Faq':0, 'Chat':1, 'DocQa': 2, 'Mutil-Turn':3}
stop_words = ['你知道','的','了','吗','啊','拉','呢', '告诉','请问']

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
def get_logger(name, level=LOG_LEVEL, log_format=LOG_FORMAT):
    """
    :param name: looger 实例的名字
    :param level: logger 日志级别
    :param log_format: logger 的输出`格式
    :return:
    """
    # 强制要求传入 name
    logger = logging.getLogger(name)
    # 如果已经实例过一个相同名字的 logger，则不用再追加 handler
    if not logger.handlers:
        logger.setLevel(level=level)
        formatter = logging.Formatter(log_format)
        # fh = logging.FileHandler(name, "a")
        # fh.setFormatter(formatter)
        # logger.addHandler(fh)
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    return logger

class DmClass(object):
    def __init__(self, args):
        super(DmClass, self).__init__()
        self.args = args
        if self.args.robot_type == 'DH':
            self.chat_repo = 1
            self.skill_type = 'DH'
            self.FAQ = False
        elif self.args.robot_type == 'KF':
            self.chat_repo = 2
            self.skill_type = 'KF'
            self.FAQ = True
        else:
            self.chat_repo = self.args.chat_repo
            self.skill_type = self.args.skill_type
            self.FAQ = self.args.FAQ
        print('robot_type: ', self.args.robot_type)
        print('chat_repo: ', self.chat_repo)
        print('skill_type: ', self.skill_type)
        print('FAQ: ', self.FAQ)
        self.faq = Faq_inference(self.args.faq_ip, self.args.faq_port)
        self.faq_chat = Faq_Chat_inference(self.chat_repo, self.args.faq_ip, self.args.faq_port)
        self.qr = IUR_inference({}, self.args.qr_ip, self.args.qr_port)
        self.docqa = DocQAInference({}, self.args.docqa_ip, self.args.docqa_port)
        self.chat = Chat_inference(self.args.chat_ip, self.args.chat_port)
        self.emotion = Emotion_inference(self.args.emotion_ip, self.args.emotion_port)
        self.chat_thres = 0.8
        self.qr_thres = 0.8
        self.faq_thres = 0.75
        self.docqa_thres = 0.72
        try:
            self.model = fasttext.load_model(r"DM/models/model.bin")
        except:
            self.model = fasttext.load_model(r"models/model.bin")
        self.DEFAULT_ANSWER = '不好意思，我目前还无法回答您这个问题'
        self.FAQ_DEFAULT_ANSWER = '不好意思，我不大明白你的意思。您想问的是不是：'
        self.DOCQA_DEFAULT_ANSWER = '不好意思，我目前还不知这个问题的答案，我会继续学习的！'
        self.DOCQA_DEFAULT_ANSWER_2 = '您想问的是不是：有关《'

    def load_data(self, query, history, session_id, robot_id):
        self.query = query
        
        self.history = history
        try:
            self.conversation = list(history.conversation)
            self.intent = list(history.intent)
            self.slots = list(history.slots)
            self.entities = list(history.entities)
            self.task_id = list(history.task_id)
        except:
            self.conversation = []
            self.intent = []
            self.slots = []
            self.entities = []
            self.task_id = []
        
        self.session_id = session_id
        self.robot_id = robot_id
        
        
    def word_segment(self, text):
        seg_list = jieba.cut(text)
        word_list = []
        for word in seg_list:
            if word not in stop_words:
                word_list.append(word)
        line = " ".join(word_list)
        return line
    
    def get_emotion(self, text):
        return self.emotion.emotion_answer(text)
        
    def strategy_2(self, query):
        pred_class = int(self.model.predict(self.word_segment(query))[0][0][-1])
        #Faq
        if pred_class==0 and self.FAQ:
            #faq结果
            answer_1, faq, score_1, match = self.faq.faq_answer(query)
            #docqa结果
            docqa_rst = self.docqa.docqa_answer('mita', query)
            res = eval(MessageToJson(docqa_rst, ensure_ascii=False, indent=2))
            #docqa是否有答案返回
            if res == {}:
                if score_1<self.faq_thres:
                    return self.FAQ_DEFAULT_ANSWER+faq, 1.0, pred_class 
                else:
                    return answer, score, pred_class
            else:
                try:
                    start = int(res['result'][0]['start'])
                except:
                    start = 0
                end = int(res['result'][0]['end'])
                answer_2, score_2 = res['result'][0]['context'][start:end], res['result'][0]['score']
                if score_1 >score_2:
                    return answer_1, score_1, pred_class
                else:
                    return answer_2, score_2, pred_class
                
        #闲聊
        elif pred_class==1 or (pred_class==0 and not self.FAQ):
            if pred_class == 1:
                answer, faq, score, match = self.faq_chat.chat_answer(query)
                if score < self.chat_thres:
                    res = self.chat.response([self.history], query)
                    answer = res[0]
                    score = res[1]
                    
            elif pred_class == 0:
                res = self.chat.response([self.history], query)
                answer = res[0]
                score = res[1]
            return answer, score, pred_class
        
        #文档问答
        else:
            docqa_rst = self.docqa.docqa_answer('wiki', query)
            res = eval(MessageToJson(docqa_rst, ensure_ascii=False, indent=2))
            if res=={}:
                return self.DOCQA_DEFAULT_ANSWER, 1.0, pred_class
            elif res['result'][0]['score']<self.docqa_thres:
                sources=[]
                for i in range(5):
                    sources.append(res['result'][i]['sourceId'])
                common_source = max(sources,key=sources.count)
                ans = self.DOCQA_DEFAULT_ANSWER_2+common_source+'》的问题，可以尝试换个问法哦～'
                return ans, res['result'][0]['score'], pred_class
            else:
                temp_ans = []
                for i in range(5):
                    try:
                        start = int(res['result'][i]['start'])
                    except:
                        start = 0
                    end = int(res['result'][i]['end'])
                    ans = res['result'][i]['context'][start:end]
                    temp_ans.append(ans)
                first_ans = temp_ans[0]
                #去重
                temp_ans = sorted(set(temp_ans), key=temp_ans.index)
                temp_ans.remove(first_ans)
                for text in temp_ans:
                    if first_ans in text:
                        temp_ans.remove(text)
                self.entities.extend(temp_ans)
                return first_ans, res['result'][0]['score'], pred_class
            
    def Do_skills(self, task_id):
        #进行guess
        if task_id == -1:
            task = build_skill(task_id, self.skill_type)
            if_stop_guess, guess_state = guess_stop(self.query)
            #是否停止猜测
            if if_stop_guess:
                answer, state = task.task_reply(guess_state)
                return answer, 1.0, 1, [state], [], []
            else:
                answer, state = task.guess(self.entities)
                if state!='end':
                    self.entities.pop(0)
                    return answer, 1.0, 3, [], [], [task_id]
                else:
                    return answer, 1.0, 3, [state], [], [task_id]

        #用户第一次询问，此时slots为空，entities为空
        elif self.slots == []:
            #获取该任务的第一个需要填充的槽值
            self.entities.clear()
            task = build_skill(task_id, self.skill_type)
            slot = task.get_first_slot()
            # 获取模版回复
            answer = task.response(slot)
            # NER -- 订票业务，首次query可能会有城市、日期信息
            if task_id == 0 and self.skill_type=='DH':
                shot_slots, entities = ner(self.query)
                #若初始槽值已被命中，找下一个
                if slot in shot_slots:
                    while slot in shot_slots:
                        slot = task.get_next_slot(slot)
                    answer = task.response(slot)
                shot_slots.append(slot)
                return answer, 1.0, 3, shot_slots, entities, [task_id]

            return answer, 1.0, 3, [slot], [], [task_id]

        #填槽
        else:
            #获取当前slot
            current_slot = self.slots[-1]
            #构建对应任务的策略
            task = build_skill(task_id, self.skill_type)
            #对用户输入进行分析，是否合法，且命中slot
            leg, entity = self.policy(current_slot, self.query)

            #更新有限状态机
            if leg:
                next_slot = task.get_next_slot(current_slot)
                #判断下一个槽值是否已存在
                while next_slot in self.slots:
                    next_slot = task.get_next_slot(next_slot)

                #返回不同状态下的模版回复
                if next_slot == 'end':
                    answer = task.response(next_slot, self.slots, self.entities)
                else:
                    answer = task.response(next_slot, self.slots, self.entities, entity)
                return answer, 1.0, 3, [next_slot], [entity], [task_id]
            elif not leg and entity!='':
                next_slot = 'end'
                answer = '已为您取消申请'
                return answer, 1.0, 3, [next_slot], [entity], [task_id]
            else:
                answer = '输入非法，请重新输入'
                return answer, 1.0, 3, [], [], [task_id]
    
    
    def policy(self,slot, query):
        if slot!='end':
            leg, match = check(query, slot)
        else:
            leg=True
            match = []
        return leg, match
    
    #改写
    def query_write_strategy(self, query, conversation, intent, task_id):
        if len(conversation)==2 or task_id!=[] or (task_id==[] and intent!=[] and intent[-1]=='Mutil-Turn'):
            return query
        if '' in  conversation[:2]:
            new_query, qr_score = self.qr.iur(conversation[2:], query)
        elif '' in conversation[2:]:
            new_query, qr_score = self.qr.iur(conversation[:2], query)
        else:
            new_query_1, qr_score_1 = self.qr.iur(conversation[:2], query)
            new_query_2, qr_score_2 = self.qr.iur(conversation[2:], query)
            new_query, qr_score = new_query_1, qr_score_1
            if qr_score_1 <qr_score_2:
                new_query = new_query_2
                qr_score = qr_score_2
        print(new_query, qr_score)
        if qr_score>self.qr_thres and new_query!=query:
            return new_query
        return query
    
    def response(self):
        logger = get_logger('log.log')
        logger.info('query input:{}'.format(self.query))
        if self.query == '':
            answer = '不好意思，我没听清你在说啥'
            score = 1.0
            intent = ''
            emotion = self.get_emotion(answer)
            logger.info('dm response :{} \n'.format(answer))
            if len(self.conversation)==4:
                self.conversation.pop(0)
                self.conversation.pop(0)
            self.conversation.insert(2, self.query)
            self.conversation.insert(3, answer)
            history = {'conversation':self.conversation,'intent':self.intent,'slots':self.slots,'entities':self.entities,'task_id':self.task_id}
            return answer, history, emotion.answer
        else:
            if self.conversation == []:
                self.conversation.insert(0,'')
                self.conversation.insert(1,'')
            #改写
            new_query = self.query_write_strategy(self.query, self.conversation, self.intent, self.task_id)
            self.query = new_query
            logger.info('query rewrite output:{}'.format(self.query))

            if self.task_id!=[]:
                if_task = True
                skill_id = self.task_id[-1]
            else:
                if_task, skill_id = If_Skill(self.query, self.intent, self.task_id, self.skill_type)
            answer = ''
            score = 1.0
            intent = ''
            slots, entities, task_id = [], [], []
            #判断是否为任务型对话，或者在多轮内（此时需要填充的槽非空）
            if if_task or self.slots!=[]:
                answer, score, intent, slots, entities, task_id = self.Do_skills(skill_id)
            else:
                answer, score, intent = self.strategy_2(self.query)
            
            intent = id_2_intent[int(intent)]
            emotion = self.get_emotion(answer)
            logger.info('predict class:{}'.format(intent))
            logger.info('slots :{} \n'.format(slots))
            logger.info('shot entities :{} \n'.format(entities))
            logger.info('current task id :{} \n'.format(task_id))
            logger.info('score :{}'.format(score))
            logger.info('dm response :{} \n'.format(answer))
                
            #更新history
            if len(self.conversation)==4:
                self.conversation.pop(0)
                self.conversation.pop(0)
            self.conversation.insert(2, self.query)
            self.conversation.insert(3, answer)
            
            #多轮对话内的意图id与task id，不重复加入
            if intent!='Mutil-Turn' or self.intent==[] or (intent == 'Mutil-Turn' and self.intent[-1]!='Mutil-Turn'):
                self.intent.append(intent)
                self.task_id.extend(task_id)
            
            if slots == ['end'] or (self.intent!=[] and self.intent[-1] in ['Faq', 'Chat']):
                self.slots.clear()
                self.entities.clear()
                self.task_id.clear()
            else:
                self.slots.extend(slots)
                self.entities.extend(str(entities))
            history = {'conversation':self.conversation,'intent':self.intent,'slots':self.slots,'entities':self.entities,'task_id':self.task_id}
            return answer, history, emotion.answer
                
    
if __name__ == '__main__':
    dm = DmClass()
    history = defaultdict(list)
    history['conversation'].insert(0,'')
    history['conversation'].insert(1,'')
    while True:
        print('用户：', end=' ')        
        query = input()
        start_time = time.time()
        session_id = 1
        robot_id = 1
        dm.load_data(query, history, session_id, robot_id)
        answer, score, intent, slot, entity, task_id, emotion = dm.response()
        end_time = time.time()
        print('*' * 20 + '回复完成!用时{:.2f}s'.format(end_time - start_time) + '*' * 20)
        print("机器人：: " + answer)
        print('score' + str(score))
        print('intent', intent)
        if len(history['conversation'])==4:
            history['conversation'].pop(0)
            history['conversation'].pop(0)
        history['conversation'].insert(2,query)
        history['conversation'].insert(3,answer)
        #多轮对话内的意图id与task id，不重复加入
        if intent!='Mutil-Turn' or history['intent']==[] or (intent == 'Mutil-Turn' and history['intent'][-1]!='Mutil-Turn'):
            history['intent'].append(intent)
            history['task_id'].extend(task_id)
        if slot == ['end'] or (history['intent']!=[] and history['intent'] in ['Faq', 'Chat']):
            history['slots'].clear()
            history['entities'].clear()
            history['task_id'].clear()
        else:
            history['slots'].extend(slot)
            history['entities'].extend(entity)
        print('历史', history)