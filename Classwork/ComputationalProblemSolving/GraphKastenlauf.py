from collections import deque
#Start with 20 bottles of beer, and drink one bottle every
#50 meters. Thus, they can walk 1000 meters before needing to refill
def get_input():
    t = int(input())
    tests=[]
    for i in range(t):
        n = int(input())
        list_of_locations = [tuple(map(int, input().split())) for i in range(n+2)]

        tests.append([n, list_of_locations])
    #Input acquired
    return tests

def do_the_prolbelem(n, lolcs):
    #Breadthfirst search would be useful here
    #If it work: print("happy")
    #else: print("sad")
    visited = [False] *(n+2)
    queue = deque([0])
    visited[0]=True

    while queue:
        current = queue.popleft()
        x1, y1 = lolcs[current]

        #see if we can reach festival
        if current == n+1: #this is the festival index
            print("happy")
            return
        #explore all reachable places
        for i in range(n+2):
            if not visited[i]:
                x2, y2 = lolcs[i]
                distance = abs(x1-x2)+abs(y1-y2)
                #can make it while drunk
                if distance<=1000:
                    visited[i] = True
                    queue.append(i)
    #if we've made it down here, no more beer
    print("sad")



if __name__== "__main__":
    tests = get_input()
    for n, lolcs in tests:
        do_the_prolbelem(n, lolcs)