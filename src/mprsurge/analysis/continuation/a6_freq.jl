# A6: limit-cycle frequency slices of M3 for the frequency map (plan 5.2 A6, 9.1, CP23; MS6 step 6f).
# Every slice is one A5-style continuation: PALC fixed-point branch of the M3 right-hand side (plan 3.1, tau units), first Hopf
# point, cycles by orthogonal collocation from the Hopf point in the "up" direction (the supercritical side; A5 showed the
# "down" direction retraces it). Slices (grids UNVERIFIED, set in 6f, DL-131):
#   eta_tau:  for Delta in DELTAS, tau_d in TD_MS, J = -21: parameter eta_bar from 0 to 8.
#   eta_J:    Delta = 0.3, tau_d = 5 ms, J in J_PLANE: parameter eta_bar from 0 to 8.
#   k10:      eta_bar = 1, Delta = 0.05, J in K10_J: parameter tau_d/tau from 0.1 to 5.0 (1 to 50 ms), for the K10 recheck.
# Run (by hand, not in pytest, DL-063):
#   julia --project=environment\julia src\mprsurge\analysis\continuation\a6_freq.jl [outdir]
# Writes a6_po.csv (all slices), a6.json (one record, per-slice metadata). scripts/run_A6.py validates them.
using BifurcationKit, Setfield, JSON3, SHA, Dates
const BK = BifurcationKit

const TAU_MS = 10.0
const DELTAS = (0.05, 0.1, 0.3)
const TD_MS = (1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 22.0, 36.0, 50.0)
const J_PLANE = (-40.0, -30.0, -21.0, -12.0, -5.0)
const K10_J = (-40.0, -30.0, -20.0, -10.0, -5.0)

function slices()
    out = NamedTuple[]
    for D in DELTAS, t in TD_MS
        push!(out, (id = "eta_tau_D$(D)_td$(t)", group = "eta_tau", par = (eta = 0.0, J = -21.0, Delta = D, td = t / TAU_MS),
                    lens = (@optic _.eta), p_min = 0.0, p_max = 8.0, ds = 0.01, dsmax_fp = 0.05, dsmax_po = 0.02, steps_po = 600))
    end
    for J in J_PLANE
        push!(out, (id = "eta_J_J$(J)", group = "eta_J", par = (eta = 0.0, J = J, Delta = 0.3, td = 0.5),
                    lens = (@optic _.eta), p_min = 0.0, p_max = 8.0, ds = 0.01, dsmax_fp = 0.05, dsmax_po = 0.02, steps_po = 600))
    end
    for J in K10_J
        push!(out, (id = "k10_J$(J)", group = "k10", par = (eta = 1.0, J = J, Delta = 0.05, td = 0.3),
                    lens = (@optic _.td), p_min = 0.1, p_max = 5.0, ds = 0.005, dsmax_fp = 0.05, dsmax_po = 0.05, steps_po = 800))
    end
    haskey(ENV, "A6_ONLY") ? filter(c -> occursin(ENV["A6_ONLY"], c.id), out) : out   # A6_ONLY: substring filter for smoke tests
end

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

function run_slice(cfg, io_po)
    t0 = time()
    meta = Dict{String,Any}("id" => cfg.id, "group" => cfg.group, "lens" => string(cfg.lens),
        "base_parameters" => Dict(string(k) => v for (k, v) in pairs(cfg.par)), "p_min" => cfg.p_min, "p_max" => cfg.p_max,
        "status" => "ok", "error" => "", "n_hopf_points" => 0, "hopf_params_all" => Float64[], "hopf_param" => nothing,
        "hopf_type" => "", "hopf_frequency_hz" => nothing, "n_po" => 0, "po_param_min" => nothing, "po_param_max" => nothing,
        "po_special_points" => Any[], "fixed_stable_at_start" => false)
    try
        roots = fixed_roots(cfg.par)
        length(roots) == 1 || error("expected one fixed point at the start, found $(length(roots))")
        r0 = roots[1]
        z0 = [r0, -cfg.par.Delta / (2pi * r0), r0]
        prob = ODEBifProblem(m3!, z0, cfg.par, cfg.lens)
        opts = ContinuationPar(p_min = cfg.p_min, p_max = cfg.p_max, dsmax = cfg.dsmax_fp, ds = cfg.ds,
            n_inversion = 8, max_steps = 4000, detect_bifurcation = 3)
        br = continuation(prob, PALC(), opts; normC = norminf)
        meta["fixed_stable_at_start"] = Bool(br.stable[1])
        hopf_idx = findall(sp -> sp.type == :hopf, br.specialpoint)
        meta["n_hopf_points"] = length(hopf_idx)
        meta["hopf_params_all"] = [br.specialpoint[i].param for i in hopf_idx]
        if isempty(hopf_idx)
            meta["status"] = "no_hopf"
        else
            meta["hopf_param"] = br.specialpoint[hopf_idx[1]].param
            nf = get_normal_form(br, hopf_idx[1])
            meta["hopf_type"] = string(nf.type)
            meta["hopf_frequency_hz"] = nf.ω / (2pi) / (TAU_MS * 1e-3)
            recordPO(x, p; state, iter, k...) = begin
                xtt = BK.get_periodic_orbit(p.prob, x, BK.getparams(iter, state))
                (vmax = maximum(xtt[2, :]), vmin = minimum(xtt[2, :]), period = getperiod(p.prob, x, p.p))
            end
            opts_po = ContinuationPar(br.contparams, ds = 0.002, dsmin = 1e-5, dsmax = cfg.dsmax_po,
                max_steps = cfg.steps_po, detect_bifurcation = 1, tol_stability = 1e-5)
            b = continuation(br, hopf_idx[1], opts_po,
                Collocation(40, 4; meshadapt = true, jacobian = BK.DenseAnalyticalInplace());
                record_from_solution = recordPO, normC = norminf, linear_algo = BK.COPBLS())
            st = b.stable
            for (i, pt) in enumerate(b.branch)
                println(io_po, join([cfg.id, pt.param, pt.vmax, pt.vmin, pt.vmax - pt.vmin, pt.period,
                                     1 / (pt.period * TAU_MS * 1e-3), st[i]], ","))
            end
            ps = [pt.param for pt in b.branch]
            meta["n_po"] = length(ps)
            if !isempty(ps)
                meta["po_param_min"] = minimum(ps); meta["po_param_max"] = maximum(ps)
            end
            for sp2 in b.specialpoint
                sp2.type in (:endpoint, :none) && continue
                push!(meta["po_special_points"], Dict("type" => string(sp2.type), "param" => sp2.param, "step" => sp2.step))
            end
            meta["status"] = isempty(ps) ? "no_cycles" : "ok"
        end
    catch e
        meta["status"] = "error"
        meta["error"] = first(sprint(showerror, e), 300)
    end
    meta["wall_s"] = time() - t0
    meta
end

function main(outdir)
    mkpath(outdir)
    t0 = time()
    metas = Any[]
    open(joinpath(outdir, "a6_po.csv"), "w") do io_po
        println(io_po, "slice,param,vmax,vmin,amplitude_v,period_tau,frequency_hz,stable")
        for cfg in slices()
            m = run_slice(cfg, io_po)
            push!(metas, m)
            println(m["id"], ": ", m["status"], ", Hopf ", m["hopf_param"], ", n_po ", m["n_po"], ", ", round(m["wall_s"], digits = 1), " s")
            flush(stdout)
        end
    end
    out = Dict{String,Any}("slices" => metas)
    root = abspath(joinpath(@__DIR__, "..", "..", "..", ".."))
    git(args...) = try strip(read(setenv(`git $args`, dir = root), String)) catch; nothing end
    manifest = joinpath(root, "environment", "julia", "Manifest.toml")
    out["commit"] = git("rev-parse", "HEAD")
    out["dirty"] = something(git("status", "--porcelain"), "") != ""
    out["julia_version"] = string(VERSION)
    out["bifurcationkit_version"] = string(pkgversion(BifurcationKit))
    out["manifest_sha256"] = bytes2hex(open(sha256, manifest))
    out["periodic_orbit_method"] = "orthogonal collocation, Collocation(Ntst=40, m=4, meshadapt=true), PALC, started from the first Hopf point, up direction, Floquet stability detect_bifurcation=1"
    out["equations"] = "M3 plan 3.1, tau-units; tau = $(TAU_MS) ms; eta_bar slices and tau_d/tau slices"
    out["timings_s"] = Dict("total" => time() - t0)
    out["written_utc"] = string(Dates.now(Dates.UTC))
    open(joinpath(outdir, "a6.json"), "w") do io
        JSON3.pretty(io, out)
    end
end

main(length(ARGS) >= 1 ? ARGS[1] : joinpath("results", "A6", "julia"))
