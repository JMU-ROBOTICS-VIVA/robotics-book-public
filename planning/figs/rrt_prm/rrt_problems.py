import numpy as np

class RRTStraightLinesImage(object):

    def __init__(self, img, step_size, goal_margin, seed=10):
        np.random.seed(seed)
        if img is None:
            self.img = np.ones((100, 100, 3))
        else:
            self.img = img
        self.width = self.img.shape[1]
        self.height = self.img.shape[0]
        self.goal_margin = goal_margin
        self.step_size = step_size

    def is_collision(self, x):
        try:
            result = self.img[int(x[1]),int(x[0]),0] != 1.0
        except IndexError:
            result = True
        return result
     
    def random_state(self):
        state = (np.random.random((2,)) *
                np.array([self.width, self.height]))
        return state

    def select_input(self, x_rand, x_near):
        assert not self.is_collision(x_near)

        u = x_rand - x_near
        length = np.linalg.norm(u)
        if length > self.step_size * self.width:
            u = u / length * self.step_size * self.width

        x_new = self.new_state(x_near, u)
        while self.is_collision(x_new):
            u *= .5
            x_new = self.new_state(x_near, u)
        if np.allclose(x_near, x_new):
            return None
        else:
            return u

    def new_state(self, x_near, u):
        return x_near + u

    def close_enough(self, x, x_goal):
        u = x - x_goal
        return np.linalg.norm(u) < self.goal_margin

    
class RRTDubinsImage(RRTStraightLinesImage):
    """ x = [x, y, theta], u = turn radius
    """

    def __init__(self, img, move_length, turn_radius, goal_margin, seed=10):
        super(RRTDubinsImage, self).__init__(img, -1, goal_margin, seed)
        self.move_length = move_length
        self.turn_radius = turn_radius

    def random_state(self):
        state = (np.random.random((3,)) *
                 np.array([self.width, self.height, 2 * np.pi]))
        return state

    def select_input(self, x_rand, x_near):
        assert not self.is_collision(x_near)

        actions = np.array([-self.turn_radius,-self.turn_radius *2 ,0.,
                             self.turn_radius, self.turn_radius * 2])
        dists = np.zeros(actions.shape)
        for i, u in enumerate(actions):
            x_new = self.new_state(x_near, u)
            if self.is_collision(x_new):
                dists[i] = float('inf')
            else:
                dists[i] = np.linalg.norm(x_rand[0:2] - x_new[0:2])

        if np.min(dists) == float('inf'):
            return None
        else:
            return actions[np.argmin(dists)]
            

    def new_state(self, x_near, u):
        x_new = self.dubins_update(x_near, self.move_length, u)
        return x_new

    def dubins_update(self, x, d, r):
        #https://math.stackexchange.com/questions/275201/
        #how-to-find-an-end-point-of-an-arc-given-another
        #-end-point-radius-and-arc-dire
        x_new = np.array(x)
        if r == 0:
            x_new[0] = x[0] + d * np.cos(x[2])
            x_new[1] = x[1] + d * np.sin(x[2])
        else:
            turn_angle = float(d) / r
            x_new[0:2] += np.array([-r * np.sin(x[2] - turn_angle) +
                                    r * np.sin(x[2]),
                                    r * np.cos(x[2] - turn_angle) -
                                    r * np.cos(x[2])])
            x_new[2] -= turn_angle;
            
        return x_new

    def close_enough(self, x, x_goal):
        u = x[0:2] - x_goal[0:2]
        return np.linalg.norm(u) < self.goal_margin

    
