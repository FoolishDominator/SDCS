from concurrent import futures
import logging

import hashlib
import os

import grpc
import datamanage_pb2,datamanage_pb2_grpc

class DataManage(datamanage_pb2_grpc.DataManageServicer):
    def __init__(self):
        self.__current_id=int(os.environ['CURRENT_ID'])
        self.db={}
        
    def __get_target_node_id(self,key):
        md5hash=hashlib.md5(key.encode())
        hexhash=md5hash.hexdigest()
        int_hash=int(hexhash,16)
        total_servers=int(os.environ['TOTAL_SERVERS'])
        target_id=int_hash%total_servers+1
        return target_id
    
    # 获取目标节点的stub
    def __create_stub(self,target_id): 
        channel=grpc.insecure_channel('server' + str(target_id) + ':50051')
        stub=datamanage_pb2_grpc.DataManageStub(channel)
        return stub
        
    def Write(self, request, context):
        target_node_id=self.__get_target_node_id(request.key)
        if target_node_id!=self.__current_id:
            stub=self.__create_stub(target_node_id)
            stub.Write(datamanage_pb2.WriteRequest(key=request.key,value=request.value))
        else:
            self.db[request.key]=request.value
        # ??
        return datamanage_pb2.WriteReply(success=True)
    
    def Read(self, request, context):
        target_node_id=self.__get_target_node_id(request.key)
        if target_node_id!=self.__current_id:
            stub=self.__create_stub(target_node_id)
            return stub.Read(datamanage_pb2.ReadRequest(key=request.key))
        else:
            if request.key in self.db:
                return datamanage_pb2.ReadReply(value=self.db[request.key])
            else:
                return datamanage_pb2.ReadReply(value=None)
            
    def Delete(self, request, context):
        target_node_id=self.__get_target_node_id(request.key)
        if target_node_id!=self.__current_id:
            stub=self.__create_stub(target_node_id)
            return stub.Delete(datamanage_pb2.DeleteRequest(key=request.key))
        else:
            if request.key in self.db:
                self.db.pop(request.key)
                return datamanage_pb2.DeleteReply(success=True)
            else:
                return datamanage_pb2.DeleteReply(success=False)

def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    datamanage_pb2_grpc.add_DataManageServicer_to_server(DataManage(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    # print("Server started, listening on " + port)
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    serve()
