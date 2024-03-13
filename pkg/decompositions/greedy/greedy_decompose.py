from pkg.Py2D.py2d.Math import Polygon

from shapely.geometry import Polygon as ShapelyPolygon

import trimesh
from trimesh.creation import extrude_polygon
from trimesh.path import polygons as trimesh_polygons
import coacd

import numpy as np

coacd.set_log_level("error")

def decompose(P):
    """
    Greedy decomposition of a polygon with holes based on works of Author[ ]
    :param P: Polygon in a standard form [ext, [inters]]
    :return cvx_set: Set of convex polygons
    """

    ext, holes = P

    # convert to shapely polygon
    poly = ShapelyPolygon(ext, holes)

    mesh = extrude_polygon(poly, 0.1)
    mesh = coacd.Mesh(mesh.vertices, mesh.faces)
    parts = coacd.run_coacd(mesh, threshold=0.01) # a list of convex hulls.

    convex_polys = []
    for vs, fs in parts:
        mesh_part = trimesh.Trimesh(vs, fs)
        polygon = trimesh_polygons.projected(mesh_part, [0, 0, 1])
        convex_polys.append(polygon)

    ##
    # # plot the convex decomposition in matplotlib
    # from matplotlib import pyplot as plt
    # for p in convex_polys:
    #     plt.fill(*p.exterior.xy, alpha=0.5)
    # plt.show()
        

    # ## NOTE: This only works for convex holes!!!!
    # polygons = Polygon.convex_decompose(poly_ext, poly_holes)

    decomposition = [[[*poly.exterior.coords], []] for poly in convex_polys]

    if not decomposition:
        # print "ERROR! Decomposition resulted in empty list"
        raise SyntaxError

    return decomposition
