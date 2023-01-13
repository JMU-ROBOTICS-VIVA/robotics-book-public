
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches
from matplotlib.collections import PatchCollection
import matplotlib
matplotlib.rcParams['text.usetex'] = True

class Model(object):

    def __init__(self):
        pass

    def states(self):
        """ Returns an iterable sequence of states. """
        pass

    def actions(self):
        """ Returns an iterable sequence of actions. """
        pass

    def motion_model(self, x, a):
        """ Returns a dictionary mapping from states to probabilities."""
        pass

    def sensor_model(self, x):
        """Returns a dictionary mapping from sensor readings to
           probabilities."""
        pass


class HallBotModelOld(object):

    def __init__(self, num_cells=10):
        self.num_cells = num_cells

    def states(self):
        """ Returns an iterable sequence of states. """
        return range(self.num_cells)

    def actions(self):
        """ Returns an iterable sequence of actions. """
        return range(-1, 2, 1)

    def num_states(self):
        return self.num_cells

    def _bound(self, x):
        return min(max(0, x), self.num_cells - 1)
    
    def motion_model(self, x, a):
        """ Returns a dictionary mapping from states to probabilities."""
        # 80 percent likely to succeed.  Otherwise, 10 percent chance
        # on either side.
        result = defaultdict(lambda: 0.0)
        result[self._bound(x + a)] += .6
        result[self._bound(x + a + 1)] += .2
        result[self._bound(x + a - 1)] += .2
        return result
        
    def sensor_model(self, x):
        """Returns a dictionary mapping from sensor readings to
           probabilities."""
        result = {}
        if self.num_cells - x < (.5 * (self.num_cells+1)):
            result['close'] = .8
            result['far'] = .2
        else:
            result['far'] = .8
            result['close'] = .2
        return result

class HallBotModel(object):

    def __init__(self, num_cells=10):
        self.num_cells = num_cells

    def states(self):
        """ Returns an iterable sequence of states. """
        return range(self.num_cells)

    def actions(self):
        """ Returns an iterable sequence of actions. """
        return range(-1, 2, 1)

    def num_states(self):
        return self.num_cells

    def _bound(self, x):
        return min(max(0, x), self.num_cells - 1)
    
    def motion_model(self, x, a):
        """ Returns a dictionary mapping from states to probabilities."""
        # 80 percent likely to succeed.  Otherwise, 10 percent chance
        # on either side.
        result = defaultdict(lambda: 0.0)
        result[self._bound(x + a)] += .6
        result[self._bound(x + a + 1)] += .2
        result[self._bound(x + a - 1)] += .2
        return result
        
    def sensor_model(self, x):
        """Returns a dictionary mapping from sensor readings to
           probabilities."""
        result = {}
        if x == 2:
            result['close'] = .9
            result['far'] = .1
        else:
            result['close'] = .25
            result['far'] = .75
        return result

class HallBotModelRadio(HallBotModel):

    def sensor_model(self, x):
        """Returns a dictionary mapping from sensor readings to
           probabilities."""
        result = {}

        result['detected'] = 1 / 2 ** abs(x - 4)
        result['-detected'] = 1 - 1 / 2 ** abs(x -4)
        return result

    

def sample(dist):
    rand = np.random.random()
    cum = 0
    for key in dist:
        cum += dist[key]
        if cum >= rand:
            return key

def normalize_distribution(dist):
    total = sum(dist.values())
    for key in dist:
        dist[key] /= float(total)


class HallBotSim(object):

    def __init__(self, start_state=0, model=HallBotModel):
        self.hbm = model()
        self.x = start_state

    def move(self, a):
        self.x = sample(self.hbm.motion_model(self.x, a))

    def sense(self):
        return sample(self.hbm.sensor_model(self.x))

class Tracker(object):

    def __init__(self, model, initial_dist=None):
        self.model = model
        if initial_dist:
            self.dist = initial_dist
        else:
            self.dist = {}
            for state in self.model.states():
                self.dist[state] = 1.0 / self.model.num_states()

    def predict(self, action):
        bel_predict = defaultdict(lambda: 0)
        for state in self.dist:
            move_dist = self.model.motion_model(state, action)
            for next_state in move_dist:
                bel_predict[next_state] += (move_dist[next_state] *
                                            self.dist[state])
        self.dist = bel_predict

    def correct(self, percept):
        for state in self.dist:
            z_probs = self.model.sensor_model(state)
            self.dist[state] *= z_probs[percept]
        normalize_distribution(self.dist)


class VIZTracker(object):

    def __init__(self, model, initial_dist=None, robot_pos=None):
        self.fig = plt.figure(figsize=(6.0, 6.0))
        self.ax = self.fig.gca()
        self.model = model
        if initial_dist:
            self.dist = initial_dist
        else:
            self.dist = {}
            for state in self.model.states():
                self.dist[state] = 1.0 / self.model.num_states()

        # PROBABILITY HISTOGRAMS
        bar_indices = np.arange(0, model.num_states(), 1)
        initial_probs = self._dist_array(self.dist)
        self.top_boxes = self.ax.bar(bar_indices, initial_probs/2.1,
                                     width=1.0, bottom=.5,
                                     linewidth=2, color=(.5,.5,.5),
                                     edgecolor=(0,0,0), clip_on=False)
        self.bottom_boxes = self.ax.bar(bar_indices, initial_probs*0,
                                        width=1.0, bottom=0,
                                        linewidth=2, color=(.5,.5,.5),
                                        edgecolor=(0, 0 ,0),
                                        clip_on=False)

        self._draw_ticks(self.bottom_boxes)
        self._draw_ticks(self.top_boxes)
        
        self.top_text = self.ax.text(-1, .5, '$Bel(X_{t-1})$',
                                     horizontalalignment='right',
                                     clip_on=False)
        self.bottom_text = self.ax.text(-1, 0, '$Bel^{-}(X_{t})$',
                                        horizontalalignment='right',
                                        clip_on=False)

        # CAPTION
        self.caption_text = self.ax.text(0.25, 1.1, '',
                                         horizontalalignment='left',
                                         verticalalignment='center',
                                         transform=self.ax.transAxes)
        # CAPTION
        self.formula_text = self.ax.text(.5, 0 , '',
                                         horizontalalignment='center',
                                         verticalalignment='center',
                                         transform=self.ax.transAxes)

        self.robot_pos = robot_pos
        if self.robot_pos is not None:
            self.bot_patches = self._build_robot_patches()
            self.move_bot(robot_pos, show=False)


        self.ax.set_ylim(-.3, 1)
        self.ax.axis('off')

        plt.ion()
        self.update_plot()

    def move_bot(self, state, show=True):
        if self.robot_pos is not None:
            self.robot_pos = state
            if show:
                self.caption_text.set_text('Robot moves!')
                self.update_plot()
            bot_box = self.bottom_boxes[state]
            draw_at = (bot_box.get_x() + bot_box.get_width() * .2,
                       bot_box.get_y() -.12)
            t_start = self.ax.transData
            transform = matplotlib.transforms.Affine2D().translate(draw_at[0],
                                                                   draw_at[1])
            t_end = transform + t_start
            self.bot_patches.set_transform(t_end)
            if show:
                self.update_plot()

            
    def _build_robot_patches(self):
        bot_box = self.bottom_boxes[0]
        width = bot_box.get_width() * .6
        height = .07
        # axis_to_data = self.ax.transAxes + self.ax.transData.inverted()
        # size_ll = np.array(axis_to_data.transform((0,0)))
        # size_ur = np.array(axis_to_data.transform((.05,.05)))
        # data_to_axis = axis_to_data.inverted()

        bot = matplotlib.patches.Rectangle((0,0), width, height,
                                           clip_on=False,
                                           edgecolor=(0,0,0),
                                           facecolor=(1,1,1))
        bot_head = matplotlib.patches.Ellipse((.5 * bot.get_width(),
                                               bot.get_height()),
                                              width, height,
                                              clip_on=False,
                                              edgecolor=(0,0,0),
                                              facecolor=(1,1,1))
        bot_wheel = matplotlib.patches.Ellipse((.5 * bot.get_width(),
                                                0), width * .5, height
                                               * .5, clip_on=False,
                                               edgecolor=(0,0,0),
                                               facecolor=(0,0,0))
        patches = [bot_wheel, bot_head, bot]
        p = PatchCollection(patches, clip_on=False, match_original=True)
        return self.ax.add_collection(p)
    
    def _draw_ticks(self, boxes):
        boxes = list(boxes)
        for box in boxes:
            self.ax.plot([box.get_x(), box.get_x()],
                         [box.get_y(), box.get_y() + .02],
                         clip_on=False,
                         color=(0,0,0))

        box = boxes[-1]
        self.ax.plot([box.get_x() + box.get_width(),
                      box.get_x() + box.get_width()],
                     [box.get_y(), box.get_y() + .02],
                     clip_on=False,
                     color=(0,0,0))

        
    def _dist_array(self, dist):
        array = np.zeros(self.model.num_states())
        for state in dist:
            array[state] = dist[state]
        return array


    def _update_boxes(self, boxes, dist, color=(.5,.5,.5)):
        probs = self._dist_array(dist)
        for i, box in enumerate(boxes):
            box.set_height(probs[i]/2.1)
            box.set_facecolor(color)


    def _draw_motion_dist(self, boxes, from_state, move_dist,
                          next_boxes, to_state=None):
        lines = []
        centers = []
        boxes = list(boxes)
        box = boxes[from_state]
        move_probs = [move_dist[k] for k in sorted(move_dist.keys())]
        psum = 0
        for p in move_probs[0:-1]:
            centers.append((box.get_x() + box.get_width() / 2.0,
                            box.get_y() + box.get_height() *
                            (psum + .5 * p)))
            psum += p
            line, = self.ax.plot([box.get_x(),
                                  box.get_x() + box.get_width()],
                                 [box.get_y() + box.get_height() * psum,
                                  box.get_y() + box.get_height() * psum],
                                 'b')
            lines.append(line)

        centers.append((box.get_x() + box.get_width() / 2.0,
                        box.get_y() + box.get_height() *
                        (psum + .5 * move_probs[-1])))

        # draw lines...
        for i, next_state in enumerate(sorted(move_dist.keys())):
            if to_state is None or next_state == to_state:
                box = next_boxes[next_state]
                mid = (box.get_x() + box.get_width() / 2.0,
                       box.get_y())
                line = self.ax.annotate('', xy=mid, xytext=centers[i],
                                        arrowprops=dict(facecolor='black',
                                                        shrink=0.0,
                                                        width=1))
                lines.append(line)

        return lines

    def update_plot(self):
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        #plt.pause(.01)
        plt.waitforbuttonpress()

    def predict(self, action):
        self.caption_text.set_text('Prediction (Arrows represent addition.)')

        formula = '$\displaystyle Bel^{-}(X_{t}) = \sum_{x_{t-1} \in X} P(X_{t} \mid x )Bel(x_{t-1})$'
        self.formula_text.set_text(formula)
        
        self.top_text.set_text('$Bel(X_{t-1})$')
        self.bottom_text.set_text('$Bel^{-}(X_{t})$')
        self.bottom_text.set_alpha(.5)
        bel_predict = defaultdict(lambda: 0)

        self._update_boxes(self.top_boxes, self.dist)
        self._update_boxes(self.bottom_boxes, bel_predict)
        self.update_plot() # INITIAL DISTRIBUTION

        lines = []
        for state in self.dist:

            move_dist = self.model.motion_model(state, action)

            lines.extend(self._draw_motion_dist(self.top_boxes, state,
                                                move_dist,
                                                self.bottom_boxes))

            for next_state in move_dist:
                bel_predict[next_state] += (move_dist[next_state] *
                                            self.dist[state])
        self.update_plot() # SHOW IMPENDING BELIEF PROPAGATION

        #for line in lines:
        #    line.remove()
        #    del line
                
        #self._update_boxes(self.top_boxes, defaultdict(lambda: 0))
        self._update_boxes(self.bottom_boxes, bel_predict)

        self.top_text.set_text('')
        self.bottom_text.set_alpha(1.0)
        self.update_plot() # DONE

        self.dist = bel_predict

    def predict_fine(self, action):
        self.caption_text.set_text('Prediction (Arrows represent addition.)')
        self.top_text.set_text('$Bel(X_{t-1})$')
        self.bottom_text.set_text('$Bel^{-}(X_{t})$')
        self.bottom_text.set_alpha(.5)

        bel_predict = defaultdict(lambda: 0)

        self._update_boxes(self.bottom_boxes, bel_predict)
        self._update_boxes(self.top_boxes, self.dist)
        self.update_plot()

        for state in self.dist:

            move_dist = self.model.motion_model(state, action)

            lines = self._draw_motion_dist(self.top_boxes, state,
                                           move_dist,
                                           self.bottom_boxes)
            self.update_plot()
            for line in lines:
                line.remove()
                del line

            for next_state in move_dist:
                bel_predict[next_state] += (move_dist[next_state] *
                                            self.dist[state])

            self._update_boxes(self.bottom_boxes, bel_predict)
            self.dist[state] = 0
            self._update_boxes(self.top_boxes, self.dist)
            self.update_plot()

        self.top_text.set_text('')
        self.bottom_text.set_alpha(1.0)
        self.update_plot()
        
        self.dist = bel_predict


    def _vertical_arrows(self):
        arrows = []
        for i in range(self.model.num_states()):
            from_box = self.top_boxes[i]
            to_box = self.bottom_boxes[i]
            top = (from_box.get_x() + from_box.get_width() / 2.0,
                   from_box.get_y())
            bottom = (to_box.get_x() + to_box.get_width() / 2.0,
                      to_box.get_y() + to_box.get_height())
            
            arrows.append(self.ax.annotate('', xy=bottom, xytext=top,
                                           arrowprops=dict(facecolor='black',
                                                           shrink=0.0,
                                                           width=.5, headwidth=4.0, headlength=8.0)))
        return arrows

    def correct(self, percept):
        caption = 'Correction. Sensor reading was: "{}"'.format(percept)
        self.caption_text.set_text(caption)

        formula = '$\displaystyle Bel(X_{t}) = \\alpha P(Z_t \mid X_t)Bel^{-}(X_t)$'
        self.formula_text.set_text(formula)
        
        self.top_text.set_text('$P({}|X)$'.format(percept))
        self.bottom_text.set_text('$Bel(X_{t})$')
        self.bottom_text.set_alpha(.5)

        all_z_probs = {}
        
        # show the whole sensor model, even if some is irrelevant...
        for i in range(self.model.num_states()):
            z_probs = self.model.sensor_model(i)
            all_z_probs[i] = z_probs[percept]

        self._update_boxes(self.top_boxes, all_z_probs, color=(.5,.5,.7))
        self._update_boxes(self.bottom_boxes, self.dist)
        self.update_plot() # INITIAL DISTRIBUTION

        arrows = self._vertical_arrows()

        caption = 'Correction (Arrows represent multiplication)'
        self.caption_text.set_text(caption)
        self.update_plot() # BEFORE MULTIPLICATION

        for arrow in arrows:
            arrow.remove()
            del arrow


        for state in self.dist:
            z_probs = self.model.sensor_model(state)
            self.dist[state] *= z_probs[percept]

        self._update_boxes(self.bottom_boxes, self.dist)
        self.update_plot() # AFTER MULTIPLICATION


        self.top_text.set_text('')
        self._update_boxes(self.top_boxes, defaultdict(lambda: 0))
        self.caption_text.set_text('Correction (Normalize distribution)')
        self.update_plot() # AFTER MULTIPLICATION

        normalize_distribution(self.dist)

        self._update_boxes(self.bottom_boxes, self.dist)
        self.bottom_text.set_alpha(1.0)
        self.update_plot() # AFTER NORMALIZATION


def to_array(dist, size):
    array = np.zeros(size)
    for state in dist:
        array[state] = dist[state]
    return array

        
def test_tracking():
    hb = HallBotModel()
    track = Tracker(hb)
    sim = HallBotSim()
    for i in range(100):
        print(sim.x)
        plt.bar(np.arange(0, sim.hbm.num_cells,1),
                to_array(track.dist, sim.hbm.num_cells), width=1.0,
                linewidth=2, color=(.7, .7, .7), edgecolor=(0,0,0))
        axes = plt.gca()
        axes.set_ylim([0,1])
        plt.axes([0, sim.hbm.num_cells, 0, 1])
        plt.show()
        sim.move(1)
        track.predict(1)
        percept = sim.sense()
        print(percept)
        track.correct(percept)

        print(track.dist)
    

def test_viz_tracker():
    hb = HallBotModelRadio()
    dist = {}
    #for i in range(2):
    #    dist[i] = .5
    dist[2] = .25
    dist[3] = .5
    dist[4] = .25
    #dist[0] = 1.0
    track = VIZTracker(hb, dist, 0)
    sim = HallBotSim(0, type(hb))
    for i in range(1000):
        track.predict(1)
        #track.predict_fine(1)
        sim.move(1)
        track.move_bot(sim.x)
        percept = sim.sense()
        track.correct(percept)

    
if __name__ == "__main__":
    test_viz_tracker()
    #test_tracking()
