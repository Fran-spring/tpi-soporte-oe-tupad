# TPI — Soporte Técnico N1 con Chatbot
**Organización Empresarial · UTN TUPaD · Comisión 16**  
**Alumno:** Francisco Cardenas  
**Fecha:** Junio 2026

---

## Descripción del proyecto

Trabajo Práctico Integrador de la materia Organización Empresarial.  
Se modela el proceso de **Soporte Técnico Nivel 1** de la empresa ficticia *TechSoluciones S.R.L.* utilizando BPMN 2.0, y se automatiza mediante un chatbot simulado con Python.

El bot implementa una **Máquina de Estados Finita (FSM)** que refleja fielmente el diagrama BPMN: clasifica problemas contra una base de datos de soluciones conocidas, resuelve automáticamente los casos conocidos y escala los demás al supervisor mediante un sistema de tickets.

---

## Estructura del repositorio

```
tpi-soporte-oe-tupad/
├── bot/
│   ├── chatbot.py              # Lógica principal del bot (FSM + clasificador)
│   ├── clasificador.py         # Módulo de clasificación por keywords
│   └── base_datos.json         # BD simulada de soluciones conocidas
├── docs/
│   ├── bpmn_soporte_n1.svg     # Diagrama BPMN exportado (alta resolución)
│   └── ia_captures/            # Capturas de pantalla de consultas a IA
├── simulador/
│   └── index.html              # Chatbot simulado funcional en navegador
├── scripts/
│   └── demo.py                 # Script de demo con casos de prueba automáticos
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Cómo ejecutar el bot (consola)

### Requisitos
- Python 3.10 o superior
- No requiere librerías externas (solo stdlib)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Fran-spring/tpi-soporte-oe-tupad.git
cd tpi-soporte-oe-tupad

# 2. Ejecutar el bot en modo consola
python bot/chatbot.py
```

### Ejemplo de sesión
```
Bot: ¡Hola! Soy el bot de Soporte Técnico N1 de TechSoluciones.
     Describí tu problema y buscaré una solución para vos.

Vos: no tengo internet

Bot: Encontré una solución para tu problema de Red:
     1. Reiniciá el router (desenchufar 30 seg).
     2. Verificá el cable si usás conexión por cable.
     3. En Windows: Configuración → Red → Solucionar problemas.
     ¿Se resolvió el problema? (Sí / No)

Vos: si

Bot: ¡Perfecto! Me alegra que se haya resuelto. ✓
```

---

## Cómo ejecutar el simulador web

No requiere servidor. Abrí directamente en el navegador:

```bash
# Opción 1: doble clic sobre el archivo
simulador/index.html

# Opción 2: desde terminal
python -m http.server 8080
# luego abrir http://localhost:8080/simulador/
```

---

## Cómo ejecutar los tests automáticos

```bash
python scripts/demo.py
```

Ejecuta 8 casos de prueba cubriendo el camino feliz, el camino infeliz y los errores de entrada.

---

## Diagrama BPMN

El archivo `docs/bpmn_soporte_n1.svg` contiene el diagrama de proceso completo con:
- **3 carriles:** Usuario · Bot/Sistema · Supervisor
- **3 gateways XOR:** Clasificación · Solución encontrada · Problema resuelto
- **Flujos AS-IS y TO-BE** documentados en el PDF del trabajo

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

## Historial de commits (Conventional Commits)

| ID | Mensaje | Etapa |
|----|---------|-------|
| TPI-1 | `feat: inicializar estructura del repositorio` | Inicialización |
| TPI-2 | `feat: agregar base de datos de soluciones conocidas` | Datos |
| TPI-3 | `feat: implementar FSM y lógica principal del bot` | Desarrollo |
| TPI-4 | `feat: agregar clasificador con normalización de tildes` | Desarrollo |
| TPI-5 | `feat: agregar simulador web con interfaz de chat` | Frontend |
| TPI-6 | `feat: agregar script de demo y tests automáticos` | QA |
| TPI-7 | `docs: agregar diagrama BPMN y capturas de IA` | Documentación |
| TPI-8 | `docs: actualizar README con instrucciones de despliegue` | Documentación |

---

## Herramientas de IA utilizadas

Se utilizó **Claude (Anthropic)** como herramienta de apoyo durante el desarrollo.  
Las capturas de pantalla de las consultas realizadas se encuentran en `docs/ia_captures/`.

| Etapa | Uso |
|-------|-----|
| Modelado BPMN | Validación de gateways y carriles |
| Diccionario de datos | Base de entidades revisada y adaptada |
| Lógica Python | Revisión de clasificador y FSM |
| Robustez | Identificación de caminos infelices |
