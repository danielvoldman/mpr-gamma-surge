# mpr-gamma-surge

## Windows setup (PowerShell)

```powershell
git clone <repository-url> mpr-gamma-surge; cd mpr-gamma-surge
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned   # once, if activation is blocked
.\.venv\Scripts\Activate.ps1
python -m pip install -r environment\requirements-lock.txt
python -m pip install -e . --no-deps
julia --project=environment\julia environment\julia\setup_julia.jl   # A5 only
python -m pytest -m "not slow"
python scripts\time_one_run.py --config configs\S5.yaml --cell headline --repeat 3
python -m mprsurge.run --config configs\S3.yaml --workers 6
python scripts\fig_FS2.py
# after a deliberate upgrade; writes UTF-8, not UTF-16:
python -m pip freeze --exclude-editable |
    Out-File -Encoding utf8 environment\requirements-lock.txt
```

The README also states the integrator, tolerances, step sizes, initial conditions, ramp protocol and gamma-power computation [R7, §6 rec. 6]. Julia is set up from a script file to avoid PowerShell quoting problems (CP8). On a clean machine: <repository-url> is a placeholder (in PowerShell, < is reserved); a repository downloaded as a ZIP carries Mark-of-the-Web, so run Get-ChildItem -Recurse | Unblock-File before activation; add -Force to Set-ExecutionPolicy when it is scripted; calling .venv\Scripts\python.exe directly avoids activation. Bootstrap order (MS0): install the direct dependencies, write environment/requirements.in with == pins from that first successful install, then write requirements-lock.txt with the freeze command above; later installs use the lock.

## To be filled when the code exists
