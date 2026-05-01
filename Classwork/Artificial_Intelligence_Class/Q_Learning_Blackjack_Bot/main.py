from Blackjack import Blackjack
from Agent import QlearningAgent, HumanAgent
import os

def play_game(learn, model):
    env = Blackjack()
    # "1" means Training (test=False), "0" means Testing (test=True)
    is_testing = (learn == "0")
    agent = QlearningAgent(is_testing, model)
    
    # Try to load existing progress
    q_file = "q_table.json"
    agent.load_q_table(q_file)
    total_wins = 0
    
    num_episodes = 500000
    wins = 0
    model_name = ""

    status = "testing" if is_testing else "training"
    if model == "1":
        model_name = "UCB"
    elif model == "2":
        model_name = "Softmax"
    else:
        model_name = "Epsilon"

    print(f"Starting {status} with {model_name} for {num_episodes} episodes...")

    for i in range(num_episodes):
        # Reset agent's memory for a new game
        state = env.reset()
        done = False
        
        agent.s = state
        agent.a = agent.explore(state)
        
        action = agent.a

        while not done:
            next_state, reward, done = env.step(action)
            
            # Pass the done flag so the agent knows if the game is over
            action = agent.q_learning(next_state, reward, game_over=done)

        if reward == 1:
            wins += 1
            total_wins+=1

        if (i + 1) % 5000 == 0:
            print(f"Episode {i+1}: Win Rate ~{(wins/5000)*100:.2f}%")
            wins = 0
        
    print(f"Total wins: {total_wins}. Win percentage: {total_wins/num_episodes}")
    # Save progress after training
    agent.save_q_table(q_file)
    print("Training complete and table saved.")
    agent.get_games_played()

def human_game():
    env = Blackjack()
    agent = HumanAgent()
    state = env.reset()
    done = False
    if state[0] == 21:
        print("Natural blackjack! You win!")
        return
    while not done:
        action = agent.get_action(state)
        state, reward, done = env.step(action)
    if reward == 1:
        print("You win!")
    elif reward == -1:
        print("You lose!")
    else:
        print("Draw!")
    return

if __name__ == "__main__":
    answer=input("Do you want to play (Y) or have an agent play (A)? ")
    if answer == "Y":
        human_game()
    else:
        model = input("Choose learning type: (1) UCB, (2) Softmax, (3) Epsilon: ")
        answer = input("Train (1) or test (0)? ")
        play_game(answer, model)
