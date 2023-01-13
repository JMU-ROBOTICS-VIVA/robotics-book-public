"""

"""
import argparse
import numpy as np
from collections import deque
from spatial_map import SpatialMap


class PRMNode(object):
    next_id = 0
    
    def __init__(self, pos):
        self.node_id = PRMNode.next_id
        PRMNode.next_id += 1
        self.pos = pos
        
    def __eq__(self, other):
        return self.node_id == other.node_id
    
    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.node_id)

    def __repr__(self):
        return "<{}, {}>".format(self.node_id, self.pos)

class Graph:

    def __init__(self):
        self._neighbors = {}
        self._sm = SpatialMap()

    def num_nodes(self):
        return len(self._neighbors)
    
    def add_node(self, q):
        new_node = PRMNode(q)
        added = self._sm.add(q, new_node)
        assert added
        self._neighbors[new_node] = set()
        
        
    def add_edge(self, q1, q2):
        node1 = self._sm.nearest(q1)
        assert np.array_equal(node1.pos, q1)
        node2 = self._sm.nearest(q2)
        assert np.array_equal(node2.pos, q2)
        self._neighbors[node1].add(node2)
        self._neighbors[node2].add(node1)

    def neighbors(self, node):
        return self._neighbors[node]

    def __iter__(self):
        return self._neighbors.__iter__()
        

    
        

    
def all_reachable(v, graph):
    frontier = deque(graph.neighbors(v))
    closed = set()
    closed.add(v)
    while frontier:
        cur = frontier.pop()
        closed.add(cur)
        for neighbor in graph.neighbors(cur):
            if neighbor not in closed:
                frontier.appendleft(neighbor)
    return closed

            
def connected_components(graph):
    components = {}
    handled = set()
    for node in graph:
        if not node in handled:
            component = all_reachable(node, graph)
            for comp_node in component:
                components[comp_node] = component
                handled.add(comp_node)
    return components
                

def neighbors(graph, q, delta):
    node = graph._sm.nearest(q)
    nodes = None
    if node is not None and np.array_equal(node.pos, q):
        nodes = set(graph._sm.within_delta(q, delta)) - set([node])
    else:
        nodes = set(graph._sm.within_delta(q, delta))
    return [node.pos for node in nodes]

def same_component(graph, q1, q2):
    components = connected_components(graph)
    node1 = graph._sm.nearest(q1)
    assert np.array_equal(node1.pos, q1)
    node2 = graph._sm.nearest(q2)
    assert np.array_equal(node2.pos, q2)
    return components[node1] == components[node2]

class PRMImageViz:

    def __init__(self, problem, save_steps=[], interactive=True,
                 show_text=True, prefix="prm", figsize=(4,4),
                 file_type="pdf", dpi=300):
        self.problem = problem
        self.save_steps = save_steps
        self.interactive = interactive
        self.show_text = show_text
        self.prefix = prefix
        self.figsize = figsize
        self.file_type = file_type
        self.dpi = dpi

    def draw_step(self, graph, q_rand, delta):
        import matplotlib.pyplot as plt
        import matplotlib
        from matplotlib.patches import Circle
        step = graph.num_nodes() +1
        print(step)
        if step in self.save_steps or self.interactive or True:
        
        
            matplotlib.rc('text', usetex = True)
            params= {'text.latex.preamble' : [r'\usepackage{amsmath}']}
        
            plt.rcParams.update(params)
            matplotlib.rcParams['lines.linewidth'] = .5
            matplotlib.rcParams['lines.markersize'] = 3
            
            fig = plt.figure(figsize=self.figsize)
            ax = fig.gca()
            near = neighbors(graph, q_rand, delta)
            ax.imshow(self.problem.img)
            plot_graph(graph, ax, linewidth=.5, markersize=3)
            ax.axis('image')
            ax.axis('off')
            ax.set_xlim(-delta*.2, self.problem.img.shape[1]+delta*.2)
            ax.set_ylim(self.problem.img.shape[0]+delta*.2, -delta*.2)
            ax.xaxis.set_major_locator(plt.NullLocator())
            ax.yaxis.set_major_locator(plt.NullLocator())
            
            if step in self.save_steps:
                plt.savefig('{}_{:03d}_B.{}'.format(self.prefix,
                                                    step-1,
                                                    self.file_type),
                            dpi=self.dpi,
                            format=self.file_type,
                            bbox_inches='tight')
                
            circle = Circle(q_rand, radius=delta, edgecolor='k', linewidth=0,
                            fill=True, linestyle=None, alpha=.3)
            ax.add_patch(circle)
            if self.show_text:
                ax.annotate(r"$\mathbf{q}_{\text{rand}}$", (q_rand[0]+5,
                                                            q_rand[1]+40))
            for n in near:
                if self.problem.no_collision(n, q_rand):
                    plt.plot([n[0], q_rand[0]], [n[1], q_rand[1]], 'k--')
                else:
                    plt.plot([n[0], q_rand[0]], [n[1], q_rand[1]], 'r--')
            plot_graph(graph, ax, linewidth=.5, markersize=3) #hack
            plt.plot(q_rand[0], q_rand[1], 'k.')

            if step in self.save_steps:
                plt.savefig('{}_{:03d}_A.{}'.format(self.prefix, step,
                                                    self.file_type),
                            dpi=self.dpi,
                            format=self.file_type,
                            bbox_inches='tight')
        
            if self.interactive:
                plt.show()
            else:
                plt.close()

def prm(problem, delta, roadmap_size, no_loops=False, viz=None):
    """ Create a Probabalistic Roadmap.

    Args:
        problem:  a problem instance that provides two methods:
            
           problem.random_state() -       
               Return a random state from C_free
           problem.no_collision(q1, q2) - 
               Return True if there is a collision free path 
               from q1 to q2

        delta: Distance threshold for connecting neighboring states
        roadmap_size: Number of nodes in the completed Roadmap 

    Returns: 
        A graph representing a Probabilistic Roadmap
                      
    """
    graph = Graph()
    while graph.num_nodes() < roadmap_size:
        q_rand = problem.random_state()

        if viz:
            viz.draw_step(graph, q_rand, delta)
            
        graph.add_node(q_rand)
        
        for q in neighbors(graph, q_rand, delta):
            if problem.no_collision(q, q_rand):
                if no_loops:
                    if not same_component(graph, q, q_rand):
                        graph.add_edge(q, q_rand)
                else:
                    graph.add_edge(q, q_rand)
    return graph

class ImageProblem(object):
    
    def __init__(self, img, seed=10):
        if seed is not None:
            np.random.seed(seed)
            
        if img is None:
            self.img = np.ones((100, 100, 3))
        else:
            self.img = img

        self.width = self.img.shape[1]
        self.height = self.img.shape[0]
        self.img = img

    def is_collision(self, x):
        try:
            result = self.img[int(x[1]),int(x[0]),0] != 1.0
        except IndexError:
            result = True
        return result
        
    def no_collision(self, q1, q2):
        vec = q2 - q1
        length = np.linalg.norm(vec)
        fracs = np.linspace(0.0, 1.0, int(length))
        for frac in fracs:
            if self.is_collision(q1 + frac * vec):
                return False
        return True


    def random_state(self):
        """ Returns a random state in the search space. """
        x = (np.random.random((2,)) *
             np.array([self.width, self.height]))
        while self.is_collision(x):
            x = (np.random.random((2,)) *
                 np.array([self.width, self.height]))
        return x

       

def plot_graph(graph, ax=None, linewidth=.5, markersize=.5):
    import matplotlib.pyplot as plt
    if not ax:
        ax = plt.gca()
    for node in graph:
        plt.plot([node.pos[0], node.pos[0]],
                 [node.pos[1], node.pos[1]], 'k.-',
                 linewidth=linewidth, markersize=markersize)
        for neighbor in graph.neighbors(node):
            plt.plot([node.pos[0], neighbor.pos[0]],
                     [node.pos[1], neighbor.pos[1]], 'k.-',
                     linewidth=linewidth, markersize=markersize)
    return ax


def write_edges(graph, file_name):
    with open(file_name, "w") as f:
        edges = set()
        for parent in graph:
            for child in graph.neighbors(parent):
                edge = (parent.node_id, child.node_id)
                if edge not in edges:
                    line = "{:.4f}, {:.4f}, {:.4f}, {:.4f}\n"
                    f.write(line.format(parent.pos[0],
                                        parent.pos[1],
                                        child.pos[0],
                                        child.pos[1]))
                    edges.add(edge)




def make_gif(file_name):
    import tempfile
    import shutil
    
    import subprocess
    import matplotlib.pyplot as plt
    import matplotlib.image
    img = matplotlib.image.imread('no_grid_c_obs.png')
    num_steps = 50
    tmp_dir = tempfile.mkdtemp()
    problem = ImageProblem(img, seed=10)
    viz = PRMImageViz(problem, save_steps=range(num_steps),
                      interactive=False, show_text=False,
                      prefix="{}/prm".format(tmp_dir),
                      figsize=(2.25,2.25), file_type='png', dpi=100)
    
    graph = prm(problem, 130., num_steps, False, viz)
    subprocess.call(["convert", "-loop", "0", "-delay", "75",
                     "{}/*.png".format(tmp_dir), file_name])
    shutil.rmtree(tmp_dir)
    
    
    
def image_fig_prm():
    import matplotlib.pyplot as plt
    import matplotlib.image
    img = matplotlib.image.imread('no_grid_c_obs.png')
    problem = ImageProblem(img, seed=206)
    viz = PRMImageViz(problem, save_steps=[8,9], interactive=False,
                      prefix="prm", figsize=(2.25,2.25))
    
    graph = prm(problem, 155., 15, False, viz)
    

def run_image_prm():
    import matplotlib.pyplot as plt
    import matplotlib.image

    img = matplotlib.image.imread('no_grid_c_obs.png')

    for i in range(20, 2000, 20):
        plt.clf()
        problem = ImageProblem(img, seed=10)
        graph = prm(problem, 60., i, False)
        #write_edges(graph, "dat/prm_edges{}.dat".format(i))
                                
        plt.imshow(img)
        plot_graph(graph, linewidth=None, markersize=None)
        plt.axis('image')
        plt.axis('off')
        plt.show()
    
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--figs", help="generate figures",
                        action="store_true")
    args = parser.parse_args()
    if args.figs:
        make_gif('prm.gif')
        image_fig_prm()
    else:
        run_image_prm()
    

