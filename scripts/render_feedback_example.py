"""Render unchanged model input frames with recorded public decisions."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/feedback_example_20261101'
def main():
    d=json.loads((DATA/'example.json').read_text())
    for line in (DATA/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==digest
    calls=d['learned_speed_residual']['calls']
    assert [c['tool'] for c in calls]==['inspect_face','reorient_target']
    fig,axes=plt.subplots(1,2,figsize=(6.6,3.25))
    fig.subplots_adjust(left=.025,right=.975,top=.86,bottom=.24,wspace=.15)
    labels=['Inspect red face','Bind T to red; reorient']
    for ax,c,label in zip(axes,calls,labels):
        ax.imshow(Image.open(DATA/c['image']),interpolation='nearest')
        ax.set_axis_off()
        ax.set_title(f"Observation {c['call']} (step {c['request_step']})",fontsize=10,pad=7)
        ax.text(.5,-.075,label,transform=ax.transAxes,ha='center',va='top',fontsize=10)
        ax.text(.5,-.17,f"Reply applied at step {c['applied_step']}",transform=ax.transAxes,ha='center',va='top',fontsize=9,color='#555555')
    fig.suptitle('Instruction: turn the face marked T upward',fontsize=12,y=.98)
    fig.text(.5,.025,'Matched initial plan: abstain  |  Feedback: correct binding and successful stop',ha='center',fontsize=9)
    fig.savefig(ROOT/'figures/feedback_example.pdf',metadata={'CreationDate':None})
    fig.savefig(ROOT/'figures/feedback_example.png',dpi=220)
    plt.close(fig)
if __name__=='__main__':main()
