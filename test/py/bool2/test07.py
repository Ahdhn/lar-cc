""" 2D polygon triangulation """
import sys
sys.path.insert(0, 'lib/py/')
from inters import *
from support import PolygonTessellator,vertex

filename = "test/py/bool2/interior.svg"
lines = svg2lines(filename)    
V,FV,EV = larFromLines(lines)
VIEW(EXPLODE(1.2,1.2,1)(MKPOLS((V,FV[:-1]+EV)) + AA(MK)(V)))

pivotFace = [V[v] for v in FV[0]+[FV[0][0]]]
pol = PolygonTessellator()
vertices = [ vertex.Vertex( (x,y,0) ) for (x,y) in pivotFace  ]
verts = pol.tessellate(vertices)
ps = [list(v.point) for v in verts]
trias = [[ps[k],ps[k+1],ps[k+2],ps[k]] for k in range(0,len(ps),3)]
VIEW(STRUCT(AA(POLYLINE)(trias)))

def orientTriangle(pointTriple):
   v1 = array(pointTriple[1])-pointTriple[0]
   v2 = array(pointTriple[2])-pointTriple[0]
   if cross(v1,v2)[2] < 0: return REVERSE(pointTriple)
   else: return pointTriple

triangles = DISTR([AA(orientTriangle)(trias),[[0,1,2]]])
VIEW(STRUCT(CAT(AA(MKPOLS)(triangles))))
