import threading
import grpc
from common_state import *


class Candidate(State):
    def __init__(self, server, list_nodes: list, base_state):
        super().__init__(server, list_nodes, base_state)
        self.role = self
        self.current_role = Roles.Candidate

    def state_action(self):
        if time() > self.timeout:
            self.current_term += 1
            self.votes_received = 1
            print('Candidate sends vote requests. Current term is {}'.format(self.current_term))
            req = pb2.RequestVoteRPC(term=self.current_term, candidateId=self.id,
                                     lastLogIndex=self.last_log_index,
                                     lastLogTerm=self.last_log_term)

            barrier = threading.Barrier(self.majority - 1)

            for address in self.list_nodes.values():
                channel = grpc.insecure_channel(address)
                stub = pb2_grpc.RaftStub(channel)
                threading.Thread(target=self.vote_init,
                                 args=(barrier, req, stub)).start()
            barrier.reset()
            self.timeout = time() + randint(3, 12)

        if self.votes_received >= self.majority:
            print("Candidate -> Leader")
            self.votes_received = 1
            self.voted_for = self.id
            self.timeout = time()
            self.current_role = Roles.Leader
            self.role = self.server.change_state(self, Roles.Leader)

    def vote_init(self, barrier, request, stub):
        try:
            response = stub.Vote(request, timeout=1)
            if response.voteGranted:
                self.votes_received += 1
                barrier.wait(timeout=1)

        except Exception as e:
            print("Cannot connect " + "with error: " + str(e))


    def append_entries(self, req):
        if req.term > self.current_term or req.prevLogTerm > self.last_log_term or \
                (req.prevLogTerm == self.last_log_term and req.prevLogIndex >= self.last_log_index
                    and req.prevLogTerm != 0 and self.last_log_term != 0
                ):
            self.current_term = req.term
            self.voted_for = -1
            self.current_leader = req.leaderId
            self.timeout = time() + randint(3, 12)
            self.current_role = Roles.Follower
            self.role = self.server.change_state(self, Roles.Follower)
            print("Candidate -> Follower")
        success = False
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
