from time import time, sleep
import threading
from queue import Queue
import grpc
import proto.raft_pb2 as pb2
import proto.raft_pb2_grpc as pb2_grpc
from common_state import State, Roles
from random import randint, uniform


class Leader(State):
    def __init__(self, server, list_nodes: list, base_state):
        super().__init__(server, list_nodes, base_state)
        self.role = self
        self.current_role = Roles.Leader

    def state_action(self):
        print('Leader. Current term is {}'.format(self.current_term))
        if time() > self.timeout:
            print("Leader sends requests")
            prev_log_index = self.last_log_index
            entry = self.log[prev_log_index] if prev_log_index in self.log else None
            request = pb2.RequestAppendEntriesRPC(term=self.current_term, leaderId=self.id,
                                                  prevLogIndex=prev_log_index, prevLogTerm=self.last_log_term,
                                                  entry=entry, leaderCommit=self.commit_index)

            threads = []
            for node in self.list_nodes.values():
                channel = grpc.insecure_channel(node)
                stub = pb2_grpc.RaftStub(channel)

                t = threading.Thread(target=self.broadcast,
                                     args=(node, prev_log_index, request, stub))
                threads.append(t)
                t.start()


            for x in threads:
                i = 0
                while i < self.majority:
                    try:
                        x.join()
                        i += 1
                    except RuntimeError:
                        pass


            self.timeout = time() + randint(3, 12)

    def broadcast(self, address, prev_log_index, req, stub):
        try:
            response = stub.AppendMessage(req, timeout=1)
            if response.success is False and response.term > self.current_term:
                self.current_term = req.term
                self.voted_for = -1
                self.current_leader = req.leaderId
                self.timeout = time() + randint(3, 12)
                self.role = self.server.change_state(self, Roles.Follower)
                self.current_role = Roles.Follower
                print("Leader -> Follower")

            while response.success is False:
                if prev_log_index >= 1:
                    prev_log_index -= 1
                entry = self.log[prev_log_index]
                request = pb2.RequestAppendEntriesRPC(term=self.current_term, leaderId=self.id,
                                                      prevLogIndex=prev_log_index, prevLogTerm=entry.term,
                                                      entry=entry, leaderCommit=self.commit_index)
                response = stub.AppendMessage(request, timeout=1)

            while prev_log_index < self.last_log_index:
                prev_log_index += 1
                entry = self.log[prev_log_index]
                req = pb2.RequestAppendEntriesRPC(term=self.current_term, leaderId=self.id,
                                                  prevLogIndex=prev_log_index, prevLogTerm=entry.term,
                                                  entry=entry, leaderCommit=self.commit_index)
                response = stub.AppendMessage(req, timeout=1)

            return response
        except grpc.RpcError as e:
            print("Cannot connect to {} ".format(address) + "with error: " + str(e))

    def append_entries(self, req):

        entry = pb2.LogEntry(term=self.current_term, command=req.entry.command)
        self.last_log_term = self.current_term
        self.last_log_index += 1
        self.log[self.last_log_index] = entry
        success = False

        if req.term > self.current_term:
            self.current_term = req.term
            self.voted_for = -1
            self.current_leader = req.leaderId
            self.timeout = time() + randint(3, 12)
            self.current_role = Roles.Follower
            self.role = self.server.change_state(self, Roles.Follower)
            success = True
            return success

        elif req.term < self.current_term:
            return success

        # self.current_term = req.term
        # self.current_leader = req.leaderId
        # self.timeout = time() + randint(3, 12)

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
              """.format(self.current_role, self.current_term, self.commit_index, self.last_log_index, self.last_log_term, self.log))
        response = pb2.ResponseListMessagesRPC(logs="".join(self.log.values()))
        return response