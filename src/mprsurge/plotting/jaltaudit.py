"""MS13 13t-11 (DL-699 P2): audit of the numbers and the claims of the ALT TEXTS of the 13 journal figures.

The number audit of 13t-9 (jnumaudit) covers the numbers that the caption builders type; the alt texts of F1, F2, F3, F5, F6 and FS1 are written by builders in figures.py that it does not scan. This module reads the RECORDED
alt text (figures/journal/supplement/<ID>_alt_text.txt) and the RECORDED source data of the same build (figures/journal/supplement/<ID>_source_data.csv, the drawn values) and compares each claim of the table CHECKS with
the value computed from the source data, at the precision that the alt text prints. `rows()` returns (figure, panel, claim, value in text, stored value, equal); `coverage()` lists the numbers of every alt text that no check,
no caption of the same figure and no structure rule covers (a number nobody compares is listed, and the test fails on it).

What it cannot cover (said, not hidden): a statement about what the image looks like (direction of a line, 'rising ridges', 'regular volleys', a mark 'on the boundary'); the choice of the right stored quantity when two
quantities have the same value; words around a number; a count that the alt text builds from the same array it is compared with (equal by construction; the claim is then checked against the table the array came from);
a number that also occurs in the caption of the same figure is accepted as covered by the caption audits (N2, O2, the independent comparison), which is weaker than a comparison with the source data.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

IDS = "F1 F2 F3 F4a F4b F5 F5c F6 FS1 FS2 FS3 FS4 FS5".split()
NUMTOK = re.compile(r"(?<![A-Za-z_0-9.])[-−]?\d[\d,]*\.?\d*(?:e[-+]?\d+)?")
_cache: dict = {}


def _root(root) -> Path:
    return Path(root)


def src(root, fid: str) -> pd.DataFrame:
    k = (str(root), fid)
    if k not in _cache:
        _cache[k] = pd.read_csv(Path(root) / f"figures/journal/supplement/{fid}_source_data.csv", low_memory=False)
    return _cache[k]


def alt(root, fid: str) -> dict:
    t = (Path(root) / f"figures/journal/supplement/{fid}_alt_text.txt").read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"Panel \(([a-z])\): (.*?)(?=\n\nPanel \(|\Z)", t, re.S)}


def _n(s):
    return pd.to_numeric(s, errors="coerce").to_numpy(float)


def sel(root, fid, panel, contains=None, startswith=None, notcontains=None) -> pd.DataFrame:
    d = src(root, fid)
    d = d[d.panel == panel]
    if contains:
        d = d[d.series.str.contains(contains, regex=False)]
    if startswith:
        d = d[d.series.str.startswith(startswith)]
    if notcontains:
        d = d[~d.series.str.contains(notcontains, regex=False)]
    return d


def X(d):
    return _n(d.x)


def Y(d):
    return _n(d.y)


def V(d):
    return _n(d.value)


def _val(tok: str) -> float:
    return float(tok.replace("−", "-").replace(",", ""))


def _tol(tok: str) -> float:
    s = tok.replace("−", "-").replace(",", "").lower()
    mant, _, ex = s.partition("e")
    dec = len(mant.split(".")[1]) if "." in mant else 0
    return 0.5 * 10 ** (-dec) * 10 ** (int(ex) if ex else 0) * (1 + 1e-9)


# each check: (figure, panel, claim, regex with one group per number, function(root) -> tuple of stored values)
def _checks():
    C = []

    def add(fid, panel, claim, rx, fn):
        C.append((fid, panel, claim, rx, fn))

    # F1
    add("F1", "a", "eta_bar from ... to (rises linearly between the guide levels)", r"from eta_bar (\S+) to (\S+) between", lambda r: (Y(sel(r, "F1", "a", startswith="eta_bar(t)")).min(), Y(sel(r, "F1", "a", startswith="eta_bar(t)")).max()))
    add("F1", "a", "ramp from ... s to ... s", r"between (\d+) s and (\d+) s", lambda r: _f1_ramp(r))
    add("F1", "a", "mean-field onset", r"onset at ([\d.]+) s", lambda r: (X(sel(r, "F1", "c", startswith="mean-field stored onset"))[0],))
    add("F1", "b", "J(t) from ... to ...", r"from ([-−]?\d+) to (\d+):", lambda r: (Y(sel(r, "F1", "b", startswith="J(t)")).min(), Y(sel(r, "F1", "b", startswith="J(t)")).max()))
    add("F1", "c", "mean-field rate below ... before the onset", r"below ([\d.]+) before", lambda r: (_f1_before(r),))
    add("F1", "c", "upper edge peaks at (largest block maximum)", r"peaks at ([\d.]+)", lambda r: (Y(sel(r, "F1", "c", contains="block maximum")).max(),))
    add("F1", "d", "raw first crossings recorded from ... to ... s", r"recorded at ([\d.]+) to ([\d.]+) s|stored at ([\d.]+) to ([\d.]+) s", lambda r: (X(sel(r, "F1", "d", contains="raw first crossing")).min(), X(sel(r, "F1", "d", contains="raw first crossing")).max()))
    add("F1", "d", "classifier onset", r"onset at ([\d.]+) s", lambda r: (X(sel(r, "F1", "d", contains="classifier onset"))[0],))
    add("F1", "e", "v from ... to (smallest block minimum, largest block maximum)", r"from ([-−]?[\d.]+) to ([\d.]+),", lambda r: (Y(sel(r, "F1", "e", contains="block minimum")).min(), Y(sel(r, "F1", "e", contains="block maximum")).max()))
    add("F1", "g", "frequency 0 to ... Hz", r"frequency 0 to (\d+) Hz", lambda r: (Y(sel(r, "F1", "g", startswith="spectrogram")).max(),))
    add("F1", "i", "rows", r"\((\d+) rows\)", lambda r: (float(len(np.unique(Y(sel(r, "F1", "i"))))),))
    add("F1", "i", "top colour starts at ... spikes; N of M cells have more", r"starts at (\d+) spikes \((\d+) of (\d+) cells", lambda r: _f1_top(r))
    add("F1", "j", "window from ... s", r"window from ([\d.]+) s", lambda r: (round(float(X(sel(r, "F1", "j")).min()), 0),))
    # F2
    add("F2", "a", "Hopf point", r"eta_bar ([\d.]+), circled", lambda r: (X(sel(r, "F2", "a", startswith="Hopf point"))[0],))
    add("F2", "a", "cycle maximum and minimum of v at eta_bar 8", r"reach about ([\d.]+) and ([-−]?[\d.]+) at", lambda r: (Y(sel(r, "F2", "a", startswith="stable cycle maximum")).max(), Y(sel(r, "F2", "a", startswith="stable cycle minimum")).min()))
    add("F2", "a", "mean-field steps each way", r"; (\d+) steps each way\) lie", lambda r: (float(len(sel(r, "F2", "a", startswith="mean field sweep maximum of v, up")),),))
    add("F2", "a", "network steps each way", r"; (\d+) steps each way\)\s*lie close", lambda r: (float(len(sel(r, "F2", "a", startswith="network sweep maximum of v, up")),),))
    add("F2", "b", "amplitude rises to about ...", r"rising to about (\d+) at", lambda r: (Y(sel(r, "F2", "b", startswith="stable cycle amplitude")).max(),))
    add("F2", "b", "network amplitude below the Hopf point", r"stand at ([\d.]+) to ([\d.]+) \(", lambda r: _f2_net(r))
    add("F2", "c", "relative difference from ... to ... percent", r"falling from \+?([\d.]+) percent to ([-−]?[\d.]+) percent", lambda r: (100 * Y(sel(r, "F2", "c")).max(), 100 * Y(sel(r, "F2", "c")).min()))
    # F3
    for p, D, mx, nc in (("a", "0.05", 60.284, 7), ("b", "0.1", 73.4969, 6), ("c", "0.3", 73.6921, 3)):
        add("F3", p, f"largest frequency of panel ({p})", r"the largest on this panel is ([\d.]+) Hz", (lambda pp: lambda r: (Y_or_V(sel(r, "F3", pp, startswith="limit-cycle frequency shading")).max(),))(p))
        add("F3", p, f"slices with a 25 Hz crossing in ({p})", r"; (\d+) slices have a 25 Hz", (lambda pp: lambda r: (float(len(sel(r, "F3", pp, startswith="25 Hz crossing"))),))(p))
        add("F3", p, f"maximum on ({p}) (no 100 Hz contour)", r"maximum ([\d.]+) Hz", (lambda pp: lambda r: (V(sel(r, "F3", pp, startswith="limit-cycle frequency shading")).max(),))(p))
    add("F3", "a", "colour scale of (a) to (c)", r"colour scale ([\d.]+) to ([\d.]+) Hz", lambda r: (min(V(sel(r, "F3", p, startswith="limit-cycle frequency shading")).min() for p in "abc"), max(V(sel(r, "F3", p, startswith="limit-cycle frequency shading")).max() for p in "abc")))
    add("F3", "d", "Hopf curve reaches eta_bar ... at Delta 1", r"eta_bar ([\d.]+) at Delta 1", lambda r: (X(sel(r, "F3", "d", startswith="A4 Hopf curve")).max(),))
    add("F3", "e", "up legs from ... to ... (eta_bar)", r"\(([\d.]+) to ([\d.]+) for the up legs", lambda r: (X(sel(r, "F3", "e")).min(), X(sel(r, "F3", "e")).max()))
    # F4a
    add("F4a", "a", "delays from about ... to ...", r"delays from about ([-−]?[\d.]+) to ([\d.]+)", lambda r: _f4a_delay(r))
    add("F4a", "c", "errors of the testable runs, ... to ... steps", r"errors, ([\d.]+) to ([\d.]+) steps", lambda r: (Y(sel(r, "F4a", "c", contains="error of the prediction")).min(), Y(sel(r, "F4a", "c", contains="error of the prediction")).max()))
    add("F4a", "d", "medians of the three levels", r"about ([-−][\d.]+), ([-−][\d.]+), ([-−][\d.]+)\)", lambda r: tuple(Y(sel(r, "F4a", "d", startswith=f"floor level {L}: median"))[0] for L in range(3)))
    add("F4a", "a", "ramp-rate axis from ... to ...", r"logarithmic axis, ([\d.e-]+) to ([\d.e-]+)\)", lambda r: (X(sel(r, "F4a", "a", startswith="P1 linear: delay, raw")).min(), X(sel(r, "F4a", "a", startswith="P1 linear: delay, raw")).max()))
    add("F4a", "e", "delays tie at ... at the two lower levels", r"tie at ([-−][\d.]+) at levels", lambda r: (float(np.unique(Y(sel(r, "F4a", "e", startswith="floor level 0")))[0]),))
    # F4b
    add("F4b", "f", "jump offset from ... to ... (slowest and fastest ramp)", r"from ([\d.]+) to ([\d.]+) over", lambda r: _f4b_offset(r))
    add("F4b", "g", "fitted rate between ... and ... per s", r"between ([-−]?[\d.]+) and ([-−]?[\d.]+) per s", lambda r: (Y(sel(r, "F4b", "g")).min(), Y(sel(r, "F4b", "g")).max()))
    add("F4b", "g", "damped at N of 13", r"damped at (\d+) of 13", lambda r: (float(len(sel(r, "F4b", "g"))),))
    add("F4b", "d", "duration floor (smallest duration at T_ramp >= 60 s)", r"dotted line at ([\d.]+) s", lambda r: (_f4b_dur(r)[0],))
    add("F4b", "d", "shortest duration of any ramp", r"down to ([\d.]+) s", lambda r: (_f4b_dur(r)[1],))
    # F5
    add("F5", "a", "D-tr cells", r"D-tr (\d+) cells", lambda r: (float((sel(r, "F5", "a", startswith="map1 class").value == "D-tr").sum()),))
    add("F5", "a", "D-none cells", r"D-none (\d+) cells of (\d+)", lambda r: (float((sel(r, "F5", "a", startswith="map1 class").value == "D-none").sum()), float(len(sel(r, "F5", "a", startswith="map1 class")))))
    add("F5", "c", "agree, disagree, tie", r"agree (\d+), disagree (\d+), tie (\d+)", lambda r: tuple(float((sel(r, "F5", "c").value.astype(str) == s).sum()) for s in ("0", "1", "2")))
    add("F5", "d", "agree, disagree, tie (post-hoc view)", r"agree (\d+), disagree (\d+), tie (\d+)", lambda r: tuple(float((sel(r, "F5", "d").value.astype(str) == s).sum()) for s in ("0", "1", "2")))
    add("F5", "e", "D-tr and D-none cells of the 325", r"D-tr (\d+) cells, D-none (\d+) cells of (\d+)", lambda r: (float((sel(r, "F5", "e", startswith="map2 class").value == "D-tr").sum()), float((sel(r, "F5", "e", startswith="map2 class").value == "D-none").sum()), float(len(sel(r, "F5", "e", startswith="map2 class")))))
    # F6
    add("F6", "d", "onset about ... to ... s", r"\(about (\d+) to (\d+) s\)", lambda r: tuple(round(v) for v in (Y(sel(r, "F6", "d", notcontains="class")).min(), Y(sel(r, "F6", "d", notcontains="class")).max())))
    add("F6", "e", "P3 and P4b and P2 near ... to ... Hz", r"near (\d+) to ([\d.]+) Hz", lambda r: (round(float(Y(sel(r, "F6", "e", startswith="P2", notcontains="class")).min())), float(Y(sel(r, "F6", "e", startswith="P2", notcontains="class")).max())))
    add("F6", "e", "P4a near ... Hz", r"P4a is near (\d+) Hz", lambda r: (round(float(Y(sel(r, "F6", "e", startswith="P4a", notcontains="class")).mean())),))
    add("F6", "e", "P3 at drive 2 near ... to ... Hz", r"near (\d+) to ([\d.]+) Hz\.?$", lambda r: (round(float(Y(sel(r, "F6", "e", startswith="P3, I_amp 2", notcontains="class")).min())), float(Y(sel(r, "F6", "e", startswith="P3, I_amp 2", notcontains="class")).max())))
    # FS1
    add("FS1", "b", "focus frequency from ... to ... Hz", r"from ([\d.]+) to ([\d.]+) Hz", lambda r: (V(sel(r, "FS1", "b", startswith="frequency of the stable focus")).min(), V(sel(r, "FS1", "b", startswith="frequency of the stable focus")).max()))
    add("FS1", "c", "largest cycles per e-fold", r"largest value ([\d.]+)", lambda r: (V(sel(r, "FS1", "c", startswith="cycles per e-fold")).max(),))
    add("FS1", "d", "r from ... towards ...", r"rises from ([\d.]+) to a first peak.*towards ([\d.]+);", lambda r: (Y(sel(r, "FS1", "d", startswith="recorded r(t)"))[0], Y(sel(r, "FS1", "d", startswith="focus value"))[0]))
    add("FS1", "d", "first peak near ...", r"first peak near ([\d.]+)", lambda r: (Y(sel(r, "FS1", "d", startswith="recorded r(t)")).max(),))
    add("FS1", "d", "fit window ... and ... ms", r"\((\d+) and (\d+) ms\)", lambda r: (X(sel(r, "FS1", "d", startswith="fit window")).min(), X(sel(r, "FS1", "d", startswith="fit window")).max()))
    add("FS1", "a", "cusp", r"cusp \(eta_bar/Delta ([-−]?[\d.]+), J/sqrt\(Delta\) ([\d.]+)\)", lambda r: (X(sel(r, "FS1", "a", startswith="cusp"))[0], Y(sel(r, "FS1", "a", startswith="cusp"))[0]))
    add("FS1", "a", "test point (eta_bar/Delta, J/sqrt(Delta))", r"test point \(([-−]?\d+), (\d+)\)", lambda r: (X(sel(r, "FS1", "a", startswith="test point"))[0], Y(sel(r, "FS1", "a", startswith="test point"))[0]))
    # FS2
    add("FS2", "a", "Hopf point", r"Hopf point \(([\d.]+) ms", lambda r: (X(sel(r, "FS2", "a", startswith="Hopf point"))[0],))
    add("FS2", "i", "largest ratio of Delta to eta_bar", r"marks lie at ([\d.]+)", lambda r: (Y(sel(r, "FS2", "i")).max(),))
    add("FS2", "j", "largest deviation from 1", r"deviation from 1 is ([\d.]+)", lambda r: (float(np.abs(Y(sel(r, "FS2", "j")) - 1).max()),))
    # FS3
    add("FS3", "a", "surge-class ramp seeds at the four N", r"seeds: (\d+), (\d+), (\d+), (\d+) of 10", lambda r: _fs3_surge(r))
    # FS4
    add("FS4", "a", "default onset", r"five rows lie at ([\d.]+) s", lambda r: (X(sel(r, "FS4", "a", startswith="Default: classifier"))[0],))
    add("FS4", "a", "Radau onset", r"Radau row at ([\d.]+) s", lambda r: (X(sel(r, "FS4", "a", startswith="Radau solver: classifier"))[0],))
    add("FS4", "a", "Radau minus default in ms", r"= (\d+) ms against", lambda r: (round(1000 * (X(sel(r, "FS4", "a", startswith="Radau solver: classifier"))[0] - X(sel(r, "FS4", "a", startswith="Default: classifier"))[0])),))
    add("FS4", "g", "changes above the bound", r"(\d+) of the (\d+) changes lie above", lambda r: (float((Y_g(r) > 0.02).sum()), float(len(Y_g(r)))))
    add("FS4", "g", "range of the changes (percent)", r"range (\d+) to (\d+) percent", lambda r: (round(100 * Y_g(r).min()), round(100 * Y_g(r).max())))
    add("FS4", "d", "delays at levels 0 and 1", r"delays are ([-−][\d.]+) at levels 0 and 1", lambda r: (float(np.unique(np.concatenate([Y(sel(r, "FS4", "d", startswith="level 0")), Y(sel(r, "FS4", "d", startswith="level 1"))]))[0]),))
    add("F6", "a", "largest primary bar of map 1 and of map 2", r"label ([a-h]) \((\d+)\) in map 1 and label ([a-h]) \((\d+)\) in map 2", lambda r: _f6_top(r))
    add("F6", "a", "largest any-label bar of map 1", r"map 1: label ([a-h]) \((\d+)\)\)", lambda r: _f6_top(r, any_=True))
    add("F6", "a", "primary label counts of both maps (a, c, f, g, h)", r"counts a (\d+), c (\d+), f (\d+), g (\d+), h (\d+)\)", lambda r: _f6_sum(r))
    add("F2", "b", "largest relative difference of the mean-field up and down amplitudes from 0.2 above the Hopf point", r"relative difference ([\d.]+), recorded", lambda r: _f2_updown(r))
    for L in range(3):
        add("FS4", "c", f"raw-crossing delays of level {L}: smallest, largest, median", rf"level {L} from ([-−]?[\d.]+) to ([-−]?[\d.]+) \(median ([-−]?[\d.]+)\)", (lambda LL: lambda r: _fs4_level(r, LL))(L))
    # FS5
    add("FS5", "e", "records that are not NS (six windows)", r"\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\)", lambda r: _fs5_nons(r))
    return [c for c in C if c is not None]


def Y_or_V(d):
    return _n(d.value)


def Y_g(r):
    return np.concatenate([Y(sel(r, "FS4", "g", startswith=f"seed {s}")) for s in (0, 1, 2)])


def _f1_ramp(r):
    d = sel(r, "F1", "a", startswith="eta_bar(t)")
    t, y = X(d), Y(d)
    lo, hi = y.min(), y.max()
    return (float(t[y > lo + 1e-9].min()), float(t[y < hi - 1e-9].max()))


def _f1_before(r):
    d = sel(r, "F1", "c", contains="block maximum")
    on = X(sel(r, "F1", "c", startswith="mean-field stored onset"))[0]
    return float(Y(d)[X(d) < on].max())


def _f1_top(r):
    from . import style as S
    v = V(sel(r, "F1", "i"))
    top = float(np.percentile(v, S.F1_RASTER["top_percentile"]))
    return (top, float((v > top).sum()), float(v.size))


def _f2_net(r):
    hopf = X(sel(r, "F2", "a", startswith="Hopf point"))[0]
    d = sel(r, "F2", "b", startswith="network sweep v amplitude")
    y, x = Y(d), X(d)
    return (float(y[x < hopf - 1e-6].min()), float(y[x < hopf - 1e-6].max()))


def _f4a_delay(r):
    d = src(r, "F4a")
    d = d[(d.panel == "a") & d.series.str.contains("delay,") & ~d.series.str.contains("main example")]
    y = Y(d)
    return (float(np.nanmin(y)), float(np.nanmax(y)))


def _f4b_offset(r):
    d = sel(r, "F4b", "f")
    o = np.argsort(X(d))
    y = Y(d)[o]
    return (float(y[0]), float(y[-1]))


def _f4b_dur(r):
    d = sel(r, "F4b", "d")
    d = d[d.series.str.contains("duration")]
    y, x = Y(d), X(d)
    ok = np.isfinite(y)
    y, x = y[ok], x[ok]
    return (float(y[0.035 / x >= 60 - 1e-9].min()), float(y.min()))


def _fs3_surge(r):
    a = src(r, "FS3")
    a = a[(a.panel == "a") & a.series.str.startswith("ramp seeds in class")]
    tot = {}
    for _, row in a.iterrows():
        cls = re.search(r"class (\S+)", row.series).group(1)
        if cls in ("S+", "S-rel", "S-abs"):
            tot[row.x] = tot.get(row.x, 0.0) + float(row.y)
    return tuple(tot[k] for k in sorted(tot))


def _fs5_nons(r):
    a = src(r, "FS5")
    a = a[(a.panel == "e") & a.series.str.contains("white-noise records in class") & ~a.series.str.contains("class NS")]
    out = {}
    for _, row in a.iterrows():
        out[row.x] = out.get(row.x, 0.0) + float(row.y)
    return tuple(out[k] for k in sorted(out))


def _f6_top(r, any_=False):
    d = sel(r, "F6", "a", startswith="map 1, every label" if any_ else "map 1, primary label")
    d2 = sel(r, "F6", "a", startswith="map 2, primary label")
    out = []
    for dd in ((d,) if any_ else (d, d2)):
        y = Y(dd)
        out += ["abcdefgh"[int(np.argmax(y))], float(y.max())]
    return tuple(out)


def _f6_sum(r):
    a = Y(sel(r, "F6", "a", startswith="map 1, primary label")) + Y(sel(r, "F6", "a", startswith="map 2, primary label"))
    return tuple(float(a["abcdefgh".index(c)]) for c in "acfgh")


def _f2_updown(r):
    hopf = X(sel(r, "F2", "a", startswith="Hopf point"))[0]
    u = sel(r, "F2", "b", startswith="mean field sweep v amplitude, up").sort_values("x")
    d = sel(r, "F2", "b", startswith="mean field sweep v amplitude, down").sort_values("x")
    x, uy, dy = X(u), Y(u), Y(d)
    m = x >= hopf + 0.2 - 1e-6
    return (float(np.nanmax((np.abs(uy - dy) / uy)[m])),)


def _fs4_level(r, L):
    y = Y(sel(r, "FS4", "c", startswith=f"level {L},"))
    return (float(y.min()), float(y.max()), float(np.median(y)))


CHECKS = None


def rows(root) -> list:
    """[(figure, panel, claim, value(s) in the text, stored value(s), equal)] for every check; a check whose pattern is not found in the alt text is a row with equal = False."""
    global CHECKS
    if CHECKS is None:
        CHECKS = _checks()
    out = []
    cache: dict = {}
    for fid, panel, claim, rx, fn in CHECKS:
        a = cache.setdefault(fid, alt(root, fid))
        m = re.search(rx, a.get(panel, ""))
        if m is None:
            out.append((fid, panel, claim, None, None, False))
            continue
        toks = [g.rstrip(".,") for g in m.groups() if g is not None]
        stored = tuple(x if isinstance(x, str) else float(x) for x in fn(root))
        if len(toks) != len(stored):
            out.append((fid, panel, claim, tuple(toks), stored, False))
            continue
        eq = all((t == s) if isinstance(s, str) else abs(_val(t) - s) <= _tol(t) for t, s in zip(toks, stored))
        out.append((fid, panel, claim, tuple(toks), tuple(s if isinstance(s, str) else round(s, 6) for s in stored), bool(eq)))
    return out


def coverage(root, allow: dict) -> list:
    """Numbers of the alt texts that no check covers, that are not in the caption of the same figure and that are not in `allow` ({figure: [token, ...]}, the structure and drawing constants, each listed with its reason in the test)."""
    global CHECKS
    if CHECKS is None:
        CHECKS = _checks()
    out = []
    for fid in IDS:
        a = alt(root, fid)
        cap = ""
        for p in Path(root).glob(f"figures/journal/{fid}/{fid}_journal_caption*.txt"):
            cap += p.read_text(encoding="utf-8") + "\n"
        cap_toks = set(NUMTOK.findall(cap))
        covered = set()
        for f2, panel, claim, rx, fn in CHECKS:
            if f2 == fid and panel in a:
                m = re.search(rx, a[panel])
                if m:
                    for g in m.groups():
                        if g is not None:
                            covered.add((panel, g))
        for panel, text in a.items():
            for tok in NUMTOK.findall(text):
                tok = tok.rstrip(".,")
                if (panel, tok) in covered or tok in cap_toks or tok in allow.get(fid, ()):
                    continue
                out.append((fid, panel, tok))
    return out
