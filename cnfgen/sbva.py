"""SBVA wrapping code."""
import subprocess
from pysat.formula import CNF

def run_sbva(cnf):
    """Run SBVA on the input CNF data."""
    dimacs = cnf.to_dimacs()
    cp = subprocess.run(['sbva'], input=dimacs, text=True, capture_output=True, check=True)
    new_cnf = CNF()
    print(cp.stdout)
    new_cnf.from_string(cp.stdout)
    return new_cnf
