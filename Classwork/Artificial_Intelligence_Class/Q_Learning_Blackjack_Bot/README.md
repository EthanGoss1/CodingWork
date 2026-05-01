This project leverages reinforcement learning to master Blackjack, utilizing a Qlearning Agent that interacts with a 
custom environment to derive an optimal policy. The environment defines each state by the player's hand sum, the dealer's
face-up card, and the presence of a "usable" ace, while the dealer follows the standard requirement of hitting until their 
sum exceeds 16. The agent refines its strategy through the Q-learning update rule and a dynamic learning rate. To ensure 
robust training, the agent supports UCB, Softmax, and Epsilon-Greedy exploration methods, allowing it to effectively balance 
trying new moves and exploiting known high-value actions.
The system is designed for modularity and ease of use, allowing you to toggle between manual play via a HumanAgent or an 
automated training loop in main.py that can simulate 500,000 episodes. Core mechanics like shuffling and dealing are 
handled by a dedicated Deck system, while a specialized Hand class manages card values and ace-reduction logic to prevent 
unnecessary busts. All learned intelligence is persisted in a q_table.json file, which stores both the calculated Q-values 
and the visit counts (N) for every encountered state, ensuring the agent's progress is saved and easily audited.
