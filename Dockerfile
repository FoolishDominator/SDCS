FROM ubuntu:20.04

# 构建环境
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && \
apt-get clean && \
apt-get update && \
apt-get install -y python3 python3-pip vim git && \
apt-get autoclean && \
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple flask requests grpcio grpcio-tools protobuf

WORKDIR /app
COPY . /app

#从.proto文件生成python代码，放在src目录下
RUN python3 -m grpc_tools.protoc -I./protos --python_out=./src --pyi_out=./src --grpc_python_out=./src ./protos/datamanage.proto

#启动服务
WORKDIR /app/script/

RUN chmod +x start_service.sh
CMD ["./start_service.sh"] 