import fitz
from pathlib import Path

ref = Path(r"c:\Users\Ashwin Singh\Downloads\Company-Profile.pdf")
out = Path(__file__).resolve().parent / "ref_pages"
out.mkdir(exist_ok=True)
doc = fitz.open(ref)
for i in range(len(doc)):
    page = doc[i]
    print("PAGE", i + 1)
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") == 0:
            for line in b.get("lines", []):
                spans = line.get("spans", [])
                if spans:
                    s = spans[0]
                    print(
                        f"  y={s['bbox'][1]:.0f} sz={s['size']:.1f} "
                        f"flags={s['flags']} {s['text'][:90].encode('ascii','replace').decode()}"
                    )
    pix = page.get_pixmap(matrix=fitz.Matrix(0.45, 0.45))
    pix.save(str(out / f"page{i+1}.png"))
    print("saved", out / f"page{i+1}.png")
