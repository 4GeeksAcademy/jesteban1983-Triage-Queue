"""
Triage Queue — Gestor de Cola de Prioridad
-------------------------------------------
Sistema de triaje hospitalario con cola de prioridad.
Usa tres colas deque separadas (una por nivel de triaje)
para garantizar O(1) en encolado/desencolado y FIFO estricto
dentro de cada nivel.

Uso: python3 triage_queue.py
"""

from dataclasses import dataclass
from collections import deque
from datetime import datetime
import sys


@dataclass
class Patient:
    """Representa un paciente en la cola de triaje."""
    name: str
    triage_level: int  # 1=crítico, 2=urgente, 3=estándar
    arrived_at: datetime

    def __str__(self) -> str:
        level_map = {1: "CRÍTICO", 2: "URGENTE", 3: "ESTÁNDAR"}
        return (f"{self.name} | Nivel {self.triage_level} "
                f"({level_map[self.triage_level]}) | "
                f"Llegó: {self.arrived_at.strftime('%H:%M:%S')}")


class TriageQueue:
    """
    Cola de prioridad para triaje hospitalario.

    Internamente usa tres deques independientes, una por cada
    nivel de triaje. Esto permite:
      - Encolar: O(1) — se añade al final del deque correspondiente.
      - Desencolar: O(1) — se extrae del frente del deque no vacío
        de mayor prioridad.
      - FIFO estricto dentro del mismo nivel.
    """

    def __init__(self):
        # Tres colas: index 1, 2, 3 (posición 0 no se usa)
        self._queues = {1: deque(), 2: deque(), 3: deque()}

    def enqueue(self, patient: Patient) -> None:
        """Añade un paciente a la cola según su nivel de triaje."""
        if patient.triage_level not in (1, 2, 3):
            raise ValueError(
                f"Nivel de triaje inválido: {patient.triage_level}. "
                "Debe ser 1 (crítico), 2 (urgente) o 3 (estándar)."
            )
        self._queues[patient.triage_level].append(patient)

    def dequeue(self) -> Patient:
        """
        Extrae y devuelve el siguiente paciente a ser atendido.

        Returns:
            Patient: el paciente de mayor prioridad que lleva más tiempo esperando.

        Raises:
            IndexError: si la cola está vacía.
        """
        for level in (1, 2, 3):
            if self._queues[level]:
                return self._queues[level].popleft()
        raise IndexError("No hay pacientes en espera. La cola está vacía.")

    def peek(self) -> Patient:
        """
        Devuelve el siguiente paciente sin extraerlo de la cola.

        Returns:
            Patient: el siguiente paciente a ser atendido.

        Raises:
            IndexError: si la cola está vacía.
        """
        for level in (1, 2, 3):
            if self._queues[level]:
                return self._queues[level][0]
        raise IndexError("No hay pacientes en espera. La cola está vacía.")

    def list_queue(self) -> list:
        """
        Devuelve todos los pacientes en espera en el orden en que
        serán atendidos (primero por nivel de triaje, luego FIFO).
        """
        result = []
        for level in (1, 2, 3):
            result.extend(self._queues[level])
        return result

    def stats(self) -> dict:
        """
        Devuelve un diccionario con el número de pacientes en espera
        por nivel de triaje.
        """
        return {
            1: len(self._queues[1]),
            2: len(self._queues[2]),
            3: len(self._queues[3]),
        }

    def is_empty(self) -> bool:
        """Verifica si la cola está vacía."""
        return all(len(q) == 0 for q in self._queues.values())

    def total_patients(self) -> int:
        """Devuelve el número total de pacientes en espera."""
        return sum(len(q) for q in self._queues.values())


def clear_screen() -> None:
    """Limpia la pantalla de la terminal."""
    print("\033c", end="")


def print_header() -> None:
    """Imprime el encabezado del programa."""
    print("=" * 60)
    print("            🏥 TRIAGE QUEUE — GESTOR DE COLA")
    print("=" * 60)


def print_menu() -> None:
    """Imprime el menú de opciones."""
    print("\n📋  MENÚ PRINCIPAL")
    print("-" * 40)
    print("  1. ➕  Añadir nuevo paciente")
    print("  2. 📞  Llamar al siguiente paciente")
    print("  3. 👀  Ver siguiente paciente (sin llamar)")
    print("  4. 📋  Ver cola completa")
    print("  5. 📊  Ver estadísticas")
    print("  6. 🚪  Salir")
    print("-" * 40)


def get_triage_level_name(level: int) -> str:
    """Devuelve el nombre descriptivo del nivel de triaje."""
    return {1: "CRÍTICO", 2: "URGENTE", 3: "ESTÁNDAR"}.get(level, "DESCONOCIDO")


def prompt_add_patient(queue: TriageQueue) -> None:
    """Solicita los datos de un nuevo paciente y lo añade a la cola."""
    print("\n--- AÑADIR NUEVO PACIENTE ---")

    # Solicitar nombre
    name = input("  Nombre del paciente: ").strip()
    if not name:
        print("  ⚠️  El nombre no puede estar vacío.")
        return

    # Solicitar nivel de triaje
    print("  Nivel de triaje:")
    print("    1 - CRÍTICO")
    print("    2 - URGENTE")
    print("    3 - ESTÁNDAR")

    try:
        level_input = input("  Selecciona nivel (1/2/3): ").strip()
        level = int(level_input)
        if level not in (1, 2, 3):
            print("  ⚠️  Nivel inválido. Debe ser 1, 2 o 3.")
            return
    except ValueError:
        print("  ⚠️  Entrada inválida. Debes introducir un número (1, 2 o 3).")
        return

    patient = Patient(
        name=name,
        triage_level=level,
        arrived_at=datetime.now()
    )
    queue.enqueue(patient)
    print(f"\n  ✅ Paciente '{name}' añadido (Nivel {level} - "
          f"{get_triage_level_name(level)}).")


def prompt_dequeue(queue: TriageQueue) -> None:
    """Llama al siguiente paciente (lo extrae de la cola)."""
    print("\n--- LLAMAR AL SIGUIENTE PACIENTE ---")
    try:
        patient = queue.dequeue()
        print(f"  📞  Llamando a: {patient}")
        print(f"  ✅  Paciente atendido y retirado de la cola.")
    except IndexError:
        print("  ℹ️  No hay pacientes en espera. La cola está vacía.")


def prompt_peek(queue: TriageQueue) -> None:
    """Muestra el siguiente paciente sin extraerlo."""
    print("\n--- SIGUIENTE PACIENTE ---")
    try:
        patient = queue.peek()
        print(f"  👀  Siguiente paciente: {patient}")
        print(f"  ℹ️  Paciente sigue en la cola.")
    except IndexError:
        print("  ℹ️  No hay pacientes en espera. La cola está vacía.")


def prompt_list_queue(queue: TriageQueue) -> None:
    """Muestra todos los pacientes en la cola."""
    print("\n--- COLA DE ESPERA COMPLETA ---")
    patients = queue.list_queue()
    if not patients:
        print("  ℹ️  No hay pacientes en espera.")
        return

    print(f"\n  Total pacientes: {queue.total_patients()}")
    level_map = {1: "🟠 CRÍTICO", 2: "🔴 URGENTE", 3: "🟢 ESTÁNDAR"}
    current_level = 0
    for i, patient in enumerate(patients, 1):
        if patient.triage_level != current_level:
            current_level = patient.triage_level
            print(f"\n  ── {level_map[current_level]} ──")
        print(f"  {i}. {patient.name:20s} | "
              f"Llegó: {patient.arrived_at.strftime('%H:%M:%S')}")


def prompt_stats(queue: TriageQueue) -> None:
    """Muestra las estadísticas de la cola."""
    print("\n--- ESTADÍSTICAS DE LA COLA ---")
    stats = queue.stats()
    total = queue.total_patients()

    level_names = {1: "CRÍTICO", 2: "URGENTE", 3: "ESTÁNDAR"}
    print(f"\n  Total pacientes en espera: {total}")
    print()
    for level in (1, 2, 3):
        count = stats[level]
        bar = "█" * count if count > 0 else "─"
        print(f"  Nivel {level} ({level_names[level]:8s}): "
              f"{count:3d} {bar}")
    print(f"\n  {'─' * 35}")
    if total > 0:
        # Mostrar el siguiente paciente
        try:
            next_patient = queue.peek()
            print(f"  Siguiente: {next_patient}")
        except IndexError:
            pass


def run_cli() -> None:
    """Bucle principal del menú interactivo CLI."""
    queue = TriageQueue()

    while True:
        clear_screen()
        print_header()
        print_menu()

        option = input("\n  Opción: ").strip()

        if option == "1":
            prompt_add_patient(queue)
        elif option == "2":
            prompt_dequeue(queue)
        elif option == "3":
            prompt_peek(queue)
        elif option == "4":
            prompt_list_queue(queue)
        elif option == "5":
            prompt_stats(queue)
        elif option == "6":
            print("\n  👋  Saliendo del gestor de triaje. ¡Hasta luego!")
            print("=" * 60)
            sys.exit(0)
        else:
            print(f"\n  ⚠️  Opción '{option}' no válida. "
                  f"Selecciona 1-6.")

        input("\n\n  Presiona Enter para continuar...")


if __name__ == "__main__":
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n\n  👋  Interrupción recibida. ¡Hasta luego!")
        sys.exit(0)