from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'test-nixl-ondemand.py').read_text().replace('256','HEAD_BYTES')
source=source.replace('ROOT = Path(__file__).resolve().parent', 'ROOT = Path('+repr(str(ROOT))+')')
source=source.replace("(ROOT/'nixl-ondemand/geometry-test.json').write_text", "(ROOT/'serving-tuning-02'/f'geometry-headbytes-{HEAD_BYTES}.json').write_text")
for width in (128,256):
 scope={'__file__':str(ROOT/'test-nixl-ondemand.py'),'HEAD_BYTES':width}
 exec(compile(source,'fp8-geometry-test','exec'),scope)
