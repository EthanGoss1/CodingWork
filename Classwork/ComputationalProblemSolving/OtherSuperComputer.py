#Tried to do this problem the dumb and simple way,
#But then ran into a timelimit problem and had to 
#do the problem properly with fenwick trees. 
#Fenwick example:
n, m = map(int, input().split())
memory = [0] * (n+1)  #One based indexing 

fernwerk = [0] * (n+1)

def fenw_update(i, delta):
    # Updaates the necessary val by delta
    while i <= n:
        fernwerk[i] += delta
        i += i & -i

def fenw_sum(i):
    #Sums the amount of 1s in the specified range
    s = 0
    while i > 0:
        s += fernwerk[i]
        i -= i & -i
    return s

def fenw_range_sum(l, r):
    return fenw_sum(r) - fenw_sum(l-1)

for _ in range(m):
    op = input().split()
    if op[0] == 'F':
        idx = int(op[1])
        # flip the bit
        old_val = memory[idx]
        new_val = 1 - old_val
        memory[idx] = new_val
        fenw_update(idx, new_val - old_val)
    else:
        l, r = int(op[1]), int(op[2])
        print(fenw_range_sum(l, r))
