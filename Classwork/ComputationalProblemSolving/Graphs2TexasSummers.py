def get_input():
    # 1. Read N
    line = input().split()
    if not line:
         return None
    n = int(line[0])
    xs = []
    ys = []
        # 2. Read Shady Spots (n lines)
    for i in range(n):
        # map(int, list) converts the two strings on the line to integers
        x, y = map(int, input().split())
        xs.append(x)
        ys.append(y)

    # 3. Read Dorm Coordinates
    dorm_x, dorm_y = map(int, input().split())
    xs.append(dorm_x)
    ys.append(dorm_y)

    # 4. Read Class Coordinates
    class_x, class_y = map(int, input().split())
    xs.append(class_x)
    ys.append(class_y)

    # Return the data as a tuple
    return n, xs, ys

def do_the_prololobelem(n, xs, ys):
    
    total_nodes = n + 2
    start_node = n      # Dorm
    end_node = n + 1    # Class

    # Djikstra's alg
    dist = [float('inf')] * total_nodes
    parent = [-1] * total_nodes
    visited = [False] * total_nodes
    
    dist[start_node] = 0
    
    # We need to loop total_nodes times to visit every node
    for _ in range(total_nodes):
        # Find unvisited node with smallest distance
        # This manual loop is O(V), making the total alg O(V^2)
        u = -1
        best_dist = float('inf')
        
        for i in range(total_nodes):
            if not visited[i] and dist[i] < best_dist:
                best_dist = dist[i]
                u = i
        
        if u == -1 or u == end_node:
            break
            
        visited[u] = True
        
        # Relax edges to all other nodes
        # We compute the weight on the fly to save memory
        ux, uy = xs[u], ys[u]
        
        for v in range(total_nodes):
            if not visited[v]:
                # Calculate squared euclidean distance
                dx = xs[v] - ux
                dy = ys[v] - uy
                weight = dx*dx + dy*dy
                
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    parent[v] = u

    # 4. Reconstruct Path
    path = []
    curr = end_node
    
    # Backtrack from Class to Dorm
    while curr != -1:
        path.append(curr)
        curr = parent[curr]
        
    path.reverse()
    
    # Filter out Dorm (n) and Class (n+1) from the output
    # We only want the shady spot indices (0 to n-1)
    result_indices = []
    for node in path:
        if 0 <= node < n:
            result_indices.append(str(node))
            
    if not result_indices:
        print("-")
    else:
        print("\n".join(result_indices))

if __name__ == "__main__":
    n, xs, xy = get_input()
    do_the_prololobelem(n, xs, xy)
