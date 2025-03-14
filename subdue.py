#!/usr/bin/python3

import argparse
import sys
from functools import reduce

import bounded_pq

vals = [94, 86_000_000, 220_000_000, 17, 2_200, 52_000, 10_000_000, 8, 9_700_000, 980_000_000]
vals.sort()

options = None

def pretty_list(l):
    return '[' + ', '.join(f'{v:_d}' for v in l) + ']'

def all_subsets_recursive(l):
    if len(l) == 0:
        yield []
    else:
        first = l[0]
        rest = l[1:]
        for s in all_subsets(rest):
            yield s
            yield [first] + s

def all_non_empty_subsets_recursive(l):
    for s in all_subsets_recursive(l):
        if s != []:
            yield s

def all_non_empty_subsets_counter(l):
    nelts = len(l)
    for mask in range(1, 2**nelts):
        ss = []
        bit = 0
        while mask != 0:
            if (mask & 1) != 0:
                ss.append(l[bit])
            mask = mask // 2
            bit = bit + 1
        yield ss

def all_non_empty_subsets(l):
    yield from all_non_empty_subsets_counter(l)

def power_up_tuple(s):
    return (reduce(lambda x,y: x*y, s), s)

def fmt_add(v):
    return f'+{v:_d}'

def fmt_op(v):
    return f'x{v:_d}'

class State:
    def __init__(self, t, v, o, s):
        # immutable
        self.t = t
        self.vals = v
        self.ops = o
        self.seq = s

    def greedy(self):
        t = self.t
        ix = 0
        s = self.seq[:]
        while ix < len(self.vals) and t > self.vals[ix]:
            t = t + self.vals[ix]
            s.append(fmt_add(self.vals[ix]))
            ix = ix + 1
        return State(t, self.vals[ix:], self.ops, s)

    def done(self):
        return len(self.vals) == 0

def pretty_state(st):
    return f'''
truck:    {st.t}
weights:  {pretty_list(st.vals)}
powerups: {pretty_list(st.ops)}
'''

def search(st, succ, fn):
    st = st.greedy()
    if st.done():
        return succ(st.seq)
    if fn is not None:
        fn()

    if options.verbose > 1:
        print(f'state: {pretty_state(st)}')

    min_ratio = st.vals[0] / st.t
    g = filter(lambda pus: pus[0] > min_ratio,
               [power_up_tuple(ss) for ss in all_non_empty_subsets(st.ops)])
    if options.pq > 1:
        g = bounded_pq.bounded_gen(options.pq, g)
    for pus in g:
        if options.verbose > 2:
            print(f'powerup set: {pus[1]}')
        t = st.t * pus[0]
        nops = st.ops[:]
        nseq = st.seq[:]
        for o in pus[1]:
            nops.remove(o)
            nseq.append(fmt_op(o))
        nst = State(t, st.vals, nops, nseq)
        if not search(nst, succ, fn):
            return False
    return True  # keep going

class Count:
    def __init__(self):
        self.n = 0
    def __call__(self):
        self.n = self.n + 1
    def val(self):
        return self.n

class SuccessAccummulator:
    def __init__(self):
        self.successes = []
    def __call__(self, succ):
        self.successes.append(' '.join(succ))
        return options.all

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count',
                        default=0,
                        help='increment the verbosity level by 1')
    parser.add_argument('--weights', '-w', nargs='+', type=int,
                        default=vals,
                        help='list of animal weights')
    parser.add_argument('--powerups', '-p', nargs='+', type=int,
                        default=list(range(2,11)),
                        help='list of powerups')
    parser.add_argument('--pq', type=int, default=511,
                        help='max priority queue for powerup sets (< 1 means no priority queue used)')
    parser.add_argument('--all', action=argparse.BooleanOptionalAction,
                        default=False,
                        help='generate all solutions instead of just the first found')
    # There are 9 powerups, so 2**9-1 possible non-empty subsets, and
    # using 511 means we fully sort.

    global options
    options = parser.parse_args(argv[1:])

    options.weights.sort()
    options.powerups.sort()
    if options.verbose:
        print(f'weights: {pretty_list(options.weights)}')
        print(f'powerups: {pretty_list(options.powerups)}')

    st = State(2, options.weights, options.powerups, list())
    acc = SuccessAccummulator()
    c = Count()

    search(st, acc, c)
    if len(acc.successes) == 0:
        print('No solutions found.')
    else:
        print('solution(s) found:')
        for ix,s in enumerate(acc.successes):
            print(f'{ix:3d}: {s}')

    print(f'{c.val()} positions explored')

if __name__ == '__main__':
    main(sys.argv)
