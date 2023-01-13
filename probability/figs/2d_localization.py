
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.colors import LinearSegmentedColormap
np.set_printoptions(precision=3, suppress=True)
CDICT = {'red':   ((0.0,  1.0, 1.0),
                   (0.0001,  1.0, 1.0),
                   (0.0002,  0.9, 0.9),
                   (1.0,  0.0, 0.0)),
         
         'green': ((0.0,  1.0, 1.0),
                   (0.0001,  1.0, 1.0),
                   (0.0002,  0.9, 0.9),
                   (1.0,  0.0, 0.0)),

         
         
         'blue':  ((0.0,  1.0, 1.0),
                   (0.0001,  1.0, 1.0),
                   (0.0002,  0.9, 0.9),
                   (1.0,  0.0, 0.0))}


PROB_MAP = LinearSegmentedColormap('prob_map', CDICT)


class Robot(object):
    def __init__(self, width, height, pos):
        self.pos = np.array(pos) # y, x
        self._width = width # x dimension
        self._height = height

    
    def move(self, action):
        possible_moves = self.move_dist(self._height, self._width, self.pos,
                                        action)        
        r = np.random.random()
        total_prob = 0
        for move in possible_moves:
            total_prob += possible_moves[move]
            if r < total_prob:
                self.pos[0] = move[0]
                self.pos[1] = move[1]
                return
    @staticmethod
    def move_dist(height, width, pos, action):
        """ actions 0 - left
                    1 - right
                    2 - up
                    3 - down
            actions succeed .8, when they fail, robot doesn't move.
            movements outside of grid have no effect. 

            Returns a dictionary for the sake of efficiency.
        """

        new_pos = np.copy(pos)
        if action == 0:
            new_pos[1] -= 1
        elif action == 1:
            new_pos[1] += 1
        elif action == 2:
            new_pos[0] -= 1
        elif action == 3:
            new_pos[0] += 1
        else:
            print("BAD ACTION")
        
        if new_pos[0] >= height or new_pos[0] < 0:
            new_pos[0] = pos[0]

        if new_pos[1] >= width or new_pos[1] < 0:
            new_pos[1] = pos[1]
        
        if np.array_equal(new_pos, pos):
            return {tuple(pos): 1.0}
        else:
            return {tuple(pos): .2,  tuple(new_pos): .8}
    

class RobotTracker(object):
    def __init__(self, width, height, sensor_noise=1):
        self.locations = self.normalize(np.ones((height, width)))
        self._height = height
        self._width = width
        self._sensor_noise = sensor_noise

    def normalize(self, grid):
        return grid / np.sum(np.sum(grid))

    def distance(self, p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) 
        
    def sensor_update(self, z):
        for row in range(self._height):
            for col in range(self._width):
                z_probs = self.sensor_model_gauss((row, col))
                self.locations[row, col] *= z_probs[z]
        self.locations = self.normalize(self.locations)

    def prediction(self, action):
        lastlocations = self.locations.copy()
        self.locations = np.zeros(lastlocations.shape)
        for row_f in range(self._height):
            for col_f in range(self._width):
                cur = (row_f, col_f)
                dist = Robot.move_dist(self._height, self._width,
                                       cur, action)
                for dest in dist:
                    self.locations[dest] += dist[dest] * lastlocations[cur]
        
    def sensor_model_uniform(self, p):
        z_probs = np.zeros((self._height, self._width))
        for row in range(p[0]-2, p[0]+3, 1):
            for col in range(p[1]-2, p[1]+3, 1):
                z_probs[row%self._height, col%self._width] = 1.0


        return self.normalize(z_probs)

                    
    def sensor_model_gauss(self, p):
        locs_row, locs_col = np.meshgrid(range(self._height),
                                         range(self._width))
        all_locs = np.append(locs_row.reshape((locs_row.size,1)),
                             locs_col.reshape((locs_col.size,1)), axis=1)
        diffs = all_locs - np.array(p)
        norms = np.sum(diffs ** 2, 1)
        phis = np.exp(-norms / (2.0 * self._sensor_noise))
        z_probs = np.ones((self._height, self._width))
        z_probs[all_locs[:,0], all_locs[:,1]] = phis
        return self.normalize(z_probs)

    

    
    """
        tmp = time.time()
        z_probs = np.ones((self._height, self._width))
        for row in range(self._height):
            for col in range(self._width):
                dist = self.distance((row, col), p)
                z_probs[row,col] = \
                    np.exp(-dist**2 / (2 * self._sensor_noise**2))
        print time.time() - tmp
        return self.normalize(z_probs)
    """
    def show_dist(self, dist, robot=None, sensor=None, size=None):
        plt.ion()
        plt.gca().clear()
        plt.clf()
        im = plt.imshow(dist,cmap=PROB_MAP,interpolation='none', 
                   origin='lower',vmin=0, vmax=1)
        #plt.colorbar()
        if size is not None:
            plt.gcf().set_size_inches(size[0], size[1], forward=True)
        plt.colorbar(im, ax=plt.gca())
    
        plt.gca().set_autoscale_on(False)
        if robot is not None:
            plt.text(robot[1], robot[0], "R",color='red')
        if sensor is not None:
            plt.plot(sensor[1], sensor[0], 'b*')
        ### https://stackoverflow.com/questions/
        # 38973868/adjusting-gridlines-and-ticks-in-matplotlib-imshow
        # Major ticks
        ax = plt.gca();
        ax.set_xticks(np.arange(0, dist.shape[1], 1));
        ax.set_yticks(np.arange(0, dist.shape[0], 1));
        
        # Labels for major ticks
        ax.set_xticklabels(np.arange(1, dist.shape[1]+1, 1));
        ax.set_yticklabels(np.arange(1, dist.shape[0]+1, 1));
        
        # Minor ticks
        ax.set_xticks(np.arange(-.5, dist.shape[1], 1), minor=True);
        ax.set_yticks(np.arange(-.5, dist.shape[0], 1), minor=True);
        
        # Gridlines based on minor ticks
        ax.grid(which='minor', color='b', linestyle='-', linewidth=1)

        
        plt.show()
        plt.draw()
        plt.ginput()




def scenario1():
    """ Motion only."""
    r = Robot(10, 10, (5,5))
    rt = RobotTracker(10, 10 )
    rt.locations[:] = 0
    rt.locations[5,5] = 1
    rt.show_dist(rt.locations, r.pos)
    for i in range(100):
        
        r.move(1)
        rt.prediction(1)
        print("After State Prediction\n", np.flipud(rt.locations))
        rt.show_dist(rt.locations,r.pos)
        

def scenario2():
    r = Robot(10, 10, (5,5))
    rt = RobotTracker(10, 10 )

    rt.show_dist(rt.locations, r.pos)
    for i in range(100):
        
        z = r.pos + np.random.randint(-2, 3, size=(2,))
        z[0] = z[0]%rt._height
        z[1] = z[1]%rt._height
        
        print("Before Sensor Update\n", np.flipud(rt.locations))
        rt.show_dist(rt.locations,r.pos, z)
        rt.sensor_update(tuple(z))
        print("After Sensor Update\n", np.flipud(rt.locations))
        rt.show_dist(rt.locations,r.pos, z)
        
        r.move(1)
        rt.prediction(1)
        print("After State Prediction\n", np.flipud(rt.locations))
        rt.show_dist(rt.locations,r.pos)

def generate_figure():
    plt.rcParams.update({'font.size': 8})
    r = Robot(10, 10, (5,5))
    rt = RobotTracker(10, 10 )
    size = (3.0, 2.0)
    
    rt.show_dist(rt.locations, None, None, size)
    for i in range(100):
        
        z = r.pos + np.random.randint(-2, 3, size=(2,))
        z[0] = z[0]%rt._height
        z[1] = z[1]%rt._height
        
        print("Before Sensor Update\n", np.flipud(rt.locations))
        rt.show_dist(rt.locations, None, None, size)
        rt.sensor_update(tuple(z))
        print("After Sensor Update\n", np.flipud(rt.locations))
        rt.show_dist(rt.locations,None, None, size)
        
        plt.savefig("2dhist.pdf")
        
        r.move(1)
        rt.prediction(1)
        print("After State Prediction\n", np.flipud(rt.locations))
        rt.show_dist(rt.locations,r.pos, size)

        
if __name__ == "__main__":
    generate_figure()

