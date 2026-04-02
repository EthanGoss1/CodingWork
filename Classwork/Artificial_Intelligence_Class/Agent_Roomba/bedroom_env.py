import random
import time

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from agent import Agent
from environment import Environment


class BedRoom(Environment):
    def __init__(self, rows: int, cols: int, toy_count: int = 5, obstacle_count: int = 10) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must be positive")
        if toy_count < 0 or obstacle_count < 0:
            raise ValueError("toy_count and obstacle_count must be non-negative")

        self.rows = rows
        self.cols = cols
        self.floor = []
        self._rng = random.Random()
        self.agent = None
        self.robot_position = None
        self._fig = None
        self._ax = None
        self._image = None
        self._text_artists = []
        self._cmap = mcolors.ListedColormap([
            "#f2f2f2",  # empty
            "#4caf50",  # toy
            "#616161",  # obstacle
            "#ffb300",  # toybox
            "#1976d2",  # robot
        ])

        self.generate_floor(toy_count, obstacle_count, place_toybox=False)

    def generate_floor(self, toy_count: int, obstacle_count: int, place_toybox: bool = True) -> None:
        total_cells = self.rows * self.cols
        required_cells = toy_count + obstacle_count + (1 if place_toybox else 0)
        if required_cells > total_cells:
            raise ValueError("Not enough cells for toys, obstacles, and toybox")

        self.floor = [["." for _ in range(self.cols)] for _ in range(self.rows)]

        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        chosen = self._rng.sample(positions, required_cells)

        if place_toybox:
            toybox_pos = chosen[0]
            toy_positions = chosen[1 : 1 + toy_count]
            obstacle_positions = chosen[1 + toy_count :]
            self.floor[toybox_pos[0]][toybox_pos[1]] = "B"
        else:
            toy_positions = chosen[:toy_count]
            obstacle_positions = chosen[toy_count:]

        for r, c in toy_positions:
            self.floor[r][c] = "t"

        for r, c in obstacle_positions:
            self.floor[r][c] = "O"

    def add_agent(self, agent: Agent) -> None:
        self.agent = agent
        for r in range(self.rows):
            for c in range(self.cols):
                if self.floor[r][c] == "R":
                    self.floor[r][c] = "."

        empty_positions = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.floor[r][c] != "O"
        ]
        if not empty_positions:
            raise ValueError("No empty location available for robot")

        r, c = self._rng.choice(empty_positions)
        self.robot_position = (r, c)
        self.floor[r][c] = "B"  # Place toybox at agent's location
        if self._image is not None:
            self.update_display()

   
    def _floor_to_grid(self) -> list[list[int]]:
        mapping = {".": 0, "t": 1, "O": 2, "B": 3, "R": 4}
        grid = [[mapping[cell] for cell in row] for row in self.floor]
        if self.robot_position is not None:
            r, c = self.robot_position
            grid[r][c] = mapping["R"]
        return grid

    def _get_label(self, row: int, col: int) -> str:
        """Get text label for a cell, considering robot position."""
        if self.robot_position == (row, col):
            return "r"
        cell = self.floor[row][col]
        return {"t": "t", "O": "O", "B": "B"}.get(cell, "")

    def _cell_contents(self, row: int, col: int) -> list[str]:
        contents = []
        cell = self.floor[row][col]
        if cell != ".":
            contents.append(cell)
        if self.robot_position == (row, col):
            contents.append("R")
        return contents or ["."]

    def _init_text_labels(self) -> None:
        if self._ax is None:
            return
        self._text_artists = []
        for r in range(self.rows):
            row_artists = []
            for c in range(self.cols):
                artist = self._ax.text(
                    c,
                    r,
                    self._get_label(r, c),
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                )
                row_artists.append(artist)
            self._text_artists.append(row_artists)

    def _update_text_labels(self) -> None:
        if not self._text_artists:
            self._init_text_labels()
            return
        for r in range(self.rows):
            for c in range(self.cols):
                self._text_artists[r][c].set_text(self._get_label(r, c))

    def _refresh_canvas(self, show: bool = False) -> None:
        """Render the canvas and optionally show it."""
        if show:
            plt.show(block=False)
        if self._fig is not None:
            self._fig.canvas.draw_idle()
            self._fig.canvas.flush_events()
            plt.pause(0.001)

    def update_display(self) -> None:
        # Initialize figure and axes if needed
        if self._fig is None or self._ax is None:
            self._fig, self._ax = plt.subplots()
            self._ax.set_xticks([])
            self._ax.set_yticks([])
        
        # Update or create image
        grid = self._floor_to_grid()
        if self._image is None:
            self._image = self._ax.imshow(grid, cmap=self._cmap, vmin=0, vmax=4)
            self._init_text_labels()
            self._refresh_canvas(show=True)
        else:
            self._image.set_data(grid)
            self._update_text_labels()
            self._refresh_canvas()


    def perform_action(self, agent: Agent, action) -> None:
        #All we really gotta do is move the agent around the floor
        #And remove toys if the agent picked up a toy, should be simple
        if self.robot_position is None:
            return

        r, c = self.robot_position
        new_r, new_c = r, c

        if action == 'UP':
            new_r -= 1
        elif action == 'DOWN':
            new_r += 1
        elif action == 'LEFT':
            new_c -= 1
        elif action == 'RIGHT':
            new_c += 1
        elif action == 'PICKUP':
            # Check if there is a toy at current position
            if self.floor[r][c] == 't':
                self.floor[r][c] = '.'  # Remove toy from floor
                agent.toys_held += 1
                print(f"Robot picked up a toy! Total held: {agent.toys_held}")
            return  # Don't move after pickup
        elif action == 'DROPOFF':
            #If the robot wanna drop toys off, make sure it's at the toybox
            if self.floor[r][c] == 'B':
                print(f"The robot has dropped off {agent.toys_held} toys! Good bot")
                agent.amt_charge = 100
                agent.toys_held = 0

            return
        elif action == "FAILURE":
            print("The dumb bot screwed up. loser")
            import sys
            sys.exit(69) #Kill the whole program since it failed

        #Now we actually gotta move the robot:
        if 0 <= new_r < self.rows and 0 <= new_c < self.cols:
            #If the spot it chose is empty:
            if self.floor[new_r][new_c] != "O":
                self.robot_position = (new_r, new_c)
                #recharge bot if it moved into the toybox
                if self.floor[new_r][new_c] == "B":
                    agent.amt_charge = 100
                    #also drop off any toys if it has any:
                    if agent.toys_held !=0:
                        print(f"Robot dropped off {agent.toys_held} toys! Good bot")
                        agent.toys_held = 0



    def get_percept(self, agent: Agent):
        #Sends info to the agent about its immediate surroundings
        #Bool return if there is a toy, as well as toy coords. Maybe return dict?
        #or just a coord val, agent move to coord, then pick up toy
        r, c = self.robot_position

        #gotta tell the agent where the toybox is located
        toybox_pos = None
        for i in range(self.rows):
            for j in range(self.cols):
                if self.floor[i][j] == 'B':
                    toybox_pos = (i, j)
                    break
            if toybox_pos: break

        #Get stuff in nearby cells.
        nearby = {}
        directions = {
            #This looks funky but it makes sense if you think about it
            #going up a row means traveling up the rows column,
            #which means subtracting from the row index
            'UP': (-1,0),
            'DOWN': (1,0),
            'LEFT': (0,-1),
            'RIGHT': (0,1),
        }

        #Check where the bot is standing
        center_content = self.floor[r][c]
        if center_content == 't':
            nearby['CENTER'] = 'toy'
        elif center_content == 'B':
            nearby['CENTER'] = 'toybox'
        else:
            nearby['CENTER'] = 'empty'

        # Check the neighboring spaces
        for direct, (dr, dc) in directions.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                content = self.floor[nr][nc]
                if content == 't':
                    nearby[direct] = 'toy'
                elif content == 'O':
                    nearby[direct] = 'obstacle'
                elif content == 'B':  # treat toybox as empty/walkable for movement purposes typically, or distinct
                    nearby[direct] = 'toybox'
                else:
                    nearby[direct] = 'empty'
            else:
                nearby[direct] = 'wall'

        #Lets the robot know where it is, as well as the toybox
        # if it is running low on battery/ space,
        #as well as what it is close to
        return {
            'robot_pos': (r, c),
            'toybox_pos': toybox_pos,
            'nearby': nearby
        }


if __name__ == "__main__":
    # quick test of display
    room = BedRoom(8, 10, toy_count=8, obstacle_count=8)

    room.update_display()
    time.sleep(5)
    print("Done")