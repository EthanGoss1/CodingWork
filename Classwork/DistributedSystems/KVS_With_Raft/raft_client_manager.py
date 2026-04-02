import asyncio
import time
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any, Tuple
from concurrent.futures import ThreadPoolExecutor

from common import NodesAddressMap
import grpc

from rpc import raft_pb2_grpc, raft_pb2


class RaftClientManager:

    def __init__(self, nodes_map: NodesAddressMap):
        self.node_stubs = {}
        for node_id, node_address in nodes_map.items():
            channel = grpc.aio.insecure_channel(node_address)
            self.node_stubs[node_id] = raft_pb2_grpc.RaftStub(channel)

    async def send_request_vote(self, node_id, term, candidate_id, last_log_index, last_log_term) -> Optional[
        Tuple[int, bool, int]]:
        if node_id not in self.node_stubs:
            print(f"Error: No stub for peer {node_id}")
            return None

        stub = self.node_stubs[node_id]

        try:
            request = raft_pb2.RequestVoteRequest(
                term=term,
                candidateId=candidate_id,
                lastLogIndex=last_log_index,
                lastLogTerm=last_log_term
            )

            response = await stub.RequestVote(request)
            return response.term, response.voteGranted, node_id
        except grpc.aio.AioRpcError as e:  # Use AioRpcError
            print(f"RPC error sending RequestVote to {node_id}: {e.details()}")
            return None

    async def send_append_entries(self, node_id, term, leader_id, prev_log_index, prev_log_term, entries,
                                  leader_commit) -> Optional[Tuple[int, bool]]:
        if node_id not in self.node_stubs:
            print(f"Error: No stub for peer {node_id}")
            return None

        stub = self.node_stubs[node_id]

        try:
            pb_entries = []
            for entry in entries:
                pb_entries.append(raft_pb2.LogEntry(
                    term=entry.term,
                    command=entry.command
                ))

            request = raft_pb2.AppendEntriesRequest(
                term=term,
                leaderId=leader_id,
                prevLogIndex=prev_log_index,
                prevLogTerm=prev_log_term,
                entries=pb_entries,  # <--- Pass the converted list here
                leaderCommit=leader_commit
            )

            response = await stub.AppendEntries(request, timeout=0.1)

            return response.term, response.success
        except grpc.aio.AioRpcError as e:
            # print(f"RPC error sending AppendEntries to {node_id}: {e.details()}")
            return None


    async def send_client_request(self,
                                  node_id: int,
                                  op_type: int,
                                  key: str,
                                  value: str,
                                  term: Optional[int] = None) -> Optional[Tuple[bool, str]]:
        if node_id not in self.node_stubs:
            print(f"Error: No stub for peer {node_id}")
            return None

        stub = self.node_stubs[node_id]

        try:
            op_int = int(op_type)

            #TODO: maybe map operationType for safety

            request = raft_pb2.ClientRequest(
                operation=op_int,
                key=key,
                value=value
            )

            if term is not None:
                request.term = term

            # Add a short timeout for discovery
            response = await stub.ClientCommand(request, timeout=1.0)

            # Proxy Rejection
            if response.result == "PROXY_REJECTED":
                return None

            return response.success, response.result

        except grpc.aio.AioRpcError as e:
            # None on network error
            return None



