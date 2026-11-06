"""Rasterize the generated table body at 600 dpi for a CVPR single-column float.

Run render_language_objects.py --verify-paper . first. The caption and label
remain native LaTeX. No outcome or statistical calculation is modified here.
"""
from pathlib import Path
import hashlib,json,os,shutil,struct,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'tables/language_objects_source.tex'
if '--check' in sys.argv:
    meta=json.loads((ROOT/'figures/language_objects.json').read_text())
    checks=[(source,'source_sha256'),(ROOT/'figures/language_objects.png','image_sha256'),(Path(__file__),'renderer_sha256')]
    for path,key in checks:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=meta.get(key):
            raise SystemExit('Stale table image: rerun scripts/render_language_table_image.py after regenerating the table source.')
    print('Table image/source/renderer hashes verified.');sys.exit(0)
text=source.read_text();body=text[text.index(r'\setlength{\tabcolsep}'):text.index(r'\end{tabular*}')+len(r'\end{tabular*}')]
build=ROOT/'build/language_table_image';build.mkdir(parents=True,exist_ok=True)
tex=r'''\documentclass[10pt,border=0pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{booktabs,times}
\begin{document}
\begin{minipage}{3.28125in}
\footnotesize
'''+body+r'''
\end{minipage}
\end{document}
'''
(build/'language_objects_image.tex').write_text(tex)
tectonic=os.environ.get('TECTONIC') or shutil.which('tectonic')
if tectonic:
    subprocess.run([tectonic,'--keep-logs','--outdir',str(build),str(build/'language_objects_image.tex')],check=True)
elif shutil.which('pdflatex'):
    subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory',str(build),str(build/'language_objects_image.tex')],check=True)
else:
    raise RuntimeError('Install tectonic or pdflatex')
out=ROOT/'figures/language_objects';out.parent.mkdir(exist_ok=True)
subprocess.run([os.environ.get('PDFTOPPM','pdftoppm'),'-r','600','-singlefile','-png',str(build/'language_objects_image.pdf'),str(out)],check=True)
png=out.with_suffix('.png');blob=png.read_bytes();assert blob[:8]==b'\x89PNG\r\n\x1a\n';width,height=struct.unpack('>II',blob[16:24]);assert 1960<=width<=1980 and 800<height<1600,(width,height)
meta=dict(renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),font_family='Times',dpi=600,width_px=width,height_px=height,column_width_inches=3.28125,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),image_sha256=hashlib.sha256(blob).hexdigest(),caption='Native LaTeX caption and table label remain outside image')
(out.with_suffix('.json')).write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
