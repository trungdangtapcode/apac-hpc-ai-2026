from pathlib import Path
import json,statistics
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');O=Path(__file__).parent
h200_jobs={52:['23904','23973','23975','24174'],54:['24131','24175','24189'],56:['24190','24235'],58:['24236']}
h200={n:[json.loads((R/'runs'/j/'summary.json').read_text())[0]['good_output_tokens_s'] for j in jobs] for n,jobs in h200_jobs.items()}
front=json.loads((R/'nscc-pbs/inspection/manual-20261017-0858/h100-frontier-comparison.json').read_text());h100={n:[next(p['good_output_tokens_s'] for p in rows if p['concurrency']==n) for rows in front['same_load_runs'].values()] for n in [48,50,52]}
factor=statistics.mean(h200[52])/statistics.mean(h100[52]);pred=statistics.mean(h100[50])*factor
sensitivity=[min(h100[50])*min(h200[52])/max(h100[52]),max(h100[50])*max(h200[52])/min(h100[52])]
data={'scope':'16GPU,officialFP8,plainPD2xTP4EP1prefill+TP8EP8decode,RR,NIXL,BF16KV,MNNVL+FlashInfer,full60/120/30,4000/200;hardware/launcher/nodes/seeds/time differ','h200_jobs':h200_jobs,'h100_jobs':list(front['same_load_runs']),'h200_good_tokens_s':h200,'h100_good_tokens_s':h100,'N52_H200_over_H100':factor,'predicted_H200_N50':pred,'minmax_input_sensitivity_NOT_CI':sensitivity,'h100_peak':max(h100[50]),'h100_best_mean':statistics.mean(h100[50]),'h200_best_mean':statistics.mean(h200[56]),'warnings':['OneconcurrencyanchorN52,nouniversaltransferfactor','SLAthresholdnonlinear,donotscaleSLA/TTFT/ITLfromgoodputratio','Observedrepeatrangedoesnotcapturemodelerror,node/interconnect/CPUdifferences','ForecastN50isnotmeasurementorofficialscore','H200N56andH100N50bestloadsaredifferent;absolutecomparisonisnotoptimizationgain','No99%organiseraccuracyclaim']}
(O/'data.json').write_text(json.dumps(data,indent=2)+'\n')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,3,figsize=(15,4.8),gridspec_kw={'width_ratios':[1.6,1,1.2]});fig.patch.set_facecolor('#f7f9fc')
colors={'h100':'#2368b5','h200':'#d67418','pred':'#7b4db3'}
ax=axes[0]
for vals,label,c in [(h100,'H100 — measured',colors['h100']),(h200,'H200 — measured',colors['h200'])]:
 ns=sorted(vals);ys=[statistics.mean(vals[n]) for n in ns];ax.plot(ns,ys,'o-',label=label,color=c,lw=2)
 for n in ns:ax.scatter([n]*len(vals[n]),vals[n],color=c,s=15,alpha=.5)
ax.errorbar([50],[pred],yerr=[[pred-sensitivity[0]],[sensitivity[1]-pred]],fmt='D',mfc='white',mec=colors['pred'],ecolor=colors['pred'],capsize=5,label='H200 N50 — ESTIMATE')
ax.axvline(52,color='#999999',linestyle=':',alpha=.6);ax.set(xlabel='Concurrent requests (N)',ylabel='Good output tokens / second',title='1. Measured load curves + forecast');ax.legend(fontsize=8,loc='lower right');ax.grid(axis='y',alpha=.15)
ax=axes[1];ax.bar(['H100','H200'],[100,100*factor],color=[colors['h100'],colors['h200']],width=.55)
for i,v in enumerate([100,100*factor]):ax.text(i,v+2,f'{v:.2f}',ha='center',fontweight='bold')
ax.set(ylim=(0,140),ylabel='H100 N52 = 100',title='2. SAME config + SAME N52');ax.text(.5,132,f'Empirical factor = {factor:.4f}x',ha='center',fontsize=10);ax.grid(axis='y',alpha=.15)
ax=axes[2];ys=[statistics.mean(h100[50]),pred,statistics.mean(h200[56])];bars=ax.bar(['H100\nN50','H200 N50\nESTIMATE','H200\nN56'],ys,color=[colors['h100'],colors['pred'],colors['h200']],width=.6);bars[1].set_hatch('///');bars[1].set_alpha(.45)
for i,v in enumerate(ys):ax.text(i,v+40,f'{v:,.1f}',ha='center',fontweight='bold')
ax.set(ylim=(0,3050),ylabel='Good output tokens / second',title='3. Best means / transferred estimate');ax.grid(axis='y',alpha=.15)
fig.suptitle('Qwen3-235B FP8: cross-platform comparison — 16 GPUs per trial',fontsize=15,fontweight='bold')
fig.text(.5,.015,'Means of retained runs; dots show individual runs. Estimate uses ONE matched N52 anchor. Sensitivity range is NOT a confidence interval.\nHardware, nodes and runtime differ; raw throughput is not a cross-platform competition ranking. Full organiser accuracy remains unverified.',ha='center',fontsize=8,color='#444444')
fig.tight_layout(rect=[0,.09,1,.94]);fig.savefig(O/'comparison.png',dpi=160,facecolor=fig.get_facecolor());fig.savefig(O/'comparison.svg',facecolor=fig.get_facecolor());plt.close(fig)
print(json.dumps({'factor':factor,'estimate':pred,'sensitivity':sensitivity,'h100_peak':max(h100[50]),'h100_mean':statistics.mean(h100[50]),'h200_mean':statistics.mean(h200[56])}))
# Report figure: distinguish matched data from within-platform tuning and forecast.
fig,axs=plt.subplots(1,3,figsize=(15,4.8));fig.patch.set_facecolor('#f7f9fc')
a=axs[0]
for i,(values,label,color) in enumerate([(h100[52],'H100 N52',colors['h100']),(h200[52],'H200 N52',colors['h200'])]):
 mean=statistics.mean(values);a.bar(i,mean,color=color,alpha=.75,width=.55);a.scatter([i]*len(values),values,color='black',s=25,zorder=4);a.text(i,mean+65,f'{mean:,.2f}\nn={len(values)} jobs',ha='center',fontsize=10)
a.set(xticks=[0,1],xticklabels=['H100 N52','H200 N52'],ylim=(0,3200),ylabel='Good output tokens / second',title='A. Matched combo + SAME N52');a.text(.5,3050,f'System ratio = {factor:.4f}x',ha='center',fontsize=9);a.grid(axis='y',alpha=.15)
a=axs[1]
for vals,label,color in [(h100,'H100',colors['h100']),(h200,'H200',colors['h200'])]:
 ns=sorted(vals);anchor=statistics.mean(vals[52]);a.plot(ns,[100*statistics.mean(vals[n])/anchor for n in ns],'o-',color=color,label=label)
a.axhline(100,color='#999999',ls=':');a.axvline(52,color='#999999',ls=':');a.set(xlabel='Concurrent requests (N)',ylabel='OWN platform N52 = 100',title='B. Load tuning within each system');a.legend();a.grid(alpha=.15)
a=axs[2]
a.bar(0,pred,color=colors['pred'],alpha=.35,hatch='///',width=.6)
a.text(0,pred+80,f'{pred:,.2f}\nFROZEN FORECAST',ha='center',fontsize=10)
validation_path=O/'holdout-validation.json'
validation=json.loads(validation_path.read_text()) if validation_path.exists() else {}
actual=validation.get('actual_good_output_tokens_s')
if actual is not None:
    a.bar(1,actual,color=colors['h200'],width=.6)
    a.text(1,actual+80,f'{actual:,.2f}\nMEASURED',ha='center',fontsize=10)
    a.text(.5,3100,f"Error: {validation['signed_error_percent']:+.2f}% (2% operational check)",ha='center',fontsize=9)
else:
    a.text(1,1400,'Job 24272\nPENDING\nNO MEASUREMENT',ha='center',fontsize=10)
a.set(xticks=[0,1],xticklabels=['N50 prediction','N50 holdout'],ylim=(0,3350),ylabel='Good output tokens / second',title='C. Held-out N50 prediction check')
a.set_xlim(-.6,1.6);a.grid(axis='y',alpha=.15)
fig.suptitle('Matched cross-platform analysis — SAME Qwen FP8 / PD / MNNVL+FlashInfer / AIPerf protocol',fontsize=13,fontweight='bold')
fig.text(.5,.018,'A: GPU/runtime/seed/node/time differ; system association, not GPU-only causal speedup. B: normalized load tuning, not a contest ranking.\nC: ONE calibration concurrency (N52). No 95% prediction interval. Best observed H100 N50: 2229.83; two-run mean: 2223.93. See REPORT.md.',ha='center',fontsize=8)
fig.tight_layout(rect=[0,.10,1,.93]);fig.savefig(O/'matched-comparison.png',dpi=160,facecolor=fig.get_facecolor());fig.savefig(O/'matched-comparison.svg',facecolor=fig.get_facecolor());plt.close(fig)
