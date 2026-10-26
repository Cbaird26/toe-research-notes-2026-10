"""Dimensionless checks of the conditional moving-probe quadratic spectrum.

Natural units, T=1, and unit total scalar charge. No experimental fitting.
"""
from pathlib import Path
import json, hashlib
import numpy as np
import mpmath as mp
from scipy.integrate import quad
from scipy.special import j0, spherical_jn

HERE=Path(__file__).resolve().parent
mp.mp.dps=55


def spectrum_mp(w,q,m):
    w,q,m=map(mp.mpf,(w,q,m))
    if w==0:return 1/(2*mp.pi*q*mp.expm1(mp.sqrt(m*m+q*q/4)))
    d=q*q-w*w
    assert d>0
    midpoint=q*mp.sqrt(1+4*m*m/d)/2
    lo,hi=midpoint-w/2,midpoint+w/2
    return (mp.log(-mp.expm1(-hi))-mp.log(-mp.expm1(-lo)))/(2*mp.pi*q*(-mp.expm1(-w)))


def spectrum_integral(w,q,m):
    w,q,m=map(mp.mpf,(w,q,m))
    lo=(q*mp.sqrt(1+4*m*m/(q*q-w*w))-w)/2
    f=lambda E: 1/mp.expm1(E) * (1+1/mp.expm1(E+w))
    return mp.quad(f,[lo,lo+1,lo+10,mp.inf])/(2*mp.pi*q)


def mixed_threshold(w,q,mi,mj):
    w,q,mi,mj=map(mp.mpf,(w,q,mi,mj))
    d=q*q-w*w;delta=mj*mj-mi*mi
    return (-w*(d+delta)+q*mp.sqrt((d+delta)**2+4*d*mi*mi))/(2*d)


def mixed_spectrum(w,q,mi,mj):
    w,q=map(mp.mpf,(w,q));lo=mixed_threshold(w,q,mi,mj)
    if w==0:return 1/(2*mp.pi*q*mp.expm1(lo))
    return (mp.log(-mp.expm1(-(lo+w)))-mp.log(-mp.expm1(-lo)))/(2*mp.pi*q*(-mp.expm1(-w)))


def spectrum_array(w,q,m):
    w=np.asarray(w,dtype=float)
    midpoint=q*np.sqrt(1+4*m*m/(q*q-w*w))/2
    out=np.empty_like(w)
    small=abs(w)<1e-6
    # Include detailed-balance first order near zero, avoiding subtractive loss.
    out[small]=(1+w[small]/2)/(2*np.pi*q*np.expm1(np.sqrt(m*m+q*q/4)))
    v=w[~small];b=midpoint[~small]
    out[~small]=(np.log(-np.expm1(-(b+v/2)))-np.log(-np.expm1(-(b-v/2))))/(2*np.pi*q*(-np.expm1(-v)))
    return out


def form_factor(q,R):
    z=np.asarray(q*R)
    return np.where(abs(z)<1e-4,1-z*z/10+z**4/280,3*spherical_jn(1,z)/np.where(z==0,1,z))


def static_rate(m,r,R):
    f=lambda q:q/(np.expm1(np.sqrt(m*m+q*q/4)))*float(form_factor(q,R))**2*(1-np.sinc(q*r/np.pi))/(4*np.pi**3)
    return quad(f,0,100,epsabs=1e-12,epsrel=2e-10,limit=200)[0]


def moving_rate(m,r,R,v,order=64):
    mu,weights=np.polynomial.legendre.leggauss(order)
    def f(q):
        w=spectrum_array(q*v*mu,q,m)
        angular=np.sum(weights*w*(1-j0(q*r*np.sqrt(1-mu*mu))))
        return q*q*float(form_factor(q,R))**2*angular/(4*np.pi**2)
    return quad(f,0,100,epsabs=1e-12,epsrel=2e-9,limit=200)[0]


def main():
    errors=[];kms=[];limits=[]
    for m in [.1,1,10]:
        for q in [.2,1,5]:
            for ratio in [0,.1,-.1,.9]:
                w=mp.mpf(str(q))*mp.mpf(str(ratio))
                a=spectrum_mp(w,q,m);b=spectrum_integral(w,q,m)
                assert a>0
                errors.append(float(abs(a-b)/b))
                kms.append(float(abs(spectrum_mp(-w,q,m)-mp.exp(-w)*a)/a))
            at0=spectrum_mp(0,q,m)
            pair=(spectrum_mp(mp.mpf('1e-8')*q,q,m)+spectrum_mp(-mp.mpf('1e-8')*q,q,m))/2
            limits.append(float(abs(pair-at0)/at0))
    static=[];motion=[]
    for m,r,R in [(1,.1,0),(1,1,0),(1,1,.3),(10,1,.3)]:
        a=static_rate(m,r,R);b=moving_rate(m,r,R,0)
        static.append({'m_over_T':m,'rT':r,'RT':R,'stationary_radial':a,'moving_at_zero':b,'relative_difference':abs(a-b)/a})
        for v in [.2,.5]:
            x=moving_rate(m,r,R,v,64);y=moving_rate(m,r,R,v,128)
            motion.append({'m_over_T':m,'rT':r,'RT':R,'v':v,'rate':x,'relative_quadrature_difference':abs(x-y)/x,'relative_to_stationary':x/a})
    # Explicit charge-coherence limits for two identical rigid constituents.
    N=2.;single=3.
    coherent=single**2*(N+N*(N-1)*1)
    incoherent=single**2*N
    assert coherent==(N*single)**2 and incoherent==N*single**2
    # Static symmetric Talbot-Lau integration of a Gaussian localization model.
    # Integral over its triangular harmonic separation must match the erf law.
    triangle_errors=[]
    for a in [.01,.3,1,5]:
        numeric=quad(lambda u:1-np.exp(-a*a*u*u/2),0,1,epsabs=1e-13)[0]
        closed=float(1-mp.sqrt(mp.pi/2)*mp.erf(mp.mpf(str(a))/mp.sqrt(2))/mp.mpf(str(a)))
        triangle_errors.append(abs(numeric-closed)/closed)
    mixed_kms=[];mixed_shell=[];mixed_fourier=[]
    for mi,mj in [(1,2),(2,1),(.1,3)]:
        for q,w in [(1,.2),(3,-1),(5,2)]:
            q,w=map(mp.mpf,(q,w));lo=mixed_threshold(w,q,mi,mj)
            assert lo>=mp.mpf(mi)-mp.mpf('1e-40') and lo+w>=mp.mpf(mj)-mp.mpf('1e-40')
            kernel=mixed_spectrum(w,q,mi,mj)
            integral=mp.quad(lambda E:1/mp.expm1(E)*(1+1/mp.expm1(E+w)),[lo,lo+1,lo+10,mp.inf])/(2*mp.pi*q)
            mixed_shell.append(float(abs(kernel-integral)/integral))
            mixed_kms.append(float(abs(mixed_spectrum(-w,q,mi,mj)-mp.exp(-w)*mixed_spectrum(w,q,mj,mi))/kernel))
    for r in [.2,1.,3.]:
        mi,mj=1.,2.
        def energy(e):
            ki,kj=np.sqrt(e*e-mi*mi),np.sqrt(e*e-mj*mj)
            n=1/np.expm1(e)
            return ki*kj*n*(1+n)*(1-np.sinc(ki*r/np.pi)*np.sinc(kj*r/np.pi))/(2*np.pi**3)
        a=quad(energy,mj,100,epsabs=1e-12,epsrel=1e-10)[0]
        def momentum(q):
            lo=np.sqrt((q*q+(mi+mj)**2)*(q*q+(mi-mj)**2))/(2*q)
            n=np.exp(-lo)/(-np.expm1(-lo))
            return q*n*(1-np.sinc(q*r/np.pi))/(4*np.pi**3)
        b=quad(momentum,0,100,epsabs=1e-12,epsrel=1e-10)[0]
        mixed_fourier.append(abs(a-b)/a)
    assert max(errors)<1e-40 and max(kms)<1e-40
    assert max(limits)<1e-12
    assert max(x['relative_difference'] for x in static)<1e-8
    assert max(x['relative_quadrature_difference'] for x in motion)<1e-8
    assert max(triangle_errors)<1e-8
    assert max(mixed_kms)<1e-40 and max(mixed_shell)<1e-40
    assert max(mixed_fourier)<1e-8
    result={'status':'conditional_moving_kernel_checks_passed','laboratory_fit':False,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'thermal_spectrum_energy_integral_cases':len(errors),'max_spectrum_relative_error':max(errors),
            'max_detailed_balance_relative_error':max(kms),'max_even_zero_frequency_limit_error':max(limits),
            'stationary_reduction':static,'moving_quadrature':motion,
            'triangular_harmonic_gaussian_reduction_error':max(triangle_errors),
            'two_mass_extension':{'ordered_scattering_cases':len(mixed_shell),
                                  'max_energy_integral_relative_error':max(mixed_shell),
                                  'max_species_reversed_detailed_balance_error':max(mixed_kms),
                                  'max_static_mixed_fourier_relative_error':max(mixed_fourier)},
            'beam_velocity_over_c_at_158mps':158/299792458,
            'scope':['massive free thermal Gaussian scalar state','quadratic composite operator at leading weak coupling',
                     'spacelike transfers only','prescribed rigid heavy probe; negligible recoil',
                     'Markov and slow trajectory approximation still conditional','no experimentally inferred bath parameters']}
    (HERE/'moving_kernel_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','thermal_spectrum_energy_integral_cases','max_spectrum_relative_error','max_detailed_balance_relative_error','max_even_zero_frequency_limit_error','triangular_harmonic_gaussian_reduction_error']},indent=2))


if __name__=='__main__': main()
