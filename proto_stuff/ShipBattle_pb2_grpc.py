# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import ShipBattle_pb2 as ShipBattle__pb2


class BattleshipServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.listenEvents = channel.stream_stream(
                '/shipbattle.BattleshipService/listenEvents',
                request_serializer=ShipBattle__pb2.EventRequest.SerializeToString,
                response_deserializer=ShipBattle__pb2.EventResponse.FromString,
                )
        self.listenEnemyMoves = channel.unary_stream(
                '/shipbattle.BattleshipService/listenEnemyMoves',
                request_serializer=ShipBattle__pb2.EnemyMovesRequest.SerializeToString,
                response_deserializer=ShipBattle__pb2.EnemyMoveResponse.FromString,
                )


class BattleshipServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def listenEvents(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def listenEnemyMoves(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BattleshipServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'listenEvents': grpc.stream_stream_rpc_method_handler(
                    servicer.listenEvents,
                    request_deserializer=ShipBattle__pb2.EventRequest.FromString,
                    response_serializer=ShipBattle__pb2.EventResponse.SerializeToString,
            ),
            'listenEnemyMoves': grpc.unary_stream_rpc_method_handler(
                    servicer.listenEnemyMoves,
                    request_deserializer=ShipBattle__pb2.EnemyMovesRequest.FromString,
                    response_serializer=ShipBattle__pb2.EnemyMoveResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'shipbattle.BattleshipService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class BattleshipService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def listenEvents(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/shipbattle.BattleshipService/listenEvents',
            ShipBattle__pb2.EventRequest.SerializeToString,
            ShipBattle__pb2.EventResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def listenEnemyMoves(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/shipbattle.BattleshipService/listenEnemyMoves',
            ShipBattle__pb2.EnemyMovesRequest.SerializeToString,
            ShipBattle__pb2.EnemyMoveResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
