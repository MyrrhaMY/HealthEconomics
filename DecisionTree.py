
class Node:
    """ base (parent) class for nodes """
    def __init__(self, name, cost):
        """
        :param name: name of this node
        :param cost: cost of visiting this node
        """

        self.name = name
        self.cost = cost

    def get_expected_cost(self):
        """ abstract method to be overridden in derived classes
        :returns expected cost of this node """


class ChanceNode(Node):

    def __init__(self, name, cost, future_nodes, probs):
        """
        :param name: name of this node
        :param cost: cost of visiting this node
        :param future_nodes: (list) future nodes connected to this node
        :param probs: (list) probability of future nodes
        """

        Node.__init__(self, name, cost)
        self.futureNodes = future_nodes
        self.probs = probs

    def get_expected_cost(self):
        """
        :return: expected cost of this chance node
        E[cost] = (cost of visiting this node)
                  + sum_{i}(probability of future node i)*(E[cost of future node i])
        """

        num_outcomes = len(self.probs)  # number of outcomes
        exp_cost = self.cost  # initialize with the cost of this node

        # go over possible outcomes
        for i in range(num_outcomes) :
            exp_cost += self.probs[i] * self.futureNodes[i].get_expected_cost()

        return exp_cost


class TerminalNode(Node):

    def __init__(self, name, cost):
        """
        :param name: name of this node
        :param cost: cost of visiting this node
        """

        Node.__init__(self, name, cost)

    def get_expected_cost(self):
        """
        :return: cost of this visiting this terminal node
        """
        return self.cost


class DecisionNode(Node):

    def __init__(self, name, cost, future_nodes):
        Node.__init__(self, name, cost)
        self.futureNode = future_nodes

    def get_expected_costs(self):
        exp_costs = dict()
        for node in self.futureNode:
            exp_costs[node.name] = self.cost + node.get_expected_cost()

        return exp_costs

# create the terminal nodes from Tirzepatide 10mg
T1 = TerminalNode(name='No Rescue Therapy', cost=8768.88)
T2 = TerminalNode(name='Rescue Therapy', cost=14168.88)
T3 = TerminalNode(name='Discontinue Therapy', cost=0)
T4 = TerminalNode(name='No Rescue Therapy', cost=8768.88)
T5 = TerminalNode(name='Rescue Therapy', cost=14168.88)
T6 = TerminalNode(name='Discontinue Therapy', cost=0)

# create the terminal nodes from Semaglutide 1mg
T7 = TerminalNode(name='No Rescue Therapy', cost=8028.72)
T8 = TerminalNode(name='Rescue Therapy', cost=13428.72)
T9 = TerminalNode(name='Discontinue Therapy', cost=0)
T10 = TerminalNode(name='No Rescue Therapy', cost=8028.72)
T11 = TerminalNode(name='Rescue Therapy', cost=13428.72)
T12 = TerminalNode(name='Discontinue Therapy', cost=0)

C7 = ChanceNode(name='No ADE', cost=0, future_nodes=[T1, T2], probs=[0.017, 0.983])
C8 = ChanceNode(name='ADE', cost=0, future_nodes=[T4, T5], probs=[0.017, 0.983])
C9 = ChanceNode(name='No ADE', cost=0, future_nodes=[T7, T8], probs=[0.031, 0.969])
C10 = ChanceNode(name='ADE', cost=0, future_nodes=[T10, T11], probs=[0.031, 0.969])

C3 = ChanceNode(name='No ADE', cost=0, future_nodes=[C7, T3], probs=[0.122, 0.878])
C4 = ChanceNode(name='ADE', cost=1527, future_nodes=[C8, T6], probs=[0.124, 0.876])
C5 = ChanceNode(name='No ADE', cost=0, future_nodes=[C9, T9], probs=[0.131, 0.869])
C6 = ChanceNode(name='ADE', cost=1618, future_nodes=[C10, T12], probs=[0.063, 0.937])

C1 = ChanceNode(name='Tirzepatide 10mg', cost=3897.28, future_nodes=[C3, C4], probs=[0.687, 0.313])
C2 = ChanceNode(name='Semaglutide 1mg', cost=3568.32, future_nodes=[C5, C6], probs=[0.642, 0.358])

# create D1
D1 = DecisionNode(name='Diabetes Treatment', cost=0, future_nodes=[C1, C2])

print(D1.get_expected_costs())
