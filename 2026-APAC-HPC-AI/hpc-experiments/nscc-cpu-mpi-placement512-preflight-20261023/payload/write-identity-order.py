"""Write the method-3 identity rank order required by the control arm."""
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('output')
args = parser.parse_args()
Path(args.output).write_text(','.join(str(i) for i in range(512)) + '\n')
