import random
import json
from datetime import datetime
import os

# ==========================================
# MEMORIA GLOBAL IA
# ==========================================
memoria = {
    "colores_que_no_tiene_el_jugador": set(),
    "colores_jugados_por_el_jugador": {"Rojo": 0, "Amarillo": 0, "Verde": 0, "Azul": 0}
}

# ==========================================
# 1. GENERACIÓN Y REPARTO DE CARTAS
# ==========================================
def crearmazo():
    colores = ["Rojo", "Amarillo", "Verde", "Azul"]
    numeros = list(range(10))
    comodines = ["bloqueo", "Reversa", "+2"]
    comodines_supremos = ["+4", "Cambio de color"]

    mazo = []
    for color in colores:
        for numero in numeros:
            mazo.append(f"{color} {numero}")
        for comodin in comodines:
            mazo.append(f"{color} {comodin}")

    for _ in range(4):
        for supremo in comodines_supremos:
            mazo.append(supremo)
    return mazo

def repartir_manos(mazo):
    random.shuffle(mazo)
    return [mazo.pop() for _ in range(7)], [mazo.pop() for _ in range(7)]

# ==========================================
# 2. REGLAS
# ==========================================
def rellenar_mazo_si_vacio(mazo, pozo):
    if not mazo:
        for c in pozo:
            if "+4" in c:
                mazo.append("+4")
            elif "Cambio de color" in c:
                mazo.append("Cambio de color")
            else:
                mazo.append(c)
        pozo.clear()
        random.shuffle(mazo)

def es_jugada_valida(carta, carta_mesa, color_actual):
    # Validar que no sea un marcador simulado temporal de Minimax
    if carta == "Placeholder": 
        return False
    if "+4" in carta or "Cambio de color" in carta:
        return True

    partes_mesa = carta_mesa.split()
    partes_carta = carta.split()

    if "Cambio" in carta_mesa or "+4" in carta_mesa:
        return partes_carta[0] == color_actual

    return partes_carta[0] == partes_mesa[0] or partes_carta[1] == partes_mesa[1]

# ==========================================
# 🧠 IA DIOS (Stockfish-like funcional)
# ==========================================
MAX_PROFUNDIDAD = 6  # Reducido un poco: profundidad 25 con combinatoria de mazo causaría lag severo.
MAX_NODOS = 4000

nodos = 0

def contar_colores(mano):
    colores = ["Rojo", "Amarillo", "Verde", "Azul"]
    conteo = {c: 0 for c in colores}
    for carta in mano:
        if carta != "Placeholder":
            for color in colores:
                if carta.startswith(color):
                    conteo[color] += 1
    return conteo

def mejor_color(mano):
    return max(contar_colores(mano), key=lambda c: contar_colores(mano)[c])

def peor_color_para_jugador():
    if memoria["colores_que_no_tiene_el_jugador"]:
        return list(memoria["colores_que_no_tiene_el_jugador"])[0]
    return min(memoria["colores_jugados_por_el_jugador"],
               key=memoria["colores_jugados_por_el_jugador"].get)

def evaluar(mano_pc, mano_j):
    # Conteo limpio ignorando marcadores virtuales de Minimax
    cartas_pc = len([c for c in mano_pc if c != "Placeholder"])
    cartas_j = len([c for c in mano_j if c != "Placeholder"])

    if cartas_pc == 0: return 100000
    if cartas_j == 0: return -100000

    score = (cartas_j - cartas_pc) * 40

    colores = contar_colores(mano_pc)
    score += max(colores.values()) * 12
    score -= len([c for c in colores if colores[c] > 0]) * 6

    return score

def obtener_validas(mano, mesa, color):
    return [c for c in mano if es_jugada_valida(c, mesa, color)]

def simular(carta, mano_pc, mano_j, mesa, color):
    pc = mano_pc.copy()
    j = mano_j.copy()

    pc.remove(carta)

    if "+4" in carta or "Cambio de color" in carta:
        color = peor_color_para_jugador()
        mesa = f"{color} Comodín {carta}"
    else:
        mesa = carta
        color = carta.split()[0]

    # Agregamos placeholders seguros que 'es_jugada_valida' sabe ignorar
    if "+2" in carta:
        j += ["Placeholder", "Placeholder"]
    if "+4" in carta:
        j += ["Placeholder", "Placeholder", "Placeholder", "Placeholder"]

    return pc, j, mesa, color

def ordenar_jugadas(jugadas):
    prioridad = []
    for c in jugadas:
        score = 0
        if "+4" in c: score += 1000
        if "+2" in c: score += 600
        if "bloqueo" in c or "Reversa" in c: score += 400
        prioridad.append((score, c))
    prioridad.sort(reverse=True)
    return [c for _, c in prioridad]

def minimax(pc, j, mesa, color, profundidad, alpha, beta, maximizando):
    global nodos

    if nodos >= MAX_NODOS or profundidad == 0:
        return evaluar(pc, j)

    nodos += 1

    # Filtrado de victorias simuladas
    if len([c for c in pc if c != "Placeholder"]) == 0: return 100000
    if len([c for c in j if c != "Placeholder"]) == 0: return -100000

    if maximizando:
        valor = -999999
        jugadas = ordenar_jugadas(obtener_validas(pc, mesa, color))

        if not jugadas:
            return evaluar(pc, j)

        for c in jugadas:
            npc, nj, nm, nc = simular(c, pc, j, mesa, color)
            valor = max(valor, minimax(npc, nj, nm, nc, profundidad-1, alpha, beta, False))
            alpha = max(alpha, valor)
            if beta <= alpha:
                break
        return valor

    else:
        valor = 999999
        jugadas = obtener_validas(j, mesa, color)

        if not jugadas:
            return evaluar(pc, j)

        for c in jugadas:
            nj = j.copy()
            npc = pc.copy()
            nj.remove(c)

            if "+2" in c: npc += ["Placeholder", "Placeholder"]
            if "+4" in c: npc += ["Placeholder", "Placeholder", "Placeholder", "Placeholder"]

            if "+4" in c or "Cambio de color" in c:
                nc = mejor_color(nj)
                nm = f"{nc} Comodín {c}"
            else:
                nm = c
                nc = c.split()[0]

            valor = min(valor, minimax(npc, nj, nm, nc, profundidad-1, alpha, beta, True))
            beta = min(beta, valor)
            if beta <= alpha:
                break
        return valor

def elegir_mejor_jugada(mano_pc, mano_j, mesa, color):
    global nodos
    nodos = 0

    jugadas = obtener_validas(mano_pc, mesa, color)

    if not jugadas:
        return None

    mejor = None
    mejor_valor = -999999

    for c in ordenar_jugadas(jugadas):
        npc, nj, nm, nc = simular(c, mano_pc, mano_j, mesa, color)
        valor = minimax(npc, nj, nm, nc, MAX_PROFUNDIDAD, -999999, 999999, False)

        if valor > mejor_valor:
            mejor_valor = valor
            mejor = c

    print(f"🧠 [IA PENSANDO]: Ramas analizadas en profundidad: {nodos}")
    return mejor

# ==========================================
# EFECTOS
# ==========================================
def aplicar_efecto_comodin(carta, rival, mazo, pozo):
    if "+2" in carta:
        for _ in range(2):
            rellenar_mazo_si_vacio(mazo, pozo)
            if mazo: rival.append(mazo.pop())
        return True
    if "+4" in carta:
        for _ in range(4):
            rellenar_mazo_si_vacio(mazo, pozo)
            if mazo: rival.append(mazo.pop())
        return True
    if "bloqueo" in carta or "Reversa" in carta:
        return True
    return False

# ==========================================
# LOG Y DIAGNÓSTICO
# ==========================================
def iniciar_log():
    return {"turnos": [], "total_turnos": 0, "ganador": None}

def registrar_turno(log, turno, jugador, accion, mano_j, mano_pc, mesa):
    log["turnos"].append({
        "turno": turno,
        "jugador": jugador,
        "accion": accion,
        "carta_mesa": mesa,
        "mano_jugador": list(mano_j),
        "mano_pc": list(mano_pc)
    })
    log["total_turnos"] += 1

def guardar_log(log):
    nombre = f"Juego_{datetime.now().strftime('%H-%M-%S')}.json"
    with open(nombre, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4, ensure_ascii=False)
    print("Log guardado con éxito:", nombre)

# ==========================================
# INTERFAZ
# ==========================================
def mostrar_interfaz(mano_j, mano_pc, carta_mesa, color):
    print("\n" + "="*40)
    print(f"Cartas IA: {len(mano_pc)}")
    print(f"Mesa: [ {carta_mesa} ] (Color Activo: {color})")
    print("-"*40)
    for i, c in enumerate(mano_j):
        print(f"  {i} -> {c}")
    print("="*40)

# ==========================================
# TURNOS
# ==========================================
def turno_jugador(mano_j, mano_pc, mazo, pozo, mesa, color):
    mostrar_interfaz(mano_j, mano_pc, mesa, color)

    while True:
        op = input("Elige número de carta o escribe 'comer': ").strip()

        if op.lower() == "comer":
            memoria["colores_que_no_tiene_el_jugador"].add(color)
            rellenar_mazo_si_vacio(mazo, pozo)
            if mazo:
                mano_j.append(mazo.pop())
            return mesa, color, False, "robó"

        if op.isdigit() and int(op) < len(mano_j):
            c = mano_j[int(op)]
            if es_jugada_valida(c, mesa, color):
                mano_j.remove(c)
                pozo.append(mesa)

                # Guardar color en memoria del comportamiento del jugador
                if " " in c:
                    col = c.split()[0]
                    memoria["colores_jugados_por_el_jugador"][col] += 1
                    memoria["colores_que_no_tiene_el_jugador"].discard(col)

                if "+4" in c or "Cambio" in c:
                    color = input("Color (Rojo/Amarillo/Verde/Azul): ").capitalize()
                    mesa = f"{color} Comodín {c}"
                else:
                    mesa = c
                    color = c.split()[0]

                salta = aplicar_efecto_comodin(c, mano_pc, mazo, pozo)
                return mesa, color, salta, f"jugó {c}"

        print("Inválido.")

def turno_pc_completo(mano_pc, mano_j, mazo, pozo, mesa, color):
    carta = elegir_mejor_jugada(mano_pc, mano_j, mesa, color)

    if carta:
        mano_pc.remove(carta)
        pozo.append(mesa)

        if "+4" in carta or "Cambio" in carta:
            color = peor_color_para_jugador()
            mesa = f"{color} Comodín {carta}"
            print(f"🤖 IA juega {carta} y cambia el color a: {color}")
        else:
            mesa = carta
            color = carta.split()[0]
            print(f"🤖 IA juega: {carta}")

        salta = aplicar_efecto_comodin(carta, mano_j, mazo, pozo)
        return mesa, color, salta, f"jugó {carta}"

    print("🤖 IA no tiene jugadas válidas y roba.")
    rellenar_mazo_si_vacio(mazo, pozo)
    if mazo:
        mano_pc.append(mazo.pop())
    return mesa, color, False, "robó"

# ==========================================
# JUEGO PRINCIPAL
# ==========================================
def jugar_uno():
    log = iniciar_log()
    turno_num = 1

    mazo = crearmazo()
    mano_j, mano_pc = repartir_manos(mazo)
    pozo = []

    mesa = mazo.pop()
    while "+4" in mesa or "Cambio" in mesa:
        mazo.insert(0, mesa)
        mesa = mazo.pop()

    color = mesa.split()[0]
    
    # Sistema de turnos binario estándar estable (0 = Jugador, 1 = PC)
    turno = 0

    while mano_j and mano_pc:
        if turno == 0:
            print("\n--- TU TURNO ---")
            mesa, color, salta, acc = turno_jugador(mano_j, mano_pc, mazo, pozo, mesa, color)
            registrar_turno(log, turno_num, "Jugador", acc, mano_j, mano_pc, mesa)
            # Si hay bloqueo/reversa, el flujo se salta al oponente y repite el jugador actual
            turno = 0 if salta else 1
        else:
            print("\n--- TURNO IA ---")
            mesa, color, salta, acc = turno_pc_completo(mano_pc, mano_j, mazo, pozo, mesa, color)
            registrar_turno(log, turno_num, "PC", acc, mano_j, mano_pc, mesa)
            turno = 1 if salta else 0

        turno_num += 1

    print("\n🏆 ¡GANASTE! 🏆" if not mano_j else "\nPERDISTE 😈")
    log["ganador"] = "Jugador" if not mano_j else "PC"
    guardar_log(log)

if __name__ == "__main__":
    jugar_uno()
