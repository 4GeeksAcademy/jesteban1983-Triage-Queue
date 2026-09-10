# Notas de Diseño — Triage Queue

## Estructura de datos elegida: Tres `deque` separadas

Para modelar la cola de prioridad del triaje hospitalario, opté por **tres colas `collections.deque` independientes**, una por cada nivel de triaje (1, 2 y 3).

### Alternativas consideradas

| Alternativa                                 | Problemas                                                                                                                                                                                |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Una sola `deque` + ordenar**              | Insertar un paciente crítico requeriría recolocar elementos, O(n) por inserción. No escala.                                                                                              |
| **Una `list` ordenada con `bisect.insort`** | Las inserciones son O(n) y el orden FIFO dentro del mismo nivel es difícil de garantizar si hay que intercalar.                                                                          |
| **`heapq` (heap)**                          | Un heap ordena por prioridad pero no preserva FIFO dentro del mismo nivel a menos que añadas un contador de orden de llegada. Además, `heapq` no ofrece `popleft()` eficiente por nivel. |
| **Tres `deque` separadas**                  | ✅ **Solución elegida.**                                                                                                                                                                 |

### Por qué tres `deque` separadas es la mejor opción

1. **Encolar (`enqueue`) es O(1)** — se añade al final del deque del nivel correspondiente mediante `append()`.
2. **Desencolar (`dequeue`) es O(1)** — se consulta el primer deque no vacío empezando por el nivel 1 y se extrae con `popleft()`.
3. **FIFO estricto dentro del mismo nivel** — cada deque es una cola FIFO por sí misma, garantizando orden de llegada sin necesidad de contadores ni timestamps adicionales.
4. **`list_queue()` es O(n)** — se concatenan los tres deques, pero es una operación de lectura poco frecuente.
5. **`stats()` es O(1)** — solo consultamos las longitudes de los tres deques.

### Coste asintótico de cada operación

| Operación          | Complejidad |
| ------------------ | ----------- |
| `enqueue(patient)` | O(1)        |
| `dequeue()`        | O(1)        |
| `peek()`           | O(1)        |
| `list_queue()`     | O(n)        |
| `stats()`          | O(1)        |
| `is_empty()`       | O(1)        |

## Manejo de concurrencia (worker encolando + desencolando)

El enunciado plantea el escenario en que un worker extrae un paciente de la cola mientras otro worker encola un nuevo paciente crítico. Aunque este programa es monohilo y no requiere bloqueos, es importante describir cómo se abordaría en un entorno concurrente real.

### Estrategia: Bloqueo por niveles (fine-grained locking)

En lugar de un candado global que proteja toda la estructura, usaríamos **tres candados independientes**, uno por deque. La razón es que las operaciones sobre distintos niveles no compiten por el mismo recurso.

```
# Pseudocódigo del esquema de bloqueo

dequeue():
    for level in (1, 2, 3):
        lock[level].acquire()
        if queue[level] non-empty:
            patient = queue[level].popleft()
            lock[level].release()
            return patient
        lock[level].release()
    raise Empty

enqueue(patient):
    lock[level].acquire()
    queue[level].append(patient)
    lock[level].release()
```

#### ¿Por qué este orden de mutación evita el doble procesamiento?

1. **El desencolado comprueba primero nivel 1, luego 2, luego 3.**  
   Mientras mantiene el candado del nivel actual, ningún otro worker puede modificar ese deque.
2. **El encolado solo adquiere el candado del nivel del paciente.**  
   Si un worker está desencolando del nivel 2, otro worker puede encolar un paciente crítico en nivel 1 sin interferencia.
3. **No hay condición de carrera (race condition) crítica** porque el desencolado comprueba existencia del elemento _dentro_ de la sección crítica. No hay ventana entre "comprobar si hay elementos" y "extraer".

#### Doble procesamiento

El "doble procesamiento" ocurriría si dos workers pudieran extraer al mismo paciente. Con bloqueo por niveles:

- Worker A adquiere `lock[1]`, encuentra un paciente, lo extrae y libera `lock[1]`.
- Worker B intenta adquirir `lock[1]` pero está tomado por A. Worker B espera.
- Cuando A libera `lock[1]`, B lo adquiere, pero el deque ya está vacío (el paciente se fue con A).
- B continúa al nivel 2.

Ningún paciente puede ser extraído dos veces porque la extracción (`popleft()`) ocurre dentro de la sección crítica y es atómica desde la perspectiva de otros workers.

### Nota sobre este proyecto

Dado que el programa actual es monohilo (CLI interactiva), no se implementan bloqueos. Esta sección describe únicamente cómo se extendería el diseño para un entorno concurrente real, como un sistema de producción con múltiples workers atendiendo pacientes simultáneamente.

---

_Documento de diseño para el proyecto Triage Queue — 4Geeks Academy_
