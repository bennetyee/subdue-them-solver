#!/usr/bin/python3

import heapq

def bounded_gen(num_elts, gen):
    q = []
    for e in gen:
        if len(q) >= num_elts:
            elt = heapq.heappop(q)
            yield elt
        heapq.heappush(q, e)
    while len(q) > 0:
        elt = heapq.heappop(q)
        yield elt
