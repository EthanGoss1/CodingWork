Another Key-Value-Store system, only now this one utilizes a  RAFT based setup.
RAFT is a consensus algorithm that makes sure that all of the logs of each server/node
are correct and up-to date. Our setup first spawns all three nodes in a follower state,
then after a timeout, they one-by-one switch to candidate state as per leader election.
After a leader is elected, the system is then ready to accept commands. These commands
will be replicated throughout each of the RAFT nodes. I completed this as a group
project with two others. 