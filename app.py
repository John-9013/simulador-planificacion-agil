"""Interfaz tkinter del simulador interactivo de planificación ágil."""
import tkinter as tk
from tkinter import messagebox, ttk

from modelo import Historia, Simulador

HISTORIAS_INICIALES = [
    ("Login de usuarios", 5), ("Registro de cuenta", 3), ("Recuperar contraseña", 3),
    ("Panel principal", 8), ("Listado de productos", 5), ("Carrito de compras", 8),
    ("Pasarela de pago", 13), ("Historial de pedidos", 5), ("Notificaciones por correo", 3),
    ("Reportes de ventas", 8), ("Perfil de usuario", 2), ("Soporte en línea", 5),
]


MORADO_OSCURO = "#2e1065"
MORADO = "#5b21b6"
MORADO_MEDIO = "#7c3aed"
MORADO_CLARO = "#ddd6fe"
LAVANDA = "#f5f3ff"
FONDO = "#ede9fe"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador interactivo de planificación ágil")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=FONDO)
        self.base = list(HISTORIAS_INICIALES)
        self.sim = None
        self._aplicar_estilos()
        self._crear_widgets()
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.reiniciar()

    def _aplicar_estilos(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=FONDO, foreground=MORADO_OSCURO, font=("Segoe UI", 9))
        s.configure("TFrame", background=FONDO)
        s.configure("TLabel", background=FONDO, foreground=MORADO_OSCURO)
        s.configure("TLabelframe", background=FONDO, bordercolor=MORADO_MEDIO)
        s.configure("TLabelframe.Label", background=FONDO, foreground=MORADO, font=("Segoe UI", 9, "bold"))
        s.configure("TButton", background=MORADO_MEDIO, foreground="white", padding=6, borderwidth=0)
        s.map("TButton", background=[("active", MORADO), ("pressed", MORADO_OSCURO)])
        s.configure("Cerrar.TButton", background="#9f1239", foreground="white")
        s.map("Cerrar.TButton", background=[("active", "#be123c"), ("pressed", "#881337")])
        s.configure("TEntry", fieldbackground=LAVANDA)
        s.configure("TSpinbox", fieldbackground=LAVANDA, arrowcolor=MORADO)
        s.configure("Treeview", background=LAVANDA, fieldbackground=LAVANDA,
                    foreground=MORADO_OSCURO, rowheight=22)
        s.configure("Treeview.Heading", background=MORADO, foreground="white",
                    font=("Segoe UI", 9, "bold"))
        s.map("Treeview", background=[("selected", MORADO_MEDIO)], foreground=[("selected", "white")])
        s.map("Treeview.Heading", background=[("active", MORADO_MEDIO)])

    def cerrar(self):
        if messagebox.askyesno("Cerrar", "¿Deseas cerrar el simulador?", parent=self):
            self.destroy()

    def _crear_widgets(self):
        panel = ttk.Frame(self, padding=8)
        panel.pack(side="left", fill="y")

        params = ttk.LabelFrame(panel, text="Parámetros", padding=6)
        params.pack(fill="x")
        self.var_equipo = tk.IntVar(value=5)
        self.var_dias = tk.IntVar(value=10)
        self.var_ppd = tk.DoubleVar(value=0.8)
        for fila, (texto, var, desde, hasta, paso) in enumerate([
            ("Desarrolladores", self.var_equipo, 1, 20, 1),
            ("Días por sprint", self.var_dias, 1, 30, 1),
            ("Puntos/dev/día", self.var_ppd, 0.1, 5, 0.1),
        ]):
            ttk.Label(params, text=texto).grid(row=fila, column=0, sticky="w", pady=2)
            ttk.Spinbox(params, textvariable=var, from_=desde, to=hasta, increment=paso,
                        width=7).grid(row=fila, column=1, padx=4)

        back = ttk.LabelFrame(panel, text="Product Backlog (orden = prioridad)", padding=6)
        back.pack(fill="both", expand=True, pady=8)
        self.tabla = ttk.Treeview(back, columns=("nombre", "puntos", "estado"),
                                  show="headings", height=14)
        for col, texto, ancho in (("nombre", "Historia", 170), ("puntos", "Pts", 45),
                                  ("estado", "Estado", 80)):
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=ancho, anchor="w" if col == "nombre" else "center")
        self.tabla.pack(fill="both", expand=True)

        nueva = ttk.Frame(back)
        nueva.pack(fill="x", pady=(6, 0))
        self.var_nombre = tk.StringVar()
        self.var_puntos = tk.StringVar(value="3")
        ttk.Entry(nueva, textvariable=self.var_nombre, width=18).pack(side="left")
        ttk.Entry(nueva, textvariable=self.var_puntos, width=4).pack(side="left", padx=4)
        ttk.Button(nueva, text="Añadir", command=self.anadir).pack(side="left")
        ttk.Button(back, text="Eliminar seleccionada", command=self.eliminar).pack(fill="x", pady=(4, 0))

        derecha = ttk.Frame(self, padding=8)
        derecha.pack(side="left", fill="both", expand=True)

        botones = ttk.Frame(derecha)
        botones.pack(fill="x")
        for texto, cmd in (("Siguiente día", self.dia), ("Completar sprint", self.sprint),
                           ("Simular todo", self.todo), ("Reiniciar", self.reiniciar)):
            ttk.Button(botones, text=texto, command=cmd).pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Cerrar", style="Cerrar.TButton", command=self.cerrar).pack(side="right")
        self.lbl_estado = ttk.Label(derecha, text="", font=("Segoe UI", 10, "bold"), foreground=MORADO)
        self.lbl_estado.pack(anchor="w", pady=6)

        self.canvas = tk.Canvas(derecha, bg=LAVANDA, highlightthickness=1, highlightbackground=MORADO_MEDIO)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.dibujar())

        res = ttk.LabelFrame(derecha, text="Resultados por sprint", padding=6)
        res.pack(fill="x", pady=(8, 0))
        self.tabla_sprints = ttk.Treeview(res, columns=("s", "c", "h", "v"), show="headings", height=6)
        for col, texto in (("s", "Sprint"), ("c", "Comprometido"), ("h", "Completado"), ("v", "Historias")):
            self.tabla_sprints.heading(col, text=texto)
            self.tabla_sprints.column(col, width=110, anchor="center")
        self.tabla_sprints.pack(fill="x")

    def anadir(self):
        nombre = self.var_nombre.get().strip()
        try:
            puntos = float(self.var_puntos.get())
            if puntos <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "Los puntos deben ser un número mayor que 0.")
            return
        if not nombre:
            messagebox.showwarning("Dato inválido", "Escribe el nombre de la historia.")
            return
        self.sim.backlog.append(Historia(nombre, puntos))
        self.base.append((nombre, puntos))
        self.var_nombre.set("")
        self.refrescar()

    def eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        indice = self.tabla.index(seleccion[0])
        if indice >= len(self.sim.backlog) or self.sim.backlog[indice] in self.sim.compromiso:
            messagebox.showinfo("No permitido", "Solo se pueden eliminar historias pendientes.")
            return
        historia = self.sim.backlog.pop(indice)
        self.base = [b for b in self.base if b != (historia.nombre, historia.puntos)]
        self.refrescar()

    def reiniciar(self):
        try:
            equipo, dias, ppd = self.var_equipo.get(), self.var_dias.get(), self.var_ppd.get()
        except tk.TclError:
            messagebox.showwarning("Parámetros inválidos", "Revisa los valores numéricos.")
            return
        self.sim = Simulador([Historia(n, p) for n, p in self.base], equipo, dias, ppd)
        self.refrescar()

    def _avanzar(self, accion):
        if self.sim.finalizado:
            messagebox.showinfo("Fin", "El backlog está completo.")
            return
        accion()
        self.refrescar()

    def dia(self):
        self._avanzar(self.sim.avanzar_dia)

    def sprint(self):
        self._avanzar(self.sim.completar_sprint)

    def todo(self):
        self._avanzar(self.sim.simular_todo)

    def refrescar(self):
        sim = self.sim
        self.tabla.delete(*self.tabla.get_children())
        for h in sim.backlog:
            self.tabla.insert("", "end", values=(h.nombre, f"{h.restante:.1f}", sim.estado(h)))
        for h in sim.terminadas:
            self.tabla.insert("", "end", values=(h.nombre, f"{h.puntos:g}", "Terminada"))
        self.tabla_sprints.delete(*self.tabla_sprints.get_children())
        for s in sim.historial:
            self.tabla_sprints.insert("", "end", values=(
                s["sprint"], f"{s['comprometido']:.1f}", f"{s['completado']:.1f}", s["historias"]))
        pendientes = sum(h.restante for h in sim.backlog)
        if sim.finalizado:
            texto = f"Proyecto completado en {len(sim.historial)} sprints."
        elif sim.compromiso:
            texto = f"Sprint {sim.numero} - día {sim.dia_actual}/{sim.dias}"
        else:
            texto = f"Listo para planificar el sprint {sim.numero + 1}"
        self.lbl_estado.config(text=f"{texto}   |   Puntos pendientes: {pendientes:.1f}")
        self.dibujar()

    def dibujar(self):
        c = self.canvas
        c.delete("all")
        sim = self.sim
        w, h = c.winfo_width(), c.winfo_height()
        izq, der, arr, aba = 50, w - 20, 30, h - 35
        c.create_text(w / 2, 14, text="Burndown del sprint actual", font=("Segoe UI", 11, "bold"), fill=MORADO)
        if not sim or not sim.burndown or der <= izq:
            c.create_text(w / 2, h / 2, text="Pulsa «Siguiente día» para iniciar el sprint", fill="#7c6fa8")
            return
        total = sim.total_comprometido or 1

        def px(dia):
            return izq + (der - izq) * dia / sim.dias

        def py(valor):
            return aba - (aba - arr) * valor / total

        c.create_line(izq, arr, izq, aba, der, aba, fill=MORADO_OSCURO)
        for d in range(sim.dias + 1):
            c.create_text(px(d), aba + 12, text=str(d), font=("Segoe UI", 8), fill=MORADO_OSCURO)
        for frac in (0, 0.5, 1):
            c.create_text(izq - 8, py(total * frac), text=f"{total * frac:.0f}", anchor="e",
                          font=("Segoe UI", 8), fill=MORADO_OSCURO)
        c.create_line(px(0), py(total), px(sim.dias), py(0), dash=(4, 3), fill="#a78bfa")
        puntos = [(px(d), py(v)) for d, v in enumerate(sim.burndown)]
        if len(puntos) > 1:
            c.create_line(*[xy for p in puntos for xy in p], fill=MORADO, width=2)
        for x, y in puntos:
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=MORADO, outline="")
        c.create_text(der, arr, text="— real   - - ideal", anchor="ne", fill=MORADO, font=("Segoe UI", 8))


if __name__ == "__main__":
    App().mainloop()


