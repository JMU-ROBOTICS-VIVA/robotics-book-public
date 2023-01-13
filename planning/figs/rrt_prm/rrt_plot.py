import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from rrt import rrt, rrt_goal
from rrt_problems import RRTStraightLinesImage, RRTDubinsImage


def draw_tree(tree, ax=None, linewidth=.5, markersize=3):
    """ Draw a full RRT using matplotlib. """
    if not ax:
        ax = plt.gca()
    for node in tree:
        if node.parent is not None:
            ax.plot([node.parent.x[0], node.x[0]], [node.parent.x[1],
                                                    node.x[1]], 'k.-',
                    linewidth=linewidth,
                    markersize=markersize)

            
def draw_dubins_edge(parent, child, problem, ax,
                     line_args={'linestyle':'-', 'color':'k'},
                     point_args={'linestyle':'', 'marker':''}):
    if not ax:
        ax = plt.gca()
        
    if child.u != 0:
        d = np.linspace(0, problem.move_length, 10)
        r = child.u
        theta = parent.x[2]
        x_offsets = -r * np.sin(theta - d/r) + r * np.sin(theta)
        y_offsets =  r * np.cos(theta - d/r) - r * np.cos(theta)
        ax.plot(parent.x[0] + x_offsets,
                parent.x[1] + y_offsets, **line_args)

    else:
        ax.plot([child.parent.x[0], child.x[0]], [child.parent.x[1],
                                                  child.x[1]], **line_args)
    #Plot the endpoints.
    ax.plot(parent.x[0], parent.x[1], **point_args)
    ax.plot(child.x[0], child.x[1], **point_args)


def draw_dubins_path(path, problem, ax=None):
    if not ax:
        ax = plt.gca()
    for i in range(len(path)-1):
        draw_dubins_edge(path[i], path[i+1], problem, ax,
                         line_args={'linestyle':'-', 'color':'r'})
         
def draw_dubins_tree(tree, problem, ax=None):
    if not ax:
        ax = plt.gca()
    for node in tree:
        if node.parent is not None:
            draw_dubins_edge(node.parent, node, problem, ax,
                             line_args={'linewidth':.5,'color':'k'})


def voronoi_plot_2d(vor, ax=None, **kw):
    """
    Plot the given Voronoi diagram in 2-D

    Parameters
    ----------
    vor : scipy.spatial.Voronoi instance
        Diagram to plot
    ax : matplotlib.axes.Axes instance, optional
        Axes to plot on
    show_points: bool, optional
        Add the Voronoi points to the plot.
    show_vertices : bool, optional
        Add the Voronoi vertices to the plot.
    line_colors : string, optional
        Specifies the line color for polygon boundaries
    line_width : float, optional
        Specifies the line width for polygon boundaries
    line_alpha: float, optional
        Specifies the line alpha for polygon boundaries
    point_size: float, optional
        Specifies the size of points


    Returns
    -------
    fig : matplotlib.figure.Figure instance
        Figure for the plot

    See Also
    --------
    Voronoi

    Notes
    -----
    Requires Matplotlib.

    Examples
    --------
    Set of point:

    >>> import matplotlib.pyplot as plt
    >>> points = np.random.rand(10,2) #random

    Voronoi diagram of the points:

    >>> from scipy.spatial import Voronoi, voronoi_plot_2d
    >>> vor = Voronoi(points)

    using `voronoi_plot_2d` for visualisation:

    >>> fig = voronoi_plot_2d(vor)

    using `voronoi_plot_2d` for visualisation with enhancements:

    >>> fig = voronoi_plot_2d(vor, show_vertices=False, line_colors='orange',
    ...                 line_width=2, line_alpha=0.6, point_size=2)
    >>> plt.show()

    """
    from matplotlib.collections import LineCollection

    if vor.points.shape[1] != 2:
        raise ValueError("Voronoi diagram is not 2-D")

    if kw.get('show_points', True):
        point_size = kw.get('point_size', None)
        ax.plot(vor.points[:,0], vor.points[:,1], '.', markersize=point_size)
    if kw.get('show_vertices', True):
        ax.plot(vor.vertices[:,0], vor.vertices[:,1], 'o')

    line_colors = kw.get('line_colors', 'k')
    line_width = kw.get('line_width', 1.0)
    line_alpha = kw.get('line_alpha', 1.0)

    center = vor.points.mean(axis=0)
    ptp_bound = vor.points.ptp(axis=0)

    
    finite_segments = []
    infinite_segments = []
    for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
        simplex = np.asarray(simplex)
        if np.all(simplex >= 0):
            finite_segments.append(vor.vertices[simplex])
        else:
            i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

            t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[pointidx].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            #far_point = vor.vertices[i] + direction * ptp_bound.max()
            far_point = vor.vertices[i] + direction * 1000

            infinite_segments.append([vor.vertices[i], far_point])

    ax.add_collection(LineCollection(finite_segments,
                                     colors=line_colors,
                                     lw=line_width,
                                     alpha=line_alpha,
                                     linestyle='solid'))
    ax.add_collection(LineCollection(infinite_segments,
                                     colors=line_colors,
                                     lw=line_width,
                                     alpha=line_alpha,
                                     linestyle='solid'))


class RRTImageViz:
    def __init__(self, problem, save_steps=[], show_vor=False,
                 interactive=False, prefix="rrt_tree", figsize=(4,4),
                 show_axis=False, file_type="pdf", dpi=300, show_text=True):
        self.problem = problem
        self.step = 0
        self.ready = False
        self.show_vor = show_vor
        self.save_steps = save_steps
        self.interactive = interactive
        self.prefix = prefix
        self.figsize = figsize
        self.show_axis = show_axis
        self.file_type = file_type
        self.dpi = dpi
        self.show_text = show_text

    def points(self, tree):
        points = np.zeros((tree.num_nodes(), 2))
        for i, node in enumerate(tree):
            points[i,:] = node.x 
        return points


    def _draw_tree(self, tree):
        from scipy.spatial import Voronoi
        matplotlib.rc('text', usetex = True)
        params= {'text.latex.preamble' : [r'\usepackage{amsmath}']}
        
        plt.rcParams.update(params)
        matplotlib.rcParams['lines.linewidth'] = .5
        matplotlib.rcParams['lines.markersize'] = 3
        
        fig = plt.figure(figsize=self.figsize)
        ax = fig.gca()
        
        if tree.num_nodes() > 4 and self.show_vor:
            points = self.points(tree)
            vor = Voronoi(points)
            voronoi_plot_2d(vor, ax, show_vertices=False,
                            show_points=False, line_width=.5,line_colors='b')

        ax.imshow(self.problem.img)
        ax.plot(tree.root.x[0], tree.root.x[1], 'k.', markersize=6)
        if self.show_text:
            ax.annotate(r"$\mathbf{q}_{I}$", (tree.root.x[0]-10,
                                              tree.root.x[1]+10))
        draw_tree(tree, ax)
        ax.axis('image')
        if not self.show_axis:
            ax.axis('off')
        ax.set_xlim(0, self.problem.img.shape[1])
        ax.set_ylim(self.problem.img.shape[0], 0)
        ax.xaxis.set_major_locator(plt.NullLocator())
        ax.yaxis.set_major_locator(plt.NullLocator())
        return ax

    def _draw_q_rand(self, q_rand, tree):
        ax = self._draw_tree(tree)
        ax.plot(q_rand[0], q_rand[1], 'b.')
        if self.show_text:
            ax.annotate(r"$\mathbf{q}_{\text{rand}}$", (q_rand[0]+3,
                                                        q_rand[1]+6))
        return ax

    def _draw_q_near(self, q_rand, q_near, tree):
        ax = self._draw_q_rand(q_rand, tree)
        ax.plot(q_near[0], q_near[1], 'b.')
        ax.plot([q_near[0], q_rand[0]], [q_near[1], q_rand[1]], '--')
        if self.show_text:
            ax.annotate(r"$\mathbf{q}_{\text{near}}$", (q_near[0]+3,
                                                        q_near[1]+6))
        return ax
        
    def draw_step(self, q_rand, q_near, u, q_new, tree):
        import matplotlib.pyplot as plt
        print(self.step)
        ax = self._draw_tree(tree)
        if self.step in self.save_steps:
            plt.savefig('{}_{:04d}_D.{}'.format(self.prefix, self.step-1,
                                             self.file_type),
                        format=self.file_type,
                        bbox_inches='tight', dpi=self.dpi)
        if self.interactive:
            plt.show()
        else:
            plt.close()
        
        
        ax = self._draw_q_rand(q_rand, tree)
        if self.step in self.save_steps:
            plt.savefig('{}_{:04d}_A.{}'.format(self.prefix, self.step,
                                               self.file_type),
                        format=self.file_type,
                        bbox_inches='tight',
                        dpi=self.dpi)
        if self.interactive:
            plt.show()
        else:
            plt.close()
        
        ax = self._draw_q_near(q_rand,q_near, tree)
        if self.step in self.save_steps:
            plt.savefig('{}_{:04d}_B.{}'.format(self.prefix, self.step,
                                               self.file_type),
                        format=self.file_type,
                        bbox_inches='tight',
                        dpi=self.dpi)
        if self.interactive:
            plt.show()
        else:
            plt.close()

        ax = self._draw_q_near(q_rand,q_near, tree)
        ax.plot(q_new[0], q_new[1], 'b.')
        if self.show_text:
            ax.annotate(r"$\mathbf{q}_{\text{new}}$", (q_new[0]+3,
                                                       q_new[1]+6))

        if self.step in self.save_steps:
            plt.savefig('{}_{:04d}_C.{}'.format(self.prefix, self.step,
                                              self.file_type),
                        format=self.file_type,
                        bbox_inches='tight',
                        dpi=self.dpi)

        if self.interactive:
            plt.show()
        else:
            plt.close()

        self.step += 1




def image_rrt_demo(save_figs=False, show_every=20, save_for_asy=False,
                   figsize=(3,3), interactive=True):
    import matplotlib.pyplot as plt
    import matplotlib.image
    img = matplotlib.image.imread('no_grid_c_obs.png')
    start = np.array([130., 295.])
    goal = np.array([310., 165.])
    
    path = None
    num_steps = show_every
    while path is None: 
        
        fig = plt.figure(figsize=figsize)
        
        problem = RRTStraightLinesImage(img, step_size=.04,
                                        goal_margin=5, seed=18)
        path, tree = rrt_goal(problem, start, goal, num_steps)

        draw_tree(tree, linewidth=.25, markersize=1)
        plt.imshow(problem.img)
        fig.gca().xaxis.set_major_locator(plt.NullLocator())
        fig.gca().yaxis.set_major_locator(plt.NullLocator())
         
        plt.axis('image')
        plt.axis('off')
        if save_figs:
            plt.savefig('rrt_triangle_{}.pdf'.format(num_steps), format="pdf",
                        bbox_inches='tight',pad_inches=-.05, dpi=300 )

        if path is not None:

            for i in range(len(path)-1):
                plt.plot([path[i].x[0], path[i+1].x[0]],
                         [path[i].x[1], path[i+1].x[1]], 'r.-',
                         linewidth=.25, markersize=1.1)
            if save_figs:
                plt.savefig('rrt_triangle_sol.pdf', format="pdf",
                            bbox_inches='tight',pad_inches=-.05, dpi=300)
                
            if save_for_asy:
                with open("dat/rrt_sol.dat".format(num_steps), "w") as f:
                    for i in range(len(path)-1):
                        line = "{:.4f}, {:.4f}, {:.4f}, {:.4f}\n"
                        f.write(line.format(path[i].x[0],
                                            path[i].x[1],
                                            path[i+1].x[0],
                                            path[i+1].x[1]))
                    f.write("{:.4f}, {:.4f}\n".format(path[-1].x[0],
                                                      path[-1].x[1]))

            
                
        if save_for_asy:
            with open("dat/rrt_tree{}.dat".format(num_steps), "w") as f:
                for node in tree:
                    if node.parent is not None:
                        f.write("{}, {}, {}, {}\n".format(node.x[0],
                                                          node.x[1],
                                                          node.parent.x[0],
                                                          node.parent.x[1]))

        num_steps += show_every

        if interactive:
            plt.show() 

def make_gif(file_name, show_vor=False, delay="30"):
    import tempfile
    import shutil
    import subprocess

    start = np.array([50, 50])
    goal =  np.array([90, 90])

    num_steps = 50
    tmp_dir = tempfile.mkdtemp()
    
    problem = RRTStraightLinesImage(None, step_size=.1,
                                    goal_margin=5, seed=18)
    viz = RRTImageViz(problem, show_vor=show_vor, save_steps=range(num_steps),
                      figsize=(2.5, 2.5), file_type='png', dpi=100,
                      prefix="{}/rrt".format(tmp_dir), show_text=False)
    path, tree = rrt_goal(problem, start, goal, max_tree_size=num_steps,
                          viz=viz)

    subprocess.call(["convert", "-loop", "0", "-delay", delay,
                     "{}/*.png".format(tmp_dir), file_name])
    shutil.rmtree(tmp_dir)
    
    
def image_rrt_figs():
    import matplotlib.image

    start = np.array([50, 50])
    goal =  np.array([90, 90])

    problem = RRTStraightLinesImage(None, step_size=.1,
                                    goal_margin=5, seed=18)
    viz = RRTImageViz(problem, show_vor=False, save_steps=[6,7],
                      figsize=(1.5, 1.5))
    path, tree = rrt_goal(problem, start, goal, max_tree_size=20,
                          viz=viz)
    
    problem = RRTStraightLinesImage(None, step_size=.05,
                                    goal_margin=5, seed=19)
    viz = RRTImageViz(problem, show_vor=True, save_steps=[10],
                      prefix="rrt_vor", figsize=(2,2), show_axis=True,
                      interactive=False, show_text=False)
    path, tree = rrt_goal(problem, start, goal, max_tree_size=20,
                          viz=viz)
    
    

def dubins_demo(save_figs=True, show_every=20,
                figsize=(3,3), interactive=True):
    import matplotlib.pyplot as plt
    import matplotlib.image
    img = matplotlib.image.imread('car_room.png')
    
    start =  np.array([150., 300., 0])
    goal = np.array([70., 300., 0])

    num_steps = show_every
    path = None
    while path is None:
        fig = plt.figure(figsize=figsize)
        problem = RRTDubinsImage(img, move_length=15, turn_radius=35,
                                 goal_margin=15, seed=12)
        path, tree = rrt_goal(problem, start, goal, num_steps,
                              dist_metric=lambda xs, y:
                              np.sum((xs[:,0:2] - y[0:2])**2, axis=1))
        draw_dubins_tree(tree, problem)
        plt.imshow(problem.img)
        fig.gca().xaxis.set_major_locator(plt.NullLocator())
        fig.gca().yaxis.set_major_locator(plt.NullLocator())
         
        plt.axis('image')
        plt.axis('off')
        if save_figs:
            plt.savefig('rrt_car_{}.pdf'.format(num_steps), format="pdf",
                        bbox_inches='tight',pad_inches=.0, dpi=300 )
        if path:
            draw_dubins_path(path, problem)
            if save_figs:
                plt.savefig('rrt_car_sol.pdf', format="pdf",
                            bbox_inches='tight',pad_inches=.00, dpi=300)
        plt.imshow(problem.img)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
    
        plt.axis('image')
        plt.axis('off')
        num_steps += show_every
        if interactive:
            plt.show()
    

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--figs", help="generate figures",
                        action="store_true")
    parser.add_argument("--gifs", help="generate gifs",
                        action="store_true")
    args = parser.parse_args()
    
    if args.figs:
        
        print("Generating triangle world figs...")
        image_rrt_figs()
        image_rrt_demo(save_figs=True, show_every=50,
                       save_for_asy=False, figsize=(1.8, 1.8),
                       interactive=False)
        
        print("Generating car world figs...")
        dubins_demo(save_figs=True, show_every=100, figsize=(1.8,
                                                             1.8),
                    interactive=False)
    elif args.gifs:
        make_gif('rrt.gif', show_vor=False)
        make_gif('rrt_vor.gif', show_vor=True, delay="60")
    else:
        image_rrt_demo()
        dubins_demo(show_every=1)

