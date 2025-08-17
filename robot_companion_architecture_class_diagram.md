# Robot Companion – Architecture & Class Diagram (MVP → v0.1)

> Objetivo: diseño extensible, iterativo/incremental y orientado a TDD, con módulos (skills) independientes, siguiendo POO (objetos completos/válidos, Null Object, inmutables, encapsulamiento estricto), preparado para futuras interfaces (CLI, HTTP/API, móvil) y futura ejecución en Raspberry Pi.

---

## 1) Vista de arquitectura (Hexagonal / Puertos y Adaptadores)

```
                        ┌───────────────────────────────────────────────────┐
                        │                    Interfaces                      │
                        │  - CLI Adapter (v0.1)                              │
                        │  - HTTP Adapter (futuro)                           │
                        │  - Mobile App (futuro)                             │
                        │  - Voice I/O (mic/tts) (futuro)                    │
                        └───────────────▲───────────────────────▲───────────┘
                                        │                       │
                         Commands/Query │                       │ Events/Responses
                                        │                       │
┌───────────────────────────────────────┼───────────────────────┼───────────────────────────────────────────┐
│                                   Núcleo (Domain/Application)                                             │
│   ┌─────────────────────┐    ┌───────────────────┐     ┌───────────────────┐     ┌────────────────┐       │
│   │ CommandRouter       │    │ Robot             │     │ EventBus          │     │ Scheduler      │       │
│   │ - route(cmd)        │    │ - dispatch(cmd)   │     │ - publish(ev)     │     │ - schedule()   │       │
│   └─────────▲───────────┘    └───────▲───────────┘     └─────────▲─────────┘     └───────▲────────┘       │
│             │                         │                           │                           │           │
│        selects Skill            owns skills[]                subscribers                time-based        │
│             │                         │                           │                   triggers/events     │
│   ┌─────────┴───────────┐   ┌─────────┴───────────┐       ┌───────┴─────────┐                 │           │
│   │ RobotSkill (porta)  │   │ Domain Objects      │       │ Event (value)   │                 │           │
│   │ + can_handle(cmd)   │   │ - Command           │       │ (inmutables)    │                 │           │
│   │ + handle(cmd,ctx)   │   │ - Reminder          │       └─────────────────┘                 │           │
│   │ + describe()        │   │ - WeatherQuery ...  │                                                       │
│   └─────────┬───────────┘   └─────────────────────┘                                                       │
│             │                                                                                             │
│   ┌─────────┼───────────┐   ┌──────────┐   ┌──────────┐                                                   │
│   │ EchoSkill           │   │ Reminder │   │ Weather  │   ... (Skills plug-in)                            │
│   └─────────────────────┘   └──────────┘   └──────────┘                                                   │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │                       │
                                        │                       │
                        ┌───────────────▼───────────────────────▼────────────┐
                        │                 Infraestructura                    │
                        │  - StoragePort (puerto)                            │
                        │  - InMemoryStorage (v0.1)                          │
                        │  - FileStorage / SQLite (futuro)                   │
                        │  - ServerStorage (NAS/home server) (futuro)        │
                        │  - GPIO/Audio/TTS adapters (Raspberry) (futuro)    │
                        └────────────────────────────────────────────────────┘
```

**Notas clave:**

- **Núcleo** no conoce nada de la infraestructura ni de las interfaces externas. Se comunica solo a través de **puertos** (`RobotSkill`, `StoragePort`, `ClockPort`, etc.).
- **Skills** son *plugins* que implementan `RobotSkill`. Se cargan en el `Robot` al iniciar. Agregar una habilidad no rompe las otras.
- **TDD**: tests de dominio (unit tests), tests de contrato para puertos (contract tests), y tests de integración por adaptador.

---

## 2) Diagrama de clases (MVP)

```
+-------------------+           1  *          +------------------+
| Robot             |------------------------>| RobotSkill       |
|-------------------|                         |------------------|
| - skills: list    |                         | + can_handle(c)  |
| - router: Router  |                         | + handle(c, ctx) |
| - bus: EventBus   |                         | + describe()     |
|-------------------|                         +------------------+
| + dispatch(cmd)   |
| + register(skill) |
+---------▲---------+
          │ uses
          │
+---------+---------+
| CommandRouter     |
|-------------------|
| + route(cmd):     |
|   RobotSkill      |
+-------------------+

+-------------------+                          +------------------+
| EventBus          |<>----------------------->| Subscriber       |
|-------------------|   publishes/subscribe    |------------------|
| + publish(event)  |                          | + on(event)      |
| + subscribe(sub)  |                          +------------------+
+-------------------+

+-------------------+                          +------------------+
| Command (value)   |                          | Context          |
|-------------------|                          |------------------|
| + name: str       |                          | + clock: Clock   |
| + args: dict      |                          | + storage: ...   |
| (inmutable)       |                          | + bus: EventBus  |
+-------------------+                          +------------------+

+-------------------+                          +------------------+
| EchoSkill         |  implements              | NullSkill        |
|-------------------|------------------------->| (Null Object)    |
| + can_handle()    |                          | + can_handle()   |
| + handle()        |                          | + handle()       |
+-------------------+                          +------------------+

+-------------------+                          +------------------+
| Scheduler         |------ time events ------>| EventBus         |
|-------------------|                          +------------------+
| + schedule(job)   |
| + tick()          |
+-------------------+

+-------------------+
| StoragePort       |  (puerto de persistencia)
|-------------------|
| + save(key, val)  |
| + get(key)        |
+-------------------+
```

**Inmutabilidad y Null Object**

- `Command` y los *value objects* (p. ej., `ReminderTime`, `SkillId`) son **inmutables**.
- `NullSkill` implementa `RobotSkill` y se usa cuando ningún módulo puede manejar un comando.

---

## 3) Contratos (puertos) iniciales

- \`\` (dominio):

  - `can_handle(command: Command) -> bool`
  - `handle(command: Command, ctx: Context) -> Result` (sin exponer estado interno)
  - `describe() -> SkillDescriptor` (para ayuda/autodescubrimiento)

- \`\` (infra): persistencia agnóstica.

  - `save(key: Key, value: Value) -> None`
  - `get(key: Key) -> Optional[Value]` (devolver `NullValue` en vez de `None` si aplica)

- \`\` (infra): reloj inyectable para TDD (control del tiempo).

  - `now() -> Instant`

- \`\` (dominio): pub/sub simple para desacoplar.

  - `publish(event: DomainEvent)`
  - `subscribe(subscriber: Subscriber)`

---

## 4) Flujo de comando (MVP)

1. **Adapter** (CLI) recibe texto: `"echo Hola"`.
2. Parser crea `Command(name="echo", args={"text":"Hola"})`.
3. `Robot.dispatch(cmd)` → `CommandRouter.route(cmd)` selecciona el `RobotSkill` adecuado.
4. `EchoSkill.handle()` devuelve `Result.success("Hola")` y publica opcionalmente un evento.
5. Adapter entrega la respuesta al usuario.

> Ningún adapter conoce la lógica de negocios; y el núcleo no conoce tecnologías externas.

---

## 5) Estrategia TDD por capas

- **Unit tests (dominio)**: `EchoSkill`, `CommandRouter`, `Robot` (dobles de prueba para puertos).
- **Contract tests (puertos)**: `StoragePort`, `ClockPort` (cualquier implementación debe pasar la misma batería de tests).
- **Integration tests (adaptadores)**: CLI + Núcleo (sin red/DB real en v0.1).
- **E2E (futuro)**: HTTP/API ↔ Núcleo ↔ Persistencia.

**Regla de oro:** no se puede escribir lógica de producción sin un test que la justifique.

---

## 6) Rutas de evolución (sin romper núcleo)

- **Recordatorios/Alarmas**: `ReminderSkill` + `Scheduler` + `ClockPort` + `StoragePort`.
- **Clima**: `WeatherSkill` + `HttpPort` (puerto HTTP) con implementación que se *simula* en tests.
- **App móvil**: agregar **HTTP Adapter** (REST/gRPC/WebSocket). Núcleo queda intacto.
- **Raspberry**: agregar adaptadores de **Audio/Mic/GPIO/TTS**; el dominio ni se entera.
- **Servidor en casa**: `ServerStorage` (NAS/SQLite/Postgres) implementando `StoragePort`.

---

## 7) Principios POO aplicados

- **Objetos completos/válidos**: constructores garantizan invariantes (no hay objetos parciales).
- **Inmutables**: `Command`, `Result`, `DomainEvent` y VOs.
- **Null Object**: `NullSkill`, `NullValue`.
- **Encapsulamiento**: evitar getters/setters; exponer comportamientos (métodos) y no estado.
- **SRP/OC**: cada clase hace una cosa; agregar skills no modifica clases existentes (Open/Closed).

---

## 8) Convenciones de comandos (MVP)

- Formato textual simple para CLI:
  - `echo <texto>`
  - `help` (mostrará `describe()` de cada skill)
- Parser mínimo (sin regex complejas todavía). En futuro, gramática más robusta.

---

## 9) Checklist para la primera iteración (v0.1)

-

---
