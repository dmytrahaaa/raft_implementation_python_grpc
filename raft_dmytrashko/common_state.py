import sys
from random import randint
from time import time
import proto.raft_pb2 as pb2
import proto.raft_pb2_grpc as pb2_grpc
from enum import Enum


class Roles(Enum):
    Follower = 1
    Candidate = 2
    Leader = 3


class State:
    def __init__(self, server, list_nodes, base_state):
        if base_state is not None:
            self.init_from_state(base_state)
        else:
            self.server = server
            self.current_term = 0
            self.voted_for = None
            self.log = {}
            self.commit_index = 0
            self.role = 0
            self.current_role = 0
            self.current_leader = 0
            self.votes_received = 0
            self.id = int(sys.argv[2])
            self.list_nodes = list_nodes
            self.list_nodes.pop(str(self.id))
            print("All nodes list: ", list_nodes)
            self.last_log_index = 0
            self.last_log_term = 0
            self.timeout = time() + randint(5, 10)
            self.majority = (len(self.list_nodes) + 1) // 2 + 1

    def init_from_state(self, base_state):
        self.server = base_state.server
        self.current_term = base_state.current_term
        self.voted_for = base_state.voted_for
        self.log = base_state.log
        self.commit_index = base_state.commit_index
        self.role = base_state.role
        self.current_role = base_state.current_role
        self.current_leader = base_state.current_leader
        self.votes_received = base_state.votes_received
        self.id = base_state.id
        self.list_nodes = base_state.list_nodes
        self.last_log_index = base_state.last_log_index
        self.last_log_term = base_state.last_log_term
        self.timeout = base_state.timeout
        self.majority = base_state.majority
