# A5: periodic-orbit continuation of M3 from the A4 Hopf points (plan 5.2 A5, 9.1, D23; MS6 step 6b).
#   branch "ceni":    parameter tau_d/tau at ref_ceni (eta 1, J -20, Delta 0.05, tau 10 ms), K7 criticality.
#   branch "devalle": parameter eta_bar at ref_devalle (J -21, Delta 0.3, tau_d 5 ms, tau 10 ms), A_ref.
#
# Run (by hand, not in pytest, DL-063):
#   julia --project=environment\julia src\mprsurge\analysis\continuation\a5_cycles.jl [outdir]
# Writes, per branch name <b> in {ceni, devalle}: a5_<b>_fixed.csv (fixed-point branch), a5_<b>_po.csv
# (periodic-orbit branch), and a5.json (one record). scripts/run_A5.py validates them.
#
# Method (UNVERIFIED choices are the numerical settings; the method follows the smoke test, DL-074):
#   fixed points: PALC continuation of the M3 right-hand side of plan 3.1 in tau-units (as models/mpr3d.py);
#   Hopf: first Hopf point of the fixed branch, normal form from get_normal_form (type = BifurcationKit's verdict);
#   cycles: orthogonal collocation Collocation(Ntst = 40, m = 4, meshadapt = true), PALC, started from the Hopf point,
#   once in each direction of the parameter; Floquet stability from the package (detect_bifurcation = 1).
# Time is in tau units; amplitude_v is v max - v min over the cycle (peak to peak, our readout, UNVERIFIED).
using BifurcationKit, Setfield, JSON3, SHA, Dates
const BK = BifurcationKit

const TAU_MS = 10.0

# name => (parameter lens name, base parameters, p_min, p_max, start parameter value for the fixed branch)
const BRANCHES = (
    ceni = (par = (eta = 1.0, J = -20.0, Delta = 0.05, td = 0.3), lens = (@optic _.td), p_min = 0.1, p_max = 1.0,
            ds = 0.005, dsmax_fp = 0.01, dsmax_po = 0.01, steps_po = 400),
    devalle = (par = (eta = 0.0, J = -21.0, Delta = 0.3, td = 0.5), lens = (@optic _.eta), p_min = 0.0, p_max = 8.0,
               ds = 0.01, dsmax_fp = 0.05, dsmax_po = 0.02, steps_po = 600),
)

function m3!(dz, z, p, t = 0)
    r, v, s = z
    dz[1] = p.Delta / pi + 2r * v
    dz[2] = v^2 + p.eta + p.J * s - pi^2 * r^2
    dz[3] = (r - s) / p.td
    dz
end

# Fixed points: s = r, v = -Delta/(2 pi r); g(r) = Delta^2/(4 pi^2 r^2) + eta + J r - pi^2 r^2 = 0.
function fixed_roots(p)
    g(r) = p.Delta^2 / (4pi^2 * r^2) + p.eta + p.J * r - pi^2 * r^2
    rs = exp10.(range(-6, 1, length = 20001))
    roots = Float64[]
    for i in 1:length(rs)-1
        if g(rs[i]) * g(rs[i+1]) < 0
            a, b = rs[i], rs[i+1]
            for _ in 1:200
                m = (a + b) / 2
                g(a) * g(m) <= 0 ? (b = m) : (a = m)
            end
            push!(roots, (a + b) / 2)
        end
    end
    roots
end

function run_branch(name, cfg, outdir)
    t0 = time()
    roots = fixed_roots(cfg.par)
    length(roots) == 1 || error("$name: expected one fixed point at the start, found $(length(roots)): $roots")
    r0 = roots[1]
    z0 = [r0, -cfg.par.Delta / (2pi * r0), r0]
    prob = ODEBifProblem(m3!, z0, cfg.par, cfg.lens;
        record_from_solution = (x, p; k...) -> (r = x[1], v = x[2], s = x[3]))
    opts = ContinuationPar(p_min = cfg.p_min, p_max = cfg.p_max, dsmax = cfg.dsmax_fp, ds = cfg.ds,
        n_inversion = 8, max_steps = 2000, detect_bifurcation = 3)
    br = continuation(prob, PALC(), opts; normC = norminf)
    t_fp = time() - t0
    hopf_idx = findall(sp -> sp.type == :hopf, br.specialpoint)
    isempty(hopf_idx) && error("$name: no Hopf point on the fixed-point branch")
    sp = br.specialpoint[hopf_idx[1]]
    nf = get_normal_form(br, hopf_idx[1])

    t1 = time()
    recordPO(x, p; state, iter, k...) = begin
        xtt = BK.get_periodic_orbit(p.prob, x, BK.getparams(iter, state))
        (vmax = maximum(xtt[2, :]), vmin = minimum(xtt[2, :]), period = getperiod(p.prob, x, p.p))
    end
    pos = Dict{String,Any}()
    for (dirname, sgn) in (("up", 1), ("down", -1))
        opts_po = ContinuationPar(br.contparams, ds = sgn * 0.002, dsmin = 1e-5, dsmax = cfg.dsmax_po,
            max_steps = cfg.steps_po, detect_bifurcation = 1, tol_stability = 1e-5)
        try
            pos[dirname] = continuation(br, hopf_idx[1], opts_po,
                Collocation(40, 4; meshadapt = true, jacobian = BK.DenseAnalyticalInplace());
                record_from_solution = recordPO, normC = norminf, linear_algo = BK.COPBLS())
        catch e
            pos[dirname] = nothing
            @warn "$name: periodic-orbit continuation $dirname failed" exception = e
        end
    end
    t_po = time() - t1

    open(joinpath(outdir, "a5_$(name)_fixed.csv"), "w") do io
        println(io, "param,r,v,s,stable")
        for (i, pt) in enumerate(br.branch)
            println(io, join([pt.param, pt.r, pt.v, pt.s, br.stable[i]], ","))
        end
    end
    open(joinpath(outdir, "a5_$(name)_po.csv"), "w") do io
        println(io, "direction,param,vmax,vmin,amplitude_v,period_tau,frequency_hz,stable")
        for dirname in ("down", "up")
            b = pos[dirname]
            b === nothing && continue
            st = b.stable        # Floquet verdict per point (forwarded to the wrapped ContResult; checked in 6b)
            for (i, pt) in enumerate(b.branch)
                println(io, join([dirname, pt.param, pt.vmax, pt.vmin, pt.vmax - pt.vmin, pt.period,
                                  1 / (pt.period * TAU_MS * 1e-3), st[i]], ","))
            end
        end
    end
    folds = Any[]
    for dirname in ("down", "up")
        b = pos[dirname]
        b === nothing && continue
        for sp2 in b.specialpoint
            sp2.type in (:endpoint, :none) && continue
            push!(folds, Dict("direction" => dirname, "type" => string(sp2.type), "param" => sp2.param, "step" => sp2.step))
        end
    end
    return Dict{String,Any}(
        "lens" => string(cfg.lens), "base_parameters" => Dict(string(k) => v for (k, v) in pairs(cfg.par)),
        "hopf_param" => sp.param, "hopf_type" => string(nf.type), "hopf_omega_per_tau" => nf.ω,
        "hopf_a" => real(nf.nf.a), "hopf_b" => real(nf.nf.b),
        "hopf_frequency_hz" => nf.ω / (2pi) / (TAU_MS * 1e-3),
        "n_hopf_points" => length(hopf_idx), "hopf_params_all" => [br.specialpoint[i].param for i in hopf_idx],
        "fixed_point_start" => Dict("r" => r0, "v" => z0[2], "s" => r0),
        "n_fixed_points" => length(br.branch),
        "n_po_up" => pos["up"] === nothing ? 0 : length(pos["up"].branch),
        "n_po_down" => pos["down"] === nothing ? 0 : length(pos["down"].branch),
        "po_special_points" => folds,
        "timings_s" => Dict("fixed_point_branch_and_normal_form" => t_fp, "periodic_orbit" => t_po))
end

function main(outdir)
    mkpath(outdir)
    t0 = time()
    out = Dict{String,Any}()
    branches = Dict{String,Any}()
    for name in keys(BRANCHES)
        branches[string(name)] = run_branch(name, BRANCHES[name], outdir)
        println(name, ": Hopf at ", branches[string(name)]["hopf_param"], ", type ", branches[string(name)]["hopf_type"])
    end
    out["branches"] = branches
    root = abspath(joinpath(@__DIR__, "..", "..", "..", ".."))
    git(args...) = try strip(read(setenv(`git $args`, dir = root), String)) catch; nothing end
    manifest = joinpath(root, "environment", "julia", "Manifest.toml")
    out["commit"] = git("rev-parse", "HEAD")
    out["dirty"] = something(git("status", "--porcelain"), "") != ""
    out["julia_version"] = string(VERSION)
    out["bifurcationkit_version"] = string(pkgversion(BifurcationKit))
    out["manifest_sha256"] = bytes2hex(open(sha256, manifest))
    out["periodic_orbit_method"] = "orthogonal collocation, Collocation(Ntst=40, m=4, meshadapt=true), PALC, started from the Hopf point, both directions, Floquet stability detect_bifurcation=1"
    out["equations"] = "M3 plan 3.1, tau-units; tau = $(TAU_MS) ms; ceni parameter tau_d/tau, devalle parameter eta_bar"
    out["timings_s"] = Dict("total" => time() - t0)
    out["written_utc"] = string(Dates.now(Dates.UTC))
    open(joinpath(outdir, "a5.json"), "w") do io
        JSON3.pretty(io, out)
    end
end

main(length(ARGS) >= 1 ? ARGS[1] : joinpath("results", "A5", "julia"))
