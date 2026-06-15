import json
import uuid
from datetime import datetime
from pathlib import Path

from clasificador import clasificar

# Ruta a tickets
TICKETS_PATH = Path(__file__).parent / "base_datos_tickets.json"


class Estado:
    INICIO               = "INICIO"
    ESPERANDO_CONSULTA   = "ESPERANDO_CONSULTA"
    CLASIFICANDO         = "CLASIFICANDO"
    SOLUCION_ENVIADA     = "SOLUCION_ENVIADA"
    TICKET_CREADO        = "TICKET_CREADO"
    SUPERVISOR_REVISANDO = "SUPERVISOR_REVISANDO"
    RESUELTO             = "RESUELTO"
    DERIVADO_N2          = "DERIVADO_N2"


class Sesion:
    def __init__(self):
        self.id                     = str(uuid.uuid4())[:8].upper()
        self.estado                 = Estado.INICIO
        self.ticket                 = None
        self.solucion               = None
        self.esperando_confirmacion = False

    def transicion(self, nuevo_estado: str):
        print(f"  [FSM] {self.estado} -> {nuevo_estado}")
        self.estado = nuevo_estado


_ticket_counter = 1000


def _cargar_tickets():
    if TICKETS_PATH.exists():
        with open(TICKETS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _guardar_tickets(tickets):
    TICKETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TICKETS_PATH, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)


def crear_ticket(descripcion, categoria="Sin categorizar"):
    global _ticket_counter
    tickets = _cargar_tickets()
    ticket = {
        "id":           _ticket_counter,
        "fecha_hora":   datetime.now().isoformat(sep=" ", timespec="seconds"),
        "descripcion":  descripcion,
        "categoria":    categoria,
        "estado":       "Abierto",
        "resuelto_por": None,
    }
    tickets.append(ticket)
    _guardar_tickets(tickets)
    _ticket_counter += 1
    return ticket


def _normalizar(texto):
    import unicodedata
    nfkd = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _es_positivo(texto):
    import re
    positivos = [r"\bsi\b", r"\byes\b", "se resolvio", "funciono",
                 r"\blisto\b", r"\bok\b", r"\bdale\b", "perfecto",
                 r"\banda\b", "ya funciona"]
    t = _normalizar(texto)
    return any(re.search(p, t) for p in positivos)


def _es_negativo(texto):
    negativos = ["no", "sigue", "no funciono", "no se resolvio",
                 "igual", "mismo", "todavia", "no anda", "no funciona"]
    t = _normalizar(texto)
    return any(n in t for n in negativos)


def procesar_mensaje(sesion, texto):
    """
    Funcion central del bot. Recibe la sesion y el texto del usuario,
    actualiza la FSM segun el diagrama BPMN y retorna la respuesta.
    """
    texto = texto.strip()
    t_norm = _normalizar(texto)

    # Validaciones — Unhappy Path
    if not texto:
        return "No recibi ningun mensaje. Por favor, describi tu problema con palabras."

    if texto.isdigit():
        return "Solo recibi numeros. Describi tu problema con palabras, por ejemplo: 'no tengo internet'."

    if len(texto) < 3 and not sesion.esperando_confirmacion:
        return "El mensaje es muy corto. Contame mas sobre tu problema para poder ayudarte."

    # Comandos que siempre interrumpen (excepto durante confirmacion los dejamos pasar)
    if any(c in t_norm for c in ["hola", "/inicio", "/start", "reiniciar"]) and not sesion.esperando_confirmacion:
        sesion.transicion(Estado.ESPERANDO_CONSULTA)
        sesion.esperando_confirmacion = False
        sesion.ticket   = None
        sesion.solucion = None
        return (
            "Hola! Soy el bot de Soporte Tecnico N1 de TechSoluciones.\n"
            "Describi tu problema y busccare una solucion.\n\n"
            "Ejemplos:\n"
            "  - no tengo internet\n"
            "  - mi PC esta lenta\n"
            "  - olvide la contrasena\n\n"
            "Comandos disponibles: /estado  /cancelar"
        )

    if "/estado" in t_norm:
        if sesion.ticket:
            t = sesion.ticket
            return (
                f"Estado de tu ticket #{t['id']}:\n"
                f"  Descripcion: {t['descripcion'][:60]}\n"
                f"  Categoria:   {t['categoria']}\n"
                f"  Fecha:       {t['fecha_hora']}\n"
                f"  Estado:      {t['estado']}"
            )
        return "No tenes tickets registrados en esta sesion."

    if "cancelar" in t_norm or "/cancelar" in t_norm:
        sesion.transicion(Estado.INICIO)
        sesion.esperando_confirmacion = False
        return "Sesion cancelada. Escribi 'hola' para iniciar una nueva consulta."

    # Confirmacion de resolucion — se evalua ANTES del flujo principal
    if sesion.esperando_confirmacion:
        sesion.esperando_confirmacion = False

        if _es_positivo(texto):
            # Gateway: resuelto = Si -> cierre
            sesion.transicion(Estado.RESUELTO)
            return (
                "Perfecto! Me alegra que se haya resuelto.\n"
                "El caso quedo registrado como cerrado.\n"
                "Escribi 'hola' si necesitas otra consulta."
            )

        elif _es_negativo(texto):
            # Gateway: resuelto = No -> escalar
            cat = sesion.solucion.get("categoria", "Sin categorizar") if sesion.solucion else "Sin categorizar"
            ticket = crear_ticket(f"Solucion automatica no efectiva - {cat}", cat)
            sesion.ticket = ticket
            sesion.transicion(Estado.TICKET_CREADO)
            sesion.transicion(Estado.SUPERVISOR_REVISANDO)
            return (
                f"Entendido. Scale el caso al supervisor.\n\n"
                f"  Ticket #{ticket['id']} - {ticket['categoria']}\n"
                f"  Fecha: {ticket['fecha_hora']}\n"
                f"  Estado: Abierto\n\n"
                "Un tecnico se pondra en contacto en los proximos 15 minutos.\n"
                "Escribi /estado para ver el estado de tu ticket."
            )

        else:
            # Unhappy path: respuesta ambigua
            sesion.esperando_confirmacion = True
            return "No entendi tu respuesta. Por favor responde Si o No para indicar si el problema se resolvio."

    # Flujo principal
    if sesion.estado in (Estado.INICIO, Estado.ESPERANDO_CONSULTA):
        sesion.transicion(Estado.CLASIFICANDO)
        solucion = clasificar(texto)   # Gateway GW-1

        if solucion:
            # GW-2: solucion encontrada
            sesion.solucion = solucion
            sesion.transicion(Estado.SOLUCION_ENVIADA)
            sesion.esperando_confirmacion = True
            return (
                f"Encontre una solucion para tu problema de {solucion['categoria']}:\n\n"
                f"{solucion['respuesta']}\n\n"
                "Se resolvio el problema? (Si / No)"
            )
        else:
            # GW-2: sin solucion -> escalar
            ticket = crear_ticket(texto)
            sesion.ticket = ticket
            sesion.transicion(Estado.TICKET_CREADO)
            sesion.transicion(Estado.SUPERVISOR_REVISANDO)
            return (
                f"No encontre una solucion automatica para tu caso.\n\n"
                f"  Ticket #{ticket['id']} creado - {ticket['fecha_hora']}\n"
                f"  Categoria: {ticket['categoria']}\n"
                f"  Estado: Abierto - asignado al Supervisor\n\n"
                "Un tecnico ya recibio tu ticket y te contactara a la brevedad.\n"
                "Escribi /estado para consultar el estado de tu caso."
            )

    elif sesion.estado == Estado.SUPERVISOR_REVISANDO:
        return (
            f"Tu caso ya esta en manos del supervisor "
            f"(Ticket #{sesion.ticket['id'] if sesion.ticket else '-'}).\n"
            "Escribi /estado para ver el estado actual."
        )

    elif sesion.estado in (Estado.RESUELTO, Estado.DERIVADO_N2):
        sesion.transicion(Estado.ESPERANDO_CONSULTA)
        return procesar_mensaje(sesion, texto)

    else:
        sesion.transicion(Estado.ESPERANDO_CONSULTA)
        return "Hubo un problema con la sesion. Escribi 'hola' para iniciar una nueva consulta."


def main():
    print("=" * 58)
    print("  TechSoluciones - Bot de Soporte Tecnico N1")
    print("  TPI Organizacion Empresarial - UTN TUPaD - Com. 16")
    print("  Comandos: hola  /estado  /cancelar  salir")
    print("=" * 58)
    print()

    sesion = Sesion()
    respuesta = procesar_mensaje(sesion, "hola")
    print(f"Bot: {respuesta}")
    print(f"\n[Estado FSM: {sesion.estado} | Sesion: {sesion.id}]\n")

    while True:
        try:
            entrada = input("Vos: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSesion finalizada.")
            break

        if entrada.lower() in ("salir", "exit", "quit", "chau"):
            print("Bot: Hasta luego! Que se resuelva todo!")
            break

        if not entrada:
            continue

        respuesta = procesar_mensaje(sesion, entrada)
        print(f"\nBot: {respuesta}")
        print(f"\n[Estado FSM: {sesion.estado}]\n")


if __name__ == "__main__":
    main()