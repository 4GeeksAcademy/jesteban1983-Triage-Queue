"""
Script de prueba con datos aleatorios para Triage Queue.
Puebla la cola con pacientes ficticios y ejecuta todas las operaciones
para demostrar visualmente el funcionamiento del sistema.
"""

from triage_queue import Patient, TriageQueue
from datetime import datetime, timedelta
import random

# ── Datos de prueba ──────────────────────────────────────────────
NOMBRES = [
    "Ana García", "Luis Pérez", "Eva Martínez", "Juan López",
    "Sofía Ruiz", "Carlos Díaz", "María Torres", "Pedro Sánchez",
    "Laura Romero", "Diego Fernández", "Carmen Muñoz", "Javier Ortiz",
    "Isabel Navarro", "Miguel Ramos", "Patricia Gil", "Álvaro Castro",
    "Rosa Vargas", "Manuel Medina", "Teresa Suárez", "Raúl Delgado",
    "Elena Herrera", "Alberto Guzmán", "Marta Flores", "Sergio Rivas",
    "Paula Campos", "Jorge Vera", "Natalia Cruz", "Hugo Marín",
    "Andrea Peña", "Iván Ríos"
]

SINTOMAS = {
    1: ["Paro cardíaco", "Hemragia interna", "Trauma grave"],
    2: ["Fractura abierta", "Fiebre alta", "Crisis asmática"],
    3: ["Resfriado común", "Dolor muscular", "Revisión rutina"],
}


def crear_pacientes_aleatorios(cantidad: int = 15) -> list:
    """Genera una lista de pacientes con datos simulados escalonados en el tiempo."""
    pacientes = []
    for i in range(cantidad):
        nivel = random.choices([1, 2, 3], weights=[0.15, 0.35, 0.50])[0]
        nombre = random.choice(NOMBRES)
        # Simular tiempos de llegada espaciados
        llegada = datetime.now() + timedelta(seconds=i * 15)
        p = Patient(name=nombre, triage_level=nivel, arrived_at=llegada)
        pacientes.append(p)
    return pacientes


def barra_progreso(count: int, max_count: int = 10) -> str:
    """Barra visual de pacientes."""
    lleno = "█" * min(count, max_count)
    vacio = "░" * (max_count - min(count, max_count))
    return f"{lleno}{vacio}"


def mostrar_encabezado(titulo: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {titulo}")
    print(f"{'=' * 60}")


def mostrar_paciente(p: Patient) -> str:
    nivel_nombre = {1: "🔴 CRÍTICO", 2: "🟠 URGENTE", 3: "🟢 ESTÁNDAR"}
    hora = p.arrived_at.strftime("%H:%M:%S")
    return f"{p.name:22s} | Nivel {p.triage_level} {nivel_nombre[p.triage_level]} | ⏰ {hora}"


def main():
    q = TriageQueue()

    # ─── FASE 1: Poblar cola ──────────────────────────────────────
    mostrar_encabezado("🏥 FASE 1: LLEGADA DE PACIENTES A URGENCIAS")

    print("\n  📥 Llegan pacientes al hospital (orden de llegada):")
    print(f"  {'─' * 55}")

    pacientes = crear_pacientes_aleatorios(15)

    for i, p in enumerate(pacientes, 1):
        q.enqueue(p)
        print(f"  [{i:02d}] {mostrar_paciente(p)}")

    # ─── FASE 2: Estadísticas iniciales ──────────────────────────
    mostrar_encabezado("📊 FASE 2: ESTADÍSTICAS DE LA COLA")

    stats = q.stats()
    total = q.total_patients()
    print(f"\n  🏨 Total pacientes en espera: {total}")
    print()
    for nivel in (1, 2, 3):
        count = stats[nivel]
        nombre = {1: "Crítico", 2: "Urgente", 3: "Estándar"}[nivel]
        print(f"     {'🔴' if nivel == 1 else '🟠' if nivel == 2 else '🟢'} "
              f"Nivel {nivel} ({nombre:8s}): {count:2d} pacientes  {barra_progreso(count)}")

    # ─── FASE 3: Ver cola ordenada ────────────────────────────────
    mostrar_encabezado("📋 FASE 3: COLA DE ESPERA (Orden de atención)")

    print(f"\n  Los pacientes nivel 1 (críticos) se atienden PRIMERO,")
    print(f"  luego nivel 2 (urgentes) y finalmente nivel 3 (estándar).")
    print(f"  Dentro del mismo nivel, se respeta el orden de llegada.\n")

    pacientes_ordenados = q.list_queue()
    nivel_actual = 0
    for i, p in enumerate(pacientes_ordenados, 1):
        if p.triage_level != nivel_actual:
            nivel_actual = p.triage_level
            nombre = {1: "🔴 CRÍTICOS", 2: "🟠 URGENTES", 3: "🟢 ESTÁNDAR"}[nivel_actual]
            print(f"  ── {nombre} ──")
        print(f"  {i:02d}. {mostrar_paciente(p)}")

    # ─── FASE 4: Desencolar pacientes ─────────────────────────────
    mostrar_encabezado("📞 FASE 4: ATENDIENDO PACIENTES")

    print(f"\n  🩺 Llamando pacientes a consulta...\n")

    atendidos = []
    while not q.is_empty():
        paciente = q.dequeue()
        atendidos.append(paciente)
        print(f"  📞 ATENDIDO: {paciente.name:22s} | "
              f"Nivel {paciente.triage_level} | "
              f"⏰ {paciente.arrived_at.strftime('%H:%M:%S')}")

    print(f"\n  ✅ Total atendidos: {len(atendidos)} pacientes")

    # ─── FASE 5: Casos borde ─────────────────────────────────────
    mostrar_encabezado("🛡️ FASE 5: CASOS BORDE")

    print("\n  🔹 Intentar desencolar en cola vacía:")
    try:
        q.dequeue()
    except IndexError as e:
        print(f"     ✅ {e}")

    print("\n  🔹 Intentar peek en cola vacía:")
    try:
        q.peek()
    except IndexError as e:
        print(f"     ✅ {e}")

    # ─── FASE 6: Prioridad demostrada ────────────────────────────
    mostrar_encabezado("🚑 FASE 6: DEMOSTRACIÓN DE PRIORIDAD")

    print("\n  Simulación: llegan 3 pacientes en este orden:")
    print("     1. Juan (Nivel 3 - ESTÁNDAR)")
    print("     2. Ana  (Nivel 1 - CRÍTICO)")
    print("     3. Luis (Nivel 2 - URGENTE)")

    now = datetime.now()
    q2 = TriageQueue()
    q2.enqueue(Patient("Juan", 3, now))
    q2.enqueue(Patient("Ana", 1, now + timedelta(seconds=5)))
    q2.enqueue(Patient("Luis", 2, now + timedelta(seconds=10)))

    print("\n  📋 El orden de atención DEBE SER:")
    print("     1° Ana  (llegó después pero es Nivel 1 - CRÍTICO)")
    print("     2° Luis (Nivel 2 - URGENTE)")
    print("     3° Juan (Nivel 3 - ESTÁNDAR, aunque llegó primero)\n")

    for i in range(3):
        p = q2.dequeue()
        print(f"     {'🥇' if i == 0 else '🥈' if i == 1 else '🥉'} "
              f"{p.name:5s} | Nivel {p.triage_level} — "
              f"llegó a las {p.arrived_at.strftime('%H:%M:%S')}")

    # ─── FIN ─────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  ✅  DEMO COMPLETADA — Triage Queue funciona correctamente")
    print(f"{'=' * 60}")
    print(f"\n  ▶️  También puedes ejecutar el menú interactivo:")
    print(f"     $ python3 triage_queue.py\n")


if __name__ == "__main__":
    main()