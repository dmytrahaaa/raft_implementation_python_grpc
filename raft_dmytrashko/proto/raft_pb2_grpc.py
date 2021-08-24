# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import raft_pb2 as raft__pb2


class RaftStub(object):
    """package "./proto"

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Vote = channel.unary_unary(
                '/Raft/Vote',
                request_serializer=raft__pb2.RequestVoteRPC.SerializeToString,
                response_deserializer=raft__pb2.ResponseVoteRPC.FromString,
                )
        self.AppendMessage = channel.unary_unary(
                '/Raft/AppendMessage',
                request_serializer=raft__pb2.RequestAppendEntriesRPC.SerializeToString,
                response_deserializer=raft__pb2.ResponseAppendEntriesRPC.FromString,
                )


class RaftServicer(object):
    """package "./proto"

    """

    def Vote(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AppendMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RaftServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Vote': grpc.unary_unary_rpc_method_handler(
                    servicer.Vote,
                    request_deserializer=raft__pb2.RequestVoteRPC.FromString,
                    response_serializer=raft__pb2.ResponseVoteRPC.SerializeToString,
            ),
            'AppendMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.AppendMessage,
                    request_deserializer=raft__pb2.RequestAppendEntriesRPC.FromString,
                    response_serializer=raft__pb2.ResponseAppendEntriesRPC.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Raft', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Raft(object):
    """package "./proto"

    """

    @staticmethod
    def Vote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Raft/Vote',
            raft__pb2.RequestVoteRPC.SerializeToString,
            raft__pb2.ResponseVoteRPC.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AppendMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Raft/AppendMessage',
            raft__pb2.RequestAppendEntriesRPC.SerializeToString,
            raft__pb2.ResponseAppendEntriesRPC.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)