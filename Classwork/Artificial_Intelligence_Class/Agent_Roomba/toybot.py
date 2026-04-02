from agent import Agent
#We don't really need a belief state, as we are just moving around randomly
#searching for toys.

class ToyBot(Agent):
    def __init__(self):
        self.toys_held = 0 #Max of 2
        self.amt_charge = 100 #amount of actions it can take
        self.toybox_pos = None #Doesn't know until gets from percept
        self.memory = {} #Psuedo belief state/memory stuff so the bot can hold on
                         # to important info like path to toybox location


    
    def next_action(self, percept):
        """
        The controller function for this agent. Given the current percept and 
        whatever belief state is stored inside the agent, update the belief state
        and return the next action.

        Args:
            percept: The agent's next perception of its environment; typically a dictionary.

        
        Returns:
            An action for the environment to contemplate.
        """
        #My belief state is simply that we are searching for y toys, and we currently have
        #x out of y toys and are still searching. While we haven't found toys, blither about in the dark
        #Until we find them or are unable to do so. We will operate based on the current precept and this knoweldge,
        #And we won't store much of anything. We will decide where to move on the fly, randomizing lefts and rights
        #And possibly ups and downs in order to move somewhat randomly around the board and collect toys.

        #Check if battery low or have 2 toys
        #If not, then move in accordance to either BFS or DFS, or that recursive thingamabob

        #Decrement power, since we are taking an action
        self.amt_charge -= 1
        #If the idiot robot let itself die, quit the program.
        if self.amt_charge <= 0:
            return "FAILURE"
        # Now that we have the toybox info from the percept, store it
        if percept.get('toybox_pos'):
            self.toybox_pos = percept['toybox_pos']
        nearby = percept.get('nearby', {})
        robot_pos = percept.get('robot_pos', {})

        #Update our memory with all important stuff we know
        if robot_pos:
            r, c = robot_pos
            # Map directions to coordinates
            dir_offsets = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1), 'CENTER': (0, 0)}

            for d, (dr, dc) in dir_offsets.items():
                if d in nearby:
                    pos = (r + dr, c + dc)
                    self.memory[pos] = nearby[d]

        #check for various robot states
        is_full = (self.toys_held >=2)
        low_battery = (self.amt_charge <=15) #15% of 100, so we have some time to get to the toybox

        #If we low on battery or full on toys and at toybox, dropoff
        at_toybox = (nearby.get('CENTER') == 'toybox') or (self.toybox_pos and robot_pos == self.toybox_pos)

        if at_toybox and (is_full or low_battery) and self.toys_held > 0:
            return 'DROPOFF'

        #If we are on a toy and not full, pick up a toy
        if nearby.get('CENTER') == 'toy' and not is_full:
            return 'PICKUP'

        #Decide on movement based on movement func:
        target = None
        #If low on battery, go home
        if is_full or low_battery:
            # If at toybox and empty, don't stay here
            if at_toybox and self.toys_held == 0:
                target = None
            elif self.toybox_pos:
                target = self.toybox_pos
        #Now we look for toys
        elif not is_full:
            #if we have a toy nearby, move towards it
            for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                if nearby.get(direction) == 'toy':
                    r, c = robot_pos
                    dr, dc = {'UP':(-1,0), 'DOWN':(1,0), 'LEFT':(0,-1), 'RIGHT':(0,1)}[direction]
                    target = (r + dr, c + dc)
                    break
        return self.randomly_move_towards(robot_pos, target, nearby)

#Random movement controllers
    def randomly_move_towards(self, robot_pos, target, nearby):
        #Move willy nilly all over the place lmao
        possible_moves = []
        # Identify all possible moves first
        for d in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            if nearby.get(d) not in ['wall', 'obstacle']:
                possible_moves.append(d)
        #If we are stuck, it's a failure
        if not possible_moves:
            return 'CENTER'  # Bad bot, but staying alive

        preferred_moves = []

        if target:
            cr, cc = robot_pos
            tr, tc = target

            # Try and only include moves that get us closer to the target
            for move in possible_moves:
                if move == 'UP' and tr < cr:
                    preferred_moves.append(move)
                elif move == 'DOWN' and tr > cr:
                    preferred_moves.append(move)
                elif move == 'LEFT' and tc < cc:
                    preferred_moves.append(move)
                elif move == 'RIGHT' and tc > cc:
                    preferred_moves.append(move)

        # Randomly do something preferred, or anything we feel like
        import random
        if preferred_moves:
            return random.choice(preferred_moves)
        else:
            # If we ain't got no preference, do whatever
            return random.choice(possible_moves)
    def informed_move_towards(self, robot_pos, target, nearby):
        pass
        #I wanna leverage the robot's memory here somehow
    