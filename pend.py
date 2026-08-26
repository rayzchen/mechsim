from mechsim.deriv import Expression, Var
from mechsim.engine import Solver
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

STEPS = 10
dt = 1/60
last = 0
def update(timestamp):
    global last
    progress = min(timestamp / 1000 - last, dt)
    last = timestamp / 1000

    while progress > dt / STEPS:
        progress -= dt / STEPS
        solver.step(dt / STEPS)

    window.drawSystem(ffi.to_js(solver.get_params()))
    window.requestAnimationFrame(ffi.create_proxy(update))

    t, v = solver.get_energies()
    label.innerHTML = f"Kinetic: {t:.2f} | Potential: {v:.2f} | Total: {t + v:.2f}"

if __name__ == "__main__":
    from pyscript import window, ffi, web
    label = web.page["#energy-label"]
    update(last)
