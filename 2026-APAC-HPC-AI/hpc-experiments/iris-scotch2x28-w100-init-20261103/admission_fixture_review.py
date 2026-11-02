"""Verify one-shot financial admission using isolated temporary files and fake RPCs only."""
from pathlib import Path
import contextlib,io,json,tempfile
import deploy_submit as admission


def check(uncertain):
    saved={key:getattr(admission,key) for key in ['E','C','run_json']}
    try:
        with tempfile.TemporaryDirectory(prefix='scotch228-admission-fixture-') as folder:
            base=Path(folder);admission.E=base/'experiment';admission.C=base/'ledger';admission.E.mkdir();admission.C.mkdir()
            files={'init.py':'fixture-only'}
            (admission.E/'deployment.json').write_text(json.dumps({'root':'/fixture-not-a-real-deployment','files':files}))
            (admission.E/'ROOT_REVIEW.json').write_text(json.dumps({'passed':True,'payload_sha256':files}))
            parent=base/'iris-scotch2x28-init-20261102/completed-2294657';parent.mkdir(parents=True)
            prior=json.dumps({'passed':True,'native_cut_offline_replay_passed':True,'job_id':'2294657'});(parent/'REVIEW.json').write_text(prior);root_review=json.loads((admission.E/'ROOT_REVIEW.json').read_text());root_review['parent_review_sha256']=__import__('hashlib').sha256(prior.encode()).hexdigest();(admission.E/'ROOT_REVIEW.json').write_text(json.dumps(root_review))
            budget={'cluster':'Iris','account':'rdmaworkshop','consumed_planning_allowance_allocated_CPU_hours':944,'reserved_maximum_allocated_CPU_hours':0,'branch_planning_ceiling_allocated_CPU_hours':1009,'jobs':[{'job_id':'fixture-parent','reservation_retired':True}]}
            (admission.C/'budget.json').write_text(json.dumps(budget));calls=[]
            def fake_remote(body,timeout):
                calls.append(body)
                if len(calls)==1:return {'host':'fixture','queue':''}
                assert len(calls)==2 and body.count("['sbatch'")==1
                assert (admission.E/'submission-intent.json').exists()
                live=json.loads((admission.C/'budget.json').read_text())
                assert live['reserved_maximum_allocated_CPU_hours']==28 and live['jobs'][-1]['maximum_allocated_CPU_hours']==28
                return {'returncode':0,'stdout':'' if uncertain else '999901\n','stderr':''}
            admission.run_json=fake_remote
            with contextlib.redirect_stdout(io.StringIO()):
                try:admission.submit(files)
                except AssertionError:
                    assert uncertain
                else:assert not uncertain
            try:admission.submit(files)
            except AssertionError:pass
            else:raise AssertionError('Repeated submission accepted')
            assert len(calls)==2
            live=json.loads((admission.C/'budget.json').read_text());assert live['reserved_maximum_allocated_CPU_hours']==28
    finally:
        for k,v in saved.items():setattr(admission,k,v)


if __name__=='__main__':
    check(False);check(True)
    out=Path(__file__).resolve().parent/'admission-fixture-review.json'
    report={'passed':True,'real_scheduler_calls':0,'real_budget_mutations':False,'checks':['Durable local intent and 28 CPU-hour reservation precede exactly one fake sbatch','Successful and uncertain fake responses both reject replay','Uncertain response retains full maximum','Fresh reviewed cut ownership and source eligibility fixtures required'],'note':'999901 is only a fake job ID inside temporary fixture files, not an accepted experiment.'}
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
