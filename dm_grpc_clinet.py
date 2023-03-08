import grpc
from protos.nlp.dm import dm_pb2
from protos.nlp.dm import dm_pb2_grpc

def run():
    # 连接 rpc 服务器
    channel = grpc.insecure_channel('localhost:50051')
    # 调用 rpc 服务
    stub = dm_pb2_grpc.DmStub(channel)
    text = '你好'
    print('text:',text)
    response = stub.GetDm(dm_pb2.DmRequest(text=text, history={}, session_id='1', robot_id = -1))
    print("Dm client received: " + response.answer)
    text = '怎么连接打印机'
    print('text:',text)
    response = stub.GetDm(dm_pb2.DmRequest(text=text, history = {'conversation':['','']}, session_id='1', robot_id = -1))
    print("Dm client received: " + response.answer)

if __name__ == '__main__':
    run()