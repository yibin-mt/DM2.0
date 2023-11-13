dayoff_slots = ['kind','lay_time','season', 'confirm', 'end']

def response_dayoff(slot, slots=None, entities=None, entity=None):
    if slot == 'kind':
        return '请确定您的休假项目(1.年假｜2.带薪病假｜3.育儿假｜4.居家办公｜5.事假｜6.病假｜7.婚假｜8.产假)'
    elif slot == 'lay_time':
        return '请输入休假的开始与结束时间（例如：2020-2-15 上午｜2020-2-15 下午）'
    elif slot == 'season':
        return '请输入您的请假理由'
    elif slot == 'confirm':
        return '确定提交上述休假事项吗？'
    else:
        return '您的休假事项已提交！'