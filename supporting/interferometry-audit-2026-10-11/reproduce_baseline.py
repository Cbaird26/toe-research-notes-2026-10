"""Audit and reproduce the deposited sodium-cluster baseline, not a new-field fit.

Source: Pedalino et al., Zenodo 17502163, CC BY 4.0. The supplied source
and observations are kept unchanged. Only its analysis prefix is executed,
with plot_data=False in memory; the supplied Talbot-Lau kernel is reused.
Independent linear least squares cross-checks each nonlinear fringe fit.
"""
from pathlib import Path
import os
import sys
import json
import hashlib
import time
import numpy as np
import scipy
import scipy.constants as co
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
AUTHOR = HERE / 'author_source/Na-Cluster-Interference'
sys.path.insert(0, str(AUTHOR))
import talbotlau as tl


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def author_prefix():
    source = (AUTHOR / 'PowerScans_April2025.py').read_text()
    assert source.count('Ps = np.linspace') == 1
    source = source.split('Ps = np.linspace', 1)[0]
    assert source.count('plot_data = True') == 1
    source = source.replace('plot_data = True', 'plot_data = False')
    scope = {'__name__': '__reproduction_prefix__'}
    previous = Path.cwd()
    try:
        os.chdir(AUTHOR)
        exec(compile(source, str(AUTHOR / 'PowerScans_April2025.py'), 'exec'), scope)
    finally:
        os.chdir(previous)
    return scope


def linear_fit(data, period):
    x, y = data['xs'], data['counts']
    X = np.column_stack((np.ones(len(x)), np.cos(2*np.pi*x/period),
                         np.sin(2*np.pi*x/period)))
    coeff, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    assert rank == 3
    residual = y-X@coeff
    covariance = np.linalg.inv(X.T@X) * (residual@residual)/(len(x)-3)
    a, b, c = coeff
    amplitude = np.hypot(b, c)
    grad = np.array([-amplitude/a**2, b/(a*amplitude), c/(a*amplitude)])
    return {'mean_counts': float(a), 'visibility': float(amplitude/a),
            'visibility_sigma': float(np.sqrt(grad@covariance@grad)),
            'phase': float(np.arctan2(-c, b)),
            'residual_sum_squares': float(residual@residual),
            'residual_variance_over_mean': float(np.var(residual, ddof=3)/a)}


def evaluate(setup, powers, n_velocity=15, classical=False):
    setup['grating_2']['classical'] = classical
    results=[]
    for power in powers:
        setup['grating_2']['power'] = float(power)
        v, t = tl.Vis_av(setup, type='sin', current=False, N_sample=n_velocity)
        results.append([float(v),float(t)])
    setup['grating_2']['classical'] = False
    return np.asarray(results)


def main():
    start=time.monotonic()
    scope=author_prefix()
    dataset=scope['dataset'];setup=scope['setup'];particle=scope['particle']
    assert len(dataset)==95 and all(len(d['counts'])==41 for d in dataset)
    records=[]
    for d in dataset:
        independent=linear_fit(d, scope['period'])
        restart, _=curve_fit(scope['model'],d['xs'],d['counts'],
                            p0=[independent['mean_counts'],independent['visibility'],independent['phase']],
                            bounds=([d['counts'].min(),0,-np.pi],[d['counts'].max(),1,np.pi]))
        records.append({'name':d['name'],'power_G1_mW':float(d['P_G1']*1e3),
                        'power_G2_mW':float(d['P_G2']*1e3),'power_G3_mW':float(d['P_G3']*1e3),
                        'author_visibility':float(d['V_fit']),
                        'author_visibility_sigma':float(d['V_fit_err']),
                        'author_phase':float(d['phase_fit']),
                        'phase_boundary_solution':bool(abs(abs(d['phase_fit'])-np.pi)<1e-7),
                        'restarted_nonlinear_visibility':float(restart[1]),
                        'independent_linear_fit':independent})
    differences=np.array([abs(d['author_visibility']-d['independent_linear_fit']['visibility']) for d in records])
    print('95 fringe fits complete; maximum visibility difference',differences.max(),flush=True)
    bins=[]
    for i in range(len(scope['bins'])-1):
        mask=scope['bin_indices']==i
        if not mask.any():continue
        v=scope['expVfits'][mask];sigma=scope['expVfit_errs'][mask];n=len(v)
        w=1/sigma**2;mean=float(np.sum(w*v)/np.sum(w))
        redchi=float(np.sum(w*(v-mean)**2)/(n-1)) if n>1 else None
        bins.append({'power_mW':float(scope['expPs'][mask].mean()*1e3),'n':int(n),
                     'deposited_arithmetic_mean':float(v.mean()),
                     'deposited_RMS_uncertainty':float(np.linalg.norm(sigma)/np.sqrt(n)),
                     'arithmetic_mean_standard_error_if_independent':float(np.linalg.norm(sigma)/n),
                     'inverse_variance_mean':mean,'inverse_variance_standard_error':float(1/np.sqrt(w.sum())),
                     'reduced_chisquare_within_bin':redchi,
                     'status':'symmetric covariance-based comparison; not the published asymmetric-CI analysis'})
    setup['grating_1']['power']=float(np.mean([d['P_G1'] for d in dataset]))
    setup['grating_3']['power']=float(np.mean([d['P_G3'] for d in dataset]))
    bin_powers=np.array([b['power_mW'] for b in bins])*1e-3
    powers=np.unique(np.r_[np.linspace(0,70e-3,71),bin_powers])
    print('Evaluating baseline with',len(particle['masses']),'mass samples and',len(powers),'powers',flush=True)
    quantum=evaluate(setup,powers)
    print('Quantum curve done',flush=True)
    classical=evaluate(setup,powers,classical=True)
    print('Classical curve done',flush=True)
    indices=[int(np.argmin(abs(powers-p))) for p in bin_powers]
    for b,i in zip(bins,indices):
        b['quantum_unscaled']=float(quantum[i,0]);b['classical_unscaled']=float(classical[i,0])
        b['quantum_times_published_factor']=float(.78*quantum[i,0])
        b['classical_times_published_factor']=float(.78*classical[i,0])
    # A convergence check samples three physically different parts of the curve.
    selected=np.array([5.,15.,40.])*1e-3
    coarse=evaluate(setup,selected,15);fine=evaluate(setup,selected,39)
    doubled=evaluate(setup,selected,79)
    convergence={'powers_mW':list(selected*1e3),'visibility_N15':coarse[:,0].tolist(),
                 'visibility_N39':fine[:,0].tolist(),'visibility_N79':doubled[:,0].tolist(),
                 'max_absolute_N15_N39':float(np.max(abs(coarse[:,0]-fine[:,0]))),
                 'max_absolute_N39_N79':float(np.max(abs(fine[:,0]-doubled[:,0])))}
    restarted_difference=max(abs(d['restarted_nonlinear_visibility']-d['independent_linear_fit']['visibility']) for d in records)
    assert restarted_difference<1e-8, 'Restarted nonlinear fits disagree with independent convex linear fits'
    assert all(0<=x<=1 for x in quantum[:,0])
    fig,ax=plt.subplots(figsize=(8.4,4.8))
    ax.plot(powers*1e3,.78*quantum[:,0],color='#b84a3c',label='Quantum kernel × published 0.78 factor')
    ax.plot(powers*1e3,.78*classical[:,0],'--',color='#36648b',label='Classical kernel × published 0.78 factor')
    ax.errorbar([b['power_mW'] for b in bins],[b['inverse_variance_mean'] for b in bins],
                yerr=[b['inverse_variance_standard_error']*max(1,np.sqrt(b['reduced_chisquare_within_bin'] or 1)) for b in bins],
                fmt='o',markersize=4,color='#163c45',label='Raw scans: independently checked fringe fits')
    ax.set(xlabel='Second-grating laser power (mW)',ylabel='Fringe visibility',
           title='Deposited-model reproduction with explicit contrast scaling',xlim=(-1,72),ylim=(0,.2))
    ax.grid(alpha=.17);ax.legend(fontsize=8);fig.tight_layout()
    fig.savefig(HERE/'baseline_comparison.png',dpi=180);plt.close(fig)
    result={'status':'baseline_and_data_audit_completed_with_documented_limits',
            'new_field_fit_performed':False,'theory_of_everything_completed':False,
            'source':'https://zenodo.org/records/17502163',
            'article':'https://doi.org/10.1038/s41586-025-09917-9',
            'source_license':'CC BY 4.0','source_code_sha256':{p.name:sha(p) for p in AUTHOR.glob('*.py')},
            'analysis_script_sha256':sha(__file__),
            'versions':{'numpy':np.__version__,'scipy':scipy.__version__},
            'scan_count':len(records),'point_count':sum(len(d['counts']) for d in dataset),
            'mass_mean_kg':float(particle['m_mean']),'mass_mean_Da':float(particle['m_mean']/co.m_u),
            'mass_samples':len(particle['masses']),
            'beam_speed_m_per_s':setup['v_mean'],'beam_speed_sigma_m_per_s':setup['sigma_v'],
            'grating_spacing_m':setup['L_1'],'grating_period_m':scope['period'],
            'flight_time_s_at_mean_speed':float((setup['L_1']+setup['L_2'])/setup['v_mean']),
            'maximum_fringe_visibility_disagreement':float(differences.max()),
            'maximum_restarted_visibility_disagreement':float(restarted_difference),
            'phase_boundary_scans':[d['name'] for d in records if d['phase_boundary_solution']],
            'maximum_default_difference_over_fit_sigma':float(max(abs(d['author_visibility']-d['independent_linear_fit']['visibility'])/d['author_visibility_sigma'] for d in records)),
            'bins':bins,'scans':records,'velocity_convergence':convergence,
            'curve':{'power_mW':(powers*1e3).tolist(),'quantum_visibility_unscaled':quantum[:,0].tolist(),
                     'classical_visibility_unscaled':classical[:,0].tolist(),'transmission_quantum':quantum[:,1].tolist()},
            'limits':['Not an exact reproduction of the published figure: asymmetric intervals and uncertainty bands are not reconstructed.',
                      'The published global visibility factor 0.78 is retained explicitly, not refitted or interpreted as a scalar effect.',
                      'Deposited arithmetic bin means and RMS errors differ from the paper Methods.',
                      'Three default nonlinear fits stop at the phase boundary; restarting from the independent linear solution resolves the small discrepancies.',
                      'The deposited absorption formula also differs from the published Methods; this curve uses the deposited formula unchanged.',
                      'Illustrative comparison uses symmetric inverse-variance averages, with errors multiplied by max(1,sqrt(reduced chi-square)).',
                      'Amplitude estimates have a positive-noise bias near zero visibility; no scalar significance or exclusion is computed.',
                      'Kernel reuse does not independently verify every optical-model formula or apparatus systematic.',
                      'A moving composite probe and its bath-frame spectrum must be derived before using the portal rate.'],
            'runtime_seconds':time.monotonic()-start}
    (HERE/'baseline_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','scan_count','point_count','mass_mean_Da','flight_time_s_at_mean_speed','maximum_fringe_visibility_disagreement','velocity_convergence','runtime_seconds']},indent=2),flush=True)


if __name__=='__main__':main()
