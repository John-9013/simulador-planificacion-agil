"""Lógica del simulador de planificación ágil (sin dependencias de interfaz)."""
import random
from dataclasses import dataclass, field


@dataclass
class Historia:
    nombre: str
    puntos: float
    restante: float = field(init=False)

    def __post_init__(self):
        self.restante = float(self.puntos)

    @property
    def terminada(self):
        return self.restante <= 1e-9


class Simulador:
    def __init__(self, historias, equipo=5, dias=10, puntos_por_dev_dia=0.8, semilla=None):
        self.equipo = equipo
        self.dias = dias
        self.ppd = puntos_por_dev_dia
        self.rng = random.Random(semilla)
        self.backlog = list(historias)  # el orden de la lista es la prioridad
        self.terminadas = []
        self.historial = []  # un dict por sprint cerrado
        self.numero = 0
        self.compromiso = []
        self.total_comprometido = 0.0
        self.dia_actual = 0
        self.burndown = []

    @property
    def sprint_activo(self):
        return bool(self.compromiso) or self.dia_actual > 0

    @property
    def finalizado(self):
        return not self.backlog

    def velocidad_estimada(self):
        if self.historial:
            ultimos = [s["completado"] for s in self.historial[-3:]]
            return sum(ultimos) / len(ultimos)
        return self.equipo * self.dias * self.ppd

    def planificar(self):
        self.numero += 1
        capacidad = self.velocidad_estimada()
        self.compromiso, acumulado = [], 0.0
        for h in self.backlog:
            if acumulado + h.restante <= capacidad:
                self.compromiso.append(h)
                acumulado += h.restante
        if not self.compromiso and self.backlog:
            self.compromiso = [self.backlog[0]]
            acumulado = self.backlog[0].restante
        self.total_comprometido = acumulado
        self.dia_actual = 0
        self.burndown = [acumulado]

    def avanzar_dia(self):
        """Simula un día de trabajo. Devuelve True si el sprint se cerró."""
        if self.finalizado:
            return False
        if not self.compromiso:
            self.planificar()
        trabajo = sum(self.rng.uniform(0.5, 1.1) * self.ppd for _ in range(self.equipo))
        for h in self.compromiso:
            if trabajo <= 0:
                break
            usado = min(h.restante, trabajo)
            h.restante -= usado
            trabajo -= usado
        self.dia_actual += 1
        self.burndown.append(sum(h.restante for h in self.compromiso))
        if self.dia_actual >= self.dias:
            self._cerrar()
            return True
        return False

    def completar_sprint(self):
        while not self.finalizado and not self.avanzar_dia():
            pass

    def simular_todo(self, max_sprints=100):
        while not self.finalizado and self.numero < max_sprints:
            self.completar_sprint()

    def _cerrar(self):
        hechas = [h for h in self.compromiso if h.terminada]
        restante = sum(h.restante for h in self.compromiso)
        self.historial.append({
            "sprint": self.numero,
            "comprometido": self.total_comprometido,
            "completado": self.total_comprometido - restante,
            "historias": len(hechas),
        })
        self.terminadas.extend(hechas)
        self.backlog = [h for h in self.backlog if not h.terminada]
        self.compromiso = []
        self.dia_actual = 0

    def estado(self, historia):
        if historia in self.terminadas:
            return "Terminada"
        if historia in self.compromiso:
            return "En sprint"
        return "Pendiente"


