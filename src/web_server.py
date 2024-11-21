'''
Author: FoolishDominator 1340995873@qq.com
Date: 2024-11-20 22:38:43
LastEditors: FoolishDominator 1340995873@qq.com
LastEditTime: 2024-11-22 00:23:08
FilePath: /sdcs/src/web_server.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import flask
from flask import request

import grpc
import datamanage_pb2,datamanage_pb2_grpc
from google.protobuf import any_pb2, wrappers_pb2

def init_stub():
    channel = grpc.insecure_channel('localhost:50051')
    stub = datamanage_pb2_grpc.DataManageStub(channel)
    return stub

app=flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
stub=init_stub()

@app.route('/')
def Welcome():
    return "Simple Distributed Cache System Working...\n",200

@app.route('/',methods=['POST'])
def Write():
    rawdata=request.json
    key,value=list(rawdata.items())[0]
    
    any_value=any_pb2.Any()
    
    if isinstance(value,str):
        wrappers_value=wrappers_pb2.StringValue(value=value)
        any_value.Pack(wrappers_value)
    elif isinstance(value,int):
        wrappers_value=wrappers_pb2.Int32Value(value=value)
        any_value.Pack(wrappers_value)
    elif isinstance(value,bool):
        wrappers_value=wrappers_pb2.BoolValue(value=value)
        any_value.Pack(wrappers_value)
    elif isinstance(value,float):
        wrappers_value=wrappers_pb2.FloatValue(value=value)
        any_value.Pack(wrappers_value)
    else:
        pass
    
    stub.Write(datamanage_pb2.WriteRequest(key=key,value=any_value))
    return '',200

@app.route('/<key>',methods=['GET'])
def Read(key):
    reply=stub.Read(datamanage_pb2.ReadRequest(key=key))
    
    if reply.value is not None:
        any_value=reply.value
        
        str_value=wrappers_pb2.StringValue()
        if any_value.Unpack(str_value):
            return '{{"{key}":"{value}"}}\n'.format(key=key,value=str_value.value),200
        
        int_value=wrappers_pb2.Int32Value()
        if any_value.Unpack(int_value):
            return '{{"{key}":{value}}}\n'.format(key=key,value=int_value.value),200
        
        bool_value=wrappers_pb2.BoolValue()
        if any_value.Unpack(bool_value):
            return '{{"{key}":{value}}}\n'.format(key=key,value=bool_value.value),200
        
        float_value=wrappers_pb2.FloatValue()
        if any_value.Unpack(float_value):
            return '{{"{key}":{value}}}\n'.format(key=key,value=float_value.value),200
        
        return '',404
    else:
        return '',404
    
@app.route('/<key>',methods=['DELETE'])
def Delete(key):
    reply=stub.Delete(datamanage_pb2.DeleteRequest(key=key))
    if reply.success:
        return '1\n',200
    else:
        return '0\n',200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)