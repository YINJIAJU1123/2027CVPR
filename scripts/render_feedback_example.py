"""Render the recorded feedback example: enlarged crops of the agent's input frames
with the agent's own recorded evidence text and decisions. No pixels are repainted."""
from pathlib import Path
import hashlib,json,textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/feedback_example_20261101'
QUOTES=['Visible dark-blue face reads R, not T; inspect red to locate T.',
        'Enlarged image shows a sideways capital T on the red upper face [...] Ground target T to red.']
DECISIONS=['inspect red (90 steps)','bind T to red, reorient']
def main():
    d=json.loads((DATA/'example.json').read_text())
    for line in (DATA/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==digest
    calls=d['learned_speed_residual']['calls']
    assert [c['tool'] for c in calls]==['inspect_face','reorient_target']
    # the quoted evidence must come from the recorded replies
    assert QUOTES[0]==calls[0]['arguments']['evidence']
    head,tail=QUOTES[1].split(' [...] ')
    assert calls[1]['arguments']['evidence'].startswith(head) and calls[1]['arguments']['evidence'].endswith(tail)
    images=[np.asarray(Image.open(DATA/c['image']).convert('RGB')) for c in calls]
    # one shared square crop around the object in both frames
    mask=np.any(np.stack(images)>12,axis=(0,3))
    ys,xs=np.where(mask);cy,cx=(ys.min()+ys.max())//2,(xs.min()+xs.max())//2
    half=max(ys.max()-ys.min(),xs.max()-xs.min())//2+8
    y0,y1,x0,x1=max(cy-half,0),min(cy+half,mask.shape[0]),max(cx-half,0),min(cx+half,mask.shape[1])
    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','Times','DejaVu Serif']})
    fig,axes=plt.subplots(1,2,figsize=(3.35,2.42))
    fig.subplots_adjust(left=.02,right=.98,top=.885,bottom=.28,wspace=.06)
    for ax,c,img,quote,decision in zip(axes,calls,images,QUOTES,DECISIONS):
        ax.imshow(img[y0:y1,x0:x1],interpolation='lanczos')
        ax.set_xticks([]);ax.set_yticks([])
        for s in ax.spines.values():s.set_edgecolor('#888888');s.set_linewidth(.6)
        ax.set_title(f"Call {c['call']}: view at step {c['request_step']}",fontsize=8,pad=3)
        ax.text(.5,-.04,'\u201c'+textwrap.fill(quote,31)+'\u201d',transform=ax.transAxes,ha='center',va='top',fontsize=6.1,style='italic',linespacing=1.15)
        ax.text(.5,-.37,'\u2192 '+decision,transform=ax.transAxes,ha='center',va='top',fontsize=7,weight='bold')
    fig.suptitle('\u201cTurn the face marked T upward\u201d',fontsize=8.5,y=.995)
    fig.savefig(ROOT/'figures/feedback_example.pdf',metadata={'CreationDate':None})
    fig.savefig(ROOT/'figures/feedback_example.png',dpi=300)
    plt.close(fig)
if __name__=='__main__':main()
