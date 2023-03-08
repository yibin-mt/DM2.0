# rewrite_grpc_server

import sys
# sys.path.append('./DM/')
# sys.path.append('./protos/')
import time
import grpc
import rewrite_pb2
import rewrite_pb2_grpc
from concurrent import futures

# 实现 proto 文件中定义的 ReWriteServicer
class ReWriteService(rewrite_pb2_grpc.ReWriteServicer):
    
    def __init__(self):
        super(ReWriteService, self).__init__()
        # self.dm  = DmClass()
    
    # 实现 proto 文件中定义的 rpc 调用
    def GetReWrite(self, request, context):
        query = request.text
        history a= request.history
        session_id = request.session_id
        robot_id = request.robot_id
        
        # self.dm.load_data(query, history, session_id, robot_id)
        # ans, scores = self.dm.response()
        
        return rewrite_pb2.ReWriteResponse(query = ans)


def serve():
    # 启动 rpc 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rewrite_pb2_grpc.add_ReWriteServicer_to_server(ReWriteService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(60*60*24) 
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()