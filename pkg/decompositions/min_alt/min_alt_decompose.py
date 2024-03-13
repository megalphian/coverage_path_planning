from shapely.geometry import LineString
from shapely.geometry import LinearRing
from math import sqrt
import operator
import itertools


def get_first_shared_edge(v, adj):

    for i in range(len(adj)):
        for j in range(i, len(adj)):

            if not adj[i][j] is None:
                if v[1] in adj[i][j]:
                    return (i, j, adj[i][j])
    return []


def combine_polygons_from_decomposition(v, decomposition):

    # Build a set of all shared edges in the decomposition which shared v
    new_decomposition = decomposition
    adj = adjacency.get_adjacency_as_matrix(new_decomposition)
    shared_edge_tuple = get_first_shared_edge(v, adj)
    # print adj
#	print("Shared edge tuple: %s"%(shared_edge_tuple,))

    while shared_edge_tuple:
        p1_id, p2_id, test_edge = shared_edge_tuple
#		print("Two adjacent ps: %d, %d"%(p1_id, p2_id))
#		# Get the exterior of the polygon since this is what will be combined
        P1 = new_decomposition[p1_id][0]
        P2 = new_decomposition[p2_id][0]

        # Combine the two into one polygon
        P = operations.combine_two_adjacent_polys(P1, P2, test_edge)
#		print("Combined chain: %s"%(P,))
        # Remove P1 and P2 from decomposition set
        if p1_id > p2_id:
            new_decomposition.pop(p1_id)
            new_decomposition.pop(p2_id)
        else:
            new_decomposition.pop(p2_id)
            new_decomposition.pop(p1_id)
#		print("Popoed decomp: %s"%(new_decomposition,))
        # Insert the new polygon in the decomposition, assuming no new holes
        new_decomposition.append([P, []])
        adj = adjacency.get_adjacency_as_matrix(new_decomposition)
#		print("Adj: %s"%(adj,))
#		print("Decomp after pop+add: %s"%(new_decomposition,))
        shared_edge_tuple = get_first_shared_edge(v, adj)

    return new_decomposition


def get_polygon_containing_point(decomposition, v):
    """
    """

    for i in range(len(decomposition)):

        chain = decomposition[i][0]

        if v[1] in chain:
            return decomposition[i], i


def update_v_id(P, v):

    for i in range(len(P[0])):
        if v[1] == P[0][i]:
            return (i, v[1])


def round_vertecies(p):
    new_p = []
    for v in p:
        new_p.append((round(v[0], 5), round(v[1], 5)))
    return new_p


def euc_distance(p1, p2):
    return sqrt((p2[1]-p1[1])**2+(p2[0]-p1[0])**2)


def post_processs_decomposition(decomp):

    for a in range(len(decomp)):
        for b in range(a+1, len(decomp)):

            p1 = decomp[a][0]  # ext only
            p2 = decomp[b][0]  # ext only

            p1_new = p1
            p2_new = p2

            n1 = len(p1)
            n2 = len(p2)

            # Test every pair of edges from both polygons to see equality
            for i in range(n1):
                edge1 = [p1[i]]+[p1[(i+1) % n1]]

                for j in range(n2):
                    edge2 = [p2[j]]+[p2[(j+1) % n2]]

                    #print("Edge1: %s Edge2: %s"%(edge1, edge2))
                    has_overlap, coords = edges.check_for_overlap(edge1, edge2)
                    if has_overlap:

                        # Consider each edge separately.
                        if euc_distance(edge1[0], coords[0]) < euc_distance(edge1[0], coords[1]):
                            if euc_distance(edge1[0], coords[0]) > 0.001:
                                new_edge1 = [edge1[0]]+[coords[0]]
                            else:
                                new_edge1 = [edge1[0]]

                            if euc_distance(edge1[1], coords[1]) > 0.001:
                                new_edge1 = new_edge1+[coords[1]]+[edge1[1]]
                            else:
                                new_edge1 = new_edge1 + [edge1[1]]
                        else:
                            if euc_distance(edge1[0], coords[1]) > 0.001:
                                new_edge1 = [edge1[0]]+[coords[1]]
                            else:
                                new_edge1 = [edge1[0]]

                            if euc_distance(edge1[1], coords[0]) > 0.001:
                                new_edge1 = new_edge1+[coords[0]]+[edge1[1]]
                            else:
                                new_edge1 = new_edge1 + [edge1[1]]

                        if euc_distance(edge2[0], coords[0]) < euc_distance(edge2[0], coords[1]):
                            if euc_distance(edge2[0], coords[0]) > 0.001:
                                new_edge2 = [edge2[0]]+[coords[0]]
                            else:
                                new_edge2 = [edge2[0]]

                            if euc_distance(edge2[1], coords[1]) > 0.001:
                                new_edge2 = new_edge2+[coords[1]]+[edge2[1]]
                            else:
                                new_edge2 = new_edge2 + [edge2[1]]
                        else:
                            if euc_distance(edge2[0], coords[1]) > 0.001:
                                new_edge2 = [edge2[0]]+[coords[1]]
                            else:
                                new_edge2 = [edge2[0]]

                            if euc_distance(edge2[1], coords[0]) > 0.001:
                                new_edge2 = new_edge2+[coords[0]]+[edge2[1]]
                            else:
                                new_edge2 = new_edge2 + [edge2[1]]

#						print("Nedge1: %s"%(new_edge1,))
#						print("Nedge2: %s"%(new_edge2,))
#
                        # Now insert new_edges to the polygon
                        if len(new_edge1) == 3:
                            p1_new.insert(i+1, new_edge1[1])
                        elif len(new_edge1) == 4:
                            p1_new.insert(i+1, new_edge1[1])
                            p1_new.insert(i+2, new_edge1[2])

                        if len(new_edge2) == 3:
                            p2_new.insert(j+1, new_edge2[1])
                        elif len(new_edge1) == 4:
                            p2_new.insert(j+1, new_edge2[1])
                            p2_new.insert(j+2, new_edge2[2])

#						print("Before Proces: %s"%(decomp[a],))
                        decomp[a] = [p1_new, []]
#						print("After Proces:  %s"%(decomp[a],))
                        decomp[b] = [p2_new, []]

    return decomp


def reoptimize(P, decomposition, adj):
    """
    Assuming running on convex decomposition
    """

    # Build a set of reflex verticies
    new_decomposition = decomposition
    R = reflex.find_reflex_vertices(P)

    while R:
        # Pick one reflex vertex from R
        v = R.pop()

#		print("Old decomp: %s"%(new_decomposition,))
#		print("V: %s"%(v,))
        # Combine all polygons in shared_edges to form one polygon
        new_decomposition = combine_polygons_from_decomposition(
            v, new_decomposition)
#		print("New decomp: %s"%(new_decomposition,))
        # v should belong to only one polygon at this point
        adj = adjacency.get_adjacency_as_matrix(new_decomposition)
        if get_first_shared_edge(v[1], adj):
            print("COMBINATION INCOMPLETE?")

        # Find the polygon containing v[1] and its altitude
        P, P_id = get_polygon_containing_point(new_decomposition, v)
#		print("Reflex containing P: %s, %d"%(P,P_id))
        altitude_P = alt.get_min_altitude(P)

        # Update v within P
        test_lr = LinearRing(P[0])
        if not test_lr.is_ccw:
            P[0] = P[0][::-1]
        v_new = update_v_id(P, v)

        # Find an optimal cut from v[1] within P
        cut = cuts.find_optimal_cut(P, v_new)
#		print("Proposed cut: %s"%(cut,))
        # Evaluate the potential optimal cut
        if cut and cut is not None:  # Not empty
            p_l, p_r = cuts.perform_cut(P, [v[1], cut[0]])

            p_l = round_vertecies(p_l)
            p_r = round_vertecies(p_r)
            # print p_l
            # print p_r
            altitude_pl = alt.get_min_altitude([p_l, []])
            altitude_pr = alt.get_min_altitude([p_r, []])

            # If cut improves altitude
            if altitude_pr+altitude_pl < altitude_P:

                decomposition.pop(P_id)
                decomposition.append([p_l, []])
                decomposition.append([p_r, []])

                # Need to process all polygons in the decomposition to introduce
                # 	aditional veritices where cuts were made
                decomposition = post_processs_decomposition(decomposition)
                # print decompsition
#		print("Decomp. after one reflex: %s"%(decomposition,))
    # print decomposition
    return decomposition


def decompose(P):
    """
    Min altitude decomposition.

    1: Connect all simple chains of a polygon
    2: Perform a series of decomposing cuts
    3: Run an iterative minimization step to reoptimize cuts

    :param P: Polygin in the standard form
    :return decomposition: A set of polygons
    """

    min_alt, theta = alt.get_min_altitude(P)
    #print("Min Alt: %2f, Theta: %2f"%(min_alt, 180*theta/3.14))
    P_fused, modified_edges = chain_combination.combine_chains(P, theta)

    #D = recursive_cuts(P_fused)
    recursive_cuts(P_fused)
    #print("List of polygons after recursion: %s"%(list_of_polygons,))

    # Need a smarter way of doing this
    # if len(D) == 2:
    #	if not D[1]:
    #		D = [D]

    return list_of_polygons


list_of_polygons = []


def recursive_cuts(P):
    """
    Recursive cut of Polygon
    """

    R = reflex.find_reflex_vertices(P)
    while R:
        v = R.pop()

        cut = cuts.find_optimal_cut(P, v)
        #print("Ref: %s"%(v[1],))
        #print("Cut: %s"%(cut,))

        if cut and cut is not None:  # Not empty
            p_l, p_r = cuts.perform_cut(P, [v[1], cut[0]])

            # return [recursive_cuts([p_l,[]]), recursive_cuts([p_r,[]])]
            recursive_cuts([p_l, []])
            recursive_cuts([p_r, []])
            return
    # return P
    list_of_polygons.append(P)


if __name__ == '__main__':
    if __package__ is None:
        import os
        import sys
        sys.path.insert(0, os.path.abspath("../.."))
        from aux.geometry import rotation
        import reflex
else:
    from ...aux.altitudes import altitude as alt
    from ...decompositions.min_alt import cuts
    from ...poly_operations.others import chain_combination
    from ...poly_operations.others import reflex
    from ...poly_operations.others import operations
    from pkg.decompositions import adjacency
    from pkg.decompositions import edges
