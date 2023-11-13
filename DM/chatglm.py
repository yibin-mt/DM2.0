import grpc
import sys
sys.path.append('chatglm_protos/')
import nlg_pb2
import nlg_pb2_grpc
from grpc.beta import implementations

class ChatGlm_inference(object):
    
    def __init__(self, ip, port):
        super(ChatGlm_inference, self).__init__()
        self.ip = ip
        self.port = port
        
    def response(self, hisorty, query):
        conn = implementations.insecure_channel(self.ip,self.port)
        client = nlg_pb2_grpc.NLGServiceStub(channel=conn._channel)
        system = '你是摩尔线程的对话数字人，名字叫做穆莎。你所在的空间，是真实存在于摩尔北京总部的一个展厅，它是通过混合渲染管线制作和渲染的。接下来的问题，回答尽量不超过90个字。'
        message = hisorty+[query]
        print(message)
        res = client.NLGGet(nlg_pb2.NLGMessage(context=message, prompt_prefix=system))
        for i in res:
            yield i.output.replace('<n>', '\n')