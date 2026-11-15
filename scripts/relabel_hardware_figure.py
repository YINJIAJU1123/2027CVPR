"""Update text-only placeholder labels in the exported vector hardware layout.

The original editable layout stays available. Exporting the deck applies this
small label update so the paper's photo slots match the evaluated cohort.
No experimental or reference image pixels are modified.
"""
from pathlib import Path
import subprocess
import fitz

ROOT = Path(__file__).resolve().parents[1]
REPLACEMENTS = {
    'Hand + camera setup': 'Cube',
    'Die: six-dot face': 'Die',
    'Camera: lens': 'Ball',
    'Milk carton: label': 'Duck',
}


def relabel(path):
    path = Path(path)
    doc = fitz.open(path)
    page = doc[0]
    spans = [s for b in page.get_text('dict')['blocks']
             for line in b.get('lines', []) for s in line.get('spans', [])
             if s['text'] in REPLACEMENTS]
    if not spans:
        doc.close()
        return
    assert len(spans) == 4
    # A PDF subset font cannot encode arbitrary replacement text reliably.
    # Use an installed full font; the exported PDF embeds the needed glyphs.
    try:
        font_path = subprocess.check_output(
            ['fc-match', 'Comic Sans MS:style=Bold', '-f', '%{file}'], text=True).strip()
        font_data = Path(font_path).read_bytes()
        font = fitz.Font(fontbuffer=font_data)
        font_name = 'HardwareLabel'
    except (OSError, subprocess.CalledProcessError):
        font_data = None
        font = fitz.Font('hebo')
        font_name = 'hebo'
    for s in spans:
        page.add_redact_annot(fitz.Rect(s['bbox']), fill=False)
    page.apply_redactions(images=0, graphics=0)
    page.insert_font(fontname=font_name, fontbuffer=font_data)
    for s in spans:
        word = REPLACEMENTS[s['text']]
        rect = fitz.Rect(s['bbox'])
        x = (rect.x0+rect.x1-font.text_length(word, fontsize=s['size']))/2
        c = s['color']
        color = ((c>>16)/255, ((c>>8)&255)/255, (c&255)/255)
        page.insert_text((x, s['origin'][1]), word, fontsize=s['size'],
                         fontname=font_name, color=color)
    tmp = path.with_suffix('.updated.pdf')
    doc.save(tmp, garbage=4, deflate=True)
    doc.close()
    tmp.replace(path)


if __name__ == '__main__':
    relabel(ROOT/'figures/imported/aimi_real_cases.pdf')
