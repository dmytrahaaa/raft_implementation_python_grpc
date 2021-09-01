from concurrent import futures
from state_follower import Follower
from state_candidate import Candidate
from state_leader import Leader
from common_state import Roles
from os.path import isfile
from time import time, sleep
import grpc
import proto.raft_pb2_grpc as pb2_grpc
import proto.raft_pb2 as pb2
import sys


class RaftServer(pb2_grpc.RaftServicer):
    def __init__(self, list_nodes):
        self.role = Follower(self, list_nodes, None)
        self.current_role = Roles.Follower
        self.current_term = self.role.current_term

        if isfile('log.txt'):
            with open('log.txt', 'r') as fp:
                line = fp.readline()
                while line:
                    temp_list = line.strip('\n').split(' ')
                    entry = pb2.LogEntry(term=int(temp_list[0]), index=int(temp_list[1]), decree=temp_list[2])
                    self.log[entry.index] = entry
                    self.last_log_idx = entry.index
                    self.last_log_term = entry.term
                    self.term = entry.term
                    line = fp.readline()

    def change_state(self, prev_state, next_state):
        if next_state is Roles.Follower:
            self.role = Follower(self, self.role.list_nodes, base_state=prev_state)
        elif next_state is Roles.Candidate:
            self.role = Candidate(self, self.role.list_nodes, base_state=prev_state)
        else:
            self.role = Leader(self, self.role.list_nodes, base_state=prev_state)
        self.role.state_action()

    def Vote(self, request, context):
        print("Vote request")
        response = self.role.vote(request, context)
        return response

    def AppendMessage(self, request, context):
        print("Append message")
        success = self.role.append_entries(request)
        return pb2.ResponseAppendEntriesRPC(term=self.current_term, success=success)

    def ListMessages(self, request, context):
        response = self.role.list_messages(request)
        return response


if __name__ == '__main__':
    raft_server = None
    list_nodes = {}
    with open('nodes.txt', 'r') as nodes:
        line = nodes.readline()
        while line:
            temp_list = line.split()
            list_nodes[temp_list[0]] = temp_list[1]
            line = nodes.readline()

    raft_server = RaftServer(list_nodes)
    server = grpc.server(futures.ThreadPoolExecutor())
    pb2_grpc.add_RaftServicer_to_server(raft_server, server)
    server.add_insecure_port('[::]:' + sys.argv[1])
    server.start()
    while True:
        sleep(1)
        raft_server.role.state_action()
