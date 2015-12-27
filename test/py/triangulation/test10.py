""" Test example of LAR of a 2-complex with non-contractible and non-manifold cells"""
from larlib import *
sys.path.insert(0, 'test/py/triangulation/')
from test09 import *

model = V,FV,EV

faces = MKFACES(model)
colors = [CYAN,MAGENTA,WHITE,RED,YELLOW,GRAY,GREEN,ORANGE,BLUE,PURPLE,BROWN,BLACK]
n = len(FV)
components = [COLOR(colors[k%n])(faces[k]) for k in range(len(FV))]
VIEW(STRUCT(components))