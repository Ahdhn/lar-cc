from larlib import *
from meshpy.tet import MeshInfo, build, Options

V = [[0.25, 0.25, 0.0], [0.25, 0.75, 0.0], [0.75, 0.75, 0.0], [0.75, 0.25, 0.0], [1.0, 
0.0, 0.0], [0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.25, 0.25, 1.0], [0.25, 
0.25, 2.0], [0.25, 0.75, 2.0], [0.25, 0.75, 1.0], [0.25, 0.75, -1.0], [0.25, 0.25, 
-1.0], [0.75, 0.75, -1.0], [0.75, 0.25, -1.0], [0.75, 0.25, 1.0], [0.75, 0.75, 1.0], 
[1.0, 0.0, 1.0], [0.0, 0.0, 1.0], [1.0, 1.0, 1.0], [0.0, 1.0, 1.0], [0.75, 0.75, 2.0], 
[0.75, 0.25, 2.0]]

CV = [(0,1,2,3,4,5,6,7,8,11,16,17,18,19,20,21), (0,1,2,3,8,11,16,17),
(0,1,2,3,12,13,14,15), (8,9,10,11,16,17,22,23)]

FV = [(2,3,16,17),(6,7,20,21),(12,13,14,15),(0,1,8,11),(1,2,11,17),(0,1,12,13),
(4,6,18,20),(5,7,19,21),(0,3,13,15),(0,3,8,16),(0,1,2,3),(10,11,17,22),(2,3,14,
15),(8,9,16,23),(8,11,16,17),(1,2,12,14),(16,17,22,23),(4,5,18,19),(8,9,10,11),(
9,10,22,23),(0,1,2,3,4,5,6,7),(8, 11,16,17,18,19,20,21)]

EV =[(3,15),(7,21),(10,11),(4,18),(12,13),(5,19),(8,9),(18,19),(22,23),(0,3),(1,11),
(16,17),(0,8),(6,7),(20,21),(3,16),(10,22),(18,20),(19,21),(1,2),(12,14),(4,5),(
8,11),(13,15),(16,23),(14,15),(11,17),(17,22),(2,14),(2,17),(0,1),(9,10),(8,16),
(4,6),(1,12),(5,7),(0,13),( 9,23),(6,20),(2,3)]

VV = AA(LIST)(range(len(V)))
hpc = STRUCT(MKPOLS((V,EV)))
VIEW(larModelNumbering(1,1,1)(V,[CV,FV],hpc,1))


VIEW(EXPLODE(1.2,1.2,1.2)(MKPOLS((V,FV+EV))+AA(MK)(V)))
VIEW(EXPLODE(1.2,1.2,1.2)(AA(SKEL_1)(MKPOLS((V,CV)))))

FE = crossRelation(V,FV,EV)
cycles = []
for k,face in enumerate(FV):
    vcycles,_ = makeCycles((V,[EV[e] for e in FE[k]]))
    cycles += [[vcycle for k,vcycle in enumerate(vcycles) if k%2==0]]
    
cycles = [[[16, 17, 2, 3]],   # removed dups ...
 [[20, 21, 7, 6]],
 [[14, 15, 13, 12]],
 [[8, 11, 1, 0]],
 [[11, 17, 2, 1]],
 [[12, 13, 0, 1]],
 [[18, 20, 6, 4]],
 [[19, 21, 7, 5]],
 [[13, 15, 3, 0]],
 [[8, 16, 3, 0]],
 [[17, 22, 10, 11]],
 [[14, 15, 3, 2]],
 [[16, 23, 9, 8]],
 [[12, 14, 2, 1]],
 [[22, 23, 16, 17]],
 [[18, 19, 5, 4]],
 [[10, 11, 8, 9]],
 [[22, 23, 9, 10]],
 [[6, 7, 5, 4], [2, 3, 0, 1]],
 [[20, 21, 19, 18], [16, 17, 11, 8]]]

    
VIEW(EXPLODE(1.2,1.2,1.2)(AA(POLYLINE)([[V[v] for v in cycle]+[V[cycle[0]]] 
     for cycle in CAT(cycles)])))

def faces(tet):
	v1,v2,v3,v4 = tet
	return AA(sorted)([(v1,v2,v3),(v2,v3,v4),(v3,v4,v1),(v4,v1,v2)])

def edges(tria):
	v1,v2,v3 = tria
	return AA(sorted)([(v1,v2),(v1,v3),(v2,v3)])

def brep2lar(model):
    V,FV,EV = model    
    FE = crossRelation(V,FV,EV)
    mesh_info = MeshInfo()
    mesh_info.set_points(V)
    mesh_info.set_facets_ex(cycles)
    mesh = build(mesh_info,options=Options("pqYY"))
    W = [v for h,v in enumerate(mesh.points)]
    CW = [tet for k,tet in enumerate(mesh.elements)]
    FW = sorted(set(AA(tuple)(CAT(AA(faces)(CW)))))
    EW = sorted(set(AA(tuple)(CAT(AA(edges)(FW)))))
    return W,CW,FW,EW

W,CW,FW,EW = brep2lar((V,FV,EV))  

WW = AA(LIST)(range(len(W)))
hpc = STRUCT(MKPOLS((W,EV)))
VIEW(larModelNumbering(1,1,1)(W,[WW,CW],hpc,0.2))
VIEW(larModelNumbering(1,1,1)(W,[WW,CW,FW,EW],hpc,0.2))



print boundary(CV,FV).todense()

CF = crossRelation1(len(V),CV,FV)

CF = [[21, 1, 7, 17, 6, 0, 4, 20, 9, 3],    # with corrections
 [14, 0, 4, 10, 9, 3],
 [2, 12, 15, 10, 8, 5],
 [16, 11, 19, 14, 18, 13]]

FT, TV, CT = ??

estendere le facce con i triangoli interni
EW = extendEV(EV,ET,TV)



