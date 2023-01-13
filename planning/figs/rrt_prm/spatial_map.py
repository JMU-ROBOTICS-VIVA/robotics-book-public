import numpy as np


class SpatialMap(object):
    """The SpatialMap class supports map functionality with lookup based
    on nearest neighbor searches.  Lookups are brute force, but based
    on vectorized numpy operations.  Reasonbly fast for smallish
    collections.

    """

    def __init__(self, dim=2, dist_metric=None):
        """
        Build an initially empty spatial map.

        Arguments:
           dim - dimensionality of the keys
           dist_metric - this must be a python function that takes
                         two arguments: the first is a n x dim numpy array
                         and the second is a length dim numpy array. It should
                         return a length n numpy array of distances. Default is
                         scaled Euclidian distance.

        """
        self.xs = np.empty((2, dim))
        self.xs[:, :] = float('inf')
        self.item_dict = {} # allows fast lookup for exact matches.
        self.values = [None for _ in range(2)]
        self.num_values = 0
        if not dist_metric:
            self.dist_metric = lambda xs, y: np.sqrt(np.sum((xs -
                                                             y)**2, axis=1))
        else:
            self.dist_metric = dist_metric

    def add(self, pos, value):
        """Add a new value with pos as the spatial key. 
        Return False and do not add if the key is already in the tree"""

        if tuple(pos) in self.item_dict:
            return False
        else:
            
            if self.num_values == self.xs.shape[0]:
                new_xs = np.empty((self.xs.shape[0] * 2, self.xs.shape[1]))
                new_xs[:, :] = float('inf')
                new_xs[0:self.num_values, :] = self.xs
                self.xs = new_xs
                new_values = [None for _ in range(len(self.values) * 2)]
                new_values[0:self.num_values] = self.values[:]
                self.values = new_values

            self.xs[self.num_values, :] = pos
            self.values[self.num_values] = value
            self.item_dict[tuple(pos)] = value
            self.num_values += 1
            return True

    def within_delta_items(self, pos, delta):
        """ Return the (key, value) tuples within delta of pos. """
        result = []
        dists = self.dist_metric(self.xs, pos)
        indices = np.argsort(dists)
        for i in indices:
            if dists[i] < delta:
                result.append((self.xs[i,:], self.values[i]))
            else:
                break

        return result

    
    def within_delta(self, pos, delta):
        """ Return the (key, value) tuples within delta of pos. """
        return [item[1] for item in self.within_delta_items(pos, delta)]
        
    def nearest(self, pos):
        """ Return the value with the key closest to pos. """
        return self.nearest_item(pos)[1]

    def nearest_item(self, pos):
        """ Return the (key, value) tuple with the key closest to pos. """

        dists = self.dist_metric(self.xs, pos)
        min_index = np.argmin(dists)
        return (self.xs[min_index, :], self.values[min_index])

    def get_value(self, pos):
        """ Exact non-nearest neighbor lookup """
        if tuple(pos) in self.item_dict:
            return self.item_dict[tuple(pos)]
        else:
            return None

    def __iter__(self):
        """ Iterator over the stored values. """
        for i in range(self.num_values):
            yield self.values[i]
            
