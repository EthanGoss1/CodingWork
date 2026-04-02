import math
def calc_mug():
    dist_to_be_m = int(input())
    #need a and b in order to compute n1 and n2
    #a can be from 1->sqrt(D)
    for a in range(math.floor(math.sqrt(dist_to_be_m)), 0, -1):
        if(a==0): continue
        if(dist_to_be_m % a !=0):
            continue
        b = dist_to_be_m/a
        if ((a+b)%2 !=0):
            #Check fails, they don't have the same parity
            continue
        n2 = (a+b)/2
        n1 = (b-a)/2
        if(n1>=0):
            print(f"{int(n1)} {int(n2)}")
            return
    
    print("impossible")

if __name__=="__main__":
    calc_mug()