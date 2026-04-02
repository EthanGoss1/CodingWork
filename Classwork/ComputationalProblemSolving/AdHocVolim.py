#k = who had the box initially
#n = num of questions answered
#ppl = time passed mapping to a T, N, or P (true, false, skipped)
def compute_who_dies(k, n, rounds):
    current_player = k
    elapsed_time = 0

    for person in rounds:
        elapsed_time += person[0]
        #If it's been 3 minutes, kill someone
        if elapsed_time >= 210:
            break
        #If it hasn't, either pass or stay
        #Only pass if true, stay otherwise
        if person[1] == 'T':
            # Pass to next player, will be 8 players per game
            current_player = (current_player % 8) + 1  # wrap around 1-8

    return current_player

if __name__ == "__main__":
    k = int(input())
    n = int(input())

    rounds = []
    for _ in range(n):
        time_str, answer = input().split()
        rounds.append((int(time_str), answer))
    print(compute_who_dies(k,n,rounds))
    # Debug check
    # print("Start player:", k)
    # print("Rounds:")
    # for t, a in rounds:
    #     print(f"  Time: {t}, Answer: {a}")
