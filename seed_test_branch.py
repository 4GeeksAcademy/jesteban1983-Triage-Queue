"""
Script de prueba con datos aleatorios para Branch Queue.
Puebla la cola con tickets ficticios y ejecuta todas las operaciones
para demostrar visualmente el funcionamiento del sistema bancario.
"""

from branch_queue import Ticket, BranchQueue, SERVICE_NAMES
from datetime import datetime, timedelta
import random

# ── Datos de prueba ──────────────────────────────────────────────
CLIENTES = [
    "Ana García", "Luis Pérez", "Eva Martínez", "Juan López",
    "Sofía Ruiz", "Carlos Díaz", "María Torres", "Pedro Sánchez",
    "Laura Romero", "Diego Fernández", "Carmen Muñoz", "Javier Ortiz",
    "Isabel Navarro", "Miguel Ramos", "Patricia Gil", "Álvaro Castro",
    "Rosa Vargas", "Manuel Medina", "Teresa Suárez", "Raúl Delgado",
    "Elena Herrera", "Alberto Guzmán", "Marta Flores", "Sergio Rivas",
    "Paula Campos", "Jorge Vera", "Natalia Cruz", "Hugo Marín",
    "Andrea Peña", "Iván Ríos", "Silvia Vega", "Óscar Molina",
    "Clara Pastor", "Daniel Gil", "Lucía Ferrer", "Adrián Domínguez",
    "Lara Márquez", "Pablo Cortés", "Nuria Ibáñez", "Héctor Soto"
]

SERVICIOS = ["deposito", "retiro", "gestion_cuenta"]
SERVICIOS_WEIGHTS = [0.35, 0.40, 0.25]  # Más retiros, menos gestión


def barra(cantidad: int, maximo: int = 10) -> str:
    """Barra visual de clientes."""
    lleno = "█" * min(cantidad, maximo)
    vacio = "░" * (maximo - min(cantidad, maximo))
    return f"{lleno}{vacio}"


def mostrar_separador(titulo: str) -> None:
    print(f"\n{'=' * 62}")
    print(f"  {titulo}")
    print(f"{'=' * 62}")


def main():
    q = BranchQueue()

    # ─── FASE 1: Emitir tickets ─────────────────────────────────
    mostrar_separador("🏦 FASE 1: EMISIÓN DE TICKETS")

    print("\n  🎫 Los clientes toman ticket en la entrada:\n")

    tickets_emitidos = []
    # Simular 20 clientes llegando en orden aleatorio
    for i in range(20):
        nombre = random.choice(CLIENTES)
        servicio = random.choices(SERVICIOS, weights=SERVICIOS_WEIGHTS)[0]
        ticket = q.issue_ticket(nombre, servicio)
        tickets_emitidos.append(ticket)
        hora = ticket.issued_at.strftime("%H:%M:%S")
        print(f"  [{i+1:02d}] #{ticket.number:03d} | {nombre:22s} → "
              f"{SERVICE_NAMES[servicio]:24s} | {hora}")

    # ─── FASE 2: Verificar numeración secuencial ────────────────
    mostrar_separador("🔢 FASE 2: VERIFICACIÓN DE NUMERACIÓN GLOBAL")

    print("\n  Los números de ticket deben ser SECUENCIALES (1 al 20):")
    numeros = [t.number for t in tickets_emitidos]
    print(f"  Números emitidos: {numeros}")
    assert numeros == list(range(1, 21)), "Error: números no secuenciales"
    print(f"  ✅ Correcto: {len(numeros)} tickets, del #1 al #20")
    print(f"  ✅ Último ticket emitido: #{q.last_ticket_number}")

    # ─── FASE 3: Stats iniciales ────────────────────────────────
    mostrar_separador("📊 FASE 3: ESTADÍSTICAS INICIALES")

    stats = q.stats()
    print(f"\n  🏦 Clientes en espera por servicio:")
    print()
    for servicio in SERVICIOS:
        cantidad = stats[servicio]
        nombre_serv = SERVICE_NAMES[servicio]
        print(f"     {nombre_serv:24s}: {cantidad:3d}  {barra(cantidad)}")
    print(f"\n     {'─' * 40}")
    print(f"     {'TOTAL':24s}: {stats['total']:3d}")

    # ─── FASE 4: Lista de espera agrupada ──────────────────────
    mostrar_separador("📋 FASE 4: LISTA DE ESPERA AGRUPADA POR SERVICIO")

    print("""
  Cada agente solo ve los clientes de su propio servicio.
  No tiene que recorrer clientes de otros servicios.""")
    print()

    espera = q.list_waiting()
    for servicio in SERVICIOS:
        tickets = espera[servicio]
        nombre_serv = SERVICE_NAMES[servicio]
        if tickets:
            print(f"  ── {nombre_serv} ({len(tickets)} esperando) ──")
            for i, t in enumerate(tickets, 1):
                print(f"     {i:02d}. #{t.number:03d} | {t.client_name:22s} | "
                      f"{t.issued_at.strftime('%H:%M:%S')}")
        else:
            print(f"  ── {nombre_serv} (0 esperando) ──")
        print()

    # ─── FASE 5: Atender clientes por servicio ─────────────────
    mostrar_separador("📞 FASE 5: AGENTES ATENDIENDO CLIENTES")

    print("""
  Cada agente llama al siguiente cliente de SU cola de servicio,
  sin interferir con los otros agentes.
  """)

    for servicio in SERVICIOS:
        nombre_serv = SERVICE_NAMES[servicio]
        cant = len(espera[servicio])
        print(f"  🧑‍💼 Agente de {nombre_serv} ({cant} clientes esperando):")
        for j in range(cant):
            ticket = q.call_next(servicio)
            print(f"     📞 Llamando → #{ticket.number:03d} {ticket.client_name}")
        # Intentar llamar a uno más (debe fallar)
        try:
            q.call_next(servicio)
        except IndexError as e:
            print(f"     ℹ️  {e}")
        print()

    # ─── FASE 6: Stats finales ─────────────────────────────────
    mostrar_separador("📊 FASE 6: ESTADÍSTICAS FINALES (Sucursal vacía)")

    stats_final = q.stats()
    print(f"\n  Clientes en espera: {stats_final['total']}")
    assert stats_final['total'] == 0, "Error: debería estar vacío"
    print(f"  ✅ Todos los clientes fueron atendidos.")
    print(f"  ✅ La sucursal está vacía.")

    # ─── FASE 7: Casos borde ───────────────────────────────────
    mostrar_separador("🛡️ FASE 7: CASOS BORDE")

    print("\n  🔹 call_next() en cola vacía:")
    try:
        q.call_next("deposito")
    except IndexError as e:
        print(f"     ✅ {e}")

    print("\n  🔹 peek_next() en cola vacía:")
    try:
        q.peek_next("retiro")
    except IndexError as e:
        print(f"     ✅ {e}")

    print("\n  🔹 Tipo de servicio inválido:")
    try:
        q.issue_ticket("Cliente", "hipotecas")
    except ValueError as e:
        print(f"     ✅ {e}")

    print("\n  🔹 Peek y list_waiting no mutan estado:")
    q2 = BranchQueue()
    q2.issue_ticket("Test", "deposito")
    q2.peek_next("deposito")
    assert len(q2.list_waiting()["deposito"]) == 1, "peek no debe extraer"
    print(f"     ✅ peek_next no extrae. Cola aún tiene 1 cliente.")
    print(f"     ✅ list_waiting muestra datos sin mutar.")

    # ─── FIN ───────────────────────────────────────────────────
    print(f"\n{'=' * 62}")
    print(f"  ✅  DEMO COMPLETADA — Branch Queue funciona correctamente")
    print(f"{'=' * 62}")
    print(f"\n  ▶️  También puedes ejecutar el menú interactivo:")
    print(f"     $ python3 branch_queue.py\n")


if __name__ == "__main__":
    main()