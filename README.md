# TPI — Soporte Técnico N1 con Chatbot
**Organización Empresarial · UTN TUPaD · Comisión 16**  
**Alumno:** Francisco Cardenas  
**Fecha:** Junio 2026

---

## Descripción del proyecto

Trabajo Práctico Integrador de la materia Organización Empresarial.  
Se modela el proceso de **Soporte Técnico Nivel 1** de la empresa ficticia *TechSoluciones S.R.L.* utilizando BPMN 2.0, y se automatiza mediante un chatbot simulado en consola (Python).

El bot implementa una **Máquina de Estados Finita (FSM)** que refleja fielmente el diagrama BPMN: clasifica problemas contra una base de datos de soluciones conocidas, resuelve automáticamente los casos conocidos y escala los demás al supervisor mediante un sistema de tickets.

---

## Estructura del repositorio

```
tpi-soporte-oe-tupad/
├── bot/
│   ├── chatbot.py              # Lógica principal del bot (FSM + clasificador)
│   ├── clasificador.py         # Módulo de clasificación por keywords
│   └── base_datos.json         # BD simulada de soluciones conocidas
├── README.md
└── .gitignore
```

---

## Cómo ejecutar el bot

### Requisitos
- Python 3.10 o superior
- No requiere librerías externas (solo stdlib)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Fran-spring/tpi-soporte-oe-tupad.git
cd tpi-soporte-oe-tupad

# 2. Ejecutar el bot en consola
python bot/chatbot.py
```

### Ejemplo de sesión
```
Bot: Hola! Soy el bot de Soporte Tecnico N1 de TechSoluciones.
     Describi tu problema y buscare una solucion.

Vos: no tengo internet

Bot: Encontre una solucion para tu problema de Red:
     1. Reinicia el router (desenchufar 30 seg).
     2. Verifica el cable si usas conexion por cable.
     3. En Windows: Configuracion -> Red -> Solucionar problemas.
     Se resolvio el problema? (Si / No)

Vos: si

Bot: Perfecto! Me alegra que se haya resuelto.
```

---

## Diagrama BPMN

El diagrama de proceso completo (3 carriles, 3 gateways XOR, eventos de inicio/fin) se incluye como imagen en el documento de entrega (PDF/Word), sección "Modelado del Proceso".

---

## Máquina de estados (FSM)

```
INICIO → ESPERANDO_CONSULTA → CLASIFICANDO
                                    ├── (solución encontrada) → SOLUCION_ENVIADA → RESUELTO
                                    │                                └── (no resuelto) → TICKET_CREADO → SUPERVISOR_REVISANDO
                                    └── (sin solución) → TICKET_CREADO → SUPERVISOR_REVISANDO
                                                                              └── (no resuelve) → DERIVADO_N2
```

---

## Herramientas de IA utilizadas

Se utilizó **Claude (Anthropic)** como herramienta de apoyo durante el desarrollo, principalmente para validar el diagrama BPMN, revisar la lógica de la FSM y detectar errores en el clasificador.

---