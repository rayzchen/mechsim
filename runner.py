from mechsim import Expression, Solver
from pyscript import window, ffi, web

main_solver = None
energy_label = web.page["#energy-label"]

steps = 20
dt = 1/60
last = 0
paused = False
def update(timestamp):
    global last
    progress = min(timestamp / 1000 - last, dt + 1e-6)
    last = timestamp / 1000

    if paused:
        return

    while progress > dt / steps:
        progress -= dt / steps
        main_solver.step(dt / steps)

    window.drawSystem(ffi.to_js(main_solver.get_params()))
    request_update()

    t, v = main_solver.get_energies()
    window.setEnergyLabel(t, v)

def request_update():
    window.requestAnimationFrame(ffi.to_js(update))

def toggle_playback():
    global paused
    paused = not paused
    if not paused:
        request_update()

def step_playback():
    if paused:
        request_update()

def load_solver(solver, custom_steps=None, render_equations=True):
    global main_solver, steps
    main_solver = solver
    if custom_steps is not None:
        steps = custom_steps

    if render_equations:
        Expression.latex_mode = True
        solver2 = Solver(*solver.original)
        solver2.load_constants({})

        latex = "\\begin{align*}"
        latex += "\\\\".join(solver2.display_equations())
        latex += "\\end{align*}"
        window.setEquationlabel(latex)

    request_update()
