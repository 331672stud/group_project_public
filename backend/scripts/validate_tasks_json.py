import json
p='/app/scripts/tasks/tasks.json'
s=open(p,'r',encoding='utf-8').read()
try:
    json.loads(s)
    print('OK')
except Exception as e:
    print('ERROR:', e)
    import re
    m=re.search(r'char (\d+)', repr(e))
    pos=int(m.group(1)) if m else None
    if pos:
        lines=s[:pos].splitlines()
        line_no=len(lines)
        col=len(lines[-1])+1 if lines else 1
        print('At char',pos,'line',line_no,'col',col)
        L=s.splitlines()
        start=max(0,line_no-5)
        end=min(len(L),line_no+4)
        print('\nContext:')
        for i in range(start,end):
            print(f'{i+1:4}: {L[i]}')
