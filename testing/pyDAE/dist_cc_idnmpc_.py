#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from nmpc_mhe.pyomo_dae.MHEGen_pyDAE import MheGen_DAE
from sample_mods.distc_pyDAE.dist_cc import mod
from nmpc_mhe.aux.utils import load_iguess, create_bounds
from pyomo.environ import *
from pyomo.core.base import Var, Constraint, Param
from pyomo.opt import SolverFactory, ProblemFormat
from numpy import random
import sys, os
from shutil import copyfile, rmtree

__author__ = "David Thierry"

def disp_vars(mod, file):
    if not file is None:
        with open(file, "w") as f:
            for i in mod.component_objects(Var):
                i.display(ostream=f)
    else:
        for i in mod.component_objects(Var):
            i.display()

def disp_cons(mod, file):
    if not file is None:
        with open(file, "w") as f:
            for i in mod.component_objects(Constraint):
                i.pprint(ostream=f)
    else:
        for i in mod.component_objects(Constraint):
            i.pprint()

def disp_params(mod, file):
    if not file is None:
        with open(file, "w") as f:
            for i in mod.component_objects(Param):
                i.pprint(ostream=f)
    else:
        for i in mod.component_objects(Param):
            i.pprint()


def main():
    states = ["x", "M"]
    state_bounds = {#"M": (0.0, None),
                    #"Mv_p_": (0.0 - 1E-08, None),
                    #"T": (200, 512.4 - 1E-08),
                    #"pm": (1.0, None),
                    #"pn": (1.0, None),
                    #"L": (0.0, None),
                    #"V": (0.0, None),
                    #"x": (None, 1.0 + 1E-06),
                    #"y": (0.0, 1.0 + 1E-06),
                    #"hl": (1.0, 1e+07),
                    #"hv": (1.0, 1e+07),
                    #"Qc": (0.0, None),
                    #"D": (0.0, None),
                    #"Vm": (0.0, 1e+04),
                    #"beta": (0.0, 1.0 + 1E-06),
                    #"Mv": (0.155 + 1e-06, 1e+04),
                    #"Mv1": (8.5 + 1e-06, 1e+04),
                    #"Mvn": (0.17 + 1e-06, 1e+04)
                    }
    parfois = ["beta", "T", "y"]
    measurements = ["T", "Mv", "Qc"]
    controls = ["u1", "u2"]
    u_bounds = {"u1": (0000.1, 99.999), "u2": (0, None)}
    ref_state1 = {("T", (29,)): 343.15, ("T", (14,)): 361.15}
    ref_state2 = {("T", (29,)): 345.22, ("T", (14,)): 356.23}
    ref_state = ref_state1
    ref_state = {("y", (1,)): 1.0}
    ds = {}
    for k in ref_state2.keys():
        ds[k] = ref_state1[k] - ref_state2[k]



    e = MheGen_DAE(mod, 1, states, controls, states, measurements,
                   u_bounds=u_bounds,
                   ref_state=ref_state,
                   override_solver_check=True,
                   var_bounds=state_bounds,
                   nfe_t=2,
                   k_aug_executable='/home/dav0/in_dev_/kaugma57/bin/k_aug',
                   #ipopt_executable='/home/dav0/PycharmProjects/ipopt_van/build/bin/ipopt')
                   ipopt_executable='/home/dav0/in_dev_/ipopt_vanilla_l1/builds/ipopt_l1/bin/ipopt',
                   ncp_t=1,
                   parfois_v=parfois)
    Q = {}
    U = {}
    R = {}
    Q["x"] = 1e-05
    Q["M"] = 1
    R["T"] = 6.25e-02
    R["Qc"] = 1.00E+06
    R["Mv"] = 10e-08
    R["Mv1"] = 10e-08
    R["Mvn"] = 10e-08
    U["u1"] = 7.72700925775773761472464684629813E-01 * 0.01
    U["u2"] = 1.78604740940007800236344337463379E+06 * 0.001

    e.set_covariance_disturb(Q)
    e.set_covariance_u(U)
    e.set_covariance_meas(R)
    e.create_rh_sfx()

    e.get_state_vars()

    #create_bounds(e.SteadyRef, bounds=state_bounds)
    #create_bounds(e.PlantSample, bounds=state_bounds)

    e.SteadyRef.M[:, :].setlb(-1E-08)
    e.SteadyRef.L[:, :].setlb(-1E-08)
    e.SteadyRef.V[:, :].setlb(-1E-08)

    e.SteadyRef.T[:, :].setlb(100.0)
    e.SteadyRef.T[:, :].setub(512.4 - 1E-08)

    e.SteadyRef.Mv_p_[:, :].setlb(-1E-08)
    e.SteadyRef.Mv_n_[:, :].setlb(-1E-08)

    e.SteadyRef.y[:, :].setlb(-1E-08)
    e.SteadyRef.x[:, :].setlb(-1E-08)

    e.SteadyRef.y[:, :].setub(1.0 + 1E-6)
    e.SteadyRef.x[:, :].setub(1.0 + 1E-6)

    e.SteadyRef.beta[:, :].setlb(-1E-08)
    e.SteadyRef.beta[:, :].setub(1.0 + 1E-06)

    e.SteadyRef.nu_l[:, :].setlb(-1E-08)

    e.SteadyRef.write(filename="my_steady.nl", io_options={"symbolic_solver_labels": True})
    e.SteadyRef.display(filename="steady.disp0")
    e.solve_dyn(e.SteadyRef, stop_if_nopt=True, l1_mode=True, bound_push=1E-01, halt_on_ampl_error=True, iter_max=30000)

    e.SteadyRef.pprint(filename="steady.pprint")
    e.SteadyRef.display(filename="steady.disp")

    e.PlantSample.M[:,:].setlb(-1E-08)
    e.PlantSample.L[:, :].setlb(-1E-08)
    e.PlantSample.V[:, :].setlb(-1E-08)

    e.PlantSample.T[:, :].setlb(100.0)
    e.PlantSample.T[:, :].setub(512.4 - 1E-08)

    e.PlantSample.Mv_p_[:, :].setlb(-1E-08)
    e.PlantSample.Mv_n_[:, :].setlb(-1E-08)

    e.PlantSample.y[:, :].setlb(-1E-08)
    e.PlantSample.x[:, :].setlb(-1E-08)
    e.PlantSample.y[:, :].setub(1.0 + 1E-6)
    e.PlantSample.x[:, :].setub(1.0 + 1E-6)

    e.PlantSample.beta[:, :].setlb(-1E-08)
    e.PlantSample.beta[:, :].setub(1.0 + 1E-6)

    e.PlantSample.nu_l[:, :].setlb(-1E-08)

    #e.load_iguess_steady()
    load_iguess(e.SteadyRef, e.PlantSample, 0, 0)
    e.cycleSamPlant()
    stat = e.solve_dyn(e.PlantSample, stop_if_nopt=False, halt_on_ampl_error=False, l1_mode=True, bound_push=1e-2)
    e.PlantSample.display(filename="plant0.txt")
    # ipopt.solve(e.PlantSample, tee=True)

    # disp_vars(e.lsmhe, "vars_mhe")
    # disp_params(e.lsmhe, "parm_mhe")

    #: Prepare NMPC
    e.find_target_ss()
    e.SteadyRef2.display(filename="steady2.disp")

    e.create_nmpc()
    e.create_suffixes_nmpc()
    e.update_targets_nmpc()
    e.compute_QR_nmpc(n=-1)
    e.new_weights_olnmpc(1e-04, 1e-04)
    ii = 0
    f = open("errors_mhe", "w")
    f.close()
    f = open("errors_nmpc", "w")
    f.close()
    stat_mhe = 0
    stat_nmpc = 0
    #: Problem loop
    e.olnmpc.M[:, :].setlb(-1E-08)
    e.olnmpc.L[:, :].setlb(-1E-08)
    e.olnmpc.V[:, :].setlb(-1E-08)

    e.olnmpc.T[:, :].setlb(100.0)
    e.olnmpc.T[:, :].setub(512.4 - 1E-08)
    # e.olnmpc.Mv_p_.domain = Reals
    # e.olnmpc.Mv_p_[:, :].setlb(-1E-09)
    with open("mvplb0.txt", "w") as f:
        e.olnmpc.Mv_p_.display(ostream=f)
    # for i in e.olnmpc.Mv_p_.itervalues():
    #     i.setlb(-1E-08)
    with open("mvplb1.txt", "w") as f:
        e.olnmpc.Mv_p_.display(ostream=f)

    e.olnmpc.Mv_n_[:, :].setlb(-1E-08)

    e.olnmpc.y[:, :].setlb(-1E-08)
    e.olnmpc.x[:, :].setlb(-1E-08)

    e.olnmpc.y[:, :].setub(1.0 + 1E-6)
    e.olnmpc.x[:, :].setub(1.0 + 1E-6)
    e.olnmpc.beta.domain = Reals
    e.olnmpc.nu_l.domain = Reals
    e.olnmpc.beta[:, :].setlb(-1E-08)
    e.olnmpc.beta[:, :].setub(1.0 + 1E-6)
    e.olnmpc.nu_l[:, :].setlb(-1E-08)

    for i in range(0, 4000):
        #: Plant
        e.PlantSample.name = "plant_" + str(i)  #: To keep track
        stat = 0
        stat = e.solve_dyn(e.PlantSample, stop_if_nopt=False, halt_on_ampl_error=False, l1_mode=True)
        if stat != 0:
            print("heck...\tsecond try.", file=sys.stderr)
            stat = e.solve_dyn(e.PlantSample, stop_if_nopt=False, halt_on_ampl_error=False, l1_mode=True,
                               bound_push=1e-2)
        if stat != 0:
            print("heck...\tthird try.", file=sys.stderr)
            stat = e.solve_dyn(e.PlantSample, stop_if_nopt=False, halt_on_ampl_error=True, l1_mode=True,
                               bound_push=1e-1)
        if stat != 0:
            print("heck...\tlast try.", file=sys.stderr)
            stat = e.solve_dyn(e.PlantSample, stop_if_nopt=True, halt_on_ampl_error=True, l1_mode=True,
                               bound_push=1e-1)

        e.update_state_real()  # Update the current state
        e.update_soi_sp_nmpc()  #: To keep track of the state of interest.

        e.update_measurement()  # Update the current measurement
        e.compute_y_offset()  #: Get the offset for y
        #: State-estimation MHE

        e.print_r_dyn()
        #: Control NMPC
        e.preparation_phase_nmpc(as_strategy=False, make_prediction=False, plant_state=True)

        if i == 3:
            rmtree("nl_epsi")
            os.mkdir("nl_epsi")
            for j in range(0, 5):
                ep = 1 * 10 ** (-8 + j)
                e.olnmpc.epsi.set_value(ep)
                name = "olnmpc_" + str(8 - j) + ".nl"
                e.olnmpc.write(filename=name, io_options={"symbolic_solver_labels": True})
                copyfile(name, "./nl_epsi/" + name)

        e.olnmpc.epsi.set_value(1e-04)
        stat_nmpc = e.solve_dyn(e.olnmpc,
                                skip_update=False,
                                tag="olnmpc",
                                stop_if_nopt=False,
                                l1_mode=True, iter_max=30000)
        if stat_nmpc != 0:
            print("heck...\tsecond try [ol-NMPC].", file=sys.stderr)
            e.olnmpc.display(filename="failed_nmpc.txt")
            #e.olnmpc.epsi.set_value(1e-05)
            stat_nmpc = e.solve_dyn(e.olnmpc,
                                    skip_update=False,
                                    tag="olnmpc",
                                    stop_if_nopt=False,
                                    bound_push=1E-01,
                                    l1_mode=True,
                                    iter_max=30000,
                                    halt_on_ampl_error=True,
                                    rho_f_max=1E+08)
        if stat_nmpc != 0:
            print("heck...\tthird    try [ol-NMPC].", file=sys.stderr)
            #e.olnmpc.epsi.set_value(1e-03)
            stat_nmpc = e.solve_dyn(e.olnmpc,
                                    skip_update=False,
                                    tag="olnmpc",
                                    stop_if_nopt=True,
                                    bound_push=1E-00,
                                    l1_mode=True,
                                    iter_max=30000,
                                    halt_on_ampl_error=True,
                                    rho_f_max=1E+09)

        e.print_r_nmpc()

        if stat_nmpc == 0:
            e.olnmpc.display(filename="olnmpc_success.txt")
            e.update_u(e.olnmpc)
        else:
            e.update_u(e.SteadyRef2)

        #: Plant cycle
        e.cycleSamPlant(plant_step=True)
        e.plant_uinject(e.PlantSample, src_kind="dict", skip_homotopy=True)
        e.PlantSample.display(filename="plant.txt")


        #e.noisy_plant_manager(sigma=0.0001, action="apply", update_level=True)
        #: 0.001 is a good level


if __name__ == '__main__':
    e = main()