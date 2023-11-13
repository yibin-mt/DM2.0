import time
import sys
import argparse 
sys.path.append('./DM/')
sys.path.append('./DM/models/')
sys.path.append('./DM/chatglm_protos/')
from concurrent import futures
import grpc
from protos.nlp.dm import dm_stream_pb2
from protos.nlp.dm import dm_stream_pb2_grpc
from DmClass import DmClass

# 实现 proto 文件中定义的 DmServicer
class DmService(dm_stream_pb2_grpc.Dm_StreamServicer):
    
    def __init__(self, args):
        super(DmService, self).__init__()
        self.dm  = DmClass(args)
        
    
    # 实现 proto 文件中定义的 rpc 调用
    def GetDmStream(self, request, context):
        query = request.text
        history = request.history
        system_prompt = request.system_prompt
        self.dm.load_data(query, history, system_prompt)
        pre = ''
        for res in self.dm.response():
            if res:
                yield dm_stream_pb2.DmResponseStream(answer = res[len(pre):].encode('utf-8','ignore').decode('utf-8'))
                pre = res

def serve(args):
    # 启动 rpc 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dm_stream_pb2_grpc.add_Dm_StreamServicer_to_server(DmService(args), server)
    server.add_insecure_port('[::]:50051')
    # print('server start in port: ', args.dm_port)
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
    parser.add_argument('--chatgpt', action="store_true", default=False, help='if use chatgpt server')
    parser.add_argument('--chatglm', action="store_true", default=False, help='if use chatglm server')
    parser.add_argument('--musachat', action="store_true", default=False, help='if use musachat server')
    #对应字段的解释可以查看https://confluence.mthreads.com/pages/viewpage.action?pageId=93088300
    parser.add_argument('--GLM_ip', default='192.168.68.26', type=str)
    parser.add_argument('--GLM_port', default='60005', type=int)
    # parser.add_argument('--role', default='woman', type=str)
    parser.add_argument('--musachat_ip', default='192.168.68.26', type=str)
    parser.add_argument('--musachat_port', default='58090', type=str)
    parser.add_argument('--faq_ip', default='172.31.208.10', type=str)
    parser.add_argument('--faq_port', default='58999', type=str)
    parser.add_argument('--len_prompt', default='', type=str)
    parser.add_argument('--musachat_max_tokens', default=256, type=int)
    parser.add_argument('--emotion_ip', default='172.31.208.10', type=str)
    parser.add_argument('--emotion_port', default='58999', type=str)
    parser.add_argument('--dm_port', default='68999', type=str)
    args = parser.parse_args()
    serve(args)
    