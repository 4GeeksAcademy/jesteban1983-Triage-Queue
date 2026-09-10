# Notas de Diseño — Branch Queue

## Estructura de datos elegida: Un deque por tipo de servicio

Para gestionar las colas de la sucursal bancaria, opté por **un diccionario con tres `collections.deque` independientes**, una por cada tipo de servicio (`deposito`, `retiro`, `gestion_cuenta`), más un **contador global** para los números de ticket secuenciales.

### ¿Por qué una cola separada por servicio es mejor que una única cola compartida?

| Enfoque                                      | Problema                                                                                                                                                                                                                                                     |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Una única lista/deque compartida**         | Cuando un agente de, p. ej., depósitos queda libre, necesita encontrar al _próximo cliente de depósitos_. Con una sola cola mezclada, debe recorrerla entera (O(n)) hasta encontrar un cliente de depósitos. En una sucursal llena, esto es muy ineficiente. |
| **Una cola por servicio (solución elegida)** | ✅ Cada agente tiene acceso directo a la cola de su servicio. `call_next("deposito")` es **O(1)**: solo hace `popleft()` sobre el deque de depósitos. Nunca ve clientes de otros servicios.                                                                  |

### Coste asintótico de cada operación

| Operación                        | Complejidad | Explicación                                                  |
| -------------------------------- | ----------- | ------------------------------------------------------------ |
| `issue_ticket(nombre, servicio)` | O(1)        | Incrementa contador global, `append()` al deque del servicio |
| `call_next(servicio)`            | O(1)        | `popleft()` del deque del servicio indicado                  |
| `peek_next(servicio)`            | O(1)        | Acceso a `deque[0]` del servicio indicado                    |
| `list_waiting()`                 | O(n)        | Concatena los 3 deques en un diccionario                     |
| `stats()`                        | O(1)        | Consulta `len()` de cada deque                               |

### Numeración global secuencial

El contador `self._counter` se incrementa en cada `issue_ticket()` **antes** de encolar el ticket. Así:

- El ticket #5 de depósitos y el ticket #5 de retiros **no pueden coexistir**: cada número es único globalmente.
- El orden de emisión entre servicios distintos se preserva en el número de ticket (si el ticket #10 es de retiros y el #11 de depósitos, sabemos que el #10 se emitió antes).

## Concurrencia: dos agentes del mismo servicio llaman a `call_next` simultáneamente

El enunciado plantea: ¿qué ocurre si dos agentes del mismo tipo de servicio llaman a `call_next` al mismo tiempo? ¿Cómo evitamos que el mismo cliente sea llamado dos veces?

### Estrategia: Bloqueo por cola de servicio (fine-grained locking)

En un entorno concurrente real, asignaríamos **un candado por deque** (uno por tipo de servicio):

```python
# Pseudocódigo del esquema de bloqueo

call_next(service_type):
    lock[service_type].acquire()          # 1. Adquirir candado PRIMERO
    if queue[service_type] non-empty:
        ticket = queue[service_type].popleft()  # 2. Mutar DENTRO del candado
        lock[service_type].release()
        return ticket
    else:
        lock[service_type].release()
        raise Empty
```

#### ¿Por qué este orden evita el doble procesamiento?

1. **La adquisición del candado ocurre antes de cualquier comprobación.**  
   Dos agentes nunca pueden estar dentro de la misma sección crítica al mismo tiempo.

2. **La comprobación de existencia y la extracción son atómicas.**  
   No hay ventana entre "comprobar si hay elementos" y "extraer". Si el deque tiene un elemento, el agente que adquirió el candado primero lo extrae; el otro agente espera y, cuando adquiere el candado, encuentra el deque vacío.

3. **El candado por servicio permite concurrencia real entre servicios diferentes.**  
   Un agente de depósitos y uno de retiros pueden operar en paralelo sin bloquearse mutuamente, porque adquieren candados distintos.

### Orden de mutación crítico

```
ADQUIRIR candado → COMPROBAR si hay elementos → EXTRAER y DEVOLVER → LIBERAR candado
```

Si invirtiéramos el orden —comprobar primero, luego adquirir—, dos agentes podrían ver `len(queue) > 0` simultáneamente antes de que ninguno adquiera el candado, y ambos intentarían extraer al mismo cliente.

### Nota sobre este proyecto

Dado que el programa actual es monohilo (CLI interactiva), no se implementan bloqueos. Esta sección describe cómo se extendería el diseño para un entorno concurrente real con múltiples agentes (hilos) atendiendo clientes simultáneamente en la misma sucursal.

---

_Documento de diseño para el proyecto Branch Queue — 4Geeks Academy_
