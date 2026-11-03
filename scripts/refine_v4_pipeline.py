from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
ROOT=Path(__file__).resolve().parents[1]
p=Presentation(ROOT/'REVEAL_complete_paper_figures_v4.pptx')
s=p.slides[1]
replacements={
'(a) Train the privileged teacher':'(a) Privileged teacher supervision',
'(b) Distill with agentic latent embedding':'(b) Distill a goal-conditioned student',
'Agentic latent':'Goal-bank vector',
'Embodied\nAgent':'Semantic\nagent',
'Skill selection':'Public skill selection',
'(c) Closed-loop deployment':'(c) Closed-loop execution',
'Latent student':'Student policy',
'Real hand + camera':'Physical hand (pending)',
'Stable presentation':'Target presentation',
'[Insert trial instruction]':'Present the face marked T',
'RGB image':'RGB observation',
'State MSE (GT)':'State MSE (training)',
}
for sh in s.shapes:
 if not sh.has_text_frame: continue
 old=sh.text
 if old in replacements:
  runs=[r for par in sh.text_frame.paragraphs for r in par.runs]
  if runs:
   runs[0].text=replacements[old]
   for r in runs[1:]: r.text=''
 for par in sh.text_frame.paragraphs:
  for r in par.runs: r.font.name='DejaVu Sans'
 if old=='Latent student':
  for par in sh.text_frame.paragraphs:
   for r in par.runs:r.font.size=Pt(16)
 if old=='State MSE (GT)':
  for par in sh.text_frame.paragraphs:
   for r in par.runs:r.font.size=Pt(14)
# Keep the v4 second-slide layout and editable objects; label all pending photo slots.
for x,y,w,h,text in [(0.87,5.75,2.05,.8,'Observed RGB\n(simulation / camera)'),(8.1,11.45,2.65,.65,'TODO: physical\ninspection frame'),(12.35,11.45,2.65,.65,'TODO: physical\ntarget frame'),(16.3,10.9,4.4,.8,'TODO: physical setup\nNo hardware result shown')]:
 box=s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
 tf=box.text_frame;tf.word_wrap=True
 for i,line in enumerate(text.split('\n')):
  par=tf.paragraphs[0] if i==0 else tf.add_paragraph();par.text=line;par.alignment=2
  for r in par.runs:r.font.name='DejaVu Sans';r.font.size=Pt(16);r.font.color.rgb=RGBColor.from_string('687584')
p.save(ROOT/'REVEAL_complete_paper_figures_v4_refined.pptx')
# Export only slide 2 for a vector paper figure.
for i in range(len(p.slides)-1,-1,-1):
 if i==1:continue
 el=p.slides._sldIdLst[i];p.part.drop_rel(el.rId);p.slides._sldIdLst.remove(el)
p.save(ROOT/'figures/imported/pipeline_v4_slide2_refined.pptx')
# Keep the abstract evidence-led with one numerical comparison.
(ROOT/'sections/00_abstract.tex').write_text(r'''\begin{abstract}
Language-guided in-hand manipulation requires a robot to find a requested object face, reorient it while preserving contact, and continue acting while visual reasoning is pending. We present REVEAL, an asynchronous system that connects a visual agent to a history-conditioned motor policy through a shared goal bank. The agent uses updated images to inspect and bind semantic targets, while teacher-supervised local controllers adapt joint commands during reasoning and execution. We evaluate complete systems across six object-specific simulation releases and two semantic mappings, with separate cube interventions for control and feedback. Under the same maximum call budget, updated images yield 32/40 completions versus 9/40 when the initial image is repeated. Changed-mapping comparisons further support system-level adaptation within the tested releases. Independent confirmation does not establish an advantage of learned waiting control over fixed slowing. Multi-object physical-hand evaluation remains pending.
\end{abstract}
''')
method=ROOT/'sections/04_method.tex';t=method.read_text();t=t.replace('width=0.78\textwidth','width=0.88\textwidth').replace('training_distillation_pipeline.png','pipeline_v4_slide2_refined.pdf').replace('The v4 figure shows privileged teacher supervision, distillation through an agentic goal latent, and closed-loop control. Dashed deployment photo slots remain illustrative placeholders and do not indicate completed physical-hand trials.','Privileged supervision trains a student conditioned on a public goal-bank vector. The semantic agent selects skills, and local controllers adapt their execution. Dashed physical-hand slots are pending; they do not report hardware results.');method.write_text(t)
print('Saved refined editable deck, slide 2, and revised manuscript source.')
