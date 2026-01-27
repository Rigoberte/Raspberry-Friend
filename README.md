# Raspberry-Friend 🤖🍓

Un **asistente robótico personal** controlado por Raspberry Pi y Python.  
El proyecto está diseñado para crecer de forma **iterativa e incremental** aplicando **TDD (Test Driven Development)**.  

## 🚀 Objetivo
Desarrollar un robot que pueda recibir instrucciones, moverse y más adelante conectarse con aplicaciones móviles y servidores externos.  

## 📂 Estado actual
- Fase **V0.2**: GUI funcional, comandos de voz, skills extensibles, workflows, cámara con seguimiento facial
- Arquitectura hexagonal implementada
- Sistema de eventos y tareas asíncronas
- Integración con Gemini AI para transcripción e interpretación
- TTS (Text-to-Speech) y reconocimiento de voz
- Iteraciones futuras: control de hardware GPIO, conexión remota, interfaz móvil  

## ⚙️ Requisitos
- Python 3.11+  
- Entorno virtual recomendado (`.venv`)  

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno en Windows
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt