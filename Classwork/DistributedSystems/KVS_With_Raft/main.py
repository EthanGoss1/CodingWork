import asyncio
import random

from raft_node import RaftNode
from raft_client_manager import RaftClientManager
from raft_servicer import run_async_server

# --- 2. Define the Cluster ---
CLUSTER_CONFIG = {
    1: "localhost:5001",
    2: "localhost:5002",
    3: "localhost:5003",
}
nodes = []

# --- 3. The Main Launcher Function ---
async def main():
    """Launches all 3 nodes on ports 5000, 5001, 5002."""

    tasks = []

    # Loop through the config and set up each node
    for node_id, my_address in CLUSTER_CONFIG.items():

        peer_map = {id: addr for id, addr in CLUSTER_CONFIG.items() if id != node_id}
        peer_ids = list(peer_map.keys())

        client_manager = RaftClientManager(peer_map)

        node_logic = RaftNode(
            id=node_id,
            peer_ids=peer_ids,
            client_manager=client_manager
        )

        nodes.append(node_logic)

        # Create a task for this node's SERVER
        port = my_address.split(':')[-1]
        server_task = asyncio.create_task(run_async_server(node_logic, port))
        tasks.append(server_task)

        # Create a task for this node's internal LOGIC LOOP
        logic_task = asyncio.create_task(node_logic.main_loop())
        tasks.append(logic_task)

    print(f"Starting {len(CLUSTER_CONFIG)} nodes...")
    await asyncio.gather(*tasks)


# --- 4. The Entry Point ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down nodes...")