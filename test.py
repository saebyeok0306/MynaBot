import itertools


abc = list(itertools.permutations([3,4,5], 3))

print(abc)

[[3,4,5],[3,5,4],[4,3,5],[4,5,3],[5,3,4],[5,4,3]]