from bedroom_env import BedRoom
from toybot import ToyBot


if __name__ == "__main__":
    room = BedRoom(8, 10, toy_count=8, obstacle_count=8)
    robot = ToyBot()
    room.add_agent(robot)

    room.run_simulation(steps=500, delay=1, display=True)
    input('press enter to continue')
