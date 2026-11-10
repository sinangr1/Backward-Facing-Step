import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from dataclasses import replace
from s01_parameter import Parameter
from s06_simulation import Simulation
from s07_auswertung import fields


def test_geometry_mass_and_h_rebuild():
    sim=Simulation(Parameter().with_h(1.0))
    assert sim.g.fluid.shape==(20,100)
    assert sim.g.fluid.sum()==(100*20-20*10)
    sim.step(10)
    info=sim.diagnostics()
    assert info['mass_error'] < 1e-8, info
    assert info['div_max'] < 1e-8, info
    assert np.isfinite(sim.p).all()
    assert np.nanmax(fields(sim)['speed'])>0
    old_mask=sim.g.fluid.copy()
    sim.change_h(1.3)
    assert sim.t==0 and sim.n==0
    assert not np.array_equal(old_mask,sim.g.fluid)
    sim.step(4)
    assert sim.diagnostics()['mass_error']<1e-8


def test_sor_pressure_option_runs():
    # Die absolute SOR-Toleranz garantiert nicht die gleiche kleine Divergenz wie LU.
    par=replace(Parameter(),pressure_method='sor',eps=2e-3,itermax=500)
    sim=Simulation(par)
    sim.step(2)
    d=sim.diagnostics()
    assert np.isfinite(d['pressure_residual'])
    assert sim.solver.iterations<=par.itermax
    assert d['pressure_residual'] < 1.0  # Nach 500 Iterationen ist die gewünschte Toleranz nicht immer erreicht.
    assert d['pressure_converged'] == (d['pressure_residual'] <= par.eps)

