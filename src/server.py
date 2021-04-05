"""The Python AsyncIO implementation of the gRPC route guide server."""

import time
import logging
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import grpc
import chat_pb2 as chat
import chat_pb2_grpc as rpc


class ChatServicer(rpc.ChatServicer):
    """Provides methods that implement functionality of chat server."""
    def __init__(self):
        self.chats = deque(maxlen=10)
        self.running = True

    def Login(self, request, context):
        logging.info("Login called at {}".format(time.strftime("%Y-%m-%d %H:%M:%S +0000", time.gmtime())))

        message = chat.Post(user='Server', message='{} joined the chat!'.format(request.user))
        self.chats.append(message)

        return chat.Empty()

    def Logout(self, request, context):
        logging.info("Logout called at {}".format(time.strftime("%Y-%m-%d %H:%M:%S +0000", time.gmtime())))

        message = chat.Post(user='Server', message='{} left the chat!'.format(request.user))
        self.chats.append(message)

        return chat.Empty()

    def Send(self, request, context):
        logging.info("Send called at {}".format(time.strftime("%Y-%m-%d %H:%M:%S +0000", time.gmtime())))
        self.chats.append(request)

        return chat.Empty()

    def Stream(self, request, context):
        logging.info("ChatStream called at {}".format(time.strftime("%Y-%m-%d %H:%M:%S +0000", time.gmtime())))
        lastindex = 0
        # For every client a infinite loop starts (in gRPC's own managed thread)
        while True:
            # Check if there are any new messages
            while len(self.chats) > lastindex:
                message = self.chats[lastindex]
                lastindex += 1

                if len(self.chats) >= 10:
                    self.chats.clear()
                    lastindex = 0

                yield message


def serve():
    logging.info("Server started at {}".format(time.strftime("%Y-%m-%d %H:%M:%S +0000", time.gmtime())))

    servicer = ChatServicer()
    try:
        server = grpc.server(ThreadPoolExecutor())
        rpc.add_ChatServicer_to_server(servicer, server)
        server.add_insecure_port('[::]:50051')
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        servicer.running = False
        logging.info("Server closed at {}".format(time.strftime("%Y-%m-%d %H:%M:%S +0000", time.gmtime())))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
