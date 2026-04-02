import grpc
import asyncio
from grpc import aio

from raft_node import RaftNode
from rpc import raft_pb2_grpc, raft_pb2
from concurrent.futures import ThreadPoolExecutor


class RaftRequestService(raft_pb2_grpc.RaftServicer):

    def __init__(self, raft_node: RaftNode):
        super(RaftRequestService, self).__init__()

        self.raft_node = raft_node

    async def RequestVote(self, request, context) -> raft_pb2.RequestVoteResponse:
        response = self.raft_node.handle_request_vote(
            term=request.term,
            candidate_id=request.candidateId,
            last_log_index=request.lastLogIndex,
            last_log_term=request.lastLogTerm
        )

        return raft_pb2.RequestVoteResponse(
            term=response[0],
            voteGranted=response[1]
        )

    async def AppendEntries(self, request, context) -> raft_pb2.AppendEntriesResponse:
        response = self.raft_node.handle_append_entries(
            term=request.term,
            leader_id=request.leaderId,
            prev_log_index=request.prevLogIndex,
            prev_log_term=request.prevLogTerm,
            entries=request.entries,
            leader_commit=request.leaderCommit
        )

        return raft_pb2.AppendEntriesResponse(
            term=response[0],
            success=response[1]
        )

    async def ClientCommand(self, request, context) -> raft_pb2.ClientResponse:

        term = None

        if request.HasField("term"):
            term = request.term

        response = await self.raft_node.handle_client_command(
            operation_type=request.operation,
            key=request.key,
            value=request.value,
            term=term
        )

        if response is None:
            return raft_pb2.ClientResponse(
                success=False,
                result="PROXY_REJECTED"  # proxy rejection flag
            )

        success, result = response
        return raft_pb2.ClientResponse(
            success=success,
            result=result
        )




async def run_async_server(raft_node, port):
    server = grpc.aio.server()

    raft_pb2_grpc.add_RaftServicer_to_server(RaftRequestService(raft_node), server)

    server.add_insecure_port(f'[::]:{port}')
    print(f"Async server for {raft_node.id} starting on port {port}...")

    await server.start()
    await server.wait_for_termination()

