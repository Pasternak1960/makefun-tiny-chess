import json,os,urllib.request
D=((16,-16,1,-1),(15,17,-15,-17))
J=(14,18,31,33,-14,-18,-31,-33)
V=(0,100,320,335,510,950,20000)
S=[i for i in range(128) if not i&136]
def sq(s):return ord(s[0])-97+16*(int(s[1])-1)
def gen(b,c,ep):
 for i in S:
  p=b[i]*c
  if p<=0:continue
  if p==1:
   d=16*c
   if not b[i+d]:
    yield i,i+d,5 if (i+d)//16 in (0,7) else 0
    if i//16==(1 if c==1 else 6) and not b[i+2*d]:yield i,i+2*d,0
   for j in (i+d-1,i+d+1):
    if not j&136 and (b[j]*c<0 or j==ep):yield i,j,5 if j//16 in (0,7) else 0
  else:
   ds=J if p==2 else D[1] if p==3 else D[0] if p==4 else D[0]+D[1]
   for d in ds:
    j=i+d
    while not j&136 and b[j]*c<=0:
     yield i,j,0
     if b[j] or p in (2,6):break
     j+=d
def attack(b,k,c):
 if any(not (k+d)&136 and b[k+d]==-2*c for d in J):return True
 for d in D[0]+D[1]:
  j=k+d
  while not j&136:
   p=b[j]*c
   if p:
    if p in (-5,-4 if d in D[0] else -3):return True
    if j==k+d and (p==-6 or p==-1 and d in (16*c-1,16*c+1)):return True
    break
   j+=d
 return False
def play(b,c,m):
 i,j,t=m;p=b[i];a=b[:];a[i]=0;a[j]=c*t if t else p
 if abs(p)==1 and (i^j)&15 and not b[j]:a[j-16*c]=0
 if abs(p)==6 and abs(i-j)==2:
  k=i+3 if j>i else i-4;a[(i+j)//2]=a[k];a[k]=0
 return a,(i+j)//2 if abs(p)==1 and abs(i-j)==32 else -1
def evaluate(b):
 score=0
 for i in S:
  p=b[i]
  if p:
   c=1 if p>0 else -1;p=abs(p);r=i//16;f=i%16
   advance=r if c==1 else 7-r
   central=14-abs(2*f-7)-abs(2*r-7)
   score+=c*(V[p]+(advance*9+central*2 if p==1 else central*(7 if p==2 else 4) if p in (2,3) else 0))
 return score
def search(b,c,ep,d,lo,hi,ply):
 k=b.index(6*c);check=attack(b,k,c)
 if d<=0:
  v=c*evaluate(b)
  if ply>=6:return v
  if not check:
   if v>=hi:return v
   lo=max(lo,v)
 moves=list(gen(b,c,ep))
 moves.sort(key=lambda m:16*V[abs(b[m[1]])]+900*m[2]-V[abs(b[m[0]])],reverse=True)
 anymove=False
 for m in moves:
  i,j,t=m
  if d<=0 and not check and not (b[j] or t or j==ep):continue
  a,e=play(b,c,m)
  if attack(a,j if b[i]==6*c else k,c):continue
  anymove=True
  v=-search(a,-c,e,d-1,-hi,-lo,ply+1)
  if v>=hi:return v
  lo=max(lo,v)
 if not anymove and (d>0 or check):return -30000+ply if check else 0
 return lo
def choose(fen,legal):
 rows,side,_,ep,*_=fen.split();b=[0]*128;c=1 if side=='w' else -1
 for r,row in enumerate(reversed(rows.split('/'))):
  i=16*r
  for p in row:
   if p.isdigit():i+=int(p)
   else:b[i]=' pnbrqk'.index(p.lower())*(1 if p.isupper() else -1);i+=1
 best=-32000;out=None
 for u in sorted(legal):
  a,e=play(b,c,(sq(u[:2]),sq(u[2:4]),' pnbrqk'.index(u[4]) if len(u)>4 else 0))
  v=-search(a,-c,e,2,-32000,-best,1)
  if v>best:best=v;out=u
 return out
def post(route,data):
 req=urllib.request.Request(os.environ['MAKEFUN_ENV_URL']+route,json.dumps(data).encode(),{'Content-Type':'application/json'})
 with urllib.request.urlopen(req) as response:return json.load(response)
if __name__=='__main__':
 while (g:=post('/game',{}))['status']!='done':
  while g['status']=='your_move':
   g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
  print(g['outcome'],g['reason'],flush=True)
 print(g['wins'],g['draws'],g['losses'],flush=True)
