"""Render a vector schematic of the implemented cube interface; no rollout imagery."""
from pathlib import Path
from math import atan2, cos, sin, pi
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path('/usr/share/fonts/truetype/liberation2')
for name, filename in [('Diagram', 'LiberationSans-Regular.ttf'), ('DiagramBold', 'LiberationSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
C = canvas.Canvas(str(ROOT / 'figures/reveal_pipeline.pdf'), pagesize=(504, 228), invariant=1)
C.setTitle('REVEAL cube training and deployment interface')
C.setAuthor('')
INK = HexColor('#223647')
C.setStrokeColor(INK)

def label(x, y, text, size=9, bold=False, center=False, color=INK):
    C.setFillColor(color)
    C.setFont('DiagramBold' if bold else 'Diagram', size)
    (C.drawCentredString if center else C.drawString)(x, y, text)

def box(x, y, w, h, lines, fill, size=8.5):
    C.setFillColor(HexColor(fill)); C.setStrokeColor(HexColor('#a5b2bc')); C.setLineWidth(.6)
    C.roundRect(x, y, w, h, 3, fill=1, stroke=1)
    for i,line in enumerate(lines):
        label(x+w/2, y+h/2+(len(lines)-1)*5.2-i*10.4-2.6, line, size, i==0, True)

def arrow(points, dashed=False, color=INK):
    C.setStrokeColor(color); C.setFillColor(color); C.setLineWidth(.85)
    if dashed: C.setDash(3,2)
    p=C.beginPath();p.moveTo(*points[0])
    for x,y in points[1:]:p.lineTo(x,y)
    C.drawPath(p)
    C.setDash()
    x,y=points[-1]; a=atan2(y-points[-2][1],x-points[-2][0])
    p=C.beginPath();p.moveTo(x,y)
    p.lineTo(x-5*cos(a-pi/7),y-5*sin(a-pi/7));p.lineTo(x-5*cos(a+pi/7),y-5*sin(a+pi/7));p.close()
    C.drawPath(p,stroke=0,fill=1)

label(8,216,'A  Training only',10,True)
box(8,174,140,31,['Privileged teacher','State + task / holding objective'],'#e8eef7')
box(182,174,140,31,['Student adaptation','History + measured pose + goal'],'#e8eef7')
box(356,174,140,31,['Local actor fitting','Teacher actions + regularization'],'#e8eef7')
arrow([(148,190),(182,190)])
arrow([(78,174),(78,165),(426,165),(426,174)])
label(252,167,'supervised action labels',7.5,False,True)
C.setStrokeColor(HexColor('#ccd5dc'));C.line(8,158,496,158)
label(8,144,'B  Deployment: semantic decisions',10,True)
xs=[8,136,264,392];w=104
box(xs[0],100,w,34,['Current RGB','Instruction + public history'],'#edf5ec',7.9)
box(xs[1],100,w,34,['Visual agent','One request may be pending'],'#edf5ec',7.9)
box(xs[2],100,w,34,['Validate public action','Inspect / bind / reorient'],'#edf5ec',7.9)
box(xs[3],100,w,34,['Shared goal bank','Update active goal'],'#edf5ec',7.9)
for i in range(3):arrow([(xs[i]+w,117),(xs[i+1],117)])
label(8,80,'C  Continuous motor control',10,True)
box(xs[0],28,w,34,['Measurements','Pose + proprioception'],'#fff2de',8.2)
box(xs[1],28,w,34,['Motor student','History + active goal'],'#fff2de',8.2)
box(xs[2],28,w,34,['Local actor','Waiting or execution'],'#fff2de',8.2)
box(xs[3],28,w,34,['Apply joint targets','Hand--object dynamics'],'#fff2de',8.2)
for i in range(3):arrow([(xs[i]+w,45),(xs[i+1],45)])
arrow([(444,100),(444,90),(188,90),(188,62)], True)
arrow([(316,90),(316,62)], True)
label(310,93,'active goal',7.5,False,True)
arrow([(188,100),(188,96),(252,96),(252,69),(306,69),(306,62)], True,HexColor('#7b5d88'))
label(385,70,'request status / elapsed time',7,False,True,color=HexColor('#7b5d88'))
arrow([(444,28),(444,13),(60,13),(60,28)])
label(252,16,'new measurements; updated RGB for the next request',7.5,False,True)
C.showPage();C.save()
print('Rendered figures/reveal_pipeline.pdf')
