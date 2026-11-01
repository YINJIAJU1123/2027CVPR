"""Held-out action-space diagnostic; privileged teacher is used only for analysis."""
import hashlib,json,sys
from pathlib import Path
# Do not let the adjacent finite queue driver shadow the stdlib queue module.
if sys.path and Path(sys.path[0]).resolve()==Path(__file__).resolve().parent:
 sys.path.pop(0)
import torch
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/pose_latent_student_v1/waiting_feedback_ablation_20261101_v3'
sys.path.insert(0,str(OUT/'training_sources'))
from train_modules import load_data
from control_modules import features,load_maintenance_actor

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 path=OUT/'action_space_diagnostic.json'
 if path.exists():raise FileExistsError(path)
 torch.set_num_threads(2)
 manifest,data=load_data(ROOT/'outputs/pose_latent_student_v1/startup_dense_local_20261030_v1/validation')
 assert manifest['seed']==185302
 pack=torch.load(OUT/'weights/candidate_waiting.pt',map_location='cpu',weights_only=True)
 bank=pack['bank'];student=pack['manifest']['source_student_sha256']
 actors={n:load_maintenance_actor(OUT/'weights'/f,student,bank,'cpu') for n,f in [('learned_speed','speed_only.pt'),('learned_speed_residual','candidate_waiting.pt')]}
 selected=data['pending'].nonzero().flatten();errors={n:[] for n in ['continue','fixed_slow','oracle_scalar_bound',*actors]};speeds={n:[] for n in ['oracle_scalar_bound',*actors]};outside=[]
 with torch.inference_mode():
  for idx in selected.split(512):
   current=data['proprio'][idx,:21].clamp(-1,1);proposal=data['proposal'][idx].clamp(-1,1);target=data['teacher_hold_action'][idx].clamp(-1,1)
   direction=proposal-current;offset=target-current;denom=direction.square().sum(-1)
   alpha=((offset*direction).sum(-1)/denom.clamp_min(1e-12)).clamp(0,1)
   alpha=torch.where(denom>1e-12,alpha,torch.zeros_like(alpha))
   actions={'continue':proposal,'fixed_slow':current+.15*direction,'oracle_scalar_bound':current+alpha[:,None]*direction}
   speeds['oracle_scalar_bound'].append(alpha)
   for name,actor in actors.items():
    result=actor(data['sensor'][idx],bank[data['goal_index'][idx]],proposal,current,data['pending'][idx]);actions[name]=result['action'];speeds[name].append(result['speed'])
   for name,action in actions.items():errors[name].append((action-target).square().mean(-1))
   # Fraction of teacher action energy that scalar interpolation cannot explain.
   outside.append((actions['oracle_scalar_bound']-target).square().sum(-1)/(offset.square().sum(-1)+1e-12))
 errors={n:torch.cat(v) for n,v in errors.items()};speeds={n:torch.cat(v) for n,v in speeds.items()}
 assert torch.all(errors['learned_speed']>=errors['oracle_scalar_bound']-1e-6)
 groups=set(zip(data['env_id'][selected].tolist(),data['episode_id'][selected].tolist()))
 result=dict(status='completed',scope='Correlated held-out pending states, not episode success. Frozen teacher target is analysis-only and unavailable at runtime.',
  validation_seed=185302,states=len(selected),trajectory_groups=len(groups),formal_data_used=False,actual_model_calls=0,
  equation='alpha*=clip(dot(u_teacher-q, proposal-q)/||proposal-q||^2,0,1); bound=MSE(q+alpha*(proposal-q),u_teacher)',
  mean_teacher_action_mse={n:float(v.mean()) for n,v in errors.items()},
  median_teacher_action_mse={n:float(v.median()) for n,v in errors.items()},
  mean_interpolation={n:float(v.mean()) for n,v in speeds.items()},
  full_below_scalar_bound_fraction=float((errors['learned_speed_residual']<errors['oracle_scalar_bound']-1e-6).float().mean()),
  mean_fraction_target_action_energy_unexplained_by_scalar=float(torch.cat(outside).mean()),
  source_sha256=sha(Path(__file__)),validation_manifest_sha256=sha(ROOT/'outputs/pose_latent_student_v1/startup_dense_local_20261030_v1/validation/manifest.json'),
  actor_sha256={n:sha(OUT/'weights'/f) for n,f in [('learned_speed','speed_only.pt'),('learned_speed_residual','candidate_waiting.pt')]},
  limitation='The per-state optimum uses teacher labels. It is a representational lower bound, not a deployable baseline or an additional formal condition.')
 path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
