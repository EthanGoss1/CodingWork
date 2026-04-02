import grpc
import sys

from rpc import raft_pb2, raft_pb2_grpc


def run_client(port=5001):
    target = f'localhost:{port}'
    print(f"--- Connecting to Node at {target} ---")

    # Create connection
    channel = grpc.insecure_channel(target)
    stub = raft_pb2_grpc.RaftStub(channel)

    key = "burger"
    val = "15.99"
    print(f"\n[1] Sending PUT command: {key} -> {val}")

    try:
        put_request = raft_pb2.ClientRequest(
            operation=raft_pb2.PUT,
            key=key,
            value=val
        )

        response = stub.ClientCommand(put_request)

        if response.success:
            print(f"Success! Leader says: {response.result}")
        else:
            print(f"Failed. Reason: {response.result}")

    except grpc.RpcError as e:
        print(f"Network Error: {e.details()}")

    print(f"\n[2] Sending GET command: {key}")

    try:
        get_request = raft_pb2.ClientRequest(
            operation=raft_pb2.GET,  # Uses the Enum (0)
            key=key,
            value=""  # Value is ignored for GET
        )

        response = stub.ClientCommand(get_request)

        if response.success:
            print(f"Success! Value is: {response.result}")
        else:
            print(f"Failed. Reason: {response.result}")

    except grpc.RpcError as e:
        print(f"Network Error: {e.details()}")


    print(f"\n[3] Sending DELETE command: {key}")

    try:

        delete_request = raft_pb2.ClientRequest(
            operation=raft_pb2.DELETE,
            key=key,
            value=""
        )

        response = stub.ClientCommand(delete_request)

        if response.success:
            print(f"Success! Value is: {response.result}")
        else:
            print(f"Failed. Reason: {response.result}")

    except grpc.RpcError as e:
        print(f"Network Error: {e.details()}")

    print(f"\n[4] Sending GET command: {key}")

    try:
        get_request = raft_pb2.ClientRequest(
            operation=raft_pb2.GET,  # Uses the Enum (0)
            key=key,
            value=""  # Value is ignored for GET
        )

        response = stub.ClientCommand(get_request)

        if response.success:
            print(f"Success! Value is: {response.result}")
        else:
            print(f"Failed. Reason: {response.result}")

    except grpc.RpcError as e:
        print(f"Network Error: {e.details()}")


    print(f"\n[5] Sending PUT command: {key} -> {val}")

    try:
        put_request = raft_pb2.ClientRequest(
            operation=raft_pb2.PUT,
            key=key,
            value=val
        )

        response = stub.ClientCommand(put_request)

        if response.success:
            print(f"Success! Leader says: {response.result}")
        else:
            print(f"Failed. Reason: {response.result}")

    except grpc.RpcError as e:
        print(f"Network Error: {e.details()}")


if __name__ == "__main__":
    target_port = 5002
    if len(sys.argv) > 1:
        target_port = sys.argv[1]

    run_client(target_port)