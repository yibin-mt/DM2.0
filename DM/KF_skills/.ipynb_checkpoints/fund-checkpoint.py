fund_slots = ['base', 'city', 'end']

def response_fund(slot, slots=None, entities=None, entity=None):
    if slot == 'base':
        return '请输入您的税前月薪'
    elif slot == 'city':
        return '请输入您的工作城市'
    else:
        out = int(int(entities[0])*0.12*2)
        return '您每个月的公积金为：'+ str(out)+'元'