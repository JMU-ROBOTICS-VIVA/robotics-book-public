"""Pure python implementation of the Rapidly Exploring Random Tree
algorithm

author: Nathan Sprague and ...

"""
import numpy as np
from spatial_map import SpatialMap


class RRTNode(object):
    """ RRT Tree node. """
    def __init__(self, parent, u, x):
        """ Constructor.
        Arguments:
            parent - Parent node in the tree.
            u      - control signal that moves from the parents state to x.
            x      - state associated with this node.
        """
        self.parent = parent
        self.u = u
        self.x = x

    def __repr__(self):
        """ String representation for debugging purposes. """
        return "<u: {}, x: {}>".format(self.u, self.x)

    def path(self):
        """Return the sequence of nodes from the root of the tree to this
        node.

        """
        cur = self
        path = [cur]
        while cur.parent is not None:
            cur = cur.parent
            path.append(cur)
        path.reverse()
        return path

class Tree:

    def __init__(self, q_init, dist_metric=None):
        """ root - d-dimensional numpy array """
        self.sm = SpatialMap(dim=q_init.size, dist_metric=dist_metric)
        self.root = RRTNode(None, None, q_init)
        self.sm.add(q_init, self.root)
        
    def add_node(self, q_new):
        node = RRTNode(None, None, q_new)
        return self.sm.add(q_new, node)

    def add_edge(self, q_near, q_new, u):
        new_node = self.sm.get_value(q_new)
        near_node = self.sm.get_value(q_near)
        assert np.array_equal(new_node.x, q_new)
        assert np.array_equal(near_node.x, q_near)
        new_node.parent = near_node
        new_node.u = u

    def num_nodes(self):
        return self.sm.num_values

    def __iter__(self):
        return self.sm.__iter__()

    
def nearest_neighbor(tree, q):
    return tree.sm.nearest(q).x

def construct_path(tree, q):
    node = tree.sm.get_value(q)
    assert np.array_equal(node.x, q)
    return node.path()


class RRTStraightLines(object):
    """RRT class for searching in straight line steps directly toward
        intermediate target locations.

    """
    
    def random_state(self):
        return np.random.random((2,))

    def select_input(self, q_rand, q_near):
        u = q_rand - q_near
        length = np.linalg.norm(u)
        if length > .03:
            u = u / length * .03
        return u

    def new_state(self, q_near, u):
        return q_near + u

    def close_enough(self, q, q_goal):
        return np.linalg.norm(q - q_goal) < .05


    
def rrt(problem, q_init, tree_size, viz=None, dist_metric=None):
    """ Build a rapidly exploring random tree. 
    
    Args:
        problem:   a problem instance that provides three methods:

            problem.random_state() - 
               Return a randomly generated configuration
            problem.select_input(q_rand, q_near) -
               Return an action that would move the robot from 
               q_near in the direction of q_rand
            problem.new_state(q_near, u) -
               Return the state that would result from taking 
               action u in state q_near

        q_init:     the initial state
        tree_size:  the number of nodes to add to the tree
    Returns:
        A tree where ther vertices are states and the edges 
        store actions

    """
    tree = Tree(q_init, dist_metric)  # Make the start state the root
                                      # of the tree
    
    while tree.num_nodes() < tree_size:
        q_rand = problem.random_state()
        q_near = nearest_neighbor(tree, q_rand)
        u = problem.select_input(q_rand, q_near)
        if u is None:
            continue
        q_new = problem.new_state(q_near, u)
        if viz:
            viz.draw_step(q_rand, q_near, u, q_new, tree)
        if tree.add_node(q_new): # Only added if non-duplicate.
            tree.add_edge(q_near, q_new, u)
    return tree


def rrt_goal(problem, q_init, q_goal, max_tree_size, viz=None,
             dist_metric=None):
    tree = Tree(q_init, dist_metric)
    while tree.num_nodes() < max_tree_size:
        q_rand = problem.random_state()
        q_near = nearest_neighbor(tree, q_rand)
        u = problem.select_input(q_rand, q_near)
        if u is None:
            continue
        q_new = problem.new_state(q_near, u)

        if viz:
            viz.draw_step(q_rand, q_near, u, q_new, tree)

        if tree.add_node(q_new):
            tree.add_edge(q_near, q_new, u)
            if problem.close_enough(q_new, q_goal):
                return construct_path(tree, q_new), tree
            
    return None, tree
        

def test_simple_rrt():
    """ Demo the rrt algorithm on a simple 2d search task. """
    import matplotlib.pyplot as plt
    from rrt_plot import draw_tree
    x_start = np.array([.5, .5])
    x_goal = np.array([.9, .9])
    lines = RRTStraightLines()
    path, tree = rrt_goal(lines, x_start, x_goal, 10000)
    print(path)
    result = np.zeros((len(path), 2))
    for i in range(len(path)):
        result[i, :] = path[i].x
    draw_tree(tree)
    plt.plot(result[:, 0], result[:, 1], '.-')
    plt.show()


if __name__=="__main__":
    test_simple_rrt()
   
