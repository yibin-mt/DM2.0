import time
import sys
import argparse 
sys.path.append('./DM/')
sys.path.append('./DM/models/')
from concurrent import futures
import grpc
from protos.nlp.dm import dm_pb2
from protos.nlp.dm import dm_pb2_grpc
from DmClass import DmClass

# 实现 proto 文件中定义的 DmServicer
class DmService(dm_pb2_grpc.DmServicer):
    
    def __init__(self, args):
        super(DmService, self).__init__()
        self.dm  = DmClass(args)
    
    # 实现 proto 文件中定义的 rpc 调用
    def GetDm(self, request, context):
        query = request.text
        history = request.history
        session_id = request.session_id
        robot_id = request.robot_id
        self.dm.load_data(query, history, session_id, robot_id)
        answer, history, emotion = self.dm.response()
        return dm_pb2.DmResponse(answer = answer, history = history, emotion = emotion)


def serve(args):
    # 启动 rpc 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dm_pb2_grpc.add_DmServicer_to_server(DmService(args), server)
    server.add_insecure_port('[::]:50051')
    print('server start in port: ', args.dm_port)
    # server.add_insecure_port('0.0.0.0:'+args.dm_port)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--robot_type', default='', choices=['DH', 'KF'], type=str, help='Robot type, DH or KF')
    parser.add_argument('--chat_repo', default=1, choices=[0, 1], type=int, help='which repo used by chat_infer module')
    parser.add_argument('--skill_type', default='DH', choices=['DH', 'KF'], help='What type of multi-turn capability the robot has')
    parser.add_argument('--FAQ', action="store_true", default=False, help='if run the faq server')
    parser.add_argument('--QR', action="store_true", default=False, help='if run the query rewrite server')
    
    #对应字段的解释可以查看https://confluence.mthreads.com/pages/viewpage.action?pageId=93088300
    parser.add_argument('--qr_ip', default='192.168.68.26', type=str)
    parser.add_argument('--qr_port', default='60005', type=str)
    parser.add_argument('--faq_ip', default='172.31.208.10', type=str)
    parser.add_argument('--faq_port', default='58999', type=str)
    parser.add_argument('--docqa_ip', default='172.31.208.4', type=str)
    parser.add_argument('--docqa_port', default='60005', type=str)
    parser.add_argument('--chat_ip', default='172.31.208.9', type=str)
    parser.add_argument('--chat_port', default='60005', type=str)
    parser.add_argument('--emotion_ip', default='172.31.208.10', type=str)
    parser.add_argument('--emotion_port', default='58999', type=str)
    parser.add_argument('--dm_port', default='68999', type=str)
    args = parser.parse_args()
    serve(args)
    