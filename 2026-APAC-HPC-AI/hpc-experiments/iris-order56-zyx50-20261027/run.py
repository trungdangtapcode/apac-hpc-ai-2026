"""Single-arm 50-step zyx horizon extension; preserve initialized source."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,time,statistics,socket
from case_checks import source_check
from native_output import review_native_output
KIT=Path(__file__).resolve().parent;WORK=KIT.parent;RUN=None
SOURCE=Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-order-init-20261026T133526Z/initialized')
DEADLINE=time.monotonic()+1500
ORDER='zyx'; STEPS=50; INTERVALS=49; SOLVER_CAP=1250; PRE_SOLVER_REMAINING=1360

def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
def single_arm_result(row):
    assert row.get('order')=='zyx' and row.get('steps')==50 and row.get('intervals')==49
    return {'passed':True,'arms_by_order':{'zyx':row},'order':['zyx'],'hostname':socket.getfqdn(),'scored_result':False,'comparison':False,'limits':['Single-arm 50-step horizon extension; not a matched 50-step comparison, full 150-step run, or official score','Descriptive timing segments retain all measured intervals; they do not remove early or late samples','One initialized-source copy; no xyz arm is run','Procfs snapshots are whole-node counters and do not measure hardware memory bandwidth or per-process attribution']}
def node_snapshot(label,dest):
    started=time.monotonic_ns(); snap={'label':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'time_ns':time.time_ns(),'scope':'whole-node procfs counters; not per-process hardware bandwidth'}
    for name in ('meminfo','vmstat','pressure/memory'):
        try:snap[name]=(Path('/proc')/name).read_text()
        except Exception as exc:snap[name+'_error']={'type':type(exc).__name__,'message':str(exc)}
    snap['collection_elapsed_ms']=(time.monotonic_ns()-started)/1e6
    save(dest/(label+'-node-snapshot.json'),snap)
def bounded(label,args,cwd,cap):
    left=int(DEADLINE-time.monotonic())-30
    assert left>0,'shared deadline insufficient before '+label
    limit=min(cap,left)
    with (RUN/(label+'.log')).open('w') as f:
        p=subprocess.run(['timeout','--signal=TERM','--kill-after=10s',str(limit)+'s',*args],cwd=str(cwd),stdout=f,stderr=subprocess.STDOUT,timeout=limit+20)
    save(RUN/(label+'.status.json'),{'returncode':p.returncode,'cap_seconds':limit})
    assert p.returncode==0,(label,p.returncode)
def main():
    global RUN
    RUN=WORK/'runs'/os.environ['SLURM_JOB_ID'];RUN.mkdir(parents=True,exist_ok=False)
    bounded('kit-before',['sha256sum','-c','payload-sha256.txt'],KIT,30)
    remaining=int(DEADLINE-time.monotonic());assert remaining>=PRE_SOLVER_REMAINING,('insufficient global time before source preparation',remaining)
    src=SOURCE/'order-zyx';assert (src/'READY').is_file();save(RUN/'zyx-source.json',source_check(src,ORDER))
    dest=WORK/'cases'/'zyx';assert not dest.exists();dest.mkdir(parents=True)
    bounded('zyx-source-before',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'source-before.json'),'--source-only'],KIT,90)
    bounded('zyx-clone',['python3','-c','import shutil,sys;shutil.copytree(sys.argv[1],sys.argv[2],symlinks=True,dirs_exist_ok=True,ignore=shutil.ignore_patterns("source-before.json","source-after-copy.json","source-after-init.json"))',str(src),str(dest)],KIT,150)
    bounded('zyx-clone-check',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'copy-check.json'),'--compare-copy'],KIT,90)
    text=(dest/'system/controlDict.noWrite').read_text()
    for key,value in [('startFrom','startTime'),('endTime','50')]:
        text,count=re.subn(r'(?m)^'+key+r'[ \t]+[^;\n]+;[^\n]*$',key+' '+value+';',text);assert count==1
    (dest/'system/controlDict').write_text(text);shutil.copyfile(dest/'system/fvSolution.fixedIter',dest/'system/fvSolution')
    bounded('zyx-affinity',['mpirun','-np','56','--','python3',str(KIT/'affinity-probe.py'),'worker',str(dest/'affinity')],dest,60)
    bounded('zyx-affinity-check',['python3',str(KIT/'affinity-probe.py'),'validate',str(dest/'affinity')],dest,30)
    remaining=int(DEADLINE-time.monotonic());assert remaining>=PRE_SOLVER_REMAINING,('insufficient global time immediately before zyx solver',remaining)
    node_snapshot('solver-before',dest)
    with (dest/'simpleFoam.log').open('w') as out,(dest/'solver.stderr').open('w') as err:
        p=subprocess.run(['/usr/bin/time','-v','-o',str(dest/'resource-time.log'),'timeout','--signal=TERM','--kill-after=15s',str(SOLVER_CAP)+'s','mpirun','-np','56','--','simpleFoam','-parallel'],cwd=str(dest),stdout=out,stderr=err,timeout=SOLVER_CAP+20)
    node_snapshot('solver-after',dest)
    save(dest/'return-code.json',{'returncode':p.returncode});assert p.returncode==0,('zyx',p.returncode)
    log,timing,cd,counts=review_native_output(dest)
    assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped',(dest/'solver.stderr').read_text(),re.I)
    bounded('zyx-source-after',['python3',str(KIT/'tree-manifest.py'),str(src),str(dest),str(dest/'source-after.json'),'--source-only','--compare-source-snapshot'],KIT,90)
    conf=re.search(r'Minimum number of measured time steps[^\n]*=\s*(\d+)',log)
    by_step={str(step):value for step,value in zip(range(2,51),timing)}
    early=[by_step[str(s)] for s in range(2,31)];late=[by_step[str(s)] for s in range(31,51)]
    row={'order':ORDER,'steps':STEPS,'intervals':INTERVALS,'mean_seconds_per_step':statistics.mean(timing),'median_seconds_per_step':statistics.median(timing),'p95_seconds_per_step':statistics.quantiles(timing,n=100,method='inclusive')[94],'maximum_seconds_per_step':max(timing),'final_Cd':cd[-1][1],'Cd_by_step':cd,'fixed_iterations':counts,'native_minimum_samples':int(conf[1]) if conf else None,'confidence_warning_present':'smaller than the calculated one' in log,'timings_seconds':timing,'timing_by_step_seconds':by_step,'descriptive_timing_segments':{'steps_2_to_30':{'samples':len(early),'mean_seconds':statistics.mean(early),'median_seconds':statistics.median(early)},'steps_31_to_50':{'samples':len(late),'mean_seconds':statistics.mean(late),'median_seconds':statistics.median(late)}}}
    bounded('kit-after',['sha256sum','-c','payload-sha256.txt'],KIT,30)
    result=single_arm_result(row)
    save(RUN/'result.json',result);print('SINGLE_ZYX_50STEP_HORIZON_EXTENSION_PASS')
if __name__=='__main__':main()
