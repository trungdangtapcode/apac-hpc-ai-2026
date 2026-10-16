from pathlib import Path
import tempfile,shutil,os,json,hashlib,importlib.util
root=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs');out=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('candidate',root/'review-candidate-sweep.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
base=root/'collected/220575.pbs111/20261016T054555388584Z';smoke=root/'collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json'
with tempfile.TemporaryDirectory(dir=out) as tmp:
 p=Path(tmp);run=p/'runs/220720.pbs111';shutil.copytree(base/'runs/220575.pbs111',run,copy_function=os.link)
 shutil.rmtree(run/'submitted');shutil.copytree(root/'h100-mnnvl-04',run/'submitted',copy_function=os.link)
 record=json.loads((base/'review.json').read_text());record['job']='220720.pbs111';(p/'review.json').write_text(json.dumps(record))
 for name in ['pbs-accounting.txt','payload-checksums.txt']:(p/name).write_text((base/name).read_text().replace('220575.pbs111','220720.pbs111'))
 seal={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()};(p/'evidence-sha256.json').write_text(json.dumps(seal))
 r=m.compare(p,base,smoke,'h100-mnnvl-04');checks={'synthetic_terminal_fixture_pass':r['terminal_seal_short_payload_pass'],'same_exports_zero_deltas':all(x.get('goodput_change_pct')==0 for x in r['matched_points']),'missing_long_explicit':r['long_diagnostic']['state']=='MISSING','runtime_manual_and_no_promotion':r['promotion_authorized'] is False and r['runtime_status'].startswith('MANUAL')}
 (run/'submitted').chmod(0o700)
 f=run/'submitted/worker.sh';f.unlink();f.write_text('changed fixture only')
 broken=m.compare(p,base,smoke,'h100-mnnvl-04');checks['tamper_blocks_payload_and_comparison']=not broken['terminal_seal_short_payload_pass'] and all('goodput_change_pct' not in x for x in broken['matched_points'])
 report={'scope':'Synthetic candidate fixture reuses historical220575 exports with frozen04 payload. NO candidate GPU execution or measurement. Fixture removed after validation.','checks':checks,'passed':all(checks.values())};(out/'candidate-fixture-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert report['passed']
