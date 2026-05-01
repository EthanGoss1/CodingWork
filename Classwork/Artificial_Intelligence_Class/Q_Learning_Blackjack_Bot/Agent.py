import random
import json
import ast
import math

#To check to make sure the blackjack game actually works
#And also because gambling is awesome
class HumanAgent:
    def __init__(self):
        pass

    def get_action(self, state):
        p_sum, d_card, ace = state
        print(f"\n--- Your Hand: {p_sum} (Usable Ace: {ace}) | Dealer shows: {d_card} ---")
        
        while True:
            choice = input("Enter (1) Hit or (0) Hold: ")
            if choice in ['0', '1']:
                return int(choice)

class QlearningAgent:
    def __init__(self, test_bool=False, model="1"):
        self.Q = {}  # (state, action) -> float
        self.N = {}  # (state, action) -> int
        self.s = None 
        self.a = None 
        self.gamma = 1.0 #Win as soon as possible
        self.test = test_bool #This is the flag that determines if it is a training or testing model
        self.model_type = model #defines which learning style to use, default  = UCB learning

    def alpha(self, n):
        return 10 / (9 + n)

    def get_n_total(self, state):
        #this gets the n value for the softmax function for a more accurate
        #temperature calc
        n_hold = self.N.get((state, 0), 0)
        n_hit = self.N.get((state, 1), 0)
        return n_hold + n_hit

    #explore function using epsilon learning
    #Easily swappable to utilize different learning methods
    def explore(self, state):
        # Various types of learning it can do
        if self.model_type == "1":
            # Average: 43.26%
            return self.ucb_learning(state)
        elif self.model_type == "2":
            # Average: 43%
            return self.softmax_learning(state)
        else:
            # Average: about 41,42% ish
            return self.epsilon_learning(state)


    def ucb_learning(self, state):
        if self.test:
            q_hold = self.get_q(state, 0)
            q_hit = self.get_q(state, 1)
            return 1 if q_hit > q_hold else 0
        # N(s) is the total number of times state s has been visited
        n_hold = self.N.get((state, 0), 0)
        n_hit = self.N.get((state, 1), 0)
        n_total = n_hold + n_hit

        # If an action has never been taken in this state, take it
        if n_hold == 0: return 0
        if n_hit == 0: return 1

        #Good approximation as per the book
        c = math.sqrt(2)
        # UCB1 formula: Q(s,a) + C * sqrt( ln(N(s)) / N(s,a) )
        ucb_hold = self.get_q(state, 0) + c * math.sqrt(math.log(n_total) / n_hold)
        ucb_hit = self.get_q(state, 1) + c * math.sqrt(math.log(n_total) / n_hit)

        return 1 if ucb_hit > ucb_hold else 0

    def softmax_learning(self, state):
        if self.test:
            q_hold = self.get_q(state, 0)
            q_hit = self.get_q(state, 1)
            return 1 if q_hit > q_hold else 0
        q_hold = self.get_q(state, 0)
        q_hit = self.get_q(state, 1)

        #Temperature calc
        temp = 1.0 / (1.0 + math.log(1 + self.get_n_total(state)))
        #Gets the max q, then does the numerator for each one of the book's
        #softmax calc
        max_q = max(q_hold, q_hit)
        exp_hold = math.exp((q_hold - max_q) / temp)
        exp_hit = math.exp((q_hit - max_q) / temp)

        # Calculate prob of choosing hit using softmax
        prob_hit = exp_hit / (exp_hold + exp_hit)

        #random.random() calculates a random number between 0 and 1
        #Allows semi-random exploration
        return 1 if random.random() < prob_hit else 0

    def epsilon_learning(self, state):
        # epsilon-greedy exploration
        if not self.test and random.random() < 0.1:
            return random.randint(0, 1)

        q_hold = self.get_q(state, 0)
        q_hit = self.get_q(state, 1)
        return 1 if q_hit > q_hold else 0

    def get_q(self, state, action):
        return self.Q.get((state, action), 0.0)

    def q_learning(self, n_s, r, game_over=False):
        if not self.test and self.s is not None:
            s_a_key = (self.s, self.a)
            self.N[s_a_key] = self.N.get(s_a_key, 0) + 1

            # If game is over, the value of the 'next' state is 0
            if game_over:
                max_q_next = 0
            else:
                max_q_next = max(self.get_q(n_s, 0), self.get_q(n_s, 1))

            # Q-Learning Update Rule
            current_q = self.get_q(self.s, self.a)
            self.Q[s_a_key] = current_q + self.alpha(self.N[s_a_key]) * (r + (self.gamma * max_q_next) - current_q)

        if game_over:
            self.s = None
            self.a = None
            return None

        self.s = n_s
        self.a = self.explore(n_s)
        return self.a

    def get_games_played(self):
        total_games = 0
        for k, v in self.N.items():
            total_games+=v
        print(f"Total games played: {total_games:,}")

    def save_q_table(self, filename="q_table.json"):
        try:
            #Saving both the Q table and the N table, because I'm curious to see how many times
            #the agent has ended up in each state
            data = {
                "Q": {str(k): v for k, v in self.Q.items()},
                "N": {str(k): v for k, v in self.N.items()}
            }           
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Successfully saved Q-table to {filename}")
        except Exception as e:
            print(f"Error saving Q-table: {e}")

    def load_q_table(self, filename="q_table.json"):
        """Loads the Q-table from a text file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                # Reconstruct the dictionaries using ast.literal_eval
                self.Q = {ast.literal_eval(k): v for k, v in data.get("Q", {}).items()}
                self.N = {ast.literal_eval(k): v for k, v in data.get("N", {}).items()}
            print(f"Successfully loaded Q-table from {filename}")
        except FileNotFoundError:
            print(f"No existing Q-table found at {filename}. Starting from scratch.")
        except Exception as e:
            print(f"Error loading Q-table: {e}")