from grpc_tools import protoc

protoc.main((
    '',
    '-I./protos',
    '--python_out=./src',
    '--grpc_python_out=./src',
    './protos/chat.proto',
))
