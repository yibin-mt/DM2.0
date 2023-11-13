from protos.nlp.docqa import docqa_pb2
from protos.nlp.docqa import docqa_pb2_grpc
from grpc.beta import implementations

class DocQAInference(object):
    def __init__(self, config, ip, port):
        self.host = config.get('host', ip)
        # self.port = config.get('port', 60005)
        self.port = config.get('port', int(port))
        self.timeout = config.get('timeout', 60)

    def docqa_answer(self, index_id, query):
        conn = implementations.insecure_channel(self.host, self.port)
        client = docqa_pb2_grpc.DocqaStub(channel=conn._channel)
        res = client.GetDocqa(docqa_pb2.DocqaRequest(index_id=index_id, query=query, session_id='1', robot_id=1), timeout=self.timeout)
        return res
