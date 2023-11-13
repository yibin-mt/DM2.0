import grpc
from protos.nlp.emotion import emotion_pb2, emotion_pb2_grpc
from grpc.beta import implementations
class Emotion_inference():
    def __init__(self, ip, port):
        super(Emotion_inference, self).__init__()
        self.ip = ip
        self.port = port

    def emotion_answer(self, query):
        channel = grpc.insecure_channel(self.ip+':'+self.port)
        emotion_client = emotion_pb2_grpc.EmotionStub(channel)
        res = emotion_client.GetEmotion(emotion_pb2.EmotionRequest(query=query, session_id='1', robot_id=2), timeout=1)
        return res
