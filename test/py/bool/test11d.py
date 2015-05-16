

""" Visualization of indices of the boundary triangulation """
import numpy
numpy.random.seed(0)

import sys
sys.path.insert(0, 'lib/py/')
from bool import *

V,[VV,EV,FV,CV] = larCuboids([2,2,1],True)
cubeGrid = Struct([(V,FV,EV)],"cubeGrid")
cubeGrids = Struct(2*[cubeGrid,t(0,0,0)])

V,FV,EV = struct2lar(cubeGrids)
VIEW(EXPLODE(1.2,1.2,1.2)(MKPOLS((V,FV))))
V,CV,FV,EV,CF,CE,COE,FE = partition(V,FV,EV)

cellLengths = AA(len)(CF)
boundaryPosition = cellLengths.index(max(cellLengths))
BF = CF[boundaryPosition]; del CF[boundaryPosition]; del CE[boundaryPosition]
BE = list({e for f in BF for e in FE[f]})

VIEW(EXPLODE(1.5,1.5,1.5)( MKTRIANGLES(V,[FV[f] for f in BF],[EV[e] for e in BE]) ))
VIEW(EXPLODE(2,2,2)([ MKSOLID(V,[FV[f] for f in cell],[EV[e] for e in set(CAT([FE[f] for f in cell]))]) for cell in CF]))
VIEW(EXPLODE(1.5,1.5,1.5)([STRUCT(MKPOLS((V,[EV[e] for e in cell]))) for cell in CE]))
