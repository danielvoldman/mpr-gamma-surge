"""A2: the M2 ring (plan 5.2 A2, 3.1; MS2 step 2d, DL-089).

Analysis only, no integration. Three parts:
  * the linearisation at a stable focus (eigenvalues of the M2 Jacobian, as in A1);
  * a damped-sinusoid fit to the tail of a step response, with the tail start rule of DL-079;
  * the ring map over the A1 stable-focus branch: frequency in Hz, envelope decay rate,
    cycles per e-fold and membership of the gamma band G.

Units: eigenvalues and rates are per tau; f_Hz = 1000 f_tau / tau_ms (100 f_tau at tau = 10 ms).
G1 reads the sign of the envelope growth rate (D8), not A_min (CP17). On the map the growth rate
is Re(lambda) of the focus, exact for the linear ring, so its standard error is 0.

`run_a2` is the runner task for run.kind = a2 (task(cfg, deadline) -> dict, see run.py).
"""
from __future__ import annotations

import numpy as np
import yaml
from scipy.optimize import least_squares
from scipy.signal import find_peaks

from .. import config as C
from .. import provenance as P
from ..models.fixed_points import classify_all
from ..models.mpr2d import jacobian_2d

SE_FACTOR = 2.0     # D8: damped only if the growth is negative by more than 2 standard errors


# --- linearisation --------------------------------------------------------------------------

def focus_eigenvalue(y, J):
    """Eigenvalue lambda = -decay + i omega (omega > 0, per tau) of the M2 Jacobian at y, or None for a node."""
    ev = np.linalg.eigvals(jacobian_2d(y, J))
    ev = ev[ev.imag > 0]
    return complex(ev[0]) if len(ev) else None


def post_step_focus(eta_bar, J, Delta, I):
    """(fixed point, lambda) of the one stable focus of M2 at drive I; ConfigError unless exactly one."""
    foci = [y for y, label, _ in classify_all(eta_bar, J, Delta, I) if label == "stable_focus"]
    if len(foci) != 1:
        raise C.ConfigError(f"expected exactly one stable focus at eta_bar={eta_bar}, J={J}, Delta={Delta}, I={I}; "
                          f"found {len(foci)}")
    return foci[0], focus_eigenvalue(foci[0], J)


def to_hz(omega_tau, tau_ms):
    """Angular frequency per tau to Hz."""
    return 1000.0 * np.asarray(omega_tau) / (2.0 * np.pi * tau_ms)


# --- damped-sinusoid fit --------------------------------------------------------------------

def _design(tp, decay, omega):
    e = np.exp(-decay * tp)
    return np.column_stack([np.ones_like(tp), e * np.cos(omega * tp), e * np.sin(omega * tp)])


def fit_damped_sinusoid(t, y):
    """Fit y = c + exp(-a t') (A cos(w t') + B sin(w t')), t' = t - t[0], by nonlinear least squares.

    Starting values come from the zero crossings of y - y[-1] and the log of the successive extrema.
    Returns a dict: decay a and omega w (per unit of t) with standard errors, offset, amplitude (at t[0]),
    phase, rms residual, n, cycles = w (t[-1] - t[0]) / 2 pi."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    tp = t - t[0]
    if len(t) < 8:
        raise ValueError("too few samples to fit a damped sinusoid")
    d = y - y[-1]
    cross = np.flatnonzero(np.diff(np.signbit(d).astype(np.int8)) != 0)
    if len(cross) < 2:
        raise ValueError("no oscillation in the fit window")
    w0 = np.pi * (len(cross) - 1) / (tp[cross[-1]] - tp[cross[0]])
    pk, _ = find_peaks(np.abs(d))
    a0 = max(-np.polyfit(tp[pk], np.log(np.abs(d[pk]) + 1e-300), 1)[0], 1e-6) if len(pk) >= 3 else 0.1 * w0

    def resid(p):
        X = _design(tp, p[0], p[1])
        return y - X @ np.linalg.lstsq(X, y, rcond=None)[0]

    a, w = least_squares(resid, [a0, w0], x_scale=[max(a0, 1e-3), w0], xtol=1e-14, ftol=1e-14, gtol=1e-14).x
    c, A, B = np.linalg.lstsq(_design(tp, a, w), y, rcond=None)[0]

    def full(p):    # p = (c, a, A, w, B)
        return y - (p[0] + np.exp(-p[1] * tp) * (p[2] * np.cos(p[3] * tp) + p[4] * np.sin(p[3] * tp)))

    f = least_squares(full, [c, a, A, w, B], xtol=1e-14, ftol=1e-14, gtol=1e-14)
    cov = np.linalg.pinv(f.jac.T @ f.jac) * np.sum(f.fun**2) / max(len(t) - 5, 1)
    se = np.sqrt(np.abs(np.diag(cov)))
    return {"decay": float(f.x[1]), "omega": float(f.x[3]), "se_decay": float(se[1]), "se_omega": float(se[3]),
            "offset": float(f.x[0]), "amplitude": float(np.hypot(f.x[2], f.x[4])),
            "phase": float(np.arctan2(-f.x[4], f.x[2])), "rms": float(np.sqrt(np.mean(f.fun**2))),
            "n": int(len(t)), "cycles": float(f.x[3] * (t[-1] - t[0]) / (2.0 * np.pi))}


def tail_start(r, r_star, fraction):
    """(index of the tail start, initial jump). The jump is the first local maximum of |r - r*| (DL-079);
    the tail starts at the first later local maximum of |r - r*| below fraction * jump (the envelope is
    read from the successive extrema)."""
    dev = np.abs(np.asarray(r, float) - r_star)
    pk, _ = find_peaks(dev)
    if len(pk) < 2:
        raise ValueError("no peaks in the step response")
    jump = dev[pk[0]]
    below = pk[1:][dev[pk[1:]] < fraction * jump]
    if not len(below):
        raise ValueError("the envelope never falls below the tail fraction of the initial jump")
    return int(below[0]), float(jump)


def k4_mf_check(t_tau, r, r_star, lam, fraction, tol_freq, tol_decay, t_end_tau):
    """K4-MF: fit the step response from the tail start to t_end_tau and compare with the linearisation lam.
    Returns a flat dict of floats (the fit, the linearisation, relative errors, pass)."""
    i0, jump = tail_start(r, r_star, fraction)
    sel = (np.arange(len(t_tau)) >= i0) & (t_tau <= t_end_tau)
    fit = fit_damped_sinusoid(t_tau[sel], r[sel])
    om_lin, dec_lin = lam.imag, -lam.real
    e_f, e_d = abs(fit["omega"] - om_lin) / om_lin, abs(fit["decay"] - dec_lin) / dec_lin
    return {"jump": jump, "t_start_tau": float(t_tau[i0]), "t_end_tau": float(t_tau[sel][-1]),
            "n_samples": fit["n"], "cycles": fit["cycles"],
            "omega_fit": fit["omega"], "omega_lin": float(om_lin), "decay_fit": fit["decay"], "decay_lin": float(dec_lin),
            "se_omega": fit["se_omega"], "se_decay": fit["se_decay"], "offset_fit": fit["offset"], "r_star": float(r_star),
            "rms": fit["rms"], "rel_err_frequency": float(e_f), "rel_err_decay": float(e_d),
            "tol_frequency": tol_freq, "tol_decay": tol_decay, "pass": bool(e_f <= tol_freq and e_d <= tol_decay)}


# --- ring map -------------------------------------------------------------------------------

def ring_map(J_grid, r, label_code, focus_code, tau_ms, band_hz, Delta=1.0):
    """Ring quantities on the A1 stable-focus branch. r, label_code: (n_eta, n_J, n_root). Every array has that
    shape; entries are nan (False) where the root is not a stable focus. growth_rate = Re(lambda) per tau."""
    is_focus = label_code == focus_code
    lam = np.full(r.shape, complex(np.nan, np.nan))
    for i, j, k in zip(*np.nonzero(is_focus)):
        lam[i, j, k] = focus_eigenvalue(np.array([r[i, j, k], -Delta / (2.0 * np.pi * r[i, j, k])]), J_grid[j])
    decay = -lam.real
    freq = to_hz(lam.imag, tau_ms)
    with np.errstate(invalid="ignore"):
        in_G = is_focus & (freq >= band_hz[0]) & (freq <= band_hz[1])
        # D8: damped only if the growth is negative by more than 2 SE; the linear growth is exact (SE = 0)
        nondamped = is_focus & ~(lam.real < -SE_FACTOR * 0.0)
    return {"is_focus": is_focus, "in_G": in_G, "g1_nondamped": nondamped, "r": np.where(is_focus, r, np.nan),
            "lambda_re": lam.real, "lambda_im": lam.imag, "growth_rate": lam.real, "decay_rate": decay,
            "freq_hz": freq, "cycles_per_efold": lam.imag / (2.0 * np.pi * decay)}


# --- runner task ----------------------------------------------------------------------------

UPSTREAM = {"A1": "configs/A1.yaml", "S1": "configs/S1.yaml"}
_SHA_MEMO: dict = {}


def upstream_npz(config_path):
    """Path of the complete result npz of an upstream config as written, or None."""
    from .. import run as R          # late import: run.py resolves tasks by name
    plan = R.build_plan(config_path)
    rec = P.find_complete(plan.out_dir, plan.cells[0]["cfg"])
    return None if rec is None else rec.with_suffix(".npz")


def upstream_sha256s():
    """{'A1': sha, 'S1': sha} of the upstream result files A2 reads (None where absent).

    config.hash_view puts this in the a2 hashed view (DL-090), so a changed upstream result
    changes the A2 hash. Memoised on (path, mtime, size); hashing is by content.
    """
    out = {}
    for name, cfg_path in UPSTREAM.items():
        npz = upstream_npz(cfg_path)
        if npz is None:
            out[name] = None
            continue
        st = npz.stat()
        key = (str(npz), st.st_mtime_ns, st.st_size)
        if key not in _SHA_MEMO:
            _SHA_MEMO[key] = P.sha256_file(npz)
        out[name] = _SHA_MEMO[key]
    return out


def _upstream(config_path, name):
    """(npz path, its SHA-256) of the complete result of an upstream config as written."""
    npz = upstream_npz(config_path)
    if npz is None:
        raise C.ConfigError(f"{name}: no complete result for {config_path}; run it first")
    return npz, P.sha256_file(npz)


def run_a2(cfg, deadline=None):
    m = cfg["model"]
    if m["Delta"] != 1.0 or m["type"] != "M2":
        raise C.ConfigError("A2 is defined for M2 at Delta = 1 (plan 5.2 A2)")
    tau = m["tau_ms"]
    rep_path = C.repo_root() / cfg["replication"]["tolerances_file"]
    with open(rep_path, "r", encoding="utf-8") as fh:
        mf = yaml.safe_load(fh)["K4"]["mean_field"]

    a1_npz, a1_sha = _upstream(UPSTREAM["A1"], "A1")
    with np.load(a1_npz) as z:
        eta, Jg, r, lab, names = z["eta_over_Delta"], z["J_over_sqrtDelta"], z["r"], z["label"], list(z["label_names"])
    band = cfg["analysis"]["band_primary_hz"]
    rm = ring_map(Jg, r, lab, names.index("stable_focus"), tau, band, m["Delta"])

    s1_npz, s1_sha = _upstream(UPSTREAM["S1"], "S1")
    with np.load(s1_npz) as z:
        t_tau, r_t = z["t_ms"] / tau, z["r"]
    y_star, lam = post_step_focus(m["eta_bar"], m["J"], m["Delta"], m["I_drive"] + cfg["path"]["I_amp"])
    k4 = k4_mf_check(t_tau, r_t, y_star[0], lam, mf["tail_fit_fraction"], mf["tolerance_frequency_rel"],
                     mf["tolerance_decay_rel"], C.A2_WINDOW["t_end_tau"])

    arrays = {"eta_over_Delta": eta, "J_over_sqrtDelta": Jg, "band_primary_hz": np.asarray(band, float),
              "tau_ms": np.array(tau), **{f"ring_{k}": v for k, v in rm.items()},
              **{f"k4_{k}": np.array(v) for k, v in k4.items()},
              "k4_lambda": np.array(lam), "k4_post_step_fixed_point": y_star}
    in_G, f_hz = rm["in_G"], rm["freq_hz"]
    summary = {"n_focus_roots": int(rm["is_focus"].sum()), "n_in_G": int(in_G.sum()),
               "n_g1_nondamped": int(rm["g1_nondamped"].sum()),
               "freq_hz_range": [float(np.nanmin(f_hz)), float(np.nanmax(f_hz))],
               "max_cycles_per_efold_in_G": float(np.nanmax(rm["cycles_per_efold"][in_G])) if in_G.any() else None}
    if C.hash_view(cfg)["a2"]["upstream_sha256"] != {"A1": a1_sha, "S1": s1_sha}:
        raise C.ConfigError("A2: an upstream result changed after the config was hashed; rerun")
    flags = {**summary, "k4_pass": k4["pass"], "k4": k4, "a1_npz_sha256": a1_sha, "s1_npz_sha256": s1_sha,
             "replication_yaml_sha256": P.sha256_file(rep_path), "a2_window": dict(C.A2_WINDOW),
             "status_note": "K4 tail fraction 0.1 and the 40 tau window end are UNVERIFIED (DL-076, DL-089)"}
    msg = (f"K4-MF {'pass' if k4['pass'] else 'FAIL'}: frequency error {k4['rel_err_frequency']:.3g}, decay error "
           f"{k4['rel_err_decay']:.3g}, {k4['cycles']:.1f} tail cycles; ring in G at {summary['n_in_G']} of "
           f"{summary['n_focus_roots']} focus roots")
    return {"arrays": arrays, "message": msg, "flags": flags}
