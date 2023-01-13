import numpy as np
from arm_planning import ArmProblem
import rrt

def angle_diffs(xs, y):
    #https://stackoverflow.com/questions/1878907/
    #the-smallest-difference-between-2-angles
    xs = np.deg2rad(xs)
    y = np.deg2rad(y)
    diffs = np.arctan2(np.sin(xs-y), np.cos(xs-y))
    diffs = np.rad2deg(diffs)
    return diffs
        
def angle_metric_l2(xs, y):
    diffs = angle_diffs(xs, y)
    return  np.sqrt(np.sum(diffs**2, axis=1))
    

class RRTArm(object):

    def __init__(self, arm_problem):
        self.arm_problem = arm_problem
        
    def random_state(self):
        return (np.random.random((self.arm_problem.arm.num_links(),)) *
                360. - 180.0)
        

    def select_input(self, x_rand, x_near):

        u = angle_diffs(np.array(x_rand), x_near)

        # oob_indices = np.abs(u) > self.arm_problem.MAX_ANGLE_DELTA
        # u[oob_indices] = (np.sign(u[oob_indices]) *
        #                   np.ones(u[oob_indices].shape) *
        #                   self.arm_problem.MAX_ANGLE_DELTA * .99)
        
        # max_u = np.max(np.abs(u))
        
        # if max_u > self.arm_problem.MAX_ANGLE_DELTA:
        #     u = (u / max_u) * self.arm_problem.MAX_ANGLE_DELTA * .99

        x_new = self.new_state(x_near, u)
        while not self.arm_problem.step_ok(x_near, x_new):
            u *= .9
            x_new = self.new_state(x_near, u)
        if np.allclose(x_near, x_new):
            return None
        else:
            return u

    def new_state(self, x_near, u):
        new = x_near + u
        less = new < -180.
        new[less] = 360. + new[less]  
        more = new > 180.
        new[more] = new[more] - 360.
        return new

    def close_enough(self, x, x_goal):
        return self.arm_problem.at_goal(x)



def draw_tree(tree, ax=None, linewidth=.5, markersize=3):
    """ Draw a full RRT using matplotlib. """
    import matplotlib.pyplot as plt
    if not ax:
        ax = plt.gca()
    for node in tree:
        if node.parent is not None:
            ax.plot([node.parent.x[0], node.x[0]], [node.parent.x[1],
                                                    node.x[1]], 'k.-')
                    #linewidth=linewidth,
                    #markersize=markersize)

    
def test_planning():
    from shapely.geometry import Point
    #np.random.seed(13)
    np.random.seed(58)
    #np.random.seed(15)
    obs1 = Point(-40, 60).buffer(10)
    obs2 = Point(40, 60).buffer(10)
    prob = ArmProblem([0, 0, 0, 0], [90, 0, 0, 0], goal_tolerance=25.,
                      obstacles=[obs1, obs2])
    rrt_prob = RRTArm(prob)

    #for i in range(100):
        
    path, tree =  rrt.rrt_goal(rrt_prob, prob.start(), prob.goal(), 10000,
                               dist_metric=angle_metric_l2)
    from arm_plotting import draw_c_space
    import matplotlib.pyplot as plt
    ax = plt.gca()
    # draw_c_space(rrt_prob.arm_problem.arm, ax, [obs1, obs2], [(1., .5,
    #                                                            .5),
    #                                                           (.5,
    #                                                            .5,
    #                                                            1)])
    draw_tree(tree, ax)
    plt.show()
        
    
    result = []
    if path is not None:
        for step in path:
            result.append(step.x)
    print("OK:")
    print(prob.plan_ok(result))
    print(tree.num_nodes())
    prob.animate_plan(result)  
        

    
if __name__ == "__main__":
    #import timeit
    #print(timeit.timeit(test_planning,number=3))
    test_planning()
