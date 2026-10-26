"""Build a reviewed research note from completed checks; no new data fitting."""
from pathlib import Path
import json
import hashlib
import math
import re
import matplotlib
matplotlib.use('Agg')
from matplotlib import mathtext, rcParams
from matplotlib.font_manager import FontProperties
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'output/pdf/Moving_Portal_Interferometry_Audit_2026-10-11.pdf'
TEMP = ROOT / 'tmp/pdfs/moving-portal-note'
TEMP.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
baseline = json.loads((HERE/'baseline_results.json').read_text())
optical = json.loads((HERE/'optical_input_checks.json').read_text())
checks = json.loads((HERE/'moving_kernel_checks.json').read_text())
rcParams.update({'mathtext.fontset':'cm','font.family':'serif','savefig.transparent':True})

ink = colors.HexColor('#173E49')
muted = colors.HexColor('#51626B')
blue = colors.HexColor('#176B93')
styles = {
    'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=ink, spaceAfter=12),
    'subtitle': ParagraphStyle('subtitle', fontName='Helvetica', fontSize=12, leading=16, textColor=muted, spaceAfter=12),
    'heading': ParagraphStyle('heading', fontName='Helvetica-Bold', fontSize=17, leading=21, textColor=ink, spaceAfter=10),
    'sub': ParagraphStyle('sub', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=ink, spaceBefore=9, spaceAfter=5),
    'body': ParagraphStyle('body', fontName='Helvetica', fontSize=10, leading=14, spaceAfter=8),
    'small': ParagraphStyle('small', fontName='Helvetica', fontSize=8.5, leading=11.4, textColor=muted, spaceAfter=7),
    'cell': ParagraphStyle('cell', fontName='Helvetica', fontSize=9, leading=12),
    'kicker': ParagraphStyle('kicker', fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=blue, spaceAfter=14),
}
story=[]

def p(text, kind='body'):
    story.append(Paragraph(text,styles[kind]))

def eq(tex, max_height=52):
    tex=re.sub(r'\\mathbf\s*([A-Za-z0-9])',r'\\mathbf{\1}',tex)
    index=sum(1 for _ in TEMP.glob('eq-*.png'))
    path=TEMP/f'eq-{index:02}.png'
    mathtext.math_to_image('$'+tex+'$',str(path),prop=FontProperties(size=12),dpi=300,format='png')
    w,h=ImageReader(str(path)).getSize()
    scale=min(1,468/(w*72/300),max_height/(h*72/300))
    obj=Image(str(path),width=w*72/300*scale,height=h*72/300*scale)
    obj.hAlign='CENTER'
    story.extend([Spacer(1,3),obj,Spacer(1,10)])

def plot(name, width=478):
    w,h=ImageReader(str(HERE/name)).getSize()
    story.append(Image(str(HERE/name),width=width,height=width*h/w))
    story.append(Spacer(1,5))

def table(rows,widths):
    rows=[[Paragraph(str(c),styles['cell']) for c in row] for row in rows]
    tab=Table(rows,colWidths=widths,hAlign='LEFT')
    tab.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8F0F2')),
        ('LINEBELOW',(0,0),(-1,0),.6,ink),
        ('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#A7B7BC')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    story.extend([tab,Spacer(1,10)])

def page(title):
    story.append(PageBreak())
    p(title,'heading')

p('ZORAASI RESEARCH PROGRAM  /  11 OCTOBER 2026','kicker')
p('Moving scalar probes and<br/>an interferometry data audit','title')
p('A conditional measurement calculation with reproducible checks<br/>Prepared for Christopher Michael Baird | Working note v0.1','subtitle')
p('<b>Result.</b> A public sodium-cluster dataset is now usable for a documented baseline reanalysis. The portal calculation has also been extended from a stationary point probe to moving, composite probes and mixed scalar species. These are advances toward a testable model; they do not establish a new field or complete a Theory of Everything.')
table([
    ['Experimental material','Reanalysis completed here'],
    ['95 fringe scans; 3,895 count observations','Independent sinusoidal fits cross-check the deposited nonlinear fits.'],
    ['Mass and velocity averaging','Ordinary quantum and classical predictions use the deposited Talbot-Lau kernel.'],
    ['Optical calibration','A code/paper cross-section mismatch changes predicted visibility appreciably. No portal fit or exclusion is reported.'],
],[153,325])
plot('baseline_comparison.png')
p('<b>Figure 1.</b> Recomputed baseline from the deposited model [1]. Both curves retain the paper\'s 0.78 contrast factor explicitly. Points use a declared symmetric-error summary; the published asymmetric intervals and model uncertainty bands have not been reconstructed. This is not an exact replication of the published figure.','small')

page('1. The calibration issue that matters first')
p('The deposited code and the paper\'s Methods use different mass dependence for the effective optical cross-section. Under the code\'s unit ionization-yield assumption, the two inputs can be compared directly. Let u be particle mass in kDa [1,2].')
eq(r'\sigma_{\rm code}=(0.5837\,u^{2/3}-1.5)\,4.24\times10^{-20}\ {\rm m}^2')
eq(r'\sigma_{\rm paper}=(0.537\,u-1.5)\,10^{-20}\ {\rm m}^2')
p('At the selected raw mass mean of 168.94 kDa, these give 6.927 and 8.922 times 10<super>-19</super> m<super>2</super>. The paper formula was checked visually on physical PDF page 7. Changing only this optical input gives a maximum absolute visibility change of <b>0.03640 before</b>, or <b>0.02839 after</b>, the shared 0.78 factor. All other inputs were held fixed; neither branch is identified here as the correct full calibration.')
plot('optical_input_sensitivity.png')
p('<b>Figure 2.</b> This controlled input substitution exposes an apparatus-model uncertainty, not a scalar signal. It is not a refit of either the paper or the new-field model.','small')
p('Fit and uncertainty checks','sub')
p('Three default nonlinear fits stop at the allowed phase boundary. Restarting them from an independent linear sine/cosine fit gives agreement within 1.55 times 10<super>-10</super> in visibility across all scans. The original maximum discrepancy was only 0.00384 of a reported fit standard deviation; it does not explain the optical difference.','small')
p('The deposited bin error is an RMS per-scan uncertainty, not the standard error of a mean. The plots here instead use symmetric inverse-variance means, inflating errors by max(1, square root of reduced chi-square). The published procedure uses asymmetric intervals and a different inflation threshold. Near zero contrast, a fitted nonnegative amplitude is noise-biased. These distinctions must be handled before statistical inference.','small')

page('2. What a moving probe samples')
p('Use natural units: hbar = c = k<sub>B</sub> = 1. Assume a massive free real scalar in a homogeneous thermal state at temperature T and zero chemical potential. The matter coupling is quadratic, O = :phi<super>2</super>:, with its thermal mean subtracted. Define positive frequency and momentum transfer as energy and momentum gained by the bath.')
eq(r'\widetilde S_O(\Omega,\mathbf Q)=\int dt\,d^3x\ e^{i\Omega t-i\mathbf Q\cdot\mathbf x}\langle\delta O(t,\mathbf x)\delta O(0,\mathbf0)\rangle')
p('For Q &gt; 0 and spacelike transfer, |Omega| &lt; Q, put D = Q<super>2</super> - Omega<super>2</super> and n(E) = [exp(E/T) - 1]<super>-1</super>. Wick contraction followed by the scattering-shell angular integral gives')
eq(r'E_-=\frac{Q\sqrt{1+4m^2/D}-\Omega}{2},\qquad E_+=E_-+\Omega')
eq(r'\widetilde S_O(\Omega,Q)=\frac{1}{2\pi Q}\int_{E_-}^{\infty}dE\ n(E)[1+n(E+\Omega)]')
eq(r'\widetilde S_O(\Omega,Q)=\frac{T}{2\pi Q(1-e^{-\Omega/T})}\ln\frac{1-e^{-E_+/T}}{1-e^{-E_-/T}}')
p('The zero-frequency expression is the continuous limit, not direct substitution into a 0/0 expression. The reverse-frequency relation is thermal detailed balance:')
eq(r'\widetilde S_O(0,Q)=\frac{T}{2\pi Q}\,n\!\left(\sqrt{m^2+Q^2/4}\right),\quad\widetilde S_O(-\Omega,Q)=e^{-\Omega/T}\widetilde S_O(\Omega,Q)')
p('An externally prescribed, rigid heavy probe moving with velocity v samples Omega = Q dot v. A recoiling probe instead exchanges Omega = E(P) - E(P - Q), approximately Q dot v - Q<super>2</super>/(2M). Keeping recoil generally requires momentum evolution, not just a position-dephasing rate.')
eq(r'\Gamma_{\mathbf v}(\mathbf r)=\int\frac{d^3Q}{(2\pi)^3}\,\widetilde S_O(\mathbf Q\cdot\mathbf v,Q)\,|A(\mathbf Q)|^2[1-\cos(\mathbf Q\cdot\mathbf r)]')
p('A(Q) is the total scalar charge form factor, including portal couplings. This rate requires weak coupling, negligible recoil and a short bath memory relative to the changing trajectory. Vacuum spacelike noise vanishes at this free-field order. Pair production lies outside the spacelike expression.')
p('For the beam speed 158 m/s, v/c = 5.2703 times 10<super>-7</super>. A nonrelativistic bath can still be slower: the stationary approximation needs v much smaller than its typical speed, of order square root of T/m. A small laboratory v/c alone is insufficient.','small')

page('3. Two scalar species and a composite particle')
p('Let the probe couple to B = s<super>T</super>Cs, with positive scalar masses and a real symmetric coefficient matrix C. An ordered channel i to j describes an incoming bath quantum of species i and an outgoing one of species j. Write Delta = m<sub>j</sub><super>2</super> - m<sub>i</sub><super>2</super>. In the same spacelike domain,')
eq(r'a_{ij}=\frac{-\Omega(D+\Delta)+Q\sqrt{(D+\Delta)^2+4Dm_i^2}}{2D}')
eq(r'S_{ij}(\Omega,Q)=\frac{1}{2\pi Q}\int_{a_{ij}}^\infty dE\ n(E)[1+n(E+\Omega)]')
eq(r'S_{ij}(\Omega,Q)=\frac{T}{2\pi Q(1-e^{-\Omega/T})}\ln\frac{1-e^{-(a_{ij}+\Omega)/T}}{1-e^{-a_{ij}/T}}')
eq(r'a_{ij}(0,Q)=\frac{\sqrt{[Q^2+(m_i+m_j)^2][Q^2+(m_i-m_j)^2]}}{2Q}')
p('Both conversion directions must be retained. The threshold obeys a<sub>ij</sub> + Omega = a<sub>ji</sub>(-Omega), and each directed spectrum obeys a species-reversed detailed-balance relation:')
eq(r'S_{ij}(-\Omega,Q)=e^{-\Omega/T}S_{ji}(\Omega,Q),\qquad S_B=\sum_{i,j}C_{ij}^2S_{ij}')
p('For a rigid composite with constituent positions u<sub>a</sub>, replace the point-charge factor by the corresponding channel amplitude:')
eq(r'A_{ij}(\mathbf Q)=\sum_a C_{ij,a}e^{i\mathbf Q\cdot\mathbf u_a},\qquad |A|^2\widetilde S_O\ \longrightarrow\ \sum_{i,j}|A_{ij}|^2S_{ij}')
p('For one scalar, A(Q) = sum of c<sub>a</sub> exp(iQ dot u<sub>a</sub>). Unresolved identical constituents add coherently: the response is N<super>2</super>c<super>2</super>. At resolved separations, constituent structure matters. A spherical continuum model has A = C<sub>tot</sub> 3j<sub>1</sub>(QR)/(QR), but misses a discrete self term when individual scatterers are resolved.')
eq(r'\langle|A|^2\rangle=c^2\{N+N(N-1)|F(Q)|^2\}\quad\mathrm{(independent\ positions)}')
p('Nucleon charges follow the conditional portal matching c<sub>N</sub> = kappa f<sub>N</sub>m<sub>N</sub>/(2m<sub>h</sub><super>2</super>). Binding effects and scalar form factors prevent automatic identification with total inertial mass. Quantum internal transitions require a dynamic structure factor. These extensions have not been fitted to the nanoparticle data.','small')
p('The displayed spectrum covers spacelike transfer only. Unequal-mass conversion can also occur at timelike transfer up to (m<sub>i</sub> - m<sub>j</sub>)<super>2</super>; pair channels start at (m<sub>i</sub> + m<sub>j</sub>)<super>2</super>. The spacelike restriction suffices for constant subluminal motion and elastic recoil at unchanged probe rest mass.','small')

page('4. From the rate to the observed harmonic')
p('A Talbot-Lau device is not a literal fixed-separation two-arm interferometer. For equal grating periods and equal gaps L, a paraxial, translation-covariant Markov treatment attenuates its nth signal harmonic using an effective triangular separation [3]:')
eq(r'I_n(v,M)=I_n^{(0)}(v,M)e^{-\chi_n(v,M)}')
eq(r'\chi_n=\frac{1}{v}\int_0^{2L}dz\ \Gamma_{\mathbf v}(s_n(z)),\qquad s_n(z)=\frac{n\lambda_{\rm dB}}{d}[L-|z-L|]')
p('Here lambda<sub>dB</sub> = h/(Mv) in SI units. The equal-gap distance is 0.98375 m and the period 133 nm. At the selected raw mass mean and 158 m/s, the flight time is 12.45 ms and the first-harmonic maximum effective separation is about 110 nm. The full mass and speed distributions remain necessary.')
eq(r'\overline{I}_n=\int dM\,dv\ w(M,v)I_n^{(0)}(M,v)e^{-\chi_n(M,v)},\qquad V=\frac{2|\overline{I}_1|}{\overline{I}_0}')
p('Average complex harmonics before taking their magnitude. Averaging already-computed visibilities need not give the same result. In this limit chi<sub>0</sub> = 0 for pure localization; loss, recoil and heating need separate modeling.')
p('For an isotropic spherical charge response W(Q) = |A(Q)|<super>2</super> and transverse separation, the moving rate reduces to a practical two-dimensional integral:')
eq(r'\Gamma_v(r)=\frac{1}{4\pi^2}\int_0^\infty dQ\,Q^2W(Q)\int_{-1}^{1}d\mu\ \widetilde S_O(Qv\mu,Q)[1-J_0(Qr\sqrt{1-\mu^2})]')
p('Finite memory and changing paths','sub')
p('Before making the Markov approximation, the leading real second cumulant has a frequency filter. For a scalar channel, define the path-difference source f. Smooth switching and an appropriate finite-size/EFT cutoff are required when evaluating ultraviolet-sensitive terms:')
eq(r'f(\Omega,\mathbf Q)=\int dt\ e^{-i\Omega t}A(\mathbf Q,t)\left[e^{i\mathbf Q\cdot\mathbf X_L(t)}-e^{i\mathbf Q\cdot\mathbf X_R(t)}\right]')
eq(r'\chi^{(2)}=\frac{1}{2}\int\frac{d^3Q}{(2\pi)^3}\frac{d\Omega}{2\pi}\ S_{\rm sym}(\Omega,\mathbf Q)|f(\Omega,\mathbf Q)|^2')
p('S<sub>sym</sub> is the symmetrized centered correlator spectrum. A finite-time filter samples frequencies beyond the spacelike sector, so the formulas on pages 3-4 alone do not evaluate this general expression. The quadratic bath operator is non-Gaussian even for a Gaussian free field; exponentiating the second cumulant is a weak-coupling approximation, not an exact result.','small')

page('5. Verification, identifiability and remaining work')
table([
    ['Check','Result in this calculation'],
    ['Independent fringe fit','95 scans; restarted nonlinear and linear visibilities agree within 1.55 x 10<super>-10</super>.'],
    ['Grating-kernel identity','420 cases agree with an independent entire-function representation to 3.34 x 10<super>-16</super> absolute.'],
    ['Dynamic thermal spectrum','36 single-species and 9 ordered mixed-species cases agree with energy quadrature; positivity and detailed balance pass.'],
    ['Static and moving limits','Mixed spatial Fourier reduction agrees to 2.08 x 10<super>-12</super> relative. Moving angular quadrature checks agree within 5.24 x 10<super>-13</super>.'],
    ['Finite harmonic path','Triangular-path integration matches an analytic Gaussian-localization example within 8.10 x 10<super>-13</super> relative.'],
],[153,325])
p('These test a specified calculation, not its realization in nature. High numerical agreement does not reduce experimental systematics. The optical baseline velocity grid was refined from 15 to 39 to 79 samples at three powers; the last change was as large as 3.47 times 10<super>-5</super> in absolute visibility. This is a sampled sensitivity check, not a uniform convergence proof.','small')
p('A precise obstacle to inference','sub')
p('For fixed mass and speed, if the new coupling produces a power-independent attenuation, a power scan measures the product below. An unconstrained apparatus contrast alpha and the scalar attenuation are then exactly degenerate:')
eq(r'V(P)=\alpha\,e^{-\chi}\,V_0(P)')
p('Mass/speed averaging can change this conclusion because attenuation reweights different harmonics. That information must be modeled, not presumed. Nor can a null result bound the portal coupling independently of the bath: an absent or negligibly populated bath gives negligible thermal scattering at any coupling allowed by other tests.')
p('Required next steps','sub')
p('<b>1.</b> Reconcile optical cross-section, ionization yield, contrast scale, mass selection and speed distributions. Preserve both current optical branches until this is established.<br/><b>2.</b> Specify the scalar masses, portal matrix, bath distribution and composite response. Verify recoil, memory and internal-state approximations for that parameter region.<br/><b>3.</b> Integrate attenuation into the apparatus harmonics and fit raw counts with justified noise, background and calibration parameters. Use the same nuisance treatment in ordinary and scalar models; assess independent-data predictions.<br/><b>4.</b> Continue the broader theory audit: a common action, quantum consistency and gravity, recovery of established limits, and quantitative novel predictions remain necessary. This laboratory calculation does not supply those missing foundations.')
p('Sources and reproducibility','sub')
p('[1] Pedalino et al., <link href="https://zenodo.org/records/17502163" color="#176B93">dataset and code, Zenodo 17502163</link> (CC BY 4.0). Original author files remain unchanged.<br/>[2] Pedalino et al., <link href="https://doi.org/10.1038/s41586-025-09917-9" color="#176B93">Nature 649, 866-870 (2026)</link>, Fig. 2 and Methods; <link href="https://www.klaus-hornberger.de/pdf/nature2.pdf" color="#176B93">author-hosted paper</link>.<br/>[3] Hornberger, Sipe and Arndt, <link href="https://arxiv.org/html/quant-ph/0407245" color="#176B93">Theory of decoherence in a matter wave Talbot-Lau interferometer</link>, Eqs. 70-71 (2004).<br/>Companion scripts, JSON results and manifest: output/research/toe-interferometer-reproduction-20261011.','small')

def header(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#C2D0D4'))
    canvas.line(54,752,558,752)
    canvas.setFont('Helvetica',7.5)
    canvas.setFillColor(muted)
    canvas.drawString(54,763,'ZORAASI | CONDITIONAL THEORY AND DATA AUDIT')
    canvas.drawRightString(558,763,'11 OCTOBER 2026')
    canvas.drawString(54,29,'AI-assisted working calculation | No detection or theory-completion claim')
    canvas.drawRightString(558,29,str(doc.page))
    canvas.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=(612,792),leftMargin=67,rightMargin=67,topMargin=57,bottomMargin=51,
                      title='Moving scalar probes and an interferometry data audit',
                      author='AI-assisted research calculation prepared for the ZoraASI project')
doc.build(story,onFirstPage=header,onLaterPages=header)
print(OUT)
