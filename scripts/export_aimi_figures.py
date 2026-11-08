"""Export paper figures from the existing AIMI editable deck.

Use --from-pdf to reuse a LibreOffice export. This preserves source simulation
images and vector text; it neither retouches nor generates experimental images.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile
import fitz
from relabel_hardware_figure import relabel

ROOT = Path(__file__).resolve().parents[1]
CROPS = [
    (0, 'aimi_teaser', (0, 1.65, 21.875, 12.50)),
    (1, 'aimi_pipeline', (.15, .10, 21.72, 13.55)),
    (2, 'aimi_controller', (5.8, 1.65, 16.08, 12.05)),
    (3, 'aimi_exploration', (5.8, 1.65, 16.08, 12.05)),
    (4, 'aimi_sim_real', (.35, 1.24, 21.47, 12.55)),
    (5, 'aimi_real_cases', (.49, .30, 21.39, 13.57)),
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-pdf', type=Path)
    args = parser.parse_args()
    build = ROOT / 'build/aimi_revision_20261109'
    build.mkdir(parents=True, exist_ok=True)
    pdf = args.from_pdf
    if pdf is None:
        with tempfile.TemporaryDirectory(prefix='aimi-office-') as profile:
            subprocess.run([
                'libreoffice', '-env:UserInstallation=' + Path(profile).as_uri(),
                '--headless', '--convert-to', 'pdf', '--outdir', str(build),
                str(ROOT / 'figures/AIMI_paper_figures.pptx'),
            ], check=True)
        pdf = build / 'AIMI_paper_figures.pdf'
    source = fitz.open(pdf)
    assert len(source) == 6
    for index, name, bounds in CROPS:
        crop = fitz.Rect(*[v * 72 for v in bounds])
        output = fitz.open()
        page = output.new_page(width=crop.width, height=crop.height)
        page.show_pdf_page(page.rect, source, index, clip=crop)
        output.set_metadata({
            'title': name.replace('_', ' ').title(),
            'subject': 'AIMI paper figure; existing simulation assets and slide design',
        })
        output.save(ROOT / 'figures/imported' / (name + '.pdf'), garbage=4, deflate=True)
        page.get_pixmap(matrix=fitz.Matrix(1, 1)).save(build / (name + '.png'))
    relabel(ROOT / 'figures/imported/aimi_real_cases.pdf')
    print('Exported six figures from the editable AIMI source deck.')

if __name__ == '__main__':
    main()
