import random
class Task(object):
    def __init__(self, slots):
        super(Task, self).__init__()
        self.slots = slots
        self.templ = ['我又找了一下，是', '我想了想，是', '我思考了一下，是']
        
    def get_next_slot(self, slot):
        index = self.slots.index(slot)
        return self.slots[index+1]
    
    def get_first_slot(self):
        return self.slots[0]
    
    def guess(self, entities):
        #猜测答案
        if len(entities)>0:
            num = random.randint(0,2)
            return self.templ[num]+entities[0]+'吗？', '_'
        #猜测失败
        else:
            return '不好意思，我目前的学习能力有限，我会下去更新知识的！', 'end'
        
    def task_reply(self, state):
        #任务完成/猜测成功/猜测失败后的模版回复
        if state == 'guess_sucess':
            return '嘿嘿～，厉害吧', 'end'
        elif state == 'guess_stop':
            return '好吧～我会继续学习的，争取下次为您找到正确的答案！', 'end'
        elif state == 'praise':
            return '谢谢', 'end'
        