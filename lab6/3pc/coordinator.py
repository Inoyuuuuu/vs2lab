import random
import logging

import stablelog

# coordinator messages
from const3PC import VOTE_REQUEST, PREPARE_COMMIT, GLOBAL_COMMIT, GLOBAL_ABORT
# participant messages
from const3PC import VOTE_COMMIT, VOTE_ABORT, READY_COMMIT
# states
from const3PC import INIT, ABORT, WAIT, PRECOMMIT, COMMIT
# misc constants
from const3PC import TIMEOUT


class Coordinator:
    """
    Implements a two phase commit coordinator.
    - state written to stable log (but recovery is not considered)
    - simulates possible crash failure after vote request
    """

    def __init__(self, chan):
        self.channel = chan
        self.coordinator = self.channel.join('coordinator')
        self.participants = []  # list of all participants
        self.log = stablelog.create_log("coordinator-" + self.coordinator)
        self.stable_log = stablelog.create_log("coordinator-"
                                               + self.coordinator)
        self.logger = logging.getLogger("vs2lab.lab6.3pc.Coordinator")
        self.state = None

    def _enter_state(self, state):
        self.stable_log.info(state)  # Write to recoverable persistant log file
        self.logger.info("Coordinator {} entered state {}."
                         .format(self.coordinator, state))
        self.state = state

    def init(self):
        self.channel.bind(self.coordinator)
        #-------- INIT --------
        self._enter_state(INIT)

        # Prepare participant information.
        self.participants = self.channel.subgroup('participant')

    def run(self):
        #if random.random() > 3/4:  # simulate a crash
         #   return "Coordinator crashed in state INIT."
        
        self.channel.send_to(self.participants, VOTE_REQUEST)

        #-------- WAIT --------
        self._enter_state(WAIT)

        if random.random() > 0: #2/3:  # simulate a crash
            return "Coordinator crashed in state WAIT."

        yet_to_receive = list(self.participants)
        while len(yet_to_receive) > 0:
            msg = self.channel.receive_from(self.participants, TIMEOUT)

            # aborts on timeout or abort-response
            if (not msg) or (msg[1] == VOTE_ABORT):
                reason = "timeout" if not msg else "local_abort from " + msg[0]
                self._enter_state(ABORT)
                self.channel.send_to(self.participants, GLOBAL_ABORT)
                return "Coordinator {} terminated in state ABORT. Reason: {}.".format(self.coordinator, reason)
            else:
                assert msg[1] == VOTE_COMMIT
                yet_to_receive.remove(msg[0])

        #-------- PRECOMMIT --------
        self._enter_state(PRECOMMIT)
        self.channel.send_to(self.participants, PREPARE_COMMIT)

        #if random.random() > 2/3:  # simulate a crash
         #   return "Coordinator crashed in state PRECOMMIT."

        #commit when all (non-crashed) p_i responded
        yet_to_receive = list(self.participants)
        p_timeouts = 0
        while len(yet_to_receive) > p_timeouts:
            msg = self.channel.receive_from(self.participants, TIMEOUT)

            # aborts on timeout or abort-response
            if (not msg):
                p_timeouts += 1
            else:
                assert msg[1] == READY_COMMIT
                yet_to_receive.remove(msg[0])

        #-------- COMMIT --------
        self._enter_state(COMMIT)
        self.channel.send_to(self.participants, GLOBAL_COMMIT)

        return f"Coordinator {self.coordinator} terminated in state COMMIT."
