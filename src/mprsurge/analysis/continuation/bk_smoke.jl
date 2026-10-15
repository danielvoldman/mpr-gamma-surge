# BifurcationKit smoke test (plan 9.1, D23, DL-063): Hopf normal form and periodic-orbit
# continuation of M3 at ref_ceni (K7, Table 7.1). Calls follow the package examples
# (examples/TMModel.jl of BifurcationKit 0.8.7): ODEBifProblem, continuation, get_normal_form,
# continuation(br, ind, opts, Collocation(...)).
#
# Run: julia --project=environment\julia src\mprsurge\analysis\continuation\bk_smoke.jl [outdir]
# Writes smoke_branch.csv (fixed-point branch), smoke_po.csv (periodic-orbit branch), smoke.json.
#
# Periodic-orbit method: orthogonal collocation, Collocation(Ntst = 40, m = 4, meshadapt = true).
# Equations are the M3 right-hand side of plan 3.1 in tau-units (as src/mprsurge/models/mpr3d.py);
# the continuation parameter is tau_d/tau. Time in the periodic orbit is in tau units (tau = 10 ms).
using BifurcationKit, Setfield, JSON3, SHA, Dates
const BK = BifurcationKit

const TAU_MS = 10.0                 # Table 3.2, ref_ceni (tau = 10 ms)
const PAR = (eta = 1.0, J = -20.0, Delta = 0.05, td = 0.3)   # td = tau_d/tau = 3 ms / 10 ms (K7: damped)

function m3!(dz, z, p, t = 0)
    r, v, s = z
    dz[1] = p.Delta / pi + 2r * v
    dz[2] = v^2 + p.eta + p.J * s - pi^2 * r^2
    dz[3] = (r - s) / p.td
    dz
end

# Fixed points: s = r, v = -Delta/(2 pi r), so g(r) = Delta^2/(4 pi^2 r^2) + eta + J r - pi^2 r^2 = 0.
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

function main(outdir)
    mkpath(outdir)
    t0 = time()
    roots = fixed_roots(PAR)
    length(roots) == 1 || error("expected one fixed point at ref_ceni, found $(length(roots)): $roots")
    r0 = roots[1]
    z0 = [r0, -PAR.Delta / (2pi * r0), r0]

    prob = ODEBifProblem(m3!, z0, PAR, (@optic _.td);
        record_from_solution = (x, p; k...) -> (r = x[1], v = x[2], s = x[3]))
    opts = ContinuationPar(p_min = 0.1, p_max = 1.0, dsmax = 0.01, ds = 0.005, n_inversion = 8,
        max_steps = 200, detect_bifurcation = 3)
    br = continuation(prob, PALC(), opts; normC = norminf)
    t_fp = time() - t0

    hopf_idx = findall(sp -> sp.type == :hopf, br.specialpoint)
    isempty(hopf_idx) && error("no Hopf point found on the fixed-point branch")
    sp = br.specialpoint[hopf_idx[1]]
    td_H = sp.param                                   # tau_d/tau at the Hopf point
    nf = get_normal_form(br, hopf_idx[1])
    # nf.nf.a is the first Lyapunov coefficient (see the package docs for the sign convention; nf.type is the package's own verdict).
    nfd = nf.nf
    out = Dict{String,Any}(
        "hopf_td_over_tau" => td_H, "hopf_tau_d_ms" => td_H * TAU_MS,
        
        "hopf_type" => string(nf.type), "hopf_omega_per_tau" => nf.ω, "hopf_a" => real(nfd.a), "hopf_b" => real(nfd.b),
        "fixed_point" => Dict("r" => r0, "v" => z0[2], "s" => r0))
    out["hopf_frequency_hz"] = nf.ω / (2pi) / (TAU_MS * 1e-3)   # omega is in rad per tau

    # Periodic orbits by orthogonal collocation, from the Hopf point.
    t1 = time()
    opts_po = ContinuationPar(br.contparams, ds = 0.002, dsmin = 1e-5, dsmax = 0.02, max_steps = 60,
        detect_bifurcation = 0, tol_stability = 1e-5)
    function recordPO(x, p; state, iter, k...)
        xtt = BK.get_periodic_orbit(p.prob, x, BK.getparams(iter, state))
        return (vmax = maximum(xtt[2, :]), vmin = minimum(xtt[2, :]), period = getperiod(p.prob, x, p.p))
    end
    br_po = continuation(br, hopf_idx[1], opts_po,
        Collocation(40, 4; meshadapt = true, jacobian = BK.DenseAnalyticalInplace());
        record_from_solution = recordPO, normC = norminf, linear_algo = BK.COPBLS())
    t_po = time() - t1

    open(joinpath(outdir, "smoke_branch.csv"), "w") do io
        println(io, "td_over_tau,tau_d_ms,r,v,s,stable")
        for (i, pt) in enumerate(br.branch)
            println(io, join([pt.param, pt.param * TAU_MS, pt.r, pt.v, pt.s, br.stable[i]], ","))
        end
    end
    open(joinpath(outdir, "smoke_po.csv"), "w") do io
        println(io, "td_over_tau,tau_d_ms,vmax,vmin,amplitude_v,period_tau,frequency_hz")
        for pt in br_po.branch
            println(io, join([pt.param, pt.param * TAU_MS, pt.vmax, pt.vmin, pt.vmax - pt.vmin,
                              pt.period, 1 / (pt.period * TAU_MS * 1e-3)], ","))
        end
    end

    root = abspath(joinpath(@__DIR__, "..", "..", "..", ".."))
    git(args...) = try strip(read(setenv(`git $args`, dir = root), String)) catch; nothing end
    manifest = joinpath(root, "environment", "julia", "Manifest.toml")
    out["commit"] = git("rev-parse", "HEAD")
    out["dirty"] = something(git("status", "--porcelain"), "") != ""
    out["julia_version"] = string(VERSION)
    out["bifurcationkit_version"] = string(pkgversion(BifurcationKit))
    out["manifest_sha256"] = bytes2hex(open(sha256, manifest))
    out["periodic_orbit_method"] = "orthogonal collocation, Collocation(Ntst=40, m=4, meshadapt=true), PALC, started from the Hopf point"
    out["equations"] = "M3 plan 3.1, tau-units; parameter tau_d/tau; eta=$(PAR.eta), J=$(PAR.J), Delta=$(PAR.Delta), tau=$(TAU_MS) ms"
    out["n_fixed_branch_points"] = length(br.branch)
    out["n_po_points"] = length(br_po.branch)
    out["timings_s"] = Dict("fixed_point_branch_and_normal_form" => t_fp, "periodic_orbit" => t_po, "total" => time() - t0)
    out["written_utc"] = string(Dates.now(Dates.UTC))
    open(joinpath(outdir, "smoke.json"), "w") do io
        JSON3.pretty(io, out)
    end
    println("Hopf tau_d = ", td_H * TAU_MS, " ms; type ", nf.type, "; a = ", real(nfd.a))
end

main(length(ARGS) >= 1 ? ARGS[1] : joinpath("results", "A5", "smoke"))
