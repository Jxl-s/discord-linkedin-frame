from PIL import Image
from frame import apply_frame
from text import apply_arc_text

img = Image.open("assets/sample.webp")
framed = apply_frame(img, (88, 101, 242))
result = apply_arc_text(framed, "#OPENTOWORK")
result.save("assets/output_text.png")
print("Saved assets/output_text.png")

sample_output = Image.open("assets/sample-output.png").convert("RGBA").resize(result.size)
merged = Image.blend(result, sample_output, alpha=0.5)
merged.save("assets/output_merged.png")
print("Saved assets/output_merged.png")
