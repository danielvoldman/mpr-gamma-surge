# Julia environment for A5 (plan 9.1, 10.2). Run: julia --project=environment\julia environment\julia\setup_julia.jl
# First time (creating Project.toml/Manifest.toml): set MPRSURGE_JULIA_ADD=1. Otherwise instantiate from the committed Manifest.
using Pkg
if get(ENV, "MPRSURGE_JULIA_ADD", "") == "1"
    Pkg.add(["BifurcationKit", "Setfield", "ForwardDiff", "JSON3", "SHA"])
else
    Pkg.instantiate()
end
Pkg.precompile()
Pkg.status()
using BifurcationKit
println("BifurcationKit ", pkgversion(BifurcationKit))
