from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

class nodeState(Enum):
    LEADER = 1
    CANDIDATE = 2
    FOLLOWER = 3

class operationType(Enum):
    GET = 0
    PUT = 1
    DELETE = 2

@dataclass
class LogEntry:
    term: int
    command: str

NodesAddressMap = Dict[int, str]