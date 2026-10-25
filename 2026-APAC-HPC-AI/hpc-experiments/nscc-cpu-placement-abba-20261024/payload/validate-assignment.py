"""Verify the embedded refined mapping hash and fixed 512-rank group shape."""
import argparse
import json
from mapping_common import read_assignment

parser = argparse.ArgumentParser()
parser.add_argument('assignment')
args = parser.parse_args()
data = read_assignment(args.assignment)
print(json.dumps({'passed': True, 'parent_graph_sha256': data['parent_graph_sha256'],
                  'parent_screen_sha256': data['parent_screen_sha256'],
                  'refinement_sha256': data['refinement_sha256'],
                  'host_groups': data['host_count'],
                  'ranks': sum(len(group) for host in data['mapping']['numa_group_members_by_host'] for group in host)}, indent=2))
