from mechsim import Expression, Var, Solver
from mechsim.system import Mass, Vector

Expression.context = ["theta1", "theta2"]
mass1 = Mass("m1")
mass1.constrain_offset("theta1", Vector(0, -Var("l1")))
mass2 = Mass("m2")
mass2.constrain_offset("theta2", Vector(0, -Var("l2")), mass1.position)
kinetic = mass1.kinetic() + mass2.kinetic()
potential = mass1.potential() + mass2.potential()

solver = Solver(kinetic, potential)
solver.load_constants({"m1": 1, "m2": 1, "g": 10, "l1": 0.5, "l2": 0.5})
solver.load_initial_values([2, 3.14])

if __name__ == "__main__":
    from runner import load_solver
    load_solver(solver)
