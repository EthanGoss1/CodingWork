# CodingWork

A collection of projects from my Computer Science coursework at Lebanon Valley College, plus the website that placed second in the PA Media Art and Design Competition. Each project folder has its own README with details on how it works and how to run it.

**Languages:** Python, C++, HTML/CSS/JavaScript
**Topics:** Distributed systems, reinforcement learning, machine learning, intelligent agents, algorithms

---

## Featured Projects

### Raft-Based Key-Value Store
`Classwork/DistributedSystems/KVS_With_Raft` · Python, gRPC · Group project (3 people)

A distributed key-value store kept consistent across nodes using the Raft consensus algorithm. The cluster starts three nodes as followers; after an election timeout, they move to candidate state and elect a leader. Once a leader is elected, the system accepts commands and replicates them to every node's log. Nodes communicate over gRPC using Protocol Buffers (`raft.proto`).

### Q-Learning Blackjack Agent
`Classwork/Artificial_Intelligence_Class/Q_Learning_Blackjack_Bot` · Python

A reinforcement learning agent that learns an optimal Blackjack strategy through Q-learning. Each state is defined by the player's hand total, the dealer's face-up card and whether the player holds a usable ace. Highlights:

- Q-learning update rule with a dynamic learning rate
- Three exploration strategies: UCB, Softmax and Epsilon-Greedy
- Automated training loop that can simulate 500,000 episodes, plus a manual mode to play against the dealer yourself
- Learned Q-values and visit counts saved to `q_table.json`, so training progress persists and can be audited

---

## All Projects

### Distributed Systems
| Project | Language | Description |
|---|---|---|
| [KVS_With_Raft](Classwork/DistributedSystems/KVS_With_Raft) | Python, gRPC | Replicated key-value store using Raft leader election and log replication (group project) |
| [BasicKVS](Classwork/DistributedSystems/BasicKVS) | C++ | A basic key-value store with HTTP command support and tests, built with CMake (group project) |

### Artificial Intelligence
| Project | Language | Description |
|---|---|---|
| [Q_Learning_Blackjack_Bot](Classwork/Artificial_Intelligence_Class/Q_Learning_Blackjack_Bot) | Python | Reinforcement learning agent for Blackjack (see above) |
| [Card_Default_Classifier](Classwork/Artificial_Intelligence_Class/Card_Default_Classifier) | Python | Decision tree classifier that predicts credit card default, built on the [AIPython](https://artint.info/AIPython/) library. `model_writeup.txt` explains my data cleaning and model choices (log loss, split limits, 80/20 train-test split) |
| [Agent_Roomba](Classwork/Artificial_Intelligence_Class/Agent_Roomba) | Python | A toy-collecting robot agent in a simulated bedroom environment, visualized with matplotlib |

### Computational Problem Solving
| Project | Language | Description |
|---|---|---|
| [ComputationalProblemSolving](Classwork/ComputationalProblemSolving) | Python | Solutions to [Kattis](https://open.kattis.com/) competitive programming problems, covering graphs, greedy algorithms, search, divide and conquer, and ad hoc problems. Files are named by technique and problem (e.g. `GraphKastenlauf.py`) |

### Web Development
| Project | Language | Description |
|---|---|---|
| [Website_2nd_Place](WebsiteForPADesignComp/Website_2nd_Place) | HTML, CSS, JavaScript | Multi-page website I built solo for the PA Media Art and Design Competition, where it placed 2nd. Sources are cited in `sources.html` |

> **Note:** The competition website is preserved exactly as submitted. My web development skills have grown since then, but I've left it unchanged so it reflects the original entry.

---

## Repository Structure

```
CodingWork/
├── Classwork/
│   ├── Artificial_Intelligence_Class/
│   │   ├── Agent_Roomba/
│   │   ├── Card_Default_Classifier/
│   │   └── Q_Learning_Blackjack_Bot/
│   ├── ComputationalProblemSolving/
│   └── DistributedSystems/
│       ├── BasicKVS/
│       └── KVS_With_Raft/
└── WebsiteForPADesignComp/
    └── Website_2nd_Place/
```

## Contact

**Ethan Goss** · [ethan.goss123@outlook.com](mailto:ethan.goss123@outlook.com)