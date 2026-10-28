#!/usr/bin/env python3
# filtro q-score equivalente ao padrão do q2-quality-filter (min_quality=4, quality_window=3,
# min_length_fraction=0.75, max_ambiguous=0): trunca na primeira janela de 3 bases com Q<4.
import sys,gzip
inp,out=sys.argv[1],sys.argv[2]; kept=tot=0
with open(inp) as f, open(out,'w') as o:
    while True:
        h=f.readline()
        if not h: break
        s=f.readline().strip(); f.readline(); q=f.readline().strip(); tot+=1
        L=len(s); cut=L; run=0
        for i,c in enumerate(q):
            if ord(c)-33<4:
                run+=1
                if run>=3: cut=i-2; break
            else: run=0
        s,q=s[:cut],q[:cut]
        if len(s) < 0.75*L or 'N' in s: continue
        o.write(f"{h}{s}\n+\n{q}\n"); kept+=1
print(inp.split('/')[-1],tot,kept)
