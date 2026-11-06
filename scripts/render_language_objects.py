"""Build reproducible common-service-eligible paper tables from frozen trial exports."""
import argparse,hashlib,itertools,json,math
from pathlib import Path
C=['en_standard','en_rewrite','zh_standard','zh_rewrite'];M=['astra','vlm','rule'];O=['cube','duck','hedgehog']
N={'astra':'Full Astra','vlm':'Fine-tuned VLM','rule':'Rule VLM','cube':'Cube','duck':'Duck','hedgehog':'Hedgehog'}
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def exact(a,b):
 n=a+b
 return min(1.,2*sum(math.comb(n,k) for k in range(min(a,b)+1))/2**n) if n else 1.
def holm(tests,key):
 for family in ['methods','language_and_wording']:
  xs=sorted([x for x in tests if x['family']==family],key=lambda x:x[key]);v=0.
  for i,x in enumerate(xs):v=max(v,min(1.,(len(xs)-i)*x[key]));x[key+'_holm']=v

def analyze(exports):
 trials=[];tests=[];panels=[];audits={}
 for obj in O:
  rs=exports[obj]['trials'];lookup={(r['condition'],r['method'],r['episode']):r for r in rs}
  assert len(rs)==len(lookup)==720
  assert set(lookup)==set(itertools.product(C,M,range(60)))
  state_mismatches=[];state_deltas={}
  for row in rs:
   if 'initial_state_values' in row:assert hashlib.sha256(json.dumps(row['initial_state_values'],sort_keys=True).encode()).hexdigest()==row['initial_state_sha256']
  def flatten(v):
   return [z for x in v for z in flatten(x)] if isinstance(v,list) else [v]
  for i in range(60):
   assert len({(lookup[c,m,i]['trial_seed'],lookup[c,m,i]['goal_index']) for c in C for m in M})==1
   if len({lookup[c,m,i]['initial_state_sha256'] for c in C for m in M})!=1:
    state_mismatches.append(i);reference=lookup[C[0],M[0],i]['initial_state_values']
    for c in C:
     for m in M:
      values=lookup[c,m,i]['initial_state_values'];assert set(values)==set(reference)
      for k in reference:
       a,b=flatten(values[k]),flatten(reference[k]);assert len(a)==len(b)
       delta=max(abs(x-y) for x,y in zip(a,b));state_deltas[k]=max(state_deltas.get(k,0.),delta)
       assert delta<=1e-6,(obj,i,k,delta,'material reset mismatch')
   assert all(lookup[c,m,i]['first_image_sha256'] for c in C for m in M)
  for row in rs:
   assert bool(row['success'])==(row['reason']=='success')
   assert not row['success'] or (row['declared_goal']==row['goal_index'] and row['final_error_rad']<=.16)
   trials.append({**row,'object':obj})
  audits[obj]=dict(recorded=720,exact_initial_state_slots=60-len(state_mismatches),initial_state_mismatch_slots=state_mismatches,max_initial_state_component_difference=state_deltas,reset_audit_tolerance=1e-6,first_image_mismatch_slots=[i for i in range(60) if len({lookup[c,m,i]['first_image_sha256'] for c in C for m in M})!=1])
  elig={}
  for c in C:
   ids=[i for i in range(60) if all(not lookup[c,m,i]['exclusion_reason'] for m in M)];elig[c]=ids
   strict=[i for i in ids if len({lookup[c,m,i]['first_image_sha256'] for m in M})==1 and len({lookup[c,m,i]['initial_state_sha256'] for m in M})==1]
   panel=dict(object=obj,condition=c,eligible_slots=ids,n=len(ids),strict_slots=strict,strict_n=len(strict),service_excluded_slots=sorted(set(range(60))-set(ids)),strict_pairing_excluded_slots=sorted(set(ids)-set(strict)),methods={})
   for m in M:
    panel['methods'][m]=dict(success=sum(lookup[c,m,i]['success'] for i in ids),raw_success=sum(lookup[c,m,i]['success'] for i in range(60)),service_excluded=sum(bool(lookup[c,m,i]['exclusion_reason']) for i in range(60)),strict_success=sum(lookup[c,m,i]['success'] for i in strict))
   panels.append(panel)
  def contrast(family,name,left,right,ids,strict):
   a,b=left;z,w=right
   def calc(use):
    aa=sum(lookup[a,b,i]['success'] and not lookup[z,w,i]['success'] for i in use);bb=sum(lookup[z,w,i]['success'] and not lookup[a,b,i]['success'] for i in use)
    return dict(n=len(use),left_success=sum(lookup[a,b,i]['success'] for i in use),right_success=sum(lookup[z,w,i]['success'] for i in use),left_only=aa,right_only=bb,p_exact=exact(aa,bb))
   main=calc(ids);sens=calc(strict)
   tests.append(dict(object=obj,family=family,name=name,left='/'.join(left),right='/'.join(right),eligible_slots=ids,**main,strict=sens,strict_slots=strict,p_strict=sens['p_exact']))
  for c in C:
   panel=next(p for p in panels if p['object']==obj and p['condition']==c)
   for a,b in itertools.combinations(M,2):contrast('methods',c+':'+a+'-'+b,(c,a),(c,b),elig[c],panel['strict_slots'])
  for m in M:
   for a,b in [('en_standard','zh_standard'),('en_rewrite','zh_rewrite'),('en_standard','en_rewrite'),('zh_standard','zh_rewrite')]:
    ids=[i for i in range(60) if not lookup[a,m,i]['exclusion_reason'] and not lookup[b,m,i]['exclusion_reason']]
    strict=[i for i in ids if lookup[a,m,i]['first_image_sha256']==lookup[b,m,i]['first_image_sha256'] and lookup[a,m,i]['initial_state_sha256']==lookup[b,m,i]['initial_state_sha256']]
    contrast('language_and_wording',m+':'+a+'-'+b,(a,m),(b,m),ids,strict)
 holm(tests,'p_exact');holm(tests,'p_strict')
 return dict(recorded=2160,panels=panels,comparisons=tests,pairing_audit=audits,holm_family_size=36,main_estimand='Completion conditional on common service eligibility within object and instruction condition; no replacement; not end-to-end service reliability'),trials

def table_start(cols='lrrrr'):
 return '\\begin{table}[t]\n\\centering\\footnotesize\n\\setlength{\\tabcolsep}{2pt}\n\\begin{tabular}{@{}'+cols+'@{}}\n\\toprule\n & \\multicolumn{2}{c}{English} & \\multicolumn{2}{c}{Chinese}\\\\\nSystem & Standard & Rewrite & Standard & Rewrite\\\\\n\\midrule\n'
def ending(caption,label):return '\\bottomrule\n\\end{tabular}\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\end{table}\n'
def fmt(p):return '$<0.0001$' if p<.0001 else f'{p:.4f}'
def render(out,result):
 t=out/'tables';t.mkdir(exist_ok=True)
 panels={(p['object'],p['condition']):p for p in result['panels']}
 for mode,name,label in [('main','language_objects','tab:language-objects'),('raw','language_objects_raw','tab:language-raw'),('strict','language_objects_sensitivity','tab:language-sensitivity')]:
  s=table_start()
  if mode=='main':s=s.replace(r'\begin{tabular}{@{}lrrrr@{}}',r'\begin{tabular*}{\linewidth}{@{}l@{\extracolsep{\fill}}rrrr@{}}')
  for oi,obj in enumerate(O):
   ns=[panels[obj,c]['n' if mode=='main' else 'strict_n'] if mode!='raw' else 60 for c in C]
   if mode=='main':s+=r'\textbf{'+N[obj]+r'} ($n$) & '+' & '.join(map(str,ns))+r'\\'+'\n'
   else:s+='\\multicolumn{5}{l}{\\textit{'+N[obj]+': $n='+', '.join(map(str,ns))+'$}}\\\\\n'
   for m in (list(reversed(M)) if mode=='main' else M):
    vals=[]
    for c,n in zip(C,ns):
     q=panels[obj,c]['methods'][m];v=q['success' if mode=='main' else 'raw_success' if mode=='raw' else 'strict_success']
     value=f'{100*v/n:.1f}' if mode=='main' else f'{v}/{n}'
     if mode=='main' and v==max(panels[obj,c]['methods'][k]['success'] for k in M):value=r'\textbf{'+value+'}'
     vals.append(value)
    s+=N[m]+' & '+' & '.join(vals)+r'\\'+'\n'
   if oi<2:s+='\\midrule\n'
  captions={'main':r'\textbf{Q1: language and wording coverage.} Completion (\%) on common service-eligible trials. Methods share the listed $n$ of 60 scheduled slots. Bold denotes the highest observed rate, not significance. Raw counts and paired analyses are in the supplement.',
   'raw':r'Raw completion counts over all scheduled trials, retaining infrastructure failures in the denominator. These are separate object-specific cohorts; the four instruction variants reuse physical tasks.',
   'strict':r'Strict pairing sensitivity: common service-eligible slots additionally require identical initial-state and first-image hashes across all three methods. Numerators are successes. This is separate from the main service-eligible estimand.'}
  tail=ending(captions[mode],label)
  if mode=='main':tail=tail.replace(r'\end{tabular}',r'\end{tabular*}')
  full=s+tail
  if mode=='main':
   (t/'language_objects_source.tex').write_text(full)
   full='\\begin{table}[t]\n\\centering\n'+r'\includegraphics[width=\linewidth]{figures/language_objects.png}'+'\n'+tail[tail.index(r'\caption'):]
  (t/(name+'.tex')).write_text(full)
 s=table_start()
 for oi,obj in enumerate(O):
  s+='\\multicolumn{5}{l}{\\textit{'+N[obj]+'}}\\\\\n'
  for m in M:
   vals=[panels[obj,c]['methods'][m]['service_excluded'] for c in C];s+=N[m]+' & '+' & '.join(map(str,vals))+r'\\'+'\n'
  if oi<2:s+='\\midrule\n'
 (t/'language_objects_exclusions.tex').write_text(s+ending('Service-excluded trial counts, each out of 60 scheduled slots. All raw records are retained.','tab:language-exclusions'))
 s=''
 for family in ['language_and_wording','methods']:
  if family=='language_and_wording':
   q=table_start().replace(r'\multicolumn{2}{c}{English} & \multicolumn{2}{c}{Chinese}',r'\multicolumn{2}{c}{EN vs. ZH} & \multicolumn{2}{c}{Standard vs. rewrite}').replace('System & Standard & Rewrite & Standard & Rewrite','System & Standard & Rewrite & English & Chinese')
   for oi,obj in enumerate(O):
    q+='\\multicolumn{5}{l}{\\textit{'+N[obj]+'}}\\\\\n'
    for m in M:
     xs=[x for x in result['comparisons'] if x['object']==obj and x['family']==family and x['name'].startswith(m+':')]
     q+=N[m]+' & '+' & '.join(fmt(x['p_exact_holm']) for x in xs)+r'\\'+'\n'
    if oi<2:q+='\\midrule\n'
   s+=q+ending('Exact paired language/wording tests, Holm-adjusted jointly over 36 contrasts across three objects. Non-significance does not establish equivalence.','tab:language-wording-tests')
  else:
   q='\\begin{table}[t]\n\\centering\\footnotesize\n\\setlength{\\tabcolsep}{5pt}\n\\begin{tabular}{@{}lrrr@{}}\n\\toprule\nCondition & Astra--FT & Astra--Rule & FT--Rule\\\\\n\\midrule\n'
   for oi,obj in enumerate(O):
    q+='\\multicolumn{4}{l}{\\textit{'+N[obj]+'}}\\\\\n'
    for c in C:
     xs=[x for x in result['comparisons'] if x['object']==obj and x['family']==family and x['name'].startswith(c+':')]
     q+=c.replace('en_','EN ').replace('zh_','ZH ')+' & '+' & '.join(fmt(x['p_exact_holm']) for x in xs)+r'\\'+'\n'
    if oi<2:q+='\\midrule\n'
   s+=q+ending('Exact paired method tests on the main common service-eligible panels, Holm-adjusted over a separate family of 36 contrasts. FT denotes fine-tuning. Strict pairing sensitivity tests are archived.','tab:language-method-tests')
 (t/'language_objects_tests.tex').write_text(s)

def main():
 import sys
 if '--verify-paper' in sys.argv:
  parser=argparse.ArgumentParser();parser.add_argument('--verify-paper',type=Path,required=True);args=parser.parse_args()
  base=args.verify_paper/'data/language_objects_20261106'
  rows=json.loads((base/'trials.json').read_text());archived=json.loads((base/'results.json').read_text())
  result,_=analyze({o:dict(trials=[r for r in rows if r['object']==o]) for o in O})
  assert result==archived,'Derived tables/tests disagree with archived results'
  for line in (base/'SHA256SUMS').read_text().splitlines():
   digest,name=line.split('  ',1);assert hashlib.sha256((base/name).read_bytes()).hexdigest()==digest,name
  render(args.verify_paper,result);print('Verified 2,160 records, common panels, all 144 tests, pairing audit and source export checksums.');return
 p=argparse.ArgumentParser();p.add_argument('--cube',type=Path,required=True);p.add_argument('--duck',type=Path,required=True);p.add_argument('--hedgehog',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--cube-errors',type=Path);a=p.parse_args()
 exports={o:json.loads(getattr(a,o).read_text()) for o in ['duck','hedgehog']};exports['cube']=dict(trials=json.loads((a.cube/'trials.json').read_text()),protocol=json.loads((a.cube/'protocol.json').read_text()),source_ledger_sha256=json.loads((a.cube/'provenance.json').read_text())['source_ledger_sha256'])

 if a.cube_errors:exports['cube']['exclusions']=json.loads(a.cube_errors.read_text())
 result,trials=analyze(exports);a.output.mkdir(parents=True,exist_ok=True);data=a.output/'data/language_objects_20261106';data.mkdir(parents=True,exist_ok=True)
 dump(data/'trials.json',trials);dump(data/'results.json',result)
 dump(data/'provenance.json',{o:{k:v for k,v in exports[o].items() if k not in ['trials','prompts']} for o in O})
 for o in ['duck','hedgehog']:
  for c,d in exports[o]['prompts'].items():dump(data/'prompts'/f'{o}_{c}.json',d)
 for p in (a.cube/'prompts').glob('*.json'):
  target=data/'prompts'/('cube_'+p.name);target.write_bytes(p.read_bytes())
 render(a.output,result)
 lines=[]
 for p in sorted(data.rglob('*')):
  if p.is_file() and p.name!='SHA256SUMS':lines.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(data)))
 (data/'SHA256SUMS').write_text('\n'.join(lines)+'\n')
 print(json.dumps(dict(recorded=result['recorded'],pairing_audit=result['pairing_audit'],significant=[{k:x[k] for k in ['object','family','name','p_exact_holm','p_strict_holm']} for x in result['comparisons'] if x['p_exact_holm']<.05]),indent=2))
if __name__=='__main__':main()
