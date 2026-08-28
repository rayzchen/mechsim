from mechsim import Expression, Var, Solver
from mechsim.system import Vector, Disk, Mass, Spring, System
import math

Expression.context = ["x", "theta1", "theta2"]
ring = Disk("m", "I_m", Var("r_o"), Vector(0, -0.56 * Var("r_o")))
ring.constrain_plane("x", Vector(1, 0))
disk = Disk("m_r", "I_r", Var("r"))
disk.constrain_circle("theta1", ring.position, Var("r_i"), ring.rotation)

mass1 = Mass("m_p")
mass1.constrain_hinge("theta2", Vector(0.5 * Var("w_p"), -Var("l_p")), disk.position)
mass2 = Mass("m_p")
mass2.constrain_hinge("theta2", Vector(-0.5 * Var("w_p"), -Var("l_p")), disk.position)

midrim = 0.5 * (Var("r_o") + Var("r_i"))
spring1 = Spring(Vector(-Var("d_s"), -Var("r_o")), ring.local(Vector(0, -Var("r_o")).rotate(Var("theta_s"))), Var("l1"), Var("k"))
spring2 = Spring(Vector(Var("d_s"), -Var("r_o")), ring.local(Vector(0, -Var("r_o")).rotate(-Var("theta_s"))), Var("l1"), Var("k"))
spring3 = Spring(ring.local(Vector(0, -midrim)), disk.position, Var("l2"), Var("k2"))

system = System(ring, disk, mass1, mass2, spring1, spring2, spring3)
solver = Solver(system.kinetic(), system.potential())
solver.load_constants({
    "m": 12, "I_m": 1, "r_o": 0.32,
    "m_r": 2, "I_r": 0.02, "r": 0.08, "r_i": 0.22,
    "m_p": 0.8, "w_p": 0.1, "l_p": 0.3,
    "g": 9.81,
    "k": 400, "d_s": 0.4, "theta_s": math.pi * (3 / 8), "l1": 0.3,
    "k2": 400, "l2": 0.20
})
solver.load_initial_values([0.1, 0, 0])

if __name__ == "__main__":
    from runner import load_solver
    load_solver(solver, 2, False)
