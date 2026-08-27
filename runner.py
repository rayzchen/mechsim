from mechsim import Expression, Solver
from pyscript import window, ffi, web

main_solver = None
energy_label = None

STEPS = 20
dt = 1/60
last = 0
def update(timestamp):
    global last
    progress = min(timestamp / 1000 - last, dt)
    last = timestamp / 1000

    while progress > dt / STEPS:
        progress -= dt / STEPS
        main_solver.step(dt / STEPS)

    window.drawSystem(ffi.to_js(main_solver.get_params()))
    window.requestAnimationFrame(ffi.create_proxy(update))

    t, v = main_solver.get_energies()
    energy_label.innerHTML = f"Kinetic: {t:.2f} | Potential: {v:.2f} | Total: {t + v:.2f}"

def load_solver(solver):
    global main_solver, energy_label

    main_solver = solver
    Expression.latex_mode = True
    solver2 = Solver(*solver.original)
    solver2.load_constants({})

    latex = "\\begin{align*}"
    latex += "\\\\".join(solver2.display_equations())
    latex += "\\end{align*}"
    window.setEquationlabel(latex)

    energy_label = web.page["#energy-label"]
    window.requestAnimationFrame(ffi.create_proxy(update))
