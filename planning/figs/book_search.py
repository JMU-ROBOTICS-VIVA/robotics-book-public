import tempfile
import shutil
import subprocess
import argparse
import six
import heapq
import math
import pygame

class Queue(list):

    def add(self, item):
        self.insert(0, item)

    def is_empty(self):
        return len(self) == 0

class Stack(list):

    def add(self, item):
        self.append(item)

    def is_empty(self):
        return len(self) == 0
    
# Borrowed from CS188 pacman project.
class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def _add(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def is_empty(self):
        return len(self.heap) == 0

    def add(self, item, priority):
        # If item already in priority queue with higher priority,
        # update its priority and rebuild the heap.  If item already
        # in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as
        # self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self._add(item, priority)

    def __iter__(self):
        return [item[2] for item in self.heap].__iter__()


class GridVisualizer:
    FRONTIER_COLOR = (0, 0, 255)
    OBSTACLE_COLOR = (0, 0, 0)
    EXPENSIVE_COLOR = (150, 150,150)
    CLOSED_COLOR = (200, 200, 200)
    SOLUTION_COLOR = (255, 0., 0.)
    START_COLOR = (0, 255, 0)
    GOAL_COLOR = (255, 178, 0.)

    def __init__(self, grid_problem, search_function,
                 grid_square_size=10, fill=False, save_prefix=None):
        self.problem = grid_problem
        self.search_function = search_function
        self.grid_square_size = grid_square_size
        self.fill=fill
        self.margin = 1
        window_size = (grid_problem.grid_width *
                       (self.grid_square_size + self.margin) + self.margin,
                       grid_problem.grid_height *
                       (self.grid_square_size + self.margin) + self.margin)
                       
        pygame.init()
        pygame.key.set_repeat(50)
        self.screen = pygame.display.set_mode(window_size)
        self.clock = pygame.time.Clock()
        self.done = False
        self.save_prefix = save_prefix
        self.count = 0
        
        if self.save_prefix:
            self.tmp_dir = tempfile.mkdtemp()

        while not self.done:
            self.draw()


    def draw_rect(self, row, column, color, border=0):
        pygame.draw.rect(self.screen,
                         color,
                         [(self.margin + self.grid_square_size) *
                          column + self.margin,
                          (self.margin + self.grid_square_size) *
                          (self.problem.grid_height - row -1) + self.margin,
                          self.grid_square_size,
                          self.grid_square_size], border)
        
    def draw_grid(self):
        self.screen.fill((0, 0, 0))
         
        for row in range(self.problem.grid_height):
            for column in range(self.problem.grid_width):
                if  self.problem.grid[row][column].cost == float('inf'):
                    color = self.OBSTACLE_COLOR
                elif  self.problem.grid[row][column].cost == 2.0:
                    color = self.EXPENSIVE_COLOR
                else:
                    color = (255, 255, 255)
                    
                self.draw_rect(row, column, color)


    def label_states(self, states, color):
        if states is not None:
            for state in states:
                row = state.row
                column = state.col
                if self.fill:
                    self.draw_rect(row, column, color, border=0)
                else:
                    self.draw_rect(row, column, color, border=self.margin*2)

    def draw(self, closed=None, frontier=None, solution=None, pause=False):

        for event in pygame.event.get():  # User did something

            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                column =  pos[0] // (self.grid_square_size + self.margin)
                row = pos[1] // (self.grid_square_size + self.margin)
                row = self.problem.grid_height - row
                if event.buttons[0] == 1:
                    self.problem.grid[row][column].cost = float('inf')

                if event.buttons[2] == 1:
                    self.problem.grid[row][column].cost = 2.0

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    self.search_function(self.problem, self)


        # DRAW STUFF
        self.draw_grid()
        self.label_states(closed, self.CLOSED_COLOR)
        if frontier is not None:
            self.label_states([node.state for node in frontier],
                              self.FRONTIER_COLOR)
        self.label_states(solution, self.SOLUTION_COLOR)
        self.label_states([self.problem.start()], self.START_COLOR)
        self.label_states([self.problem.goal()], self.GOAL_COLOR)
        pygame.display.flip()

        if self.save_prefix and closed:
            pygame.image.save(self.screen,
                              "{}/{}_{:04d}.png".format(self.tmp_dir,
                                                        self.save_prefix,
                                                        self.count))
            self.count += 1
            
        self.clock.tick(60)
        

        while pause and not self.done:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pause = False
            self.clock.tick(60)
                    

class AsymptoteVisualizer:
    FRONTIER_COLOR = (0, 0, 1)
    OBSTACLE_COLOR = (0., 0., 0.)
    CLOSED_COLOR = (.7, .7, .7)
    SOLUTION_COLOR = (1, 0, 0)
    START_COLOR = (0, 1, 0)
    GOAL_COLOR = (1, .7, 0)
    
    
    def __init__(self, grid_problem, base_file, which_iterations=None):
        self.step = 1
        self.problem = grid_problem
        self.base_file = base_file
        self.obstacle_states = []
        self.which_iterations = which_iterations
        for row in range(self.problem.grid_height):
            for column in range(self.problem.grid_width):
                if self.problem.grid[row][column].cost == float('inf'):
                    self.obstacle_states.append(self.problem.grid[row][column])
        

    def label_states(self, states, color, handle):
        if states is not None:
            for state in states:
                handle.write("{}, {}, {}, {}, {}\n".format(state.row, state.col,
                                                           color[0], color[1],
                                                           color[2]))


    def draw(self, closed=None, frontier=None, solution=None, pause=False):
        if (self.which_iterations is None or
            self.step in self.which_iterations or solution is not None):
            handle = open(self.base_file.format(self.step), 'w')
            handle.write("{}, {}\n".format(self.problem.grid_height,
                                           self.problem.grid_width))
            
            
            self.label_states(self.obstacle_states, self.OBSTACLE_COLOR,
                              handle)
            self.label_states(closed, self.CLOSED_COLOR, handle)
            if frontier is not None:
                self.label_states([node.state for node in frontier],
                                  self.FRONTIER_COLOR, handle)

            self.label_states(solution, self.SOLUTION_COLOR, handle)
            self.label_states([self.problem.start()], self.START_COLOR, handle)
            self.label_states([self.problem.goal()], self.GOAL_COLOR, handle)
            handle.close()
        self.step += 1
        
            
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
    

class GridState(object):
    def __init__(self, row, col, cost):
        """ cost is cost to enter """
        self.row = row
        self.col = col
        self.cost = cost

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
        
    def __repr__(self):
        return "({}, {}, {})".format(self.row, self.col, self.cost)

    def __hash__(self):
        return self.row * 10000 + self.col

    

class GridProblem(Problem):
    def __init__(self, grid_width, grid_height, start, goal, blocked_states=[]):
        """
        blocked_states - list of (row, col) tuples
        """
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.grid = [[GridState(y, x, 0.0) for x in range(grid_height)]
                     for y in range(grid_width)]
        for row, col in blocked_states:
            self.grid[row][col].cost = float('inf')

        start_row = int(start[0] * self.grid_height)
        start_col = int(start[1] * self.grid_width)
        goal_row = int(goal[0] * self.grid_height)
        goal_col = int(goal[1] * self.grid_width)
        self._start = self.grid[start_row][start_col]
        self._goal = self.grid[goal_row][goal_col]

    def start(self):
        return self._start

    def goal(self):
        return self._goal

    def successors(self, state):
        neighbors = []


        if state.row > 0 and state.col > 0:
            nbr = self.grid[state.row - 1][state.col-1]
            neighbors.append(nbr)
        if state.row < self.grid_height - 1 and state.col < self.grid_width - 1:
            nbr = self.grid[state.row + 1][state.col + 1]
            neighbors.append(nbr)
        if state.row < self.grid_height - 1 and state.col > 0:
            nbr = self.grid[state.row+1][state.col-1]
            neighbors.append(nbr)
        if state.row > 0 and state.col < self.grid_width - 1:
            nbr = self.grid[state.row-1][state.col+1]
            neighbors.append(nbr)
        
        if state.row < self.grid_height - 1:
            nbr = self.grid[state.row + 1][state.col]
            neighbors.append(nbr)
        if state.row > 0:
            nbr = self.grid[state.row - 1][state.col]
            neighbors.append(nbr)
        if state.col < self.grid_width - 1:
            nbr = self.grid[state.row][state.col+1]
            neighbors.append(nbr)
        if state.col > 0:
            nbr = self.grid[state.row][state.col-1]
            neighbors.append(nbr)



        successors = [nbr for nbr in neighbors if nbr.cost != float('inf')]
            
        return successors

    def _dist(self, state1, state2):
        return (math.sqrt((state1.row - state2.row)**2 +
                          (state1.col - state2.col)**2))
        
    
    def cost(self, state, next_state):
        return self._dist(state, next_state) + next_state.cost

    def heuristic(self, state):
        return self._dist(state, self._goal)



def generic_search_no_nodes(problem, Collection):
    """
    Input: problem - a problem instance that provides three methods:

              problem.start() -       returns the start state
              problem.goal()  -       returns the goal state
              problem.successors(s) - returns the states that are 
                                      reachable from s

    Returns: A list of states leading from problem.start() to 
             problem.goal(), or None if no path exists
    """
    
    frontier = Collection()
    closed = set()

    frontier.add(problem.start())    

    while not frontier.is_empty():
        cur_state = frontier.pop()

        closed.add(cur_state)

        if cur_state == problem.goal():
            return True
        
        else:
            for next_state in problem.successors(cur_state):
                if (next_state not in closed and
                        next_state not in frontier):
                    frontier.add(next_state)


class Node:
    def __init__(self, state, parent_node):
        self.state = state
        self.parent = parent_node

    def __eq__(self, rhs):
        if not isinstance(rhs, Node):
            return False
        else:
            return self.state == rhs.state

    def __ne__(self, rhs):
        return not self == rhs

    def __repr__(self):
        if self.parent is not None:
            return "({}, {})".format(self.state, 
                                         self.parent.state)
        else:
            return "({}, --)".format(self.state)

            
def construct_path(node):
    path = [node.state]
    cur_node = node.parent
    while cur_node is not None:
        path.append(cur_node.state)
        cur_node = cur_node.parent
    path.reverse()
    return path
                    
def generic_search_w_nodes(problem, Collection, vis=None):
    
    frontier = Collection()
    closed = set()

    frontier.add(Node(problem.start(), None))    

    while not frontier.is_empty():
        cur_node = frontier.pop()
        cur_state = cur_node.state
        closed.add(cur_state)

        if cur_state == problem.goal():
            path = construct_path(cur_node) # path ending at this node
            vis.draw(closed, frontier, path, True)
            return path
        
        else:
            for next_state in problem.successors(cur_state):
                next_node = Node(next_state, cur_node)
                if (next_state not in closed and
                        next_node not in frontier):
                    frontier.add(next_node)
            vis.draw(closed, frontier, None, False)



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

    def __repr__(self):
        if self.parent is not None:
            return "({}, {}, {})".format(self.state, 
                                         self.parent.state,
                                         self.path_cost)
        else:
            return "({}, --, {})".format(self.state, 
                                         self.path_cost)


def dijkstra_search(problem, vis=None):
    frontier = PriorityQueue()
    closed = set()

    start_node = CostNode(problem.start(), None, 0.0)
    frontier.add(start_node, 0)

    while not frontier.is_empty():
        cur_node = frontier.pop()
        cur_state = cur_node.state
        closed.add(cur_state)

        if cur_state == problem.goal():
            path =  construct_path(cur_node)
            print(cur_node.path_cost)
            vis.draw(closed, frontier, path, True)
            return construct_path(cur_node)
         
        else:
            successors = problem.successors(cur_state)
            for next_state in successors:
                cost = problem.cost(cur_state, next_state)
                next_node = CostNode(next_state, cur_node, cost)
                if next_state not in closed:
                    frontier.add(next_node, next_node.path_cost)
            vis.draw(closed, frontier, None, False)
    return None


def astar_search(problem, vis=None):
    frontier = PriorityQueue()
    closed = set()

    start_node = CostNode(problem.start(), None, 0.0)
    frontier.add(start_node, 0)

    while not frontier.is_empty():
        cur_node = frontier.pop()
        cur_state = cur_node.state
        closed.add(cur_state)

        if cur_state == problem.goal():
            path =  construct_path(cur_node)
            print(cur_node.path_cost)
            vis.draw(closed, frontier, path, True)
            return construct_path(cur_node)
         
        else:
            successors = problem.successors(cur_state)
            for next_state in successors:
                cost = problem.cost(cur_state, next_state)
                next_node = CostNode(next_state, cur_node, cost)
                if next_state not in closed:
                    f = next_node.path_cost + problem.heuristic(next_state)
                    frontier.add(next_node, f)
            vis.draw(closed, frontier, None, False)
    return None


def load_grid_problem(file_name):
    fh = open(file_name, 'r')
    lines = fh.readlines()
    rows = int(lines[0].split()[1])
    cols = int(lines[0].split()[3])
    blocked = []
    for line in lines[1::]:
        s = line.split()
        blocked.append((int(s[1]), int(s[0])))
    return GridProblem(cols, rows, (.3, .2), (.66, .75), blocked)

bfs = lambda prob, vis: generic_search_w_nodes(prob, Queue, vis)
dfs = lambda prob, vis: generic_search_w_nodes(prob, Stack, vis)

def create_gif(search_alg, file_name):
    p = load_grid_problem('filled_grid_cells.dat')
    v = GridVisualizer(p, search_alg, grid_square_size=5, fill=True,
                       save_prefix="tmp")
    print("Generating gif...")
    subprocess.call(["convert", "-loop", "1", "-delay", "4",
                     "{}/*.png".format(v.tmp_dir), file_name])
    print("done!")
    shutil.rmtree(v.tmp_dir)

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--figs", help="generate figures",
                        action="store_true")
    parser.add_argument("--gifs", help="generate gifs",
                        action="store_true")
    args = parser.parse_args()
    
    p = load_grid_problem('filled_grid_cells.dat')
 

    if args.figs:
        print("Generating .dat files to be processed by c_asy.asy")
        v = AsymptoteVisualizer(p, "dat/astar{:04d}.dat",
                                which_iterations=[1, 2, 13, 100, 350])
        astar_search(p, v)
        
        v = AsymptoteVisualizer(p, "dat/dijkstra{:04d}.dat",
                                which_iterations=[1, 2, 13, 100, 350])
        dijkstra_search(p, v)
        
        v = AsymptoteVisualizer(p, "dat/bfs{:04d}.dat",
                                which_iterations=[1, 2, 9, 81, 350])
        bfs(p, v)
        
        v = AsymptoteVisualizer(p, "dat/dfs{:04d}.dat",
                                which_iterations=[1, 2, 9, 81, 350])
        dfs(p, v)
    elif args.gifs:
        create_gif(dfs, 'dfs.gif')
        create_gif(bfs, 'bfs.gif')
        create_gif(astar_search, 'astar.gif')
        create_gif(dijkstra_search, 'dijkstra.gif')
        
    else:
        while True:
            which = six.moves.input("d: dfs, b: bfs, a: astar, j: dijkstra ")
            if which == 'd':
                GridVisualizer(p, dfs)
            elif which == 'b':
                GridVisualizer(p, bfs)
            elif which == 'a':
                GridVisualizer(p, astar_search)
            elif which == 'j':
                GridVisualizer(p, dijkstra_search)
    
if __name__ == "__main__":
    main()

