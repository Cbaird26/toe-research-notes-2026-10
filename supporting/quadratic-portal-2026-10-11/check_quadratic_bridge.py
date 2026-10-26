#!/usr/bin/env python3
"""Conditional quadratic Higgs-portal / thermal-bath calculation.

All outputs are theoretical quadratures, never laboratory observations.
Natural units hbar=c=k_B=1. The model assumes one free massive real scalar
in a homogeneous Bose thermal state with zero chemical potential, and one
heavy fixed-path probe. The decoherence result is leading weak-coupling
Markov order, not an exact Gaussian influence functional for phi**2.

Dependencies: numpy, mpmath; matplotlib only for --plot.
Run: python check_quadratic_bridge.py --plot
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
import mpmath as mp

HERE = Path(__file__).resolve().parent
PI = math.pi


def quadrature_grid(end, width=1.0, order=32):
    x, w = np.polynomial.legendre.leggauss(order)
    edges = np.linspace(0.0, end, int(math.ceil(end / width)) + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    halves = np.diff(edges) / 2
    return ((centers[:, None] + halves[:, None] * x).ravel(),
            (halves[:, None] * np.broadcast_to(w, (len(halves), order))).ravel())


U, UW = quadrature_grid(80, width=0.25, order=64)
Q, QW = quadrature_grid(200)


def one_minus_sinc_sq(z):
    z = np.asarray(z)
    small = abs(z) < 1e-3
    z2 = z * z
    return np.where(small, z2 / 3 - 2 * z2**2 / 45 + z2**3 / 315,
                    1 - np.sinc(z / PI)**2)


def one_minus_sinc(z):
    z = np.asarray(z)
    z2 = z * z
    return np.where(abs(z) < 1e-3, z2 / 6 - z2**2 / 120 + z2**3 / 5040,
                    1 - np.sinc(z / PI))


def energy_spectrum(x, y=0.0, difference=False, cutoff=None):
    """Return exp(x)*S(0,r)/T**3, or exp(x)*[S00-S0r]/T**3.

    x=m/T>0, y=r*T. Variable u=E/T-x. cutoff=Lambda/T inserts
    F(k)^4=exp(-2*k**2/Lambda**2) for F=exp(-k**2/(2*Lambda**2)).
    """
    if x <= 0 or y < 0:
        raise ValueError("Require m/T>0 and r*T>=0")
    k2 = U * (2 * x + U)
    weight = k2 * np.exp(-U) / (-np.expm1(-x - U))**2
    z = y * np.sqrt(k2)
    kernel = one_minus_sinc_sq(z) if difference else np.sinc(z / PI)**2
    if cutoff is not None:
        if cutoff <= 0:
            raise ValueError("cutoff must be positive")
        weight *= np.exp(-2 * k2 / cutoff**2)
    return float(np.dot(UW, weight * kernel) / (2 * PI**3))


def transfer_spectrum(x, y=0.0, difference=False):
    """Independent momentum-transfer integral from S_tilde(0,Q).

    exp(x)*S/T**3 = int dq q exp(x-Eq)/(1-exp(-Eq))*sinc(q*y)/(4pi**3).
    """
    eq = np.sqrt(x*x + Q*Q/4)
    occupation = np.exp(x-eq) / (-np.expm1(-eq))
    kernel = one_minus_sinc(Q*y) if difference else np.sinc(Q*y/PI)
    return float(np.dot(QW, Q * occupation * kernel) / (4 * PI**3))


def closed_local(x):
    mp.mp.dps = 60
    xx = mp.mpf(str(x))
    z = mp.exp(-xx)
    return float(mp.exp(xx)*(-xx*mp.log1p(-z)+mp.polylog(2,z))/mp.pi**3)


def small_separation_coefficient(x):
    """exp(x)*Gamma/(g**2*T**3*y**2) in the y->0 limit."""
    k2 = U * (2*x+U)
    return float(np.dot(UW, k2*k2*np.exp(-U)/(-np.expm1(-x-U))**2)/(6*PI**3))


def collision_integral(x, y):
    """Independent gas-flux calculation: sigma=g**2/pi; Bose enhancement.

    Returns exp(x)*Gamma/(g**2*T**3). Integrate momentum k/T directly,
    with d^3k/(2pi)^3, flux k/E, and isotropic distinguishability.
    """
    k, w = Q, QW
    e = np.sqrt(k*k+x*x)
    occ = np.exp(x-e)/(-np.expm1(-e))**2
    phase = one_minus_sinc_sq(k*y)
    return float(np.dot(w, k*k*(k/e)*occ*phase)/(2*PI**3))


def mixed_rate(masses, coupling, y, width=0.125, local_spectrum=False):
    """Two/multi-scalar gamma/T**3; C entries carry inverse-energy units.

    T is set to 1 for this dimensionless check. The ordered pair sum retains
    both off-diagonal terms. Equal-temperature independent Gaussian mass modes.
    Threshold substitution E=max(m_i,m_j)+z**2 removes endpoint square roots.
    """
    masses=np.asarray(masses,dtype=float)
    coupling=np.asarray(coupling,dtype=float)
    if min(masses)<=0 or coupling.shape!=(len(masses),len(masses)):
        raise ValueError('Positive masses and matching coupling matrix required')
    if not np.allclose(coupling,coupling.T,atol=1e-14,rtol=0):
        raise ValueError('Real symmetric coupling required')
    z,w=quadrature_grid(math.sqrt(80),width=width,order=32)
    total=0.0
    for i,mi in enumerate(masses):
        for j,mj in enumerate(masses):
            lower=max(mi,mj)
            e=lower+z*z
            ki=np.sqrt((e-mi)*(e+mi));kj=np.sqrt((e-mj)*(e+mj))
            # 1-si*sj = (1-si)+(1-sj)-(1-si)*(1-sj) is stable at small r.
            ai=one_minus_sinc(ki*y);aj=one_minus_sinc(kj*y)
            phase=np.ones_like(e) if local_spectrum else ai+aj-ai*aj
            occ=np.exp(-e)/(-np.expm1(-e))**2
            total+=coupling[i,j]**2*np.dot(w,2*z*ki*kj*occ*phase)
    return float(total/(2*PI**3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    records = []
    errors = dict(local_closed_form=0.0, spatial_fourier=0.0,
                  collision_flux=0.0, small_separation=0.0,
                  resolution_doubling=0.0)
    for x in [0.1, 1.0, 10.0, 30.0]:
        s0 = energy_spectrum(x)
        errors['local_closed_form'] = max(errors['local_closed_form'], abs(s0/closed_local(x)-1))
        for y in [0.0, 1e-4, 0.1, 1.0, 3.0, 10.0]:
            s = energy_spectrum(x,y)
            g = energy_spectrum(x,y,True)
            sf = transfer_spectrum(x,y)
            gf = transfer_spectrum(x,y,True)
            gc = collision_integral(x,y)
            assert 0 <= g <= s0*(1+1e-12)
            assert abs((s+g)/s0-1) < 1e-12
            assert min(s0-s,s0+s) >= -1e-12*s0
            errors['spatial_fourier'] = max(errors['spatial_fourier'], abs(s-sf)/s0, abs(g-gf)/s0)
            errors['collision_flux'] = max(errors['collision_flux'], abs(g-gc)/s0)
            if y == 1e-4:
                errors['small_separation'] = max(errors['small_separation'], abs(g/(y*y*small_separation_coefficient(x))-1))
            records.append(dict(m_over_T=x,r_times_T=y,
                                normalized_rate=g/s0,scaled_local_spectrum=s0))
    assert errors['local_closed_form'] < 1e-10, errors
    assert errors['spatial_fourier'] < 1e-8, errors
    assert errors['collision_flux'] < 1e-8, errors
    assert errors['small_separation'] < 2e-6, errors

    # Recompute using double quadrature resolution, rather than relying on one grid.
    global U,UW,Q,QW
    saved = U,UW,Q,QW
    U,UW = quadrature_grid(100,width=0.125,order=64)
    Q,QW = quadrature_grid(240,width=0.5,order=32)
    for row in records:
        x,y = row['m_over_T'],row['r_times_T']
        v = energy_spectrum(x,y,True)/energy_spectrum(x)
        errors['resolution_doubling'] = max(errors['resolution_doubling'],abs(v-row['normalized_rate']))
    U,UW,Q,QW = saved
    assert errors['resolution_doubling'] < 1e-9

    # Limiting checks use distinct analytic information.
    low_t_x = 30.0
    low_t_error = abs(closed_local(low_t_x)/((low_t_x+1)/PI**3)-1)
    assert low_t_error < 1e-12
    high_t_x = 1e-5
    high_t_error = abs(closed_local(high_t_x)*math.exp(-high_t_x)/(1/(6*PI))-1)
    assert high_t_error < 1e-4
    # The vacuum rate is zero because every term contains a thermal occupation;
    # no test here claims to rule out finite-time vacuum dressing.

    # Fourier positivity implies PSD for every finite set of positions. Check one
    # nontrivial configuration numerically, not merely the two-path diagonal case.
    rng = np.random.default_rng(20261011)
    positions = rng.normal(size=(8,3))
    distances = np.linalg.norm(positions[:,None,:]-positions[None,:,:],axis=2)
    covariance = np.array([[energy_spectrum(1.0,float(d)) for d in row] for row in distances])
    eig = np.linalg.eigvalsh(covariance)
    assert eig.min() >= -1e-12

    cutoffs = [5.,10.,20.,50.,100.]
    regulated = [energy_spectrum(1.,1.,True,c)/energy_spectrum(1.,1.,True) for c in cutoffs]
    assert all(0 < a < b < 1 for a,b in zip(regulated,regulated[1:]))
    # Independent matching check: differentiate the eliminated-Higgs action.
    # Arbitrary dimensionless algebra inputs, not a physical benchmark.
    mp.mp.dps=60
    kap,v,mh,mf,M=map(mp.mpf,['0.2','3','5','0.7','100'])
    action=lambda phi,density: (kap*v*phi**2/2+mf*density/v)**2/(2*mh**2)
    vertex=mp.diff(lambda phi:mp.diff(lambda density:action(phi,density),0),0,2)
    matched=kap*mf/(2*mh**2)
    assert abs(vertex-2*matched)<mp.mpf('1e-55')
    sigma_from_vertex=(vertex*2*M)**2/(16*mp.pi*M**2)
    sigma_from_matching=matched**2/mp.pi
    matching_error=float(abs(sigma_from_vertex/sigma_from_matching-1))
    assert matching_error<1e-50
    wrong_vertex_rate_ratio=float(((matched*2*M)**2/(16*mp.pi*M**2))/sigma_from_vertex)
    # Artificially declaring equal means a null fails: homogeneous bath, r*T=1.
    equal_mean_rate_fraction = energy_spectrum(1.,1.,True)/energy_spectrum(1.)
    assert equal_mean_rate_fraction > 0.1

    matrix=np.array([[0.7,0.2],[0.2,-0.4]])
    angle=0.731
    rotation=np.array([[math.cos(angle),-math.sin(angle)],
                       [math.sin(angle),math.cos(angle)]])
    rotated=rotation.T@matrix@rotation
    degenerate=mixed_rate([1.,1.],matrix,0.8)
    expected=float(np.trace(matrix@matrix))*math.exp(-1)*energy_spectrum(1.,0.8,True)
    mixed_checks={'degenerate_reduction_relative_error':abs(degenerate/expected-1),
       'degenerate_rotation_relative_error':abs(mixed_rate([1.,1.],rotated,0.8)/degenerate-1)}
    unequal=mixed_rate([0.7,2.1],matrix,0.8)
    mixed_checks['unequal_mass_resolution_relative_error']=abs(mixed_rate([0.7,2.1],matrix,0.8,width=0.0625)/unequal-1)
    mixed_checks['unequal_mass_rate_T1']=unequal
    assert all(mixed_checks[k]<1e-10 for k in mixed_checks if 'error' in k)
    assert unequal>0 and mixed_rate([0.7,2.1],matrix,0.)==0
    offdiag=np.array([[0.,1.],[1.,0.]])
    y_negative=0.02*1.5*PI/math.sqrt(3)
    negative_local=mixed_rate([50.,100.],offdiag,0.,local_spectrum=True)
    overshoot=mixed_rate([50.,100.],offdiag,y_negative)/negative_local
    assert 1.17<overshoot<1.19
    mixed_checks['mixed_rate_over_local_counterexample']=overshoot

    report = {
        'status':'conditional_calculation_checks_passed',
        'evidence_class':'analytic_derivation_and_deterministic_numerical_checks',
        'laboratory_data_used':False,'theory_of_everything_completed':False,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'versions':{'numpy':np.__version__,'mpmath':mp.__version__},
        'checks':errors,'grid_cases':len(records),
        'low_temperature_leading_error':low_t_error,
        'massless_limit_error':high_t_error,
        'spatial_covariance_min_eigenvalue':float(eig.min()),
        'mixed_scalar_checks':mixed_checks,
        'portal_vertex_cross_section_relative_error':matching_error,
        'cutoff_over_temperature':cutoffs,'regulated_rate_fraction':regulated,
        'negative_controls':{'wrong_vertex_rate_ratio':wrong_vertex_rate_ratio,
          'equal_means_but_nonzero_rate_fraction':equal_mean_rate_fraction},
        'grid':records,
        'assumptions':['free scalar mass eigenmodes; heavy unmixed Higgs matching',
          'free homogeneous thermal scalar, zero chemical potential, m>0',
          'fixed paths, heavy probe, negligible recoil and bath backreaction',
          'regulated weak-coupling Markov limit, leading second order only'],
        'open':['actual scalar state and abundance','laboratory apparatus and nuisance likelihood',
          'interacting/unequal-temperature scalar baths','radiative stability and UV completion',
          'finite-time renormalized dynamics beyond the leading thermal rate']}
    (HERE/'checks.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='grid'},indent=2))
    if args.plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        ys=np.geomspace(1e-3,10,180)
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
        fig,ax=plt.subplots(figsize=(7.0,3.6),layout='constrained')
        colors=['#216869','#335c81','#a65a3c']
        for x,color in zip([0.1,1.,10.],colors):
            vals=[energy_spectrum(x,float(y),True)/energy_spectrum(x) for y in ys]
            ax.plot(ys,vals,label=f'm/T = {x:g}',color=color,lw=2)
        ax.set(xscale='log',xlabel=r'Path separation $rT$ (natural units)',
               ylabel=r'$\gamma(r)\,/\,\gamma(\infty)$',ylim=(0,1.04))
        ax.set_title('Conditional thermal scattering: quadratic growth, then saturation',loc='left',fontsize=11)
        ax.axhline(1,color='#999999',lw=.7,ls='--')
        ax.grid(alpha=.17);ax.legend(frameon=False)
        for side in ['top','right']: ax.spines[side].set_visible(False)
        fig.savefig(HERE/'rate_shape.pdf')
        fig.savefig(HERE/'rate_shape.png',dpi=180)
        plt.close(fig)


if __name__=='__main__':
    main()
