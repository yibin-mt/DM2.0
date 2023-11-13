import grpc
from protos.nlp.faq import faq_pb2 as pb2
from protos.nlp.faq import faq_pb2_grpc as pb2_grpc
from grpc.beta import implementations
class Faq_inference():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        super(Faq_inference, self).__init__()

    def faq_answer(self, query):
        # conn = grpc.insecure_channel('192.168.4.29:60009')
        # conn = grpc.insecure_channel('172.31.208.10:58999')
        conn = grpc.insecure_channel(self.ip+':'+self.port)
        client = pb2_grpc.FaqStub(conn)
        res = client.GetFaq(pb2.FaqRequest(query=query, robot_id=0), timeout=1)
        answer = res.answer #faq对应的答案
        match = res.match   #匹配到的相似问句
        faq = res.faq       #对应的标准问句
        score = res.score   #匹配模型匹配的分数，可以视为置信度
        return answer, faq, score, match

# if __name__ == "__main__":
#     query = "怎么连接打印机"
#     tt = Faq_inference()
#     print(tt.faq_answer(query))