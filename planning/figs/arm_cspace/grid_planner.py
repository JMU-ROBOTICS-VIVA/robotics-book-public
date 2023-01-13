import tempfile
import shutil
import subprocess
import argparse
import six
import heapq
import math
from arm_planning import ArmProblem as ArmProblemArm
import numpy as np



class PriorityQueue(object):
    """
    A priority set stores a collection of items, each of which has a
    priority and a key.  The item in the set with the lowest priority
    will always be returned by the pop operation.  There can be no
    duplicate keys in the collection. if an item is added to the
    collection that has the same key as an existing item, the item with
    lower priority is kept, the other is discarded.
    This code borrows from an example in the Python Documentation:
    http://docs.python.org/2/library/heapq.html
    """

    def  __init__(self):
        """ Create a new priority set. """
        self.heap = []
        self.entry_finder = {}
        self.count = 0

    def add(self, item, priority):
        """ Add an item to the collection.

        Arguments:
        item - The item that is being stored (this is what will
               be returned by pop.)
        key -  A key.  Used to prevent duplicates.
        priority - A number.  Lower priorty items will be popped first.
        """
        self.count += 1
        if item in self.entry_finder:
            if priority < self.entry_finder[item][0]:
                self.entry_finder[item][2] = 'REMOVED'
                del self.entry_finder[item]
            else:
                return

        pair = [priority, self.count, item]
        self.entry_finder[item] = pair
        heapq.heappush(self.heap, pair)

    def __repr__(self):
        result = "["
        for key in self.entry_finder.keys():
            result += repr(self.entry_finder[key][2]) +", "
        result = result.rstrip(", ")
        return result + "]"

    def pop(self):
        """ Return and remove the lowest priority item in the collection.
        """
        while len(self) != 0:
            _, _, item = heapq.heappop(self.heap)
            if item != 'REMOVED':
                del self.entry_finder[item]
                return item
        raise KeyError("Pop from empty priority queue")

    def __len__(self):
        """ Return the number of elements stored in the set. """
        return len(self.entry_finder)

    def is_empty(self):
        return len(self) == 0

    def __iter__(self):
        """ Iteration will loop over items (not keys.) """
        return [item[1][2] for item in self.entry_finder.iteritems()].__iter__()


    
# # Borrowed from CS188 pacman project.
# class PriorityQueue:
#     """
#       Implements a priority queue data structure. Each inserted item
#       has a priority associated with it and the client is usually interested
#       in quick retrieval of the lowest-priority item in the queue. This
#       data structure allows O(1) access to the lowest-priority item.
#     """
#     def  __init__(self):
#         self.heap = []
#         self.count = 0

#     def _add(self, item, priority):
#         entry = (priority, self.count, item)
#         heapq.heappush(self.heap, entry)
#         self.count += 1

#     def pop(self):
#         (_, _, item) = heapq.heappop(self.heap)
#         return item

#     def is_empty(self):
#         return len(self.heap) == 0

#     def add(self, item, priority):
#         # If item already in priority queue with higher priority,
#         # update its priority and rebuild the heap.  If item already
#         # in priority queue with equal or lower priority, do nothing.
#         # If item not in priority queue, do the same thing as
#         # self.push.
#         for index, (p, c, i) in enumerate(self.heap):
#             if i == item:
#                 if p <= priority:
#                     break
#                 del self.heap[index]
#                 self.heap.append((priority, c, item))
#                 heapq.heapify(self.heap)
#                 break
#         else:
#             self._add(item, priority)

#     def __iter__(self):
#         return [item[2] for item in self.heap].__iter__()


class Problem:

    def __init__(self):
        pass

    def start(self):
        raise NotImplementedError

    def goal(self):
        raise NotImplementedError

    def successors(self, state):
        raise NotImplementedError

    def cost(self, state, next_state):
        raise NotImplementedError
    
class ArmState(object):
    def __init__(self, q):
        """ cost is cost to enter """
        self.q = q
    
    def __repr__(self):
        return str(self.q)
    
    def __eq__(self, other):
        return np.allclose(self.q, other.q)

    def __neq__(self, other):
        return not self == other

    def __hash__(self):
        return hash(str(self.q))



def angle_diffs(xs, y):
    #https://stackoverflow.com/questions/1878907/
    #the-smallest-difference-between-2-angles
    xs = np.deg2rad(xs)
    y = np.deg2rad(y)
    diffs = np.arctan2(np.sin(xs-y), np.cos(xs-y))
    diffs = np.rad2deg(diffs)
    diffs[np.isnan(diffs)] = float('inf')
    return diffs
        
def angle_metric_l2(xs, y):
    diffs = angle_diffs(xs, y)
    return  np.sqrt(np.sum(diffs**2))

class ArmProblem:
    def __init__(self, arm_problem):
        self.arm_problem = arm_problem
        
    def start(self):
        return ArmState(self.arm_problem.start())

    def goal(self):
        return ArmState(self.arm_problem.goal())

    def _new_state(self, state, index, offset):
            new_q = np.array(state.q)
            new_q[index] += offset
            if new_q[index] < -180.0:
                new_q[index] = 360. - new_q[index]
            if new_q[index]>180.:
                new_q[index] = new_q[index] - 360.
            return ArmState(new_q)
        
    def successors(self, state):
        next_states = []
        for i in range(state.q.size):
            new_state = self._new_state(state, i, -5.0)
            if self.arm_problem.step_ok(state.q, new_state.q):
                next_states.append(new_state)
            new_state = self._new_state(state, i, 5.0)
            if self.arm_problem.step_ok(state.q, new_state.q):
                next_states.append(new_state)
        return next_states

            

    def cost(self, state, next_state):
        #return np.max(np.abs(state.q - next_state.q))
        return angle_metric_l2(state.q, next_state.q)

    def heuristic(self, state):
        return angle_metric_l2(state.q, self.arm_problem.goal())

            
def construct_path(node):
    path = [node.state]
    cur_node = node.parent
    while cur_node is not None:
        path.append(cur_node.state)
        cur_node = cur_node.parent
    path.reverse()
    return path
                    

class CostNode:
    def __init__(self, state, parent_node, step_cost):
        self.state = state
        self.parent = parent_node
        if parent_node is not None:
            self.path_cost = step_cost + parent_node.path_cost
        else:
            self.path_cost = 0

  
    def __eq__(self, rhs):
        if not isinstance(rhs, CostNode):
            return False
        else:
            return self.state == rhs.state

    def __ne__(self, rhs):
        return not self == rhs

    def __hash__(self):
        return hash(str(self.state))

    def __repr__(self):
        if self.parent is not None:
            return "({}, {}, {})".format(self.state, 
                                         self.parent.state,
                                         self.path_cost)
        else:
            return "({}, --, {})".format(self.state, 
                                         self.path_cost)


def dijkstra_search(problem):
    frontier = PriorityQueue()
    closed = set()

    start_node = CostNode(problem.start(), None, 0.0)
    frontier.add(start_node, 0)
    exp_count = 0
    

    while not frontier.is_empty():
        exp_count += 1
        cur_node = frontier.pop()
        cur_state = cur_node.state
        closed.add(cur_state)

        if cur_state == problem.goal():
            path =  construct_path(cur_node)
            print(cur_node.path_cost)
            print("Expansions: {}".format(exp_count))
            return construct_path(cur_node)
         
        else:
            successors = problem.successors(cur_state)
            for next_state in successors:
                cost = problem.cost(cur_state, next_state)
                next_node = CostNode(next_state, cur_node, cost)
                if next_state not in closed:
                    frontier.add(next_node, next_node.path_cost)
    return None


def astar_search(problem):
    frontier = PriorityQueue()
    closed = set()

    start_node = CostNode(problem.start(), None, 0.0)
    frontier.add(start_node, 0)
    exp_count = 0

    while not frontier.is_empty():
        exp_count += 1
        cur_node = frontier.pop()
        cur_state = cur_node.state
        closed.add(cur_state)

        if cur_state == problem.goal():
            path =  construct_path(cur_node)
            print(cur_node.path_cost)
            print("Expansions: {}".format(exp_count))
            return construct_path(cur_node)
         
        else:
            successors = problem.successors(cur_state)
            for next_state in successors:
                cost = problem.cost(cur_state, next_state)
                next_node = CostNode(next_state, cur_node, cost)
                if next_state not in closed:
                    f = next_node.path_cost + problem.heuristic(next_state)
                    frontier.add(next_node, f)
    return None

    
def main():
    from shapely.geometry import Point
    np.random.seed(13)
    obs1 = Point(-40, 60).buffer(10)
    obs2 = Point(40, 60).buffer(10)
    prob = ArmProblemArm([0., 0.], [90., 0.], goal_tolerance=10.,
                      obstacles=[obs1, obs2])
    grid_prob = ArmProblem(prob)               
    path = astar_search(grid_prob)
    #path = dijkstra_search(grid_prob)
    print(path)
    result = []
    if path is not None:
        for step in path:
            result.append(step.q)
    print(result)
    prob.animate_plan(result)
    
if __name__ == "__main__":
    main()

