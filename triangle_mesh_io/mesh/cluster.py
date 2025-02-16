import numpy as np
import sklearn.cluster
import scipy.spatial


def find_clusters(x, eps):
    return _find_clusters_dbscan(x=x, eps=eps)


def _find_clusters_cKDTree(x, eps):
    pass


def _find_clusters_dbscan(x, eps):
    """
    Returns the clusters found in the point cloud 'x'.

    Parameters
    ----------
    x : arraylike, floats
        A point cloud.
    eps : float
        points in 'x' closer than 'eps' will be considered part of the same
        cluster.
    """
    clustering = sklearn.cluster.DBSCAN(eps=eps).fit(x)

    NOISE = -1

    clusters = {}
    for x_i, cluster_i in enumerate(clustering.labels_):
        if cluster_i == NOISE:
            continue

        if cluster_i not in clusters:
            clusters[int(cluster_i)] = [int(x_i)]
        else:
            clusters[int(cluster_i)].append(int(x_i))

    for cluster_i in clusters:
        clusters[cluster_i] = sorted(clusters[cluster_i])

    return clusters


def find_replacement_map(x, clusters):
    """
    Returns a map indicating which point in 'x' is replaces by what other
    point in 'x'. This is to eliminate clusters of points. All points in a
    cluster will be replaced by a single point.
    """
    x = np.asarray(x)

    _temp_replacement_map = {}
    for cluster_i in clusters:
        first_vertx = clusters[cluster_i][0]
        _temp_replacement_map[first_vertx] = first_vertx
        for vertex in clusters[cluster_i][1:]:
            _temp_replacement_map[vertex] = first_vertx

    replacement_map = -1 * np.ones(shape=x.shape[0], dtype=int)
    for x_i in range(x.shape[0]):
        if x_i in _temp_replacement_map:
            replacement_map[x_i] = _temp_replacement_map[x_i]
        else:
            replacement_map[x_i] = x_i

    return replacement_map


def guess_68_percent_containment_width_1d(x):
    """
    A rather robust estimator for 68% containment width in 'x'.
    Unlike std() it ignores outliers by estiamting quantiles.
    """
    return np.quantile(x, 0.84) - np.quantile(x, 0.16)


def guess_68_percent_containment_width_3d(xyz):
    """
    A rather robust estimator for the one dimensional 68% containment width
    of a three dimensional point cloud 'xyz'.
    """
    dx = guess_68_percent_containment_width_1d(xyz[:, 0])
    dy = guess_68_percent_containment_width_1d(xyz[:, 1])
    dz = guess_68_percent_containment_width_1d(xyz[:, 2])
    return np.median([dx, dy, dz])
