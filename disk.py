from mechsim import Expression, Var, Solver
from mechsim.system import Disk, Vector

Expression.context = ["x", "theta"]
ring = Disk("m1", "I1", Var("r1"))
ring.constrain_plane("x", Vector(1, 0))
disk = Disk("m2", "I2", Var("r2"))
disk.constrain_circle("theta", ring.position, ring.radius, ring.rotation)
kinetic = ring.kinetic() + disk.kinetic()
potential = ring.potential() + disk.potential()

solver = Solver(kinetic, potential)
solver.load_constants({"m1": 1, "m2": 3, "g": 10, "I1": 0.5, "I2": 0.2, "r1": 2, "r2": 0.5})
solver.load_initial_values([-1, 1], [0, 0])

if __name__ == "__main__":
    from runner import load_solver
    load_solver(solver)
