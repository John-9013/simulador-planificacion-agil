from modelo import Historia, Simulador


def historias():
    return [Historia(f"H{i}", p) for i, p in enumerate([5, 3, 8, 13, 2])]


def test_simula_todo_el_backlog():
    sim = Simulador(historias(), equipo=4, dias=10, puntos_por_dev_dia=0.8, semilla=1)
    sim.simular_todo()
    assert sim.finalizado
    assert len(sim.terminadas) == 5
    assert sum(s["historias"] for s in sim.historial) == 5


def test_burndown_decrece_y_cierra_sprint():
    sim = Simulador(historias(), equipo=4, dias=5, semilla=2)
    sim.completar_sprint()
    assert len(sim.historial) == 1
    assert sim.compromiso == []


def test_historia_mayor_que_capacidad_se_planifica():
    sim = Simulador([Historia("Grande", 100)], equipo=1, dias=5, puntos_por_dev_dia=1, semilla=3)
    sim.simular_todo()
    assert sim.finalizado
    assert len(sim.historial) > 1


