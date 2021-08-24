from common_state import *


class Follower(State):
    def __init__(self, server, list_nodes: list, base_state):
        super().__init__(server, list_nodes, base_state)
        self.role = self
        self.current_role = Roles.Follower

    def state_action(self):
        print('Follower')
        if time() > self.timeout:
            self.role = self.server.change_state(self, Roles.Candidate)
            print("Follower -> Candidate")

    def append_entries(self, req):
        self.current_term = req.term
        self.current_leader = req.leaderId
        self.timeout = time() + randint(3, 12)
        success = False

        if req.term < self.current_term:
            return pb2.ResponseAppendEntriesRPC(term=self.current_term, successs=success)

        if self.last_log_term < req.prevLogTerm and self.last_log_index > self.commit_index:
            self.log.pop(req.prevLogIndex, None)
            self.last_log_index = self.commit_index
            return pb2.ResponseAppendEntriesRPC(term=self.current_term, success=success)

        if req.leaderCommit > self.commit_index:
            for i in range(self.commit_index, req.leaderCommit + 1):
                if i in self.log and req.prevLogTerm == self.last_log_term:
                    self.commit_index = i

        if req.prevLogIndex == self.last_log_index + 1 and req.prevLogTerm >= self.last_log_term:
            self.log[req.prevLogIndex] = req.entry
            self.last_log_index += 1
            self.last_log_term = req.prevLogTerm
            success = True
        elif req.prevLogIndex == self.last_log_index and req.prevLogTerm == self.last_log_term:
            success = True

        return pb2.ResponseAppendEntriesRPC(term=self.current_term, success=success)
