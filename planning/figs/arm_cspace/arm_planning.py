import matplotlib.pyplot as plt
from shapely.geometry import Point
import arm_plotting
import numpy as np
import arm

class Problem(object):

    def start(self):
        raise NotImplementedError()

    def goal(self):
        raise NotImplementedError()
            
    def step_ok(self, q1, q2):
        raise NotImplementedError()

    def plan_ok(self, plan):
        raise NotImplementedError()


def angle_diff(x, y):
    x = np.deg2rad(x)
    y = np.deg2rad(y)
    diff = np.arctan2(np.sin(x-y), np.cos(x-y))
    #diff = np.fmod(np.rad2deg(diff), 180.0)
    diff = np.rad2deg(diff)
    return diff

#https://stackoverflow.com/questions/42617529/
#how-can-i-vectorize-linspace-in-numpy
def vlinspace(a, b, N, endpoint=True):
    a, b = np.asanyarray(a), np.asanyarray(b)
    return a[..., None] + (b-a)[..., None]/(N-endpoint) * np.arange(N)

class ArmProblem(Problem):
    ARM_LENGTH = 100.0
    ARM_WIDTH = 3.0
    ANGLE_LIMITS = 270.0
    MAX_ANGLE_DELTA = 6.0
    
    def __init__(self, start_config, goal_config, goal_tolerance=1.0,
                 obstacles=[]):
        self.start_config = np.array(start_config)
        self.goal_config = np.array(goal_config)
        num_links = self.start_config.size
        self.obstacles = obstacles
        self.goal_tolerance = goal_tolerance
        
        lengths = [self.ARM_LENGTH / num_links for _ in range(num_links)]
        widths = [self.ARM_WIDTH for _ in range(num_links)]
        angle_limits = [[-self.ANGLE_LIMITS/2.0,
                         self.ANGLE_LIMITS/2.0] for _ in range(num_links)]
        angle_limits[0][0] = float('nan')
        angle_limits[0][1] = float('nan')

        self.arm = arm.Arm(lengths, widths, angle_limits)

    def start(self):
        return self.start_config

    def goal(self):
        return self.goal_config

    def at_goal(self, q):
        return (np.max(np.abs(angle_diff(q, self.goal_config))) <
                self.goal_tolerance)

    def angle_sequence(self, q1, q2):

        max_angle_diff = np.max(np.abs(angle_diff(q2, q1)))
        num_steps = np.ceil(float(max_angle_diff) /
                                self.MAX_ANGLE_DELTA) +1
        steps = vlinspace(q1, q1 + angle_diff(q2, q1), num_steps)
        #steps = np.fmod(steps[:,1::], 180).T
        steps = steps[:,1::].T
        
        return steps
        
    def step_ok(self, q1, q2):
        steps = self.angle_sequence(q1, q2)
        for step in range(steps.shape[0]-1, -1, -1):
            q = steps[step]
            if not self.arm.set_angles(q):
                return False
            if self.arm.self_collision():
                return False
            if self.arm.check_collision(self.obstacles):
                return False
        return True
            

    def plan_ok(self, plan):
        if len(plan) == 0:
            print("Zero length plan!")
            return False
        if not np.allclose(plan[0], self.start_config):
            print("Plan does not start at the start configuration!")
            return False
        for i in range(len(plan) - 1):
            if not self.step_ok(plan[i], plan[i + 1]):
                print("Plan includes an invalid step!")
                return False
        if not self.at_goal(plan[-1]):
            print("Plan does not terminate at the goal state!")
            return False
        return True

    def _update_animation(self, plan, handles):
        if self._frame_number < len(plan) and self._frame_number >= 0:
            self.arm.set_angles(plan[self._frame_number], False)
            links = self.arm.get_geometry()
            for i, link in enumerate(links):
                xs, ys = link.exterior.xy
                handles[i][0].set_xy(np.append([xs], [ys], axis=0).T)
                p_zero_link = self.arm.forward_kinematics(i, Point(0, 0))
                handles[i][1].set_data([p_zero_link.x], [p_zero_link.y])
        elif self._frame_number == len(plan):
            self._frame_number = -10 # create a pause at the end.
        self._frame_number += 1
        plt.draw()
        
        
    def animate_plan(self, plan):
        fig = plt.figure()
        ax = fig.gca()

        steps = []
        for i in range(len(plan)-1):
            steps.extend(list(self.angle_sequence(plan[i], plan[i+1])))
        
            

        for obs in self.obstacles:
            xs, ys = obs.exterior.xy
            ax.fill(xs, ys, edgecolor=(0, 0, 0),
                    facecolor=(.5, .5, 1.0))

        self.arm.set_angles(self.start(), False)
        arm_plotting.draw_arm(self.arm, ax, alpha=.2)
        self.arm.set_angles(self.goal(), False)
        arm_plotting.draw_arm(self.arm, ax, alpha=.2)
        
        self.arm.set_angles(plan[0], False)
        handles = arm_plotting.draw_arm(self.arm, ax)
        timer = fig.canvas.new_timer(interval=100)
        timer.add_callback(self._update_animation, steps, handles)
        self._frame_number = 1
        timer.start()
        ax.axis('scaled')
        ax.set_xlim(-self.ARM_LENGTH, self.ARM_LENGTH)
        ax.set_ylim(-self.ARM_LENGTH, self.ARM_LENGTH)
        ax.xaxis.set_major_locator(plt.NullLocator())
        ax.yaxis.set_major_locator(plt.NullLocator())

        plt.show()


    
if __name__ == "__main__":
    obs = Point(150, 150).buffer(10)
    p = ArmProblem([0, 0, 0], [45, 45, 45],
                   obstacles=[obs])

    plan = np.zeros((100,3))
    plan[:, 0] =np.linspace(0, 45, 100)
    plan[:, 1] =np.linspace(0, 45, 100)
    plan[:, 2] =np.linspace(0, 45, 100)

    print(p.plan_ok(plan))
    p.animate_plan(plan)
