""" Module for pipelined intersection of geometric objects """
from larlib import *

""" Edge cycles associated to a closed chain of edges """

from collections import defaultdict

def detachManifolds(polygonVerts):
    vertCycles = []
    for vertexList in polygonVerts:
        vertCount,counts = defaultdict(list),list
        for v in vertexList: 
            vertCount[v] += [1]
        counts = [sum(vertCount[v]) for v in vertexList]
        vertCycles += [counts]
    return vertCycles
    
def splitManifolds(cycles,vertices,manifolds):
    out = []
    for cycle,verts,manifold in zip(cycles,vertices,manifolds):
        if sum(manifold) == len(manifold):
            out += [cycle] 
        else:
            transpositionNumbers = [n for n,k in enumerate(manifold) if k>1]
            n = transpositionNumbers[0]
            cycle = rotatePermutation(cycle,n) 
            verts = rotatePermutation(verts,n) 
            manifold = rotatePermutation(manifold,n) 
            starts = AA(C(sum)(-n))(transpositionNumbers)+[len(manifold)]
            pairs = [(start,starts[k+1]) for k,start in enumerate(starts[:-1])]
            splitCycles = [[cycle[k] for k in range(*interval)] for interval in pairs]
            splitVerts = [[verts[k] for k in range(*interval)] for interval in pairs]
            out += splitCycles
    return out

def boundaryCycles(edgeBoundary,EV):
    cycles,cycle = [],[]
    vertices = []
    
    def singleBoundaryCycle(edgeBoundary):
        verts2edges = defaultdict(list)
        for e in edgeBoundary:
            verts2edges[EV[e][0]] += [e]
            verts2edges[EV[e][1]] += [e]
        cycle,verts = [],[]
        
        if edgeBoundary == []: return cycle,verts
        e = edgeBoundary[0]
        v,w = EV[e]
        verts = [v,w]
        while edgeBoundary != []:
            cycle += [e]
            edgeBoundary.remove(e)
            v,w = EV[e]
            verts2edges[v].remove(e)
            verts2edges[w].remove(e)
            w = list(set(EV[e]).difference([verts[-1]]))[0]
            if verts2edges[w] == []: break
            e = verts2edges[w][0]
            verts += [w]
        verts = verts[1:]
        return cycle,verts
        
    while edgeBoundary != []:
        edgeBoundary = list(set(edgeBoundary).difference(cycle))
        cycle,verts = singleBoundaryCycle(edgeBoundary)
        if cycle!= []: 
            cycle = [e if verts[k]==EV[e][0] else -e for k,e in enumerate(cycle)]
            cycles += [cycle]
            vertices += [verts]
    manifolds = detachManifolds(vertices)
    cycles = splitManifolds(cycles,vertices,manifolds)
    return cycles,vertices

""" Point-in-polygon classification algorithm """
""" Half-line crossing test """
def crossingTest(new,old,count,status):
    if status == 0:
        status = new
        count += 0.5
    else:
        if status == old: count += 0.5
        else: count -= 0.5
        status = 0

""" Tile codes computation """
def setTile(box):
    tiles = [[9,1,5],[8,0,4],[10,2,6]]
    b1,b2,b3,b4 = box
    def tileCode(point):
        x,y = point
        code = 0
        if y>b1: code=code|1
        if y<b2: code=code|2
        if x>b3: code=code|4
        if x<b4: code=code|8
        return code 
    return tileCode

""" Point in polygon classification """
def pointInPolygonClassification(pol):

    V,EV = pol
    # edge orientation
    FV = [sorted(set(CAT(EV)))]
    orientedCycles = boundaryPolylines(Struct([(V,FV,EV)]))
    EV = []
    for cycle in orientedCycles:
        EV += zip(cycle[:-1],cycle[1:])

    def pointInPolygonClassification0(p):
        x,y = p
        xmin,xmax,ymin,ymax = x,x,y,y
        tilecode = setTile([ymax,ymin,xmax,xmin])
        count,status = 0,0
    
        for k,edge in enumerate(EV):
            p1,p2 = edge[0],edge[1]
            (x1,y1),(x2,y2) = p1,p2
            c1,c2 = tilecode(p1),tilecode(p2)
            c_edge, c_un, c_int = c1^c2, c1|c2, c1&c2
            
            if c_edge == 0 and c_un == 0: return "p_on"
            elif c_edge == 12 and c_un == c_edge: return "p_on"
            elif c_edge == 3:
                if c_int == 0: return "p_on"
                elif c_int == 4: count += 1
            elif c_edge == 15:
                x_int = ((y-y2)*(x1-x2)/(y1-y2))+x2 
                if x_int > x: count += 1
                elif x_int == x: return "p_on"
            elif c_edge == 13 and ((c1==4) or (c2==4)):
                    crossingTest(1,2,status,count)
            elif c_edge == 14 and (c1==4) or (c2==4):
                    crossingTest(2,1,status,count)
            elif c_edge == 7: count += 1
            elif c_edge == 11: count = count
            elif c_edge == 1:
                if c_int == 0: return "p_on"
                elif c_int == 4: crossingTest(1,2,status,count)
            elif c_edge == 2:
                if c_int == 0: return "p_on"
                elif c_int == 4: crossingTest(2,1,status,count)
            elif c_edge == 4 and c_un == c_edge: return "p_on"
            elif c_edge == 8 and c_un == c_edge: return "p_on"
            elif c_edge == 5:
                if (c1==0) or (c2==0): return "p_on"
                else: crossingTest(1,2,status,count)
            elif c_edge == 6:
                if (c1==0) or (c2==0): return "p_on"
                else: crossingTest(2,1,status,count)
            elif c_edge == 9 and ((c1==0) or (c2==0)): return "p_on"
            elif c_edge == 10 and ((c1==0) or (c2==0)): return "p_on"
        if ((round(count)%2)==1): return "p_in"
        else: return "p_out"
    return pointInPolygonClassification0


""" Classification of non intersecting cycles """
def internalTo(V,ev):
    classify = pointInPolygonClassification((V,ev))
    ve = invertRelation(ev)
    for v,edgeIndices in enumerate(ve):
        if len(edgeIndices) == 2: break
    v1,v2 = set(CAT([list(ev[e]) for e in edgeIndices])).symmetric_difference([v])
    vect1 = VECTDIFF([V[v1],V[v]])
    vect2 = VECTDIFF([V[v2],V[v]])
    point = VECTSUM([ V[v], SCALARVECTPROD([ 0.05, VECTSUM([vect1,vect2]) ])])
    if classify(point) == "p_out":
        point = VECTSUM([ V[v], SCALARVECTPROD([ -0.05, VECTSUM([vect1,vect2]) ])])
    return point
    
def computeCycleLattice(V,EVs):
    n = len(EVs)
    latticeArray = []
    interiorPoints = [internalTo(V,ev) for k,ev in enumerate(EVs)]
    for k,ev in enumerate(EVs):
        row = []
        classify = pointInPolygonClassification((V,ev))
        for h in range(n):
            i = EVs[h][0][0]
            #point = V[i]
            point = interiorPoints[h]
            test = classify(point)
            if h==k: row += [-1]
            elif test=="p_in": row += [1]
            elif test=="p_out": row += [0]
            elif test=="p_on": row += [-1]
            else: print "error: in cycle classification"
        latticeArray += [row]
    for k in range(n):
        for h in range(k+1,n): 
            if latticeArray[k][h] == latticeArray[h][k]:
                latticeArray[k][h] = 0
    return latticeArray

""" Extraction of path-connected boundaries """
def cellsFromCycles (latticeArray):
    print "\nlatticeArray =\n",latticeArray,"\n"
    n = len(latticeArray)
    sons = [[h]+[k for k in range(n) if row[k]==1] for h,row in enumerate(latticeArray)]
    level = [sum(col) for col in TRANS(latticeArray)]
    
    def rank(sons): return [level[x] for x in sons]
    preCells = sorted(sons,key=rank)

    def levelDifference(son,father): return level[son]-level[father]
    root = preCells[0][0]
    out = [[son for son in preCells[0] if (levelDifference(son,root)<=1) ]]
    for k in range(1,n):
        father = preCells[k][0]
        inout = [son for son in preCells[k] if levelDifference(son,father)<=1 ]
        if not (inout[0] in CAT(out)):
            out += [inout]
    return out        

""" Transforming to polar coordinates """
def cartesian2polar(V):    
    Z = [[sqrt(x*x + y*y),math.atan2(y,x)] for x,y in V]
    VIEW(STRUCT(MKPOLS((Z,EV))))
    return Z

""" Scan line algorithm """
def scan(V,FVs, group,cycleGroup,cycleVerts):
    bridgeEdges = []
    scannedCycles = []
    for k,(point,cycle,v) in enumerate(cycleGroup[:-2]):
      
        nextCycle = cycleGroup[k+1][1]
        n = len(FVs[group][cycle])
        if nextCycle != cycle: 
            if not ((nextCycle in scannedCycles) and (cycle in scannedCycles)):
                scannedCycles += [nextCycle]
                m = len(FVs[group][nextCycle])
                v1,v2 = v,cycleGroup[k+1][2]
                minDist = VECTNORM(VECTDIFF([V[v1],V[v2]]))
                for i in FVs[group][cycle]:
                    for j in FVs[group][nextCycle]:
                        dist = VECTNORM(VECTDIFF([V[i],V[j]]))
                        if  dist < minDist: 
                            minDist = dist
                            v1,v2 = i,j
                bridgeEdges += [(v1,v2)]
    return bridgeEdges[:-1]

""" Scan line algorithm input/output """
def connectTheDots(model):
    V,EV = model
    V,EVs = biconnectedComponent((V,EV))
    FV = AA(COMP([sorted,set,CAT]))(EVs)
    latticeArray = computeCycleLattice(V,EVs)
    cells = cellsFromCycles(latticeArray)
    FVs = [[FV[cycle] for cycle in cell] for cell in cells]
    
    indexedCycles = [zip(FVs[h],range(len(FVs[h])))   for h,cell in enumerate(cells)]
    indexedVerts = [CAT(AA(DISTR)(cell)) for cell in indexedCycles]
    sortedVerts = [sorted([(V[v],c,v) for v,c in cell]) for cell in indexedVerts]
    
    bridgeEdges = []
    cellIndices = range(len(cells))
    for (group,cycleGroup,cycleVerts) in zip(cellIndices,sortedVerts,indexedVerts):
        bridgeEdges += [scan(V,FVs, group,cycleGroup,cycleVerts)]
    return cells,bridgeEdges

""" Orientation of component cycles of unconnected boundaries """
def rotatePermutation(inputPermutation,transpositionNumber):
    n = transpositionNumber
    perm = inputPermutation
    permutation = range(n,len(perm))+range(n) 
    return [perm[k] for k in permutation]

def canonicalRotation(permutation):
    n = permutation.index(min(permutation))
    return rotatePermutation(permutation,n)

def setCounterClockwise(h,k,cycle,areas,CVs):
    if areas[cycle] < 0.0: 
        chain = copy.copy(CVs[h][k])
        CVs[h][k] = canonicalRotation(REVERSE(chain))

def setClockwise(h,k,cycle,areas,CVs):
    if areas[cycle] > 0.0: 
        chain = copy.copy(CVs[h][k])
        CVs[h][k] = canonicalRotation(REVERSE(chain))

def orientBoundaryCycles(model,cells):
    V,EV = model
    edgeBoundary = range(len(EV))
    edgeCycles,_ = boundaryCycles(edgeBoundary,EV)
    vertexCycles = [[ EV[e][1] if e>0 else EV[-e][0] for e in cycle ] for cycle in edgeCycles]
    rotations = [cycle.index(min(cycle)) for cycle in vertexCycles]
    theCycles = sorted([rotatePermutation(perm,n) for perm,n in zip(vertexCycles,rotations)])
    CVs = [[theCycles[cycle] for cycle in cell] for cell in cells]
    areas = signedSurfIntegration((V,theCycles,EV),signed=True)
    
    for h,cell in enumerate(cells):
        for k,cycle in enumerate(cell):
            if k == 0: setCounterClockwise(h,k,cycle,areas,CVs)
            else: setClockwise(h,k,cycle,areas,CVs)
    return CVs

""" From nested boundary cycles to triangulation """
def larTriangulation( (V,EV) ):
    model = V,EV
    cells,bridgeEdges = connectTheDots(model)
    CVs = orientBoundaryCycles(model,cells)
    
    polygons = [[[V[u] for u in cycle] for cycle in cell] for cell in CVs]
    triangleSet = []   
    
    for polygon in polygons:
        triangledPolygon = []
        externalCycle = polygon[0]
        polyline = []
        for p in externalCycle:
            polyline.append(Point(p[0],p[1]))
        cdt = CDT(polyline)
        
        internalCycles = polygon[1:]
        for cycle in internalCycles:
            hole = []
            for p in cycle:
                hole.append(Point(p[0],p[1]))
            cdt.add_hole(hole)
            
        triangles = cdt.triangulate()
        trias = [ [[t.a.x,t.a.y,0],[t.c.x,t.c.y,0],[t.b.x,t.b.y,0]] for t in triangles ]
        triangleSet += [AA(REVERSE)(trias)]
    return triangleSet

""" Generation of 1-boundaries as vertex permutation """
def boundaryCycles2vertexPermutation( model ):
    V,EV = model
    cells,bridgeEdges = connectTheDots(model)
    CVs = orientBoundaryCycles(model,cells)
    
    verts = CAT(CAT( CVs ))
    n = len(verts)
    W = copy.copy(V)
    #assert len(verts) == sorted(verts)[n-1]-sorted(verts)[0]+1
    nextVert = dict([(v,cycle[(k+1)%(len(cycle))]) for cell in CVs for cycle in cell 
                   for k,v in enumerate(cycle)])
    for k,(u,v) in enumerate(CAT(bridgeEdges)):
        x,y = nextVert[u],nextVert[v]
        nextVert[u] = n+2*k+1
        nextVert[v] = n+2*k      
        nextVert[n+2*k] = x
        nextVert[n+2*k+1] = y
        W += [W[u]]
        W += [W[v]]
        EW = nextVert.items()
    return W,EW

""" lar2boundaryPolygons """
def lar2boundaryPolygons(model):
    W,EW = boundaryCycles2vertexPermutation( model )
    EW = AA(list)(EW)
    polygons = []
    for k,edge in enumerate(EW):
        polygon = []
        if edge[0]>=0:
            first = edge[0]
            done = False
        while (not done) and edge[0] >= 0:
            polygon += [edge[0]]
            edge[0] = -edge[0]
            edge = EW[edge[1]]
            if len(polygon)>1 and polygon[-1] == first: 
                EW[first][0] = -float(first)
                break 
        if polygon != []: 
            if polygon[0]==polygon[-1]: polygon=polygon[:-1]
            polygons += [polygon]
    return W,polygons

""" From Struct object to LAR boundary model """
def structFilter(obj):
    if isinstance(obj,list):
        if (len(obj) > 1):
            return [structFilter(obj[0])] + structFilter(obj[1:])
        return [structFilter(obj[0])]
    if isinstance(obj,Struct):
        if obj.category in ["external_wall", "internal_wall", "corridor_wall"]:
            return
        return Struct(structFilter(obj.body),obj.name,obj.category)
    return obj

def structBoundaryModel(struct):
    filteredStruct = structFilter(struct)
    #import pdb; pdb.set_trace()
    V,FV,EV = struct2lar(filteredStruct)
    edgeBoundary = boundaryCells(FV,EV)
    cycles,_ = boundaryCycles(edgeBoundary,EV)
    edges = [signedEdge for cycle in cycles for signedEdge in cycle]
    orientedBoundary = [ AA(SIGN)(edges), AA(ABS)(edges)]
    cells = [EV[e] if sign==1 else REVERSE(EV[e]) for (sign,e) in zip(*orientedBoundary)]
    if cells[0][0]==cells[1][0]: # bug badly patched! ... TODO better
        temp0 = cells[0][0]
        temp1 = cells[0][1]
        cells[0] = [temp1, temp0]
    return V,cells

""" From structures to boundary polylines """
def boundaryPolylines(struct):
    V,boundaryEdges = structBoundaryModel(struct)
    if len(V) < len(boundaryEdges):
        EV = AA(sorted)(boundaryEdges)
        boundaryEdges = range(len(boundaryEdges))
        cycles,vertices = boundaryCycles(boundaryEdges,EV)
        polylines = [[V[v] for v in verts]+[V[verts[0]]] for verts in REVERSE(vertices)]
    else:
        polylines = boundaryModel2polylines((V,boundaryEdges))
    return polylines

""" From LAR oriented boundary model to polylines """
def boundaryModel2polylines(model):
    if len(model)==2: V,EV = model
    elif len(model)==3: V,FV,EV = model
    polylines = []
    succDict = dict(EV)
    visited = [False for k in range(len(V))]
    nonVisited = [k for k in succDict.keys() if not visited[k]]
    while nonVisited != []:
        first = nonVisited[0]; v = first; polyline = []
        while visited[v] == False:
            visited[v] = True; 
            polyline += V[v], 
            v = succDict[v]
        polyline += [V[first]]
        polylines += [polyline]
        nonVisited = [k for k in succDict.keys() if not visited[k]]
    return polylines

def boundaryModel2polylines(model):
    if len(model)==2: V,EV = model
    elif len(model)==3: V,FV,EV = model
    polylines = []
    succDict = dict(EV)
    visited = [False for k in range(len(V))]
    nonVisited = [k for k in succDict.keys() if not visited[k]]
    while nonVisited != []:
        first = nonVisited[0]; v = first; polyline = []
        while visited[v] == False:
            visited[v] = True; 
            polyline += V[v], 
            v = succDict[v]
        polyline += [V[first]]
        polylines += [polyline]
        nonVisited = [k for k in succDict.keys() if not visited[k]]
    return polylines

""" Computing a LAR 2-complex from an arrangement of line segments"""
def larPair2Triple(model):
    V,EV = model
    V,cycles,EV = facesFromComps((V,EV))
    areas = integr.surfIntegration((V,cycles,EV))
    orderedCycles = sorted([[area,cycles[f]] for f,area in enumerate(areas)])
    interiorCycles = [face for area,face in orderedCycles[:-1]]
    EdgeCyclesByVertices = [zip(cycle[:-1],cycle[1:])+[(cycle[-1],cycle[0])] 
                        for cycle in interiorCycles]
    latticeArray = computeCycleLattice(V,EdgeCyclesByVertices)
    cells = cellsFromCycles(latticeArray)
    FV = [list(set(CAT([interiorCycles[k] for k in cell]))) for cell in cells]
    return V,FV,EV

""" Visualization of a 2D complex and 2-chain """
def larComplexChain(model):
    V,FV,EV = model
    VV = AA(LIST)(range(len(V)))
    csrBoundaryMat = boundary1(FV,EV,VV)
    def larComplexChain0(chain):
        boundaryChain = chain2BoundaryChain(csrBoundaryMat)(chain)
        outModel = V,[EV[e] for e in boundaryChain]
        triangleSet = larTriangulation(outModel)
        return boundaryChain,triangleSet
    return larComplexChain0
    
def viewLarComplexChain(model):
    V,FV,EV = model
    operator = larComplexChain(model)
    def viewLarComplexChain0(chain):
        boundaryChain,triangleSet = operator(chain)
        hpcChain = AA(JOIN)(AA(AA(MK))(CAT(triangleSet)))
        hpcChainBoundary = AA(COLOR(RED))(MKPOLS((V,[EV[e] for e in boundaryChain])))
        VIEW(STRUCT( hpcChain + hpcChainBoundary ))
        VIEW(EXPLODE(1.2,1.2,1.2)( hpcChain + hpcChainBoundary ))
    return viewLarComplexChain0

""" Solid PyPLaSM visualization of a 2-complex with non-contractible 
      and non-manifold cells"""
def MKFACES(model):
    V,FV,EV = model
    bmatrix = boundary(FV,EV)
    boundaryOperator = chain2BoundaryChain(bmatrix)
    chain = [0]*len(FV)
    boundingEdges = []
    for k,face in enumerate(FV):
      unitChain = copy.copy(chain)
      unitChain[k] = 1
      boundingEdges += [boundaryOperator(unitChain)]
    faces = [SOLIDIFY(STRUCT([POLYLINE([V[v] for v in EV[e]]) for e in edges])) 
        for edges in boundingEdges]
    return faces
