""" Orienting a set of non-intersecting cycles """
from larlib import *

sys.path.insert(0, 'test/py/inters/')
from test17 import *

cells,bridgeEdges = connectTheDots((V,EV))
CVs = orientBoundaryCycles((V,EV),cells)

print "\nCVs =",CVs