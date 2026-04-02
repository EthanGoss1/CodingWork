from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
import random
import time
import asyncio
from KVS import KVS

from common import nodeState, LogEntry
from raft_client_manager import RaftClientManager

DEBUG_BOOL = False

#TODO: Add common type for operation methods, instead of just numbers
#TODO: Add state machine integration for committed logs
#TODO: Client for interacting with the cluster
#TODO:


@dataclass
class RaftNode:
    id: int
    peer_ids: List[int]
    state: nodeState = nodeState.FOLLOWER
    currentTerm: int = 0

    commitIndex: int = -1
    lastApplied: int = -1
    log: List[LogEntry] = field(default_factory=list)
    next_index: Dict[int, int] = field(default_factory=dict)
    match_index: Dict[int, int] = field(default_factory=dict)
    pending_requests: Dict[int, asyncio.Future] = field(default_factory=dict)

    election_timeout: int = field(default_factory=lambda: random.randint(150, 300))
    last_activity_time: float = field(default_factory=time.time)
    heartbeat_interval: int = 50
    max_heartbeat_check: int = 200
    
    voted_for: Optional[int] = None
    votes_received: Set[int] = field(default_factory=set)

    client_manager: RaftClientManager = None
    kvs: KVS = None

    def __post_init__(self):
        filename = f"node_{self.id}_kvs.txt"
        self.kvs = KVS(filename)
        print(f"[Node {self.id}] KVS initialized at {self.kvs.full_path}")

    def is_there_another_leader(self, incoming_term) -> bool:
        if incoming_term > self.currentTerm:
            self.currentTerm = incoming_term
            self.state = nodeState.FOLLOWER
            self.voted_for = None
            self.last_activity_time = time.time()
            return True
        return False

    async def start_election(self) -> None:
        if DEBUG_BOOL:
            print(f"server {self.id} election started in term {self.currentTerm}!")
        # Set current state to candidate and update term
        self.state = nodeState.CANDIDATE
        self.currentTerm += 1

        # vote for oneself
        self.voted_for = self.id
        self.votes_received = {self.id}

        self.last_activity_time = time.time()

        last_log_index = len(self.log) - 1
        last_log_term = self.log[last_log_index].term if last_log_index >= 0 else 0

        # set up list of async tasks to send to other nodes to request votes
        tasks = [asyncio.create_task(self.client_manager.send_request_vote(
            node_id=pid,
            term=self.currentTerm,
            candidate_id=self.id,
            last_log_index=last_log_index,
            last_log_term=last_log_term)) for pid in self.peer_ids if pid != self.id]

        # compute deadline using election_timeout
        election_start = time.time()
        deadline = election_start + self.election_timeout / 1000

        if tasks:
            # wait for tasks until deadline
            timeout = max(0.0, deadline - time.time())
            done, pending = await asyncio.wait(tasks, timeout=timeout)

            # cancel any pending tasks (timed out)
            if pending or time.time() >= deadline:
                for p in pending:
                    p.cancel()
                # start a new election asynchronously and stop processing this round
                self.voted_for = None
                self.votes_received.clear()
                asyncio.create_task(self.start_election())
                return

            # collect results from completed tasks, ignoring exceptions
            results = []
            for task in done:
                try:
                    results.append(task.result())
                except Exception:
                    continue

            for reply_term, vote_granted, pid in results:
                # step down if we see a higher term using follower check logic
                if self.is_there_another_leader(reply_term):
                    self.voted_for = None
                    self.votes_received.clear()
                    return

                if vote_granted:
                    self.votes_received.add(pid)

        majority = (len(self.peer_ids) // 2) + 1
        if len(self.votes_received) >= majority and self.state == nodeState.CANDIDATE:
            print(f"[Node {self.id}] WON ELECTION for term {self.currentTerm}!")
            self.state = nodeState.LEADER
            # initialize leader state
            next_idx = len(self.log)
            for pid in self.peer_ids:
                if pid == self.id:
                    continue
                self.next_index[pid] = next_idx
                self.match_index[pid] = -1

            # reset last activity time so heartbeats start from leader
            self.last_activity_time = time.time()
            self.voted_for = None
            self.votes_received.clear()
            
            # send an immediate heartbeat
            if hasattr(self, "send_heartbeat"):
                asyncio.create_task(self.send_heartbeat())
        else:
            if DEBUG_BOOL:
                print(f"[Node {self.id}] Election lost in term {self.currentTerm}.")

            self.voted_for = None
            self.votes_received.clear()
            asyncio.create_task(self.start_election())

    def handle_request_vote(self,
                            term: int,
                            candidate_id: int,
                            last_log_index: int,
                            last_log_term: int) -> Tuple[int, bool]:
        self.last_activity_time = time.time()

        if DEBUG_BOOL:
            print(f"Candidate {candidate_id} is requesting vote from {self.id} for term {term}!")

        if term < self.currentTerm:
            return self.currentTerm, False

        if self.voted_for is None or self.voted_for == candidate_id:
            my_last_log_index = len(self.log) - 1
            my_last_log_term = self.log[my_last_log_index].term if my_last_log_index >= 0 else 0

            if (last_log_term > my_last_log_term) or \
                    (last_log_term == my_last_log_term and last_log_index >= my_last_log_index):
                self.voted_for = candidate_id
                self.last_activity_time = time.time()
                return self.currentTerm, True

        return self.currentTerm, False

    def handle_append_entries(self, term, leader_id, prev_log_index, prev_log_term, entries, leader_commit) -> Tuple[
        int, bool]:
        if self.is_there_another_leader(term):
            # this is just to revert the state back to follower if there's a higher term number
            pass

        # Reply false if term < currentTerm
        if term < self.currentTerm:
            return self.currentTerm, False

        self.last_activity_time = time.time()

        if term > self.currentTerm:
            self.currentTerm = term
            self.state = nodeState.FOLLOWER
            self.voted_for = None
            self.votes_received.clear()
        
        # Validate prev_log_index / prev_log_term
        # A prev_log_index < 0 means the leader has no prior entry to match (empty log)
        if prev_log_index >= 0:
            if prev_log_index >= len(self.log):
                # Missing the entry at prev_log_index
                return self.currentTerm, False
            if self.log[prev_log_index].term != prev_log_term:
                # Term mismatch at prev log index -> conflict
                return self.currentTerm, False

        # If an existing entry conflicts with a new one (same index
        # but different terms), delete the existing entry and all that
        # follow it
        entries = entries or []

        # Append any new entries not already in the log
        insert_index = prev_log_index + 1
        for i, entry in enumerate(entries):
            target_index = insert_index + i

            if target_index < len(self.log):
                # CONFLICT DETECTED
                if self.log[target_index].term != entry.term:

                    # [CRITICAL FIX] Fail waiting clients before deleting
                    for idx_to_cancel in range(target_index, len(self.log)):
                        if idx_to_cancel in self.pending_requests:
                            self.pending_requests[idx_to_cancel].set_result("ERR: Log Truncated/Leader Changed")
                            del self.pending_requests[idx_to_cancel]

                    self.log = self.log[:target_index]
                    self.log.append(entry)
                else:
                    continue
            else:
                self.log.append(entry)

        if leader_commit > self.commitIndex:
            # The commit index is the min of what the leader says
            # and the index of the last new entry we just added.
            last_new_entry_index = prev_log_index + len(entries)
            self.commitIndex = min(leader_commit, last_new_entry_index)
            # commit logs
            asyncio.create_task(self.apply_logs())

        return self.currentTerm, True

    async def main_loop(self):
        """Main heartbeat of the node."""
        while True:
            # Tick interval
            await asyncio.sleep(self.heartbeat_interval / 1000.0)

            if self.state == nodeState.FOLLOWER or self.state == nodeState.CANDIDATE:
                # Check Election Timeout
                timeout_ms = (time.time() - self.last_activity_time) * 1000
                if timeout_ms > self.election_timeout:
                    print(f"[Node {self.id}] Timeout! ({timeout_ms:.0f}ms). Starting Election.")
                    await self.start_election()

            elif self.state == nodeState.LEADER:
                # Send Heartbeats / Replication
                print(f'{self.id} is the leader in term {self.currentTerm}!')
                await self.send_heartbeat()

    async def handle_client_command(self,
                                    operation_type: int,
                                    key: str,
                                    value: str,
                                    term: Optional[int] = None) -> Optional[Tuple[bool, str]]:

        if self.state == nodeState.LEADER:
            # Stale check
            if term is not None and term > self.currentTerm:
                self.currentTerm = term
                self.state = nodeState.FOLLOWER
                self.voted_for = None
            else:

                if operation_type == 0:  # GET
                    # Directly handle GET without log entry
                    try:
                        result = self.kvs.GET(key)

                        if result is not None:
                            return True, result
                        else:
                            return False, "ERR: Key Not Found"
                    except Exception as e:
                        return False, f"ERR: {str(e)}"

                cmd = ""

                if operation_type == 1:  # PUT
                    cmd = f"A {key};{value}"
                elif operation_type == 2: # DELETE
                    cmd = f"D {key}"
                else:
                    return False, "Invalid Operation"

                new_entry = LogEntry(term=self.currentTerm, command=cmd)
                self.log.append(new_entry)
                entry_index = len(self.log) - 1

                # Create Future
                future = asyncio.Future()
                self.pending_requests[entry_index] = future

                try:
                    result = await asyncio.wait_for(future, timeout=5.0)
                    return True, result
                except asyncio.TimeoutError:
                    del self.pending_requests[entry_index]
                    return False, "Consensus Timeout"

        if term is not None:
            return None  # equivalent to "Not Handled"

        # We simply fire requests at everyone else in parallel.
        tasks = []
        for peer_id in self.peer_ids:
            if peer_id == self.id:
                continue

            # Forward with our term to prevent loops
            tasks.append(asyncio.create_task(
                self.client_manager.send_client_request(
                    node_id=peer_id,
                    op_type=operation_type,
                    key=key,
                    value=value,
                    term=self.currentTerm
                )
            ))

        # We don't wait for all. We return the moment any node gives a valid answer.
        for finished_task in asyncio.as_completed(tasks):
            try:
                response = await finished_task

                if response is not None:
                    success, result_val = response

                    # If we got a response (Success OR Leader Error), we return it.
                    # We assume only the actual Leader returns a non-None response.
                    return success, result_val

            except Exception:
                continue

        return False, "Cluster Unavailable"

    async def apply_logs(self):
        while self.lastApplied < self.commitIndex:
            self.lastApplied += 1
            entry = self.log[self.lastApplied]

            response = "MOCKED_OK"

            try:
                # Run blocking Disk I/O in a thread
                # Otherwise, the heartbeat loop freezes while writing to disk
                success = await asyncio.to_thread(self.kvs.commit_entry, entry.command)

                if success:
                    response = "OK"
                    print(f"[Node {self.id}] Committed index {self.lastApplied}: {entry.command}")
                else:
                    response = "ERR: KVS Commit Failed"
            except Exception as e:
                response = f"ERR: {str(e)}"

            # Notify waiting client
            if self.lastApplied in self.pending_requests:
                future = self.pending_requests[self.lastApplied]
                if not future.done():
                    future.set_result(response)
                del self.pending_requests[self.lastApplied]

    async def send_heartbeat(self):
        for peer_id in self.peer_ids:
            if peer_id == self.id: continue

            next_idx = self.next_index.get(peer_id, len(self.log))
            entries = self.log[next_idx:]  # Empty if caught up (Heartbeat)

            prev_idx = next_idx - 1
            prev_term = self.log[prev_idx].term if prev_idx >= 0 else 0

            # Send RPC (Fire and Forget)
            asyncio.create_task(self.send_replication_to_peer(peer_id, prev_idx, prev_term, entries))

    async def send_replication_to_peer(self, peer_id, prev_idx, prev_term, entries):
        res = await self.client_manager.send_append_entries(
            node_id=peer_id,
            term=self.currentTerm,
            leader_id=self.id,
            prev_log_index=prev_idx,
            prev_log_term=prev_term,
            entries=entries,
            leader_commit=self.commitIndex
        )

        if res is None:
            return  # Network error
        term, success = res

        if term > self.currentTerm:
            self.currentTerm = term
            self.state = nodeState.FOLLOWER
            self.voted_for = None
            return

        if success:
            if len(entries) > 0:
                # Update tracking
                new_match = prev_idx + len(entries)
                self.match_index[peer_id] = max(self.match_index.get(peer_id, -1), new_match)
                self.next_index[peer_id] = self.match_index[peer_id] + 1
                self.update_commit_index()
        else:
            #Log Mismatch (Follower rejected prev_log_index/term)

            # Get current next_index safely.
            # Default to len(self.log) if missing
            current_next = self.next_index.get(peer_id, len(self.log))

            #Decrement by 1 to try the previous entry next time
            # Ensure we don't go below 0
            self.next_index[peer_id] = max(0, current_next - 1)

    def update_commit_index(self):
        # Look for N > commitIndex that has majority
        for N in range(len(self.log) - 1, self.commitIndex, -1):
            if self.log[N].term != self.currentTerm: continue

            count = 1  # Self
            for peer_id in self.peer_ids:
                if peer_id == self.id: continue
                if self.match_index.get(peer_id, -1) >= N:
                    count += 1

            if count >= (len(self.peer_ids) // 2) + 1:
                self.commitIndex = N
                asyncio.create_task(self.apply_logs())
                break



