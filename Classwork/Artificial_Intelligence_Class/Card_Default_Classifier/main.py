import pandas as pd
from learnProblem import Data_from_file, Evaluate
from learnDT import DT_learner

def check_credit(file_path):
    print("Load and preprocess the data\n")
    # I've set one_hot encoding to be false to avoid 160,000+ extra trainable features
    # target_index=-1 sets the default status as the goal
    data = Data_from_file(
        file_path, 
        has_header=True, 
        target_index=-1, 
        num_train=5000, #This is so I don't have to wait an hour and a half for each run. Set to None for all the data
        one_hot=False,
        prob_test=.2, #Training it on 80% of data, testing on 20%
        seed=42
    )

    print(f"Be advised, {len(data.train)} training samples inbound\n")

    print("Training the doohickey \n")
    # split_to_optimize: log_loss (Entropy) is standard for classification problems
    # max_num_cuts: 10 cuts for numeric variables to prevent extreme complexity.
    # min_child_weight: 20 examples required in a leaf to prevent overfitting.
    learner = DT_learner(
        data, 
        split_to_optimize=Evaluate.log_loss,
        max_num_cuts=10,  #currently using 10, have tried 5 and 15. 10 seemed to be the most balanced between them.
        gamma=0.01,
        min_child_weight=20 #currently using 20, have tried 10 and 15, but 20 seems to be the best.
    )

    # Train the model
    predictor = learner.learn()

    print("Performance evaluation:\n")
    # Stealing this from learnProblem.py
    learner.evaluate()

    # Gives a look-see into the tree structure
    print("Tree structure:\n")
    tree_string = str(learner)
    print(tree_string[:500] + "...") 

if __name__ == "__main__":
    
    #Preprocess the csv file with pandas because yes
    df = pd.read_csv('carddata.csv')
    #Remove the ID column to ignore a bunch of untrainable data
    df_clean = df.iloc[:, 1:] 
    df_clean.to_csv('cleancarddata.csv', index=False)
    csv_file = 'cleancarddata.csv' 

    try:
        check_credit(csv_file)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}. Check your working directory")

    #Accuracy = 81% ish