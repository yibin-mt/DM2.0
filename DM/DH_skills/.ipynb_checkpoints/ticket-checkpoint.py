ticket_slots = ['start_city', 'end_city', 'time', 'stage_type', 'confirm', 'end']

def response_ticket(slot, slots=None, entities=None, stage_type=None):
    if slot == 'start_city':
        return '请输入您的出发地'
    elif slot == 'end_city':
        return '请输入您的目的地'
    elif slot == 'time':
        return '请输入出发时间'
    elif slot == 'stage_type':
        return '请问是要预定经济舱还是头等舱呢'
    elif slot == 'confirm':
        print(entities)
        start_city = entities[slots.index('start_city')]
        end_city = entities[slots.index('end_city')]
        time = entities[slots.index('time')]
        # stage_type=entities[slots.index('stage_type')]
        return '好的，将为您预定%s，%s飞往%s的航班，%s，确定吗？'%(time, start_city, end_city, stage_type)
    else:
        start_city = entities[slots.index('start_city')]
        end_city = entities[slots.index('end_city')]
        time = entities[slots.index('time')]
        return '好的，已为您预定%s，%s飞往%s的航班。'%(time, start_city, end_city)