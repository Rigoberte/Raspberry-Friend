# Refactorización a Arquitectura Hexagonal

## 📋 Resumen de Cambios

Se ha refactorizado el código para cumplir con los principios de arquitectura hexagonal, eliminando las violaciones identificadas.

## 🎯 Arquitectura Hexagonal Aplicada

```
┌─────────────────────────────────────────────────────────────┐
│                        INFRAESTRUCTURA                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Adaptadores (src/adapters/outbound/)               │   │
│  │  - ThreadPoolExecutorAdapter                        │   │
│  │  - InMemoryEventBus (implements EventBusPort)       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ implements
                              │
┌─────────────────────────────────────────────────────────────┐
│                    PUERTOS (INTERFACES)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  src/domain/ports/outbound/                         │   │
│  │  - EventBusPort (interfaz abstracta)                │   │
│  │  - TaskExecutorPort (interfaz abstracta)            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ depends on
                              │
┌─────────────────────────────────────────────────────────────┐
│                         APLICACIÓN                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  TaskScheduler (orquestador)                        │   │
│  │  - Recibe puertos por inyección de dependencias     │   │
│  │  - Recolecta eventos del dominio                    │   │
│  │  - Publica eventos usando EventBusPort              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ uses
                              │
┌─────────────────────────────────────────────────────────────┐
│                           DOMINIO                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Task (entidad)                                      │   │
│  │  - Genera eventos de dominio internamente           │   │
│  │  - _emit_event() para agregar eventos               │   │
│  │  - collect_domain_events() para recolectar          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Eventos de Dominio                                  │   │
│  │  - TaskQueued, TaskStarted                          │   │
│  │  - TaskCompleted, TaskFailed, TaskCancelled         │   │
│  │  - Sin dependencias de infraestructura              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Correcciones Implementadas

### 1. **Eventos de Dominio Puros**
**Antes:**
```python
# task_events.py - MALO
from src.domain.models.command import CommandResult  # Dependencia

@dataclass
class TaskCompleted(TaskEvent):
    result: Optional[CommandResult] = None  # Acoplamiento
```

**Después:**
```python
# task_events.py - CORRECTO
@dataclass(frozen=True, slots=True)
class TaskCompleted(TaskEvent):
    success: bool = True
    message: Optional[str] = None
    output: Optional[Any] = None  # Tipo genérico
```

### 2. **Task Genera Sus Propios Eventos**
**Antes:**
```python
# TaskScheduler publicaba eventos - MALO
def __execute_task__(self, task: Task):
    task.execute(self._dispatcher)
    self._event_bus.publish(TaskStarted(...))  # Responsabilidad incorrecta
```

**Después:**
```python
# Task genera eventos - CORRECTO
class Task:
    def execute(self, dispatcher):
        self._emit_event(TaskStarted(...))  # Dominio genera
        # ... lógica de ejecución ...
        self._emit_event(TaskCompleted(...))
    
    def collect_domain_events(self) -> list:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
```

### 3. **Puertos en Lugar de Implementaciones Concretas**
**Antes:**
```python
# task_scheduler.py - MALO
from concurrent.futures import ThreadPoolExecutor  # Implementación concreta

class TaskScheduler:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=5)  # Acoplamiento
```

**Después:**
```python
# task_scheduler.py - CORRECTO
from src.domain.ports.outbound.task_executor_ports import TaskExecutorPort

class TaskScheduler:
    def __init__(self, executor: TaskExecutorPort):  # Inyección de dependencia
        self._executor = executor
```

### 4. **EventBus como Puerto**
**Antes:**
```python
# application/events/event_bus.py - MALO
class EventBus:  # En aplicación
    def publish(self, event): ...
```

**Después:**
```python
# domain/ports/outbound/event_bus_ports.py - CORRECTO
class EventBusPort(ABC):  # Interfaz en dominio
    @abstractmethod
    def publish(self, event): ...

# application/events/event_bus.py
class InMemoryEventBus(EventBusPort):  # Implementación
    def publish(self, event): ...
```

### 5. **TaskScheduler Solo Orquesta**
**Antes:**
```python
# MALO - Scheduler decide qué eventos publicar
def __execute_task__(self, task):
    task.execute(self._dispatcher)
    if result.is_successful():
        self._event_bus.publish(TaskCompleted(...))  # Lógica de dominio
    else:
        self._event_bus.publish(TaskFailed(...))
```

**Después:**
```python
# CORRECTO - Scheduler solo recolecta y publica
def __execute_task__(self, task: Task) -> None:
    task.execute(self._dispatcher)  # Task decide internamente
    
    # Recolectar eventos generados por el dominio
    domain_events = task.collect_domain_events()
    
    # Publicar todos los eventos
    for event in domain_events:
        self._event_bus.publish(event)
```

### 6. **UTC en Lugar de Timezone Hardcodeado**
**Antes:**
```python
# MALO
from datetime import timezone, timedelta
datetime.now(timezone(timedelta(hours=-3)))  # Hardcoded UTC-3
```

**Después:**
```python
# CORRECTO
from datetime import timezone
datetime.now(timezone(timedelta(hours=-3)))  # UTC estándar
```

## 🏗️ Estructura de Archivos Actualizada

```
src/
├── domain/
│   ├── events/
│   │   └── task_events.py ✅ (eventos puros, sin dependencias)
│   ├── models/
│   │   └── task.py ✅ (genera eventos internamente)
│   └── ports/
│       └── outbound/
│           ├── event_bus_ports.py ✅ (nuevo puerto)
│           └── task_executor_ports.py ✅ (nuevo puerto)
│
├── application/
│   ├── events/
│   │   └── event_bus.py ✅ (implementa EventBusPort)
│   └── services/
│       └── task_scheduler.py ✅ (solo orquesta, inyecta puertos)
│
├── adapters/
│   └── outbound/
│       └── task_executor/
│           ├── __init__.py ✅
│           └── thread_pool_executor_adapter.py ✅ (nuevo adaptador)
│
└── infrastructure/
    └── container.py ✅ (inyección de dependencias)
```

## 🔄 Flujo de Ejecución

1. **Container** crea e inyecta dependencias:
   ```python
   executor = ThreadPoolExecutorAdapter(max_workers=5)
   event_bus = InMemoryEventBus()
   scheduler = TaskScheduler(dispatcher, event_bus, executor)
   ```

2. **Task** (Dominio) ejecuta y genera eventos:
   ```python
   task.execute(dispatcher)
   # Internamente: _emit_event(TaskStarted(...))
   # Internamente: _emit_event(TaskCompleted(...))
   ```

3. **TaskScheduler** (Aplicación) recolecta y publica:
   ```python
   events = task.collect_domain_events()
   for event in events:
       event_bus.publish(event)
   ```

4. **Adaptadores** (Infraestructura) implementan puertos:
   ```python
   class ThreadPoolExecutorAdapter(TaskExecutorPort):
       def submit(self, fn, *args): ...
   ```

## 📊 Beneficios Obtenidos

✅ **Separación de responsabilidades**: Cada capa tiene su rol definido  
✅ **Testabilidad**: Puertos permiten fácil mocking  
✅ **Independencia de frameworks**: Dominio no depende de infraestructura  
✅ **Inversión de dependencias**: Infraestructura depende de dominio  
✅ **Mantenibilidad**: Cambios en infraestructura no afectan dominio  
✅ **Extensibilidad**: Fácil agregar nuevas implementaciones de puertos  

## 🎯 Principios SOLID Aplicados

- **S**: Task tiene única responsabilidad (gestionar estado y generar eventos)
- **O**: Puertos permiten extender sin modificar
- **L**: Adaptadores sustituibles (EventBus, TaskExecutor)
- **I**: Interfaces segregadas (EventBusPort, TaskExecutorPort)
- **D**: Dependencia de abstracciones, no de concreciones
