from math import radians,sin,cos,asin,sqrt
R=6371.0088
def h(a,b,c,d):
    p1,p2=radians(a),radians(c);dp=p2-p1;dl=radians(d-b)
    x=sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*R*asin(sqrt(x)),x
S=(39.65472222,66.97583333)
for n,p in [("Berlin",(52.52,13.405)),("Brest",(52.13472222,23.65694444))]:
    print(n,h(*p,*S))
