from common_state import *


class Follower(State):
    def __init__(self, server, list_nodes: list, base_state):
        super().__init__(server, list_nodes, base_state)
        self.role = self
        self.current_role = Roles.Follower

    def state_action(self):
        print('Follower. Current term is {}'.format(self.current_term))
        if time() > self.timeout:
            self.role = self.server.change_state(self, Roles.Candidate)
            print("Follower -> Candidate")

    def append_entries(self, req):
        self.current_term = req.term
        self.current_leader = req.leaderId
        self.timeout = time() + randint(3, 12)
        success = False

        if req.term < self.current_term:
            return success

        if self.last_log_term < req.prevLogTerm and self.last_log_index > self.commit_index:
            self.log.pop(req.prevLogIndex, None)
            self.last_log_index = self.commit_index
            return success

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

        return success

    def vote(self, req, context):
        log_ok = ((req.lastLogTerm > self.last_log_term) or (
                req.lastLogTerm == self.last_log_term and req.lastLogIndex >= self.last_log_index))
        term_ok = ((req.term > self.current_term) or (
                req.term == self.current_term and self.voted_for in (None, req.candidateId)))

        vote_granted = False
        if term_ok and log_ok:
            self.timeout = time() + randint(3, 12)
            self.current_term = req.term
            self.current_role = Roles.Follower
            self.role = self.server.change_state(self, Roles.Follower)
            self.voted_for = req.candidateId
            vote_granted = True
        return pb2.ResponseVoteRPC(term=self.current_term, voteGranted=vote_granted)

    def list_messages(self, request):
        print("""Node current role -  {}, current term - {}, commit index - {}
                 last log index - {}, last log term - {}, log - {}
              """.format(self.current_role, self.current_term, self.commit_index, self.last_log_index,
                         self.last_log_term, self.log))
        response = pb2.ResponseListMessagesRPC(logs="".join(self.log.values()))
        return response
