
# For the grand opening of the algorithmic games in NlogNsglow, a row of tower blocks is set to be demolished in a grand demonstration of renewal. Originally the plan was to accomplish this with controlled explosions, one for each tower block, but time constraints now require a hastier solution.

# To help you remove the blocks more rapidly you have been given the use of a Universal Kinetic / Incandescent Energy Particle Cannon (UKIEPC). On a single charge, this cutting-edge contraption can remove either all of the floors in a single tower block, or all the 
# x-th floors in all the blocks simultaneously, for user’s choice of the floor number 
# x. In the latter case, the blocks that are less than 
# x floors high are left untouched, while for blocks having more than 
# x floors, all the floors above the removed 
# x-th one fall down by one level.

def solve():
    n = int(input())
    block_heights = list(map(int, input().strip().split()))
    max_height = max(block_heights)
    block_heights.sort()
    
    result = n  # worst case: destroy all towers individually
    
    idx = 0  # index of the first tower taller than x
    
    for x in range(max_height + 1):
        # move idx forward while block_heights[idx] <= x
        while idx < n and block_heights[idx] <= x:
            idx += 1
        
        towers_remaining = n - idx
        moves = x + towers_remaining
        if moves < result:
            result = moves
    
    print(result)

solve()



solve()