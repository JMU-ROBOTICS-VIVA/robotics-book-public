import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms


def confidence_ellipse(mean, cov, ax=None, n_std=3.0, facecolor='none', **kwargs):
    """

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """

    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)

    # Calculating the standard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = mean[0]

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = mean[1]

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    if ax is None:
        ax = plt.gca()
    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)

def confidence_contour(mean, cov, ax=None, stds=[.5, 1, 1.5], facecolor='none', **kwargs):
    patches = []
    for s in stds:
        patches.append(confidence_ellipse(mean, cov, ax, s, facecolor, **kwargs))
    return patches
        
    
if __name__ == "__main__":
    mean = [1.69462745, 1.49708176]
    cov = np.array([[0.09173554, 0.],
           [0.,         0.09173554 ]])
    

    ax = plt.gca()
    confidence_contour(mean, cov, ax=ax, edgecolor='black')
    plt.show()
