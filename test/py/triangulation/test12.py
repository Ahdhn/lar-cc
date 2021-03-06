""" Test example of LAR of a 2-complex with non-contractible and non-manifold cells"""
from larlib import *
sys.path.insert(0, 'test/py/triangulation/')
from test11 import *

model = V,FV,EV

faces = MKFACES(model)
colors = [CYAN,MAGENTA,WHITE,RED,YELLOW,GRAY,GREEN,ORANGE,BLUE,PURPLE,BROWN,BLACK]
components = [COLOR(colors[k%12])(faces[k]) for k in range(len(FV))]
VIEW(STRUCT(components))

VIEW(STRUCT(MKFACES((V,[FV[3]],EV))))
