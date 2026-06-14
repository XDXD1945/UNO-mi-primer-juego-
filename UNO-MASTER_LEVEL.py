import random
import json
from datetime import datetime
import os

# ==========================================
# MEMORIA GLOBAL IA
# ==========================================
# Ahora rastreamos qué colores NO tienes. 
# Si el jugador roba carta o dice "Inválido", sabemos que NO tiene el color actual.
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
        print("\n🔄 ¡Revolviendo el pozo de descarte! 🔄")
        # Limpiamos los textos de los comodines para que vuelvan limpios al mazo
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
    if "+4" in carta or "Cambio de color" in carta:
        return True
    
    # Separar los elementos de la carta de la mesa de forma segura
    partes_mesa = carta_mesa.split()
    partes_carta = carta.split()
    
    # Si es un comodín en la mesa, dependemos estrictamente del color_actual decretado
    if "Cambio" in carta_mesa or "+4" in carta_mesa:
        return partes_carta[0] == color_actual

    return partes_carta[0] == partes_mesa[0] or partes_carta[1] == partes_mesa[1]

# ==========================================
# 🧠 IA EXTREMA (Optimizada)
# ==========================================
def contar_colores(mano):
    colores = ["Rojo", "Amarillo", "Verde", "Azul"]
    conteo = {c: 0 for c in colores}
    for carta in mano:
        for color in colores:
            if carta.startswith(color):
                conteo[color] += 1
    return conteo

def mejor_color(mano):
    return max(contar_colores(mano), key=lambda c: contar_colores(mano)[c])

def peor_color_para_jugador():
    # Si sabemos con certeza que te falta un color, la IA elegirá ese primero
    if memoria["colores_que_no_tiene_el_jugador"]:
        return list(memoria["colores_que_no_tiene_el_jugador"])[0]
    
    # Si no, deduce cuál es tu color más débil basándose en lo que MENOS has jugado
    return min(memoria["colores_jugados_por_el_jugador"], key=memoria["colores_jugados_por_el_jugador"].get)

def actualizar_memoria_jugada_rival(carta):
    for color in memoria["colores_jugados_por_el_jugador"]:
        if carta.startswith(color):
            memoria["colores_jugados_por_el_jugador"][color] += 1
            # Si lo jugó, obviamente sí tiene este color:
            memoria["colores_que_no_tiene_el_jugador"].discard(color)

def evaluar_estado_futuro(mano_pc):
    colores = contar_colores(mano_pc)
    return max(colores.values())

def evaluar_jugada(carta, mano_pc, mano_jugador):
    score = 0
    colores = contar_colores(mano_pc)

    # ATAQUE
    if "+4" in carta:
        score += 100
    elif "+2" in carta:
        score += 70
    elif "bloqueo" in carta or "Reversa" in carta:
        score += 50

    # COLOR PROPIO (Sinergia de mano)
    if " " in carta and not ("Cambio" in carta or "+4" in carta):
        color = carta.split()[0]
        score += colores[color] * 8  # Subimos el peso estratégico

    # CONTRA JUGADOR (Color letal para el rival)
    if " " in carta and not ("Cambio" in carta or "+4" in carta):
        color = carta.split()[0]
        if color == peor_color_para_jugador():
            score += 60

    # ENDGAME
    if len(mano_pc) <= 3:
        score += 100

    # KILL PLAYER (Frenar victoria inminente)
    if len(mano_jugador) <= 2:
        if "+4" in carta: score += 400
        elif "+2" in carta: score += 250
        elif "bloqueo" in carta or "Reversa" in carta: score += 180

    # GUARDAR +4
    if "+4" in carta and len(mano_pc) > 4 and len(mano_jugador) > 2:
        score -= 120

    return score

def simular_jugada(carta, mano_pc):
    copia = mano_pc.copy()
    copia.remove(carta)
    return evaluar_estado_futuro(copia)

def elegir_mejor_jugada(mano_pc, mano_jugador, carta_mesa, color_actual):
    validas = [c for c in mano_pc if es_jugada_valida(c, carta_mesa, color_actual)]
    if not validas:
        return None

    mejor = None
    mejor_score = -9999

    for carta in validas:
        score = evaluar_jugada(carta, mano_pc, mano_jugador)
        score += simular_jugada(carta, mano_pc) * 4  # Ajuste de peso del futuro

        if score > mejor_score:
            mejor_score = score
            mejor = carta

    return mejor

# ==========================================
# EFECTOS
# ==========================================
def aplicar_efecto_comodin(carta, rival, mazo, pozo):
    if "+2" in carta:
        print("¡Toma 2!")
        for _ in range(2):
            rellenar_mazo_si_vacio(mazo, pozo)
            if mazo: rival.append(mazo.pop())
        return True
    if "+4" in carta:
        print("¡+4!")
        for _ in range(4):
            rellenar_mazo_si_vacio(mazo, pozo)
            if mazo: rival.append(mazo.pop())
        return True
    if "bloqueo" in carta or "Reversa" in carta:
        print("¡Turno saltado!")
        return True
    return False

# ==========================================
# LOG
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
    print("\n📁 Log guardado en:", nombre)

# ==========================================
# INTERFAZ
# ==========================================
def mostrar_interfaz(mano_j, mano_pc, carta_mesa, color):
    print("\n" + "="*40)
    print(f"Cartas de la IA IMPOSIBLE: {len(mano_pc)}")
    print(f"CARTA EN MESA: [ {carta_mesa} ] (Color activo: {color})")
    print("-"*40)
    print("TUS CARTAS:")
    for i, c in enumerate(mano_j):
        print(f"  {i} -> {c}")
    print("="*40)

# ==========================================
# TURNOS
# ==========================================
def turno_jugador(mano_j, mano_pc, mazo, pozo, mesa, color_actual):
    print("\n--- TU TURNO ---")
    mostrar_interfaz(mano_j, mano_pc, mesa, color_actual)

    while True:
        op = input("Elige número de carta o escribe 'comer': ").strip()

        if op.lower() == "comer":
            # Si el jugador come, la IA deduce que NO tenías el color actual en mano
            if color_actual:
                memoria["colores_que_no_tiene_el_jugador"].add(color_actual)
                
            rellenar_mazo_si_vacio(mazo, pozo)
            if mazo:
                c = mazo.pop()
                mano_j.append(c)
                print("Robaste:", c)
            return mesa, color_actual, False, "robó"

        if op.isdigit() and int(op) < len(mano_j):
            c = mano_j[int(op)]
            if es_jugada_valida(c, mesa, color_actual):
                mano_j.remove(c)
                pozo.append(mesa)
                actualizar_memoria_jugada_rival(c)

                if "+4" in c or "Cambio de color" in c:
                    while True:
                        nuevo = input("Color (Rojo/Amarillo/Verde/Azul): ").strip().capitalize()
                        if nuevo in ["Rojo", "Amarillo", "Verde", "Azul"]:
                            break
                    mesa = f"{nuevo} Comodín {c}"
                    color_actual = nuevo
                else:
                    mesa = c
                    color_actual = c.split()[0]

                salta = aplicar_efecto_comodin(c, mano_pc, mazo, pozo)
                return mesa, color_actual, salta, f"jugó {c}"

        print("❌ Selección inválida o carta no jugable.")

def turno_pc_completo(mano_pc, mano_j, mazo, pozo, mesa, color_actual):
    print("\n--- IA IMPOSIBLE 😈 ---")

    carta = elegir_mejor_jugada(mano_pc, mano_j, mesa, color_actual)

    if carta:
        mano_pc.remove(carta)
        pozo.append(mesa)

        if "+4" in carta or "Cambio de color" in carta:
            propio = mejor_color(mano_pc)
            enemigo = peor_color_para_jugador()
            # 70% de probabilidad de elegir tu peor color si está acorralada
            color_actual = enemigo if (random.random() > 0.3 and enemigo) else propio

            mesa = f"{color_actual} Comodín {carta}"
            print("😈 IA cambia el color a:", color_actual)
        else:
            mesa = carta
            color_actual = carta.split()[0]
            print("🤖 IA juega:", carta)

        salta = aplicar_efecto_comodin(carta, mano_j, mazo, pozo)
        return mesa, color_actual, salta, f"jugó {carta}"

    print("IA no tiene cartas y tiene que robar.")
    rellenar_mazo_si_vacio(mazo, pozo)
    if mazo:
        mano_pc.append(mazo.pop())
    return mesa, color_actual, False, "robó"

# ==========================================
# CONFIGURACIÓN DEL JUEGO
# ==========================================
def jugar_uno():
    print("¡UNO TERMINAL - EDICIÓN IMPOSIBLE!")

    log = iniciar_log()
    turno_num = 1

    mazo = crearmazo()
    mano_j, mano_pc = repartir_manos(mazo)
    pozo = []

    # Obtener carta inicial válida
    mesa = mazo.pop()
    while "+4" in mesa or "Cambio de color" in mesa:
        mazo.insert(0, mesa)
        mesa = mazo.pop()

    color_actual = mesa.split()[0]
    turno = 0

    while mano_j and mano_pc:
        if turno == 0:
            mesa, color_actual, salta, acc = turno_jugador(
                mano_j, mano_pc, mazo, pozo, mesa, color_actual
            )
            registrar_turno(log, turno_num, "Jugador", acc, mano_j, mano_pc, mesa)
            turno_num += 1
            if not salta:
                turno = 1
        else:
            mesa, color_actual, salta, acc = turno_pc_completo(
                mano_pc, mano_j, mazo, pozo, mesa, color_actual
            )
            registrar_turno(log, turno_num, "PC", acc, mano_j, mano_pc, mesa)
            turno_num += 1
            if not salta:
                turno = 0

    print("\n🏆 ¡GANASTE! 🏆" if not mano_j else "\nPERDISTE 😈 Tu historial fue guardado.")
    log["ganador"] = "Jugador" if not mano_j else "PC"
    guardar_log(log)

# ==========================================
if __name__ == "__main__":
    jugar_uno()
