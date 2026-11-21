import json
raw=json.load(open('raw.json'))
CATS=['G','A','PPP','SOG','HIT','BLK','W','SV%']
MGR={"Criss de prof":"Phil","Sean":"Sean","Cerebroni":"Ponpon","ODM":"Oli","Has been":"Gaby","L'aveuglette":"Vincent","Monadnocks":"Hudon","Carter Convicts":"Djipp","ZibanHijab":"Amine","Lou Skunt":"Boobs"}
weeks={}
for m in raw:
    a,b=m['rows']
    def parse(r):
        v=dict(zip(['G','A','PPP','SOG','HIT','BLK','W'],map(int,r[1:8])))
        v['SV%']=float(r[10]); v['_sv']=int(r[8]); v['_sa']=int(r[9]); v['_yahoo_wins']=int(r[11]); return r[0],v
    (na,va),(nb,vb)=parse(a),parse(b)
    weeks.setdefault(m['w'],{})[na]=dict(stats=va,opp=nb)
    weeks[m['w']][nb]=dict(stats=vb,opp=na)
def res(x,y): return 1.0 if x>y else (0.5 if x==y else 0.0)
# Teams under the 3-goalie-start weekly minimum forfeit W and SV% (Yahoo rule); confirmed by Yahoo's scoring
FORFEIT={(5,'ZibanHijab')}
def cres(w,t,u,c):
    if c in ('W','SV%'):
        ft,fu=(w,t) in FORFEIT,(w,u) in FORFEIT
        if ft or fu: return 0.5 if (ft and fu) else (0.0 if ft else 1.0)
    return res(weeks[w][t]['stats'][c],weeks[w][u]['stats'][c])
teams=sorted(MGR)
T={t:dict(actual={c:0.0 for c in CATS},expected={c:0.0 for c in CATS},totals={c:0 for c in CATS},wins=0,losses=0,ties=0,matchW=0,matchL=0,matchT=0,expMatch=0.0,weekly=[]) for t in teams}
check=[]
for w,wk in sorted(weeks.items()):
    for t,info in wk.items():
        s=info['stats']; o=wk[info['opp']]['stats']
        wk_act=0; wk_exp=0
        cw=cl=0
        for c in CATS:
            r=cres(w,t,info['opp'],c); T[t]['actual'][c]+=r
            e=sum(cres(w,t,u,c) for u in wk if u!=t)/9
            T[t]['expected'][c]+=e; wk_act+=r; wk_exp+=e
            if c!='SV%': T[t]['totals'][c]+=s[c]
            if r==1: T[t]['wins']+=1; cw+=1
            elif r==0: T[t]['losses']+=1; cl+=1
            else: T[t]['ties']+=1
        T[t].setdefault('sv',0); T[t].setdefault('sa',0); T[t]['sv']+=s['_sv']; T[t]['sa']+=s['_sa']
        check.append((w,t,cw,s['_yahoo_wins']))
        if cw>cl: T[t]['matchW']+=1
        elif cw<cl: T[t]['matchL']+=1
        else: T[t]['matchT']+=1
        # all-play matchup: share of other teams you'd beat head-to-head on category count
        def cats_vs(u):
            x=sum(cres(w,t,u,c) for c in CATS); return res(x,8-x)
        T[t]['expMatch']+=sum(cats_vs(u) for u in wk if u!=t)/9
        T[t]['weekly'].append(dict(week=w,opp=info['opp'],oppMgr=MGR[info['opp']],actual=wk_act,expected=round(wk_exp,3),luck=round(wk_act-wk_exp,3),
            cats={c:dict(v=s[c],ov=o[c],r=cres(w,t,info['opp'],c),e=round(sum(cres(w,t,u,c) for u in wk if u!=t)/9,3)) for c in CATS}))
bad=[c for c in check if c[2]!=c[3]]
print('mismatches vs Yahoo:',bad)
out=[]
for t in teams:
    d=T[t]; act=sum(d['actual'].values()); exp=sum(d['expected'].values())
    out.append(dict(team=t,manager=MGR[t],record=f"{d['wins']}-{d['losses']}-{d['ties']}",actual=round(act,2),expected=round(exp,3),luck=round(act-exp,3),
      catLuck={c:round(d['actual'][c]-d['expected'][c],3) for c in CATS},catActual=d['actual'],catExpected={c:round(d['expected'][c],3) for c in CATS},
      totals={**d['totals'],'SV%':round(d['sv']/d['sa'],3)},matchRecord=f"{d['matchW']}-{d['matchL']}-{d['matchT']}",expMatch=round(d['expMatch'],3),weekly=d['weekly']))
out.sort(key=lambda x:-x['luck'])
for o in out: print(f"{o['manager']:8} {o['team']:16} {o['record']:8} act {o['actual']:5} exp {o['expected']:6} luck {o['luck']:+.2f} | "+' '.join(f"{c}:{v:+.1f}" for c,v in o['catLuck'].items()))
json.dump(dict(updated='2026-11-21',weeks=7,through="Week 7",teams=out),open('luck.json','w'),indent=1)
