
def stack_dvds(dvd_lists):
    output_list = []
    for dvd_list in dvd_lists:
        #We don't actually have to sort the list
        #only have to find the most number of moves. This,
        #We have to find the longest increasing subsequence of
        #Numbers, subtracted by the total number of dvds.
        next_num = 1
        for dvd in dvd_list:
            if dvd == next_num:
                #This helps find the longest sequence of ordered numbers
                next_num+=1
        #This ends this list, thus reset next_num
        #And add this to the return list
        output_list.append(len(dvd_list) - (next_num - 1))
    
    return output_list
if __name__ == "__main__":
    dvd_lists = []
    k = int(input())
    for i in range(k):
        amt_dvds = int(input())
        dvd_lists.append(list(map(int, input().strip().split(" "))))
    output_list = stack_dvds(dvd_lists)
    for i in output_list:
        print(i)