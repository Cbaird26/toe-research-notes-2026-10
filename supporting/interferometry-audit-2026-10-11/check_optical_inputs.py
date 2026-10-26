"""Separate optical-input sensitivity; this is not a new-physics fit."""
from pathlib import Path
import json,hashlib,math
import numpy as np
import scipy.special as sp
import scipy.constants as co
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import reproduce_baseline as base

HERE=Path(__file__).resolve().parent


def stable_B(n,xi,g):
    a=g['reflectivity']*np.sin(np.pi*xi)*g['phi_0']
    b=g['reflectivity']*(np.sin(np.pi*xi/2)**2-g['ionization probability']/2)*g['n_0']
    if g['classical']:
        a=g['reflectivity']*np.pi*xi*g['phi_0']
        b=-g['reflectivity']*g['ionization probability']*g['n_0']/2
    phi=(-(g['reflectivity']**2+1)/4*g['n_0']+
          (1-g['ionization probability'])*(g['reflectivity']**2+1)/4*np.cos(np.pi*xi)*g['n_0'])
    k=abs(n)
    pref=((a+b)/2)**k if n>=0 else (-(a-b)/2)**k
    return np.exp(phi)*pref/math.factorial(k)*sp.hyp0f1(k+1,-(a*a-b*b)/4)


def main():
    result=json.loads((HERE/'baseline_results.json').read_text())
    scope=base.author_prefix();setup=scope['setup'];particle=scope['particle']
    setup['grating_1']['power']=np.mean([d['P_G1'] for d in scope['dataset']])
    setup['grating_3']['power']=np.mean([d['P_G3'] for d in scope['dataset']])
    powers=np.array(result['curve']['power_mW'])*1e-3
    particle['mass']=particle['m_mean']
    sigma_deposit=particle['sigma_abs_of_m']()
    # Formula printed in paper Methods; every other source input stays fixed.
    particle['sigma_abs_of_m']=lambda:(.537*particle['mass']/co.m_u/1000-1.5)*1e-20
    sigma_paper=particle['sigma_abs_of_m']()
    paper_curve=base.evaluate(setup,powers)
    # Independent entire-function form for the small integer harmonics in use.
    diffs=[]
    for xi in [0,.01,.2,.5,.99,1.,1.5]:
        for phi in [-10,-1,0,1,10]:
            for n0 in [0,.1,1,10]:
                g={'type':'laser','reflectivity':1.,'ionization probability':1.,
                   'phi_0':phi,'n_0':n0,'classical':False}
                for n in [-1,0,2]:
                    x=base.tl.B(n,xi,g);y=stable_B(n,xi,g)
                    diffs.append(abs(x-y))
    # Construct the singular-expression point analytically: a=b=-1.
    g={'type':'laser','reflectivity':1.,'ionization probability':1.,
       'phi_0':-2.,'n_0':2/math.cos(math.pi/6),'classical':False}
    cusp_original=base.tl.B(2,1/6,g);cusp_stable=stable_B(2,1/6,g)
    # Default near a=b may avoid the literal threshold because of rounding;
    # audit the limiting expression directly, without claiming typical bias.
    formal_limit=math.exp(-g['n_0']/2)/2
    assert abs(cusp_stable-formal_limit)<1e-12
    assert max(diffs)<1e-10
    fig,ax=plt.subplots(figsize=(8.4,4.8))
    ax.plot(powers*1e3,.78*np.array(result['curve']['quantum_visibility_unscaled']),color='#b84a3c',label='Deposited absorption formula')
    ax.plot(powers*1e3,.78*paper_curve[:,0],color='#276a65',label='Paper absorption formula; other inputs unchanged')
    b=result['bins']
    ax.errorbar([x['power_mW'] for x in b],[x['inverse_variance_mean'] for x in b],
                yerr=[x['inverse_variance_standard_error']*max(1,np.sqrt(x['reduced_chisquare_within_bin'] or 1)) for x in b],
                fmt='o',markersize=4,color='#25353a',label='Measured scans, declared symmetric reanalysis')
    ax.set(xlabel='Second-grating laser power (mW)',ylabel='Fringe visibility',xlim=(-1,72),ylim=(0,.13),
           title='Optical calibration changes the ordinary quantum prediction')
    ax.grid(alpha=.17);ax.legend(fontsize=8);fig.tight_layout()
    fig.savefig(HERE/'optical_input_sensitivity.png',dpi=180);plt.close(fig)
    out={'status':'documented_optical_input_sensitivity','new_field_fit':False,
         'source':'https://www.klaus-hornberger.de/pdf/nature2.pdf',
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'sigma_abs_deposit_at_mean_mass_m2':sigma_deposit,'sigma_abs_paper_at_mean_mass_m2':sigma_paper,
         'power_mW':list(powers*1e3),'paper_absorption_visibility':paper_curve[:,0].tolist(),
         'maximum_unscaled_visibility_change':float(np.max(abs(paper_curve[:,0]-result['curve']['quantum_visibility_unscaled']))),
         'entire_function_B_check':{'cases':len(diffs),'maximum_absolute_difference':float(max(diffs)),
                                   'near_cusp_original_real':float(cusp_original.real),'near_cusp_stable':float(cusp_stable),
                                   'analytic_limit':formal_limit},
         'limits':['The paper-input branch changes only one optical assumption; it is not the complete published fit.',
                   'Both curves retain the published 0.78 contrast factor explicitly.',
                   'This comparison demonstrates a baseline systematic that must be resolved before scalar inference.']}
    (HERE/'optical_input_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','sigma_abs_deposit_at_mean_mass_m2','sigma_abs_paper_at_mean_mass_m2','maximum_unscaled_visibility_change','entire_function_B_check']},indent=2))


if __name__=='__main__':main()
