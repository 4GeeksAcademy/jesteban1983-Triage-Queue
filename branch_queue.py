"""
Branch Queue — Gestor de Cola por Servicio
-------------------------------------------
Sistema de gestión de colas para una sucursal bancaria.
Cada tipo de servicio (deposito, retiro, gestion_cuenta) tiene su
propia cola independiente, con un contador global de tickets secuenciales.

Los agentes están dedicados a un solo tipo de servicio y llaman al
siguiente cliente de su cola sin interferir con otros agentes.

Uso: python3 branch_queue.py
"""

from dataclasses import dataclass
from collections import deque
from datetime import datetime
import sys


# ─── Constantes ─────────────────────────────────────────────────
SERVICE_TYPES = ("deposito", "retiro", "gestion_cuenta")
# Traducción a nombres legibles para el menú
SERVICE_NAMES = {
    "deposito":       "💰 Depósito",
    "retiro":         "🏧 Retiro",
    "gestion_cuenta": "📋 Gestión de Cuenta",
}


@dataclass
class Ticket:
    """
    Representa un ticket emitido a un cliente en la sucursal.

    Attributes:
        number (int): Número de ticket (global secuencial, empieza en 1).
        client_name (str): Nombre del cliente.
        service_type (str): Tipo de servicio solicitado.
                           Uno de: "deposito", "retiro", "gestion_cuenta".
        issued_at (datetime): Momento en que se emitió el ticket.
    """
    number: int
    client_name: str
    service_type: str
    issued_at: datetime

    def __str__(self) -> str:
        """Representación legible del ticket."""
        servicio = SERVICE_NAMES.get(self.service_type, self.service_type)
        hora = self.issued_at.strftime("%H:%M:%S")
        return (f"#{self.number:03d} | {self.client_name:20s} | "
                f"{servicio:22s} | {hora}")


class BranchQueue:
    """
    Gestor de colas por servicio para una sucursal bancaria.

    Internamente mantiene un diccionario con un deque por cada tipo
    de servicio, más un contador global que asigna números de ticket
    secuenciales entre todos los servicios.

    Beneficio frente a una única cola compartida:
        - call_next() es O(1): cada agente accede directamente a la
          cola de su servicio sin recorrer ni filtrar clientes de
          otros servicios.
        - list_waiting() agrupa por servicio de forma natural.
    """

    def __init__(self):
        """Inicializa el gestor con colas vacías y contador en 0."""
        # Diccionario: cada tipo de servicio tiene su propio deque
        self._queues = {
            "deposito":       deque(),
            "retiro":         deque(),
            "gestion_cuenta": deque(),
        }
        # Contador global para asignar números de ticket secuenciales
        self._counter = 0

    # ── Operaciones públicas ───────────────────────────────────

    def issue_ticket(self, client_name: str, service_type: str) -> Ticket:
        """
        Emite un nuevo ticket para un cliente.

        1. Valida que el tipo de servicio exista.
        2. Incrementa el contador global.
        3. Crea el Ticket con el número asignado.
        4. Encola el ticket en la cola del servicio correspondiente.

        Args:
            client_name: Nombre del cliente.
            service_type: Tipo de servicio ("deposito", "retiro", "gestion_cuenta").

        Returns:
            Ticket: El ticket emitido.

        Raises:
            ValueError: Si service_type no es válido.
        """
        self._validar_servicio(service_type)

        # Incremento global: cada ticket recibe el siguiente número,
        # independientemente del servicio al que vaya.
        self._counter += 1

        ticket = Ticket(
            number=self._counter,
            client_name=client_name.strip(),
            service_type=service_type,
            issued_at=datetime.now()
        )
        self._queues[service_type].append(ticket)
        return ticket

    def call_next(self, service_type: str) -> Ticket:
        """
        Llama al siguiente cliente de un tipo de servicio específico.

        El agente asignado a ese servicio extrae al cliente que lleva
        más tiempo esperando (FIFO) en su cola.

        Args:
            service_type: Tipo de servicio.

        Returns:
            Ticket: El ticket del cliente llamado.

        Raises:
            IndexError: Si no hay clientes esperando para ese servicio.
            ValueError: Si service_type no es válido.
        """
        self._validar_servicio(service_type)

        if not self._queues[service_type]:
            raise IndexError(
                f"No hay clientes esperando para '{service_type}'. "
                "La cola está vacía."
            )

        return self._queues[service_type].popleft()

    def peek_next(self, service_type: str) -> Ticket:
        """
        Muestra el siguiente cliente para un servicio sin retirarlo.

        Args:
            service_type: Tipo de servicio.

        Returns:
            Ticket: El siguiente ticket (sin extraerlo).

        Raises:
            IndexError: Si no hay clientes esperando para ese servicio.
            ValueError: Si service_type no es válido.
        """
        self._validar_servicio(service_type)

        if not self._queues[service_type]:
            raise IndexError(
                f"No hay clientes esperando para '{service_type}'. "
                "La cola está vacía."
            )

        return self._queues[service_type][0]

    def list_waiting(self) -> dict:
        """
        Devuelve todos los tickets en espera agrupados por servicio.

        Returns:
            dict: {service_type: [Ticket, ...]} con cada cola ordenada
                  FIFO dentro de su servicio.
        """
        resultado = {}
        for servicio in SERVICE_TYPES:
            resultado[servicio] = list(self._queues[servicio])
        return resultado

    def stats(self) -> dict:
        """
        Reporta estadísticas de clientes en espera.

        Returns:
            dict: {service_type: int, "total": int} con el número de
                  clientes por servicio y el total global.
        """
        conteo = {}
        total = 0
        for servicio in SERVICE_TYPES:
            cantidad = len(self._queues[servicio])
            conteo[servicio] = cantidad
            total += cantidad
        conteo["total"] = total
        return conteo

    def is_empty(self) -> bool:
        """Verifica si todas las colas de servicio están vacías."""
        return all(len(q) == 0 for q in self._queues.values())

    # ── Métodos auxiliares ──────────────────────────────────────

    def _validar_servicio(self, service_type: str) -> None:
        """
        Valida que el tipo de servicio sea uno de los permitidos.

        Args:
            service_type: Tipo de servicio a validar.

        Raises:
            ValueError: Si el servicio no es válido.
        """
        if service_type not in SERVICE_TYPES:
            servicios = ", ".join(f"'{s}'" for s in SERVICE_TYPES)
            raise ValueError(
                f"Tipo de servicio inválido: '{service_type}'. "
                f"Los válidos son: {servicios}."
            )

    @property
    def last_ticket_number(self) -> int:
        """Número del último ticket emitido (0 si no hay tickets)."""
        return self._counter


# ═══════════════════════════════════════════════════════════════════
# INTERFAZ CLI — Menú interactivo para el operador de la sucursal
# ═══════════════════════════════════════════════════════════════════

def limpiar_pantalla() -> None:
    """Limpia la pantalla de la terminal."""
    print("\033c", end="")


def mostrar_encabezado() -> None:
    """Imprime el encabezado del programa."""
    print("=" * 62)
    print("       🏦 BRANCH QUEUE — GESTOR DE COLAS BANCARIAS")
    print("=" * 62)


def mostrar_menu() -> None:
    """Imprime el menú de opciones principales."""
    print("\n📋  MENÚ PRINCIPAL")
    print("-" * 44)
    print("  1. 🎫  Emitir nuevo ticket")
    print("  2. 📞  Llamar al siguiente cliente (por servicio)")
    print("  3. 👀  Ver siguiente cliente (sin llamar)")
    print("  4. 📋  Ver lista de espera completa")
    print("  5. 📊  Ver estadísticas")
    print("  6. 🚪  Salir")
    print("-" * 44)


def mostrar_servicios() -> None:
    """Muestra los tipos de servicio disponibles."""
    print("\n  Tipos de servicio disponibles:")
    for key, name in SERVICE_NAMES.items():
        print(f"     {name}")


def solicitar_servicio(mensaje: str = "  Tipo de servicio") -> str:
    """
    Solicita al usuario que seleccione un tipo de servicio.

    Args:
        mensaje: Texto del prompt.

    Returns:
        str: Código de servicio válido, o None si cancela.
    """
    print()
    for num, (key, name) in enumerate(SERVICE_NAMES.items(), 1):
        print(f"    {num}. {name}")
    print("    (Deja vacío para cancelar)")

    entrada = input(f"  {mensaje} (1/2/3): ").strip()

    if entrada == "":
        return None

    try:
        idx = int(entrada)
        if 1 <= idx <= 3:
            return SERVICE_TYPES[idx - 1]
    except ValueError:
        pass

    print("  ⚠️  Opción inválida. Debe ser 1, 2 o 3.")
    return None


def prompt_issue_ticket(queue: BranchQueue) -> None:
    """
    Emite un nuevo ticket: solicita nombre y tipo de servicio.
    """
    print("\n--- 🎫 EMITIR NUEVO TICKET ---")

    # Solicitar nombre del cliente
    nombre = input("  Nombre del cliente: ").strip()
    if not nombre:
        print("  ⚠️  El nombre no puede estar vacío.")
        return

    # Seleccionar tipo de servicio
    servicio = solicitar_servicio("Selecciona servicio")
    if servicio is None:
        print("  ⚠️  Operación cancelada.")
        return

    # Emitir el ticket
    ticket = queue.issue_ticket(nombre, servicio)
    print(f"\n  ✅ Ticket emitido correctamente:")
    print(f"     {ticket}")
    print(f"     El cliente debe esperar en la fila de "
          f"'{SERVICE_NAMES[servicio]}'.")


def prompt_call_next(queue: BranchQueue) -> None:
    """
    Llama al siguiente cliente para un tipo de servicio.
    """
    print("\n--- 📞 LLAMAR AL SIGUIENTE CLIENTE ---")

    servicio = solicitar_servicio("¿Qué servicio?")
    if servicio is None:
        print("  ⚠️  Operación cancelada.")
        return

    try:
        ticket = queue.call_next(servicio)
        print(f"\n  📞  Llamando a cliente:")
        print(f"      {ticket}")
        print(f"  ✅  Cliente atendido. Retirado de la cola de "
              f"'{SERVICE_NAMES[servicio]}'.")
    except IndexError as e:
        print(f"  ℹ️  {e}")


def prompt_peek_next(queue: BranchQueue) -> None:
    """
    Muestra el siguiente cliente para un servicio sin extraerlo.
    """
    print("\n--- 👀 VER SIGUIENTE CLIENTE (SIN LLAMAR) ---")

    servicio = solicitar_servicio("¿Qué servicio?")
    if servicio is None:
        print("  ⚠️  Operación cancelada.")
        return

    try:
        ticket = queue.peek_next(servicio)
        print(f"\n  👀  Siguiente cliente en '{SERVICE_NAMES[servicio]}':")
        print(f"      {ticket}")
        print(f"  ℹ️  El cliente sigue en espera.")
    except IndexError as e:
        print(f"  ℹ️  {e}")


def prompt_list_waiting(queue: BranchQueue) -> None:
    """
    Muestra todos los tickets en espera agrupados por servicio.
    """
    print("\n--- 📋 LISTA DE ESPERA COMPLETA ---")

    espera = queue.list_waiting()
    stats = queue.stats()
    hay_clientes = any(len(tickets) > 0 for tickets in espera.values())

    if not hay_clientes:
        print("  ℹ️  No hay clientes en espera. La sucursal está vacía.")
        return

    print(f"\n  Total clientes en espera: {stats['total']}")
    print()

    for servicio in SERVICE_TYPES:
        tickets = espera[servicio]
        nombre_serv = SERVICE_NAMES[servicio]
        if tickets:
            print(f"  ── {nombre_serv} ({len(tickets)} esperando) ──")
            for i, ticket in enumerate(tickets, 1):
                print(f"     {i:02d}. #{ticket.number:03d} | "
                      f"{ticket.client_name:20s} | "
                      f"{ticket.issued_at.strftime('%H:%M:%S')}")
            print()
        else:
            print(f"  ── {nombre_serv} (0 esperando) ──")
            print(f"     (Sin clientes)\n")


def prompt_stats(queue: BranchQueue) -> None:
    """
    Muestra estadísticas de clientes en espera por servicio.
    """
    print("\n--- 📊 ESTADÍSTICAS DE LA SUCURSAL ---")

    stats = queue.stats()
    total = stats["total"]

    print(f"\n  🏦 Clientes en espera por servicio:")
    print()
    for servicio in SERVICE_TYPES:
        cantidad = stats[servicio]
        nombre = SERVICE_NAMES[servicio]
        # Barra visual: cada █ representa 1 cliente
        barra = "█" * cantidad if cantidad > 0 else "─"
        print(f"     {nombre:24s}: {cantidad:3d}  {barra}")

    print(f"\n     {'─' * 40}")
    print(f"     {'TOTAL':24s}: {total:3d}")

    if total > 0:
        # Mostrar el siguiente cliente de cada servicio
        print(f"\n  👀 Siguientes por servicio:")
        for servicio in SERVICE_TYPES:
            try:
                ticket = queue.peek_next(servicio)
                print(f"     {SERVICE_NAMES[servicio]:24s} → "
                      f"#{ticket.number:03d} {ticket.client_name}")
            except IndexError:
                print(f"     {SERVICE_NAMES[servicio]:24s} → (vacía)")


def ejecutar_cli() -> None:
    """Bucle principal del menú interactivo CLI."""
    queue = BranchQueue()

    while True:
        limpiar_pantalla()
        mostrar_encabezado()
        mostrar_menu()

        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            prompt_issue_ticket(queue)
        elif opcion == "2":
            prompt_call_next(queue)
        elif opcion == "3":
            prompt_peek_next(queue)
        elif opcion == "4":
            prompt_list_waiting(queue)
        elif opcion == "5":
            prompt_stats(queue)
        elif opcion == "6":
            print("\n  👋  Saliendo del gestor de colas. ¡Hasta luego!")
            print("=" * 62)
            sys.exit(0)
        else:
            print(f"\n  ⚠️  Opción '{opcion}' no válida. "
                  f"Selecciona 1-6.")

        input("\n\n  Presiona Enter para continuar...")


if __name__ == "__main__":
    try:
        ejecutar_cli()
    except KeyboardInterrupt:
        print("\n\n  👋  Interrupción recibida. ¡Hasta luego!")
        sys.exit(0)