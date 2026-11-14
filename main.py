# tiny-chess-01 (MIT): 4 KB chess engine; rank-flip board, alpha-beta+quiescence.
import json,os,urllib.request
V=[0,100,320,330,500,900,0]
PS=["KKKKbb__XXXZPPSXNNPUNKNPNNNDKKKK"]
D8=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
ND=[(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
MATE=100000;FL=bytes(i+16 if 0<i<7 else i-16 if 16<i<23 else i for i in range(256))
B=bytes(64);C=0;N=0;FLIP=0
CM={0:13,7:14,4:12,56:7,63:11,60:3}.get
class TO(Exception):pass
def fl(b):return b"".join(b[i:i+8]for i in range(56,-1,-8)).translate(FL)
def ray(s,dr,df,n=7):
 r,f=divmod(s,8);r+=dr;f+=df
 while 0<=r<8 and 0<=f<8 and n:
  yield r*8+f;r+=dr;f+=df;n-=1
def atk(sq):
 f=sq&7
 if(sq<55 and f<7 and B[sq+9]==17)or(sq<57 and f>0 and B[sq+7]==17):return True
 for dr,df in ND:
  for t in ray(sq,dr,df,1):
   if B[t]==18:return True
 for dr,df in D8:
  for i,t in enumerate(ray(sq,dr,df)):
   p=B[t]
   if p:
    if p>16 and((p&15)in((3,5)if dr*df else(4,5))or(p==22 and i==0)):return True
    break
 return False
def pm(s,t):return[s|t<<6|w<<12 for w in(5,4,3,2)]
def gen(cap=False):
 ms=[];ap=ms.append
 for s,p in enumerate(B):
  if not 1<=p<=6:continue
  f=s&7
  if p==1:
   t1=s+8
   if not B[t1]:
    if t1>=56:ms+=pm(s,t1)
    elif not cap:
     ap(s|t1<<6)
     if s<16 and not B[s+16]:ap(s|(s+16)<<6)
   for dd,ok in((7,f>0),(9,f<7)):
    t2=s+dd
    if ok and t2<64:
     q=B[t2]
     if q>16:
      if t2>=56:ms+=pm(s,t2)
      else:ap(s|t2<<6)
  else:
   ds=ND if p==2 else D8[1::2]if p==3 else D8[::2]if p==4 else D8
   for dr,df in ds:
    for t2 in ray(s,dr,df,1 if p in(2,6)else 7):
     q=B[t2]
     if q:
      if q>16:ap(s|t2<<6)
      break
     if not cap:ap(s|t2<<6)
   if p==6 and not cap and s==4:
    for bit,tg,em,th in((1,6,(5,6),(4,5,6)),(2,2,(3,2,1),(4,3,2))):
     if C&bit and not any(B[x]for x in em)and not any(atk(x)for x in th):ap(4|tg<<6)
 return ms
def mk(m):
 global B,C
 f=m&63;t=(m>>6)&63;pr=(m>>12)&7
 p=B[f]
 st=B,C
 b=bytearray(B)
 b[f]=0
 b[t]=pr if pr else p
 if p==6 and abs(t-f)==2:
  rf,rt=(f+3,f+1)if t>f else(f-4,f-1)
  b[rt]=b[rf];b[rf]=0
 nc=C&CM(f,15)&CM(t,15)
 B=fl(bytes(b))
 C=((nc&3)<<2)|((nc>>2)&3)
 return st
def ev():
 s=0
 for sq,p in enumerate(B):
  if not p:continue
  t=p&15;v=V[t]
  if t==1:
   f=sq&7;r=sq>>3
   v+=(ord(PS[0][((7-r)if p<16 else r)*4+(f if f<4 else 7-f)])-75)*2
  s+=v if p<16 else-v
 return s
def se(d,a,b,ply):
 global B,C,N
 N+=1
 if N>=50000:raise TO
 ic=atk(B.index(6))
 if ic and d<=0:d=1
 ms=gen(d<=0)
 if any(B[(m>>6)&63]==22 for m in ms):return MATE-ply
 best=ev()if d<=0 else-MATE-1000
 if d<=0:
  if best>=b:return best
  a=max(a,best)
 ms.sort(key=lambda m:V[B[(m>>6)&63]&15]*32-(B[m&63]&15)+V[(m>>12)&7]*32,reverse=True)
 for m in ms:
  st=mk(m)
  try:s=-se(d-1,-b,-a,ply+1)
  finally:B,C=st
  if s>best:best=s
  if s>a:a=s
  if a>=b:break
 if not ms and d>0:return-MATE+ply if ic else 0
 return best
def set_fen(fen):
 global B,C,FLIP
 ps=fen.split()
 L=[0]*64;sq=56
 for c in ps[0]:
  if c=="/":sq-=16
  elif c.isdigit():sq+=int(c)
  else:L[sq]="pnbrqk".index(c.lower())+1+(0 if c.isupper()else 16);sq+=1
 B=bytes(L);C=0
 if len(ps)>2:C=sum(1<<i for i,c in enumerate("KQkq")if c in ps[2])
 FLIP=len(ps)>1 and ps[1]=="b"
 if FLIP:
  B=fl(B)
  C=((C&3)<<2)|((C>>2)&3)
def choose():
 global B,C,N
 ms=gen()
 best=ms[0]
 for d in range(1,25):
  N=0;a=-MATE-1000;cb=best
  try:
   for m in ms:
    st=mk(m)
    try:s=-se(d-1,-MATE-1000,-a,1)
    finally:B,C=st
    if s>a:a=s;cb=m
  except TO:break
  best=cb
  ms.remove(best);ms.insert(0,best)
 return best
U=os.environ["MAKEFUN_ENV_URL"]
def post(p,b):
 with urllib.request.urlopen(U+p,json.dumps(b).encode())as x:return json.load(x)
if __name__=="__main__":
 while True:
  g=post("/game",{})
  if g["status"]=="done":break
  while g["status"]=="your_move":
   set_fen(g["fen"])
   m=choose()
   f=m&63;t=(m>>6)&63
   if FLIP:f ^= 56;t ^= 56
   u=f"{chr(97+(f&7))}{(f>>3)+1}{chr(97+(t&7))}{(t>>3)+1}"
   if m>>12:u+="nbrq"[(m>>12)-2]
   g=post("/move",{"game":g["game"],"move":u})
