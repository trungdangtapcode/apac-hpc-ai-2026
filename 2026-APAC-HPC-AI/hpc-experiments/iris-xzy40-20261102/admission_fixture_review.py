"""Offline one-shot submission and budget safety fixtures; no real cluster calls."""
from pathlib import Path
import contextlib,io,json,tempfile
import admit


def rejected(call):
    try:call()
    except (AssertionError,ValueError,KeyError):return
    raise AssertionError('Unsafe fixture accepted')


def fixture(uncertain):
    old={name:getattr(admit,name) for name in ['E','C','reviewed','run_json']}
    try:
        with tempfile.TemporaryDirectory(prefix='xzy40-admission-fixture-') as folder:
            base=Path(folder);admit.E=base/'experiment';admit.C=base/'ledger';admit.E.mkdir();admit.C.mkdir();files={'run.py':'fixture-only'}
            remote='/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-xzy40-20261102T000000Z'
            (admit.E/'deployment.json').write_text(json.dumps({'root':remote,'payload_sha256':files}))
            budget={'cluster':'Iris','account':'rdmaworkshop','branch_planning_ceiling_allocated_CPU_hours':890,'consumed_planning_allowance_allocated_CPU_hours':750,'reserved_maximum_allocated_CPU_hours':0,'jobs':[]}
            (admit.C/'budget.json').write_text(json.dumps(budget));admit.reviewed=lambda:files;calls=[]
            def fake(body,timeout):
                calls.append(body)
                if len(calls)==1:return {'queue':'','utc':'fixture'}
                assert len(calls)==2 and body.count("['sbatch'")==1 and '--dependency=' not in body
                assert (admit.E/'submission-intent.json').exists()
                live=json.loads((admit.C/'budget.json').read_text());assert live['reserved_maximum_allocated_CPU_hours']==140
                assert live['jobs'][-1]['maximum_allocated_CPU_hours']==140
                response={'returncode':0,'stdout':'' if uncertain else '999902\n','root':remote}
                if not uncertain:response['job_id']='999902'
                return response
            admit.run_json=fake
            with contextlib.redirect_stdout(io.StringIO()):
                if uncertain:rejected(lambda:admit.submit(files))
                else:assert admit.submit(files)['job_id']=='999902'
            rejected(lambda:admit.submit(files));assert len(calls)==2
            live=json.loads((admit.C/'budget.json').read_text());assert live['reserved_maximum_allocated_CPU_hours']==140
            if uncertain:assert (admit.E/'submission-uncertain.json').exists()
    finally:
        for name,value in old.items():setattr(admit,name,value)


if __name__=='__main__':
    base={'cluster':'Iris','account':'rdmaworkshop','branch_planning_ceiling_allocated_CPU_hours':890,'consumed_planning_allowance_allocated_CPU_hours':750,'reserved_maximum_allocated_CPU_hours':0,'jobs':[]}
    assert admit.financial(base)['new_maximum_CPU_hours']==140
    rejected(lambda:admit.financial(dict(base,branch_planning_ceiling_allocated_CPU_hours=889)))
    rejected(lambda:admit.financial(dict(base,jobs=[{'job_id':'unreconciled'}])))
    rejected(lambda:admit.financial(dict(base,consumed_planning_allowance_allocated_CPU_hours=float('nan'))))
    assert admit.queue_allowed('');rejected(lambda:admit.queue_allowed('2294642|tu-iris-xzyinit|RUNNING\n'))
    fixture(False);fixture(True)
    report={'passed':True,'real_scheduler_calls':0,'real_budget_mutations':False,'checks':['Exact maximum affordability; old insufficient stage rejects','Outstanding own row, NaN finances and existing own job reject','Durable local intent plus140 CPU-hour reservation before exactly one fake sbatch','Success and unknown response both reject replay; unknown retains full maximum'],'fixture_job_id_note':'999902 appears only in temporary mocked files, not in a real receipt.'}
    (Path(__file__).resolve().parent/'admission-fixture-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
