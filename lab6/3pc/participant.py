import random
import logging

# coordinator messages
from const3PC import VOTE_REQUEST, PREPARE_COMMIT, GLOBAL_COMMIT, GLOBAL_ABORT
# participant decissions
from const3PC import LOCAL_SUCCESS, LOCAL_ABORT
# participant messages
from const3PC import VOTE_COMMIT, VOTE_ABORT, READY_COMMIT, NEED_DECISION, NEED_NEW_C, NEW_C
# states
from const3PC import INIT, READY, ABORT, PRECOMMIT, COMMIT
# misc constants
from const3PC import TIMEOUT

import stablelog


class Participant:
    """
    Implements a two phase commit participant.
    - state written to stable log (but recovery is not considered)
    - in case of coordinator crash, participants mutually synchronize states
    - system blocks if all participants vote commit and coordinator crashes
    - allows for partially synchronous behavior with fail-noisy crashes
    """

    def __init__(self, chan):
        self.channel = chan
        self.participant = self.channel.join('participant')
        self.stable_log = stablelog.create_log("participant-" + self.participant)
        self.logger = logging.getLogger("vs2lab.lab6.3pc.Participant")
        self.coordinator = {}
        self.all_participants = {}
        self.other_participants = []
        self.is_coordinator = False
        self.state = 'NEW'

    def coordinator_init(self, chan):
        self.channel = chan
        self.coordinator = self.channel.join('coordinator')
        self.participants = []  # list of all participants
        self.log = stablelog.create_log("coordinator-" + self.coordinator)
        self.stable_log = stablelog.create_log("coordinator-" + self.coordinator)
        self.logger = logging.getLogger("vs2lab.lab6.3pc.Coordinator")
        self.is_coordinator = True

    @staticmethod
    def _do_work():
        # Simulate local activities that may succeed or not
        return LOCAL_ABORT if random.random() > 2/3 else LOCAL_SUCCESS

    def _enter_state(self, state):
        self.stable_log.info(state)  # Write to recoverable persistant log file
        self.logger.info("Participant {} entered state {}.".format(self.participant, state))
        self.state = state

    def init(self):
        self.channel.bind(self.participant)
        self.coordinator = self.channel.subgroup('coordinator')
        self.all_participants = self.channel.subgroup('participant')
        self.other_participants = list(self.all_participants)
        self.other_participants.remove(self.participant)
        self.logger.info(f"Participants {self.participant} other p {self.other_participants}")
        #-------- INIT --------
        self._enter_state(INIT)  # Start in local INIT state.

    def run(self):
        # Wait for start of joint commit
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)

        if not msg:  # Crashed coordinator - give up entirely
            self._enter_state(ABORT)
            return

        # Coordinator requested to vote, joint commit starts
        assert msg[1] == VOTE_REQUEST

        # Firstly, come to a local decision
        decision = self._do_work()  # proceed with local activities

        # If local decision is negative,
        # then vote for abort and quit directly
        if decision == LOCAL_ABORT:
            self._enter_state(ABORT)
            self.channel.send_to(self.coordinator, VOTE_ABORT)
            return
        
        # If local decision is positive,
        # we are ready to proceed the joint commit
        assert decision == LOCAL_SUCCESS

        #-------- READY --------
        self._enter_state(READY)

        # Notify coordinator about local commit vote
        self.channel.send_to(self.coordinator, VOTE_COMMIT)

        # Wait for coordinator to notify the final outcome
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)
        self.logger.info(f"1 reached by Participant {self.participant}")

        if not msg:  # Crashed coordinator

            # Ask all processes for their ids
            self.channel.send_to(self.other_participants, NEED_NEW_C)
            p_ids = []
            p_timeouts = 0
            self.logger.info(f"2 reached by Participant {self.participant}")

            while len(self.other_participants) > p_timeouts + len(p_ids):
                msg = self.channel.receive_from(self.other_participants, TIMEOUT)

                if not msg:
                    p_timeouts += 1
                elif msg[1] == NEED_NEW_C:
                    self.logger.info(f"Participant {self.participant} received msg {msg} from {msg[0]} with req {msg[1]}, timeouts {p_timeouts}, p_ids {p_ids}")

                    p_ids.append(msg[0])
                    self.logger.info(f"Participant {self.participant} added {msg[0]} to their ids")
                else:
                    self.logger.info(f"early return 1 - - - Participant {self.participant} received msg {msg} from {msg[0]} with req {msg[1]}, timeouts {p_timeouts}, p_ids {p_ids}")
                    return
            
            if len(p_ids) == 0:
                self.logger.info(f"early return 2 - - - Participant {self.participant} only received timeouts")
                return
                
            self.logger.info(f"3 reached by Participant {self.participant}, pids {p_ids}")
            p_ids.append(self.participant)
            p_ids.sort()

            if p_ids[0] == self.participant:
                self.coordinator_init(self.channel)
                self.channel.send_to(self.all_participants, (NEW_C, self.participant))
                self.logger.info("Participant {} (me) is new C.".format(self.participant))
            else:
                self.logger.info("Participant {} is new C.".format(self.participant))
                msg = self.channel.receive_from(self.all_participants, TIMEOUT)
                if not msg:
                    return
                self.coordinator = self.channel.subgroup('coordinator')
                

        if not self.is_coordinator:
            decision = msg[1]

            self.logger.info(f"4 reached by Participant {self.participant}, dec is {decision}")
            if decision != PREPARE_COMMIT:
                assert decision in [GLOBAL_ABORT, LOCAL_ABORT] #TODO: Local abort nur, wenn vorher mit nahcbarn kommuniziert, aka. c crash verhalten implementiert
                self._enter_state(ABORT)
                return
            
            #-------- PRECOMMIT --------
            self._enter_state(PRECOMMIT)
            self.channel.send_to(self.coordinator, READY_COMMIT)

            # Wait for coordinator to notify the final outcome
            msg = self.channel.receive_from(self.coordinator, TIMEOUT)
            
            #TODO: coordinator crash behaviour 

            decision = msg[1]

            if decision != PREPARE_COMMIT:
                assert decision == GLOBAL_ABORT #TODO: Local abort nur, wenn vorher mit nahcbarn kommuniziert, aka. c crash verhalten implementiert
                self._enter_state(ABORT)
                return
            
            #-------- COMMIT --------
            self._enter_state(COMMIT)
            return
        
            # end
        else:
            reason = "test abort"
            self._enter_state(ABORT)
            self.channel.send_to(self.participants, GLOBAL_ABORT)
            return "New coordinator {} terminated in state ABORT. Reason: {}.".format(self.coordinator, reason)

    
        if not msg:  # Crashed coordinator
            # Ask all processes for their decisions
            self.channel.send_to(self.all_participants, NEED_DECISION)
            while True:
                msg = self.channel.receive_from_any()
                # If someone reports a final decision,
                # we locally adjust to it
                if msg[1] in [
                        GLOBAL_COMMIT, GLOBAL_ABORT, LOCAL_ABORT]:
                    decision = msg[1]
                    break

        else:  # Coordinator came to a decision
            decision = msg[1]

        # Change local state based on the outcome of the joint commit protocol
        # Note: If the protocol has blocked due to coordinator crash,
        # we will never reach this point
        if decision == GLOBAL_COMMIT:
            self._enter_state('COMMIT')
        else:
            assert decision in [GLOBAL_ABORT, LOCAL_ABORT]
            self._enter_state('ABORT')

        # Help any other participant when coordinator crashed
        num_of_others = len(self.all_participants) - 1
        while num_of_others > 0:
            num_of_others -= 1
            msg = self.channel.receive_from(self.all_participants, TIMEOUT * 2)
            if msg and msg[1] == NEED_DECISION:
                self.channel.send_to({msg[0]}, decision)

        return "Participant {} terminated in state {} due to {}.".format(
            self.participant, self.state, decision)
