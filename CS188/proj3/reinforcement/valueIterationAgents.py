# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        mdp = self.mdp

        for i in range(self.iterations):
            copyValues = self.values.copy()
            for state in mdp.getStates():
                Qvalues = util.Counter()
                actions = mdp.getPossibleActions(state)
                for action in actions:
                    Qvalues[action] = self.computeQValueFromValues(state, action)
                copyValues[state] = Qvalues[Qvalues.argMax()]
            self.values = copyValues





    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        mdp = self.mdp
        discount = self.discount
        values = self.values
        T = mdp.getTransitionStatesAndProbs(state, action)
        b = util.Counter()
        for nextState, prob in T:
            b[nextState] = prob*(mdp.getReward(state, action, nextState) + discount*(values[nextState]))
        return b.totalCount()


    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        mdp = self.mdp
        values = self.values
        discount = self.discount
        actions = mdp.getPossibleActions(state)
        if mdp.isTerminal(state):
            return None
        optimalAction = None
        qValue = float('-inf')
        for action in actions:
            qVal = self.computeQValueFromValues(state, action)
            if qVal > qValue:
                qValue = qVal
                optimalAction = action
        return optimalAction

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        mdp = self.mdp
        iterations = self.iterations
        states = mdp.getStates()
        numStates = len(states)
        copyValues = self.values.copy()
        for i in range(iterations):
            state = states[i%numStates]
            if i%numStates == 0:
                self.values = copyValues
            if mdp.isTerminal(state):
                continue
            Qvalues = util.Counter()
            actions = mdp.getPossibleActions(state)
            for action in actions:
                Qvalues[action] = self.computeQValueFromValues(state, action)
            copyValues[state] = Qvalues[Qvalues.argMax()]
        self.values = copyValues


class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        mdp = self.mdp
        PQ = util.PriorityQueue()
        states = mdp.getStates()
        for state in states:
            if mdp.isTerminal(state) is False:
                Qvalues = util.Counter()
                actions = mdp.getPossibleActions(state)
                for action in actions:
                    Qvalues[action] = self.computeQValueFromValues(state, action)
                diff = abs(self.values[state] - Qvalues[Qvalues.argMax()])
                PQ.push(state, -diff)
        for i in range(self.iterations):
            if PQ.isEmpty():
                break
            s = PQ.pop()
            if mdp.isTerminal(s) is False:
                Qvalues = util.Counter()
                actions = mdp.getPossibleActions(s)
                for action in actions:
                    Qvalues[action] = self.computeQValueFromValues(s, action)
                self.values[s] = Qvalues[Qvalues.argMax()]
            predecessors = set([])
            for state in states:
                actions = mdp.getPossibleActions(state)
                for action in actions:
                    nextStates = [nextState for nextState, prob in mdp.getTransitionStatesAndProbs(state, action)]
                    if s in nextStates:
                        predecessors.add(state)
            for p in predecessors:
                Qvalues = util.Counter()
                actions = mdp.getPossibleActions(p)
                for action in actions:
                    Qvalues[action] = self.computeQValueFromValues(p, action)
                diff = abs(self.values[p] - Qvalues[Qvalues.argMax()])
                if diff > self.theta:
                    PQ.update(p, -diff)
