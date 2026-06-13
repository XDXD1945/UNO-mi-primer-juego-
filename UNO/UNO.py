import random
import json
from datetime import datetime
import os

# ==========================================
# 1. GENERACIÓN Y REPARTO DE CARTAS
# ==========================================
def crearmazo():
    colores = ["Rojo", "Amarillo", "Verde", "Azul"]
    numeros = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    comodines = ["+2", "Reversa", "bloqueo"]
    comodines_supremos = ["+4", "Cambio de color"]
    
    mazo_nuevo = []
    for color in colores:
        for numero in numeros:
            mazo_nuevo.append(f"{color} {numero}")
    for color in colores:
        for comodin in comodines:
            mazo_nuevo.append(f"{color} {comodin}")
    for _ in range(4):
        for supremo in comodines_supremos:
            mazo_nuevo.append(supremo)
            
    return mazo_nuevo

def repartir_manos(mazo):
    random.shuffle(mazo)
    mano_jugador = [mazo.pop() for _ in range(7)]
    mano_pc = [mazo.pop() for _ in range(7)]
    return mano_jugador, mano_pc

# ==========================================
# 2. REGLAS Y VALIDACIONES
# ==========================================
def rellenar_mazo_si_vacio(mazo, pozo_descarte):
    if len(mazo) == 0:
        print("\n¡Se acabaron las cartas! Revolviendo descarte...")
        # Al regresar las cartas al mazo, nos aseguramos de que los comodines limpien su color
        for carta in pozo_descarte:
            if "Comodín" in carta:
                # Si guardaste por ejemplo "Rojo Comodín +4", recuperamos solo el "+4"
                if "+4" in carta: mazo.append("+4")
                else: mazo.append("Cambio de color")
            else:
                mazo.append(carta)
        pozo_descarte.clear()
        random.shuffle(mazo)

def es_jugada_valida(carta_elegida, carta_mesa, color_actual):
    # Los comodines siempre se pueden tirar
    if "+4" in carta_elegida or "Cambio de color" in carta_elegida:
        return True
        
    # Si en la mesa hay un comodín activo, validamos contra el color elegido
    if "Comodín" in carta_mesa:
        detalles_elegida = carta_elegida.split()
        return detalles_elegida[0] == color_actual

    # Validación normal para cartas físicas de color
    detalles_elegida = carta_elegida.split()
    detalles_mesa = carta_mesa.split()
    
    return detalles_elegida[0] == detalles_mesa[0] or detalles_elegida[1] == detalles_mesa[1]

def aplicar_efecto_comodin(carta_jugada, mano_rival, mazo, pozo_descarte):
    if "+2" in carta_jugada:
        print("¡Toma 2!")
        for _ in range(2):
            rellenar_mazo_si_vacio(mazo, pozo_descarte)
            if mazo: mano_rival.append(mazo.pop())
        return True # En UNO normal de 2p, el +2 también salta el turno del rival
    elif "+4" in carta_jugada:
        print("¡+4!")
        for _ in range(4):
            rellenar_mazo_si_vacio(mazo, pozo_descarte)
            if mazo: mano_rival.append(mazo.pop())
        return True # El +4 también salta el turno
    elif "bloqueo" in carta_jugada or "Reversa" in carta_jugada:
        print("¡Turno saltado!")
        return True 
    return False

# ==========================================
# 2.5 LOG DE PARTIDA
# ==========================================
def iniciar_log():
    return {
        "turnos": [],
        "total_turnos": 0,
        "ganador": None
    }

def registrar_turno(log, turno_num, jugador, accion, mano_jugador, mano_pc, carta_mesa):
    log["turnos"].append({
        "turno": turno_num,
        "jugador": jugador,
        "accion": accion,
        "carta_mesa": carta_mesa,
        "mano_jugador": list(mano_jugador),
        "mano_pc": list(mano_pc)
    })
    log["total_turnos"] += 1

def guardar_log(log):
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    numero = 1
    while os.path.exists(f"Juego_{numero}-{fecha}.json"):
        numero += 1
    
    nombre_archivo = f"Juego_{numero}-{fecha}.json"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4, ensure_ascii=False)
    print(f"\n📁 Partida guardada en: {nombre_archivo}")

# ==========================================
# 3. INTERFAZ Y TURNOS
# ==========================================
def mostrar_interfaz(mano_jugador, mano_pc, carta_mesa, color_actual):
    print("\n" + "="*40)
    print(f"Cartas de la PC: {len(mano_pc)}") 
    print("-"*40)
    if "Comodín" in carta_mesa:
        print(f"CARTA EN LA MESA: [ {carta_mesa} ] (Color activo: {color_actual})")
    else:
        print(f"CARTA EN LA MESA: [ {carta_mesa} ]")
    print("-"*40)
    print("TUS CARTAS:")
    for indice, carta in enumerate(mano_jugador):
        print(f" {indice} -> {carta}")
    print("="*40 + "\n")

def turno_jugador(mano_jugador, mano_pc, mazo, pozo_descarte, carta_mesa, color_actual):
    print("\n--- TU TURNO ---")
    mostrar_interfaz(mano_jugador, mano_pc, carta_mesa, color_actual)
    
    while True:
        opcion = input("Elige carta o 'comer': ").strip()
        
        if opcion.lower() == "comer":
            rellenar_mazo_si_vacio(mazo, pozo_descarte)
            if mazo:
                nueva = mazo.pop()
                mano_jugador.append(nueva)
                print(f"Robaste: {nueva}")
            return carta_mesa, color_actual, False, "robó carta"
            
        if opcion.isdigit() and 0 <= int(opcion) < len(mano_jugador):
            carta = mano_jugador[int(opcion)]
            
            if es_jugada_valida(carta, carta_mesa, color_actual):
                mano_jugador.remove(carta)
                pozo_descarte.append(carta_mesa)
                
                if "+4" in carta or "Cambio de color" in carta:
                    while True:
                        color = input("Nuevo color (Rojo/Amarillo/Verde/Azul): ").capitalize()
                        if color in ["Rojo","Amarillo","Verde","Azul"]:
                            break
                    color_actual = color
                    carta_mesa = f"{color} Comodín {carta}"
                else:
                    carta_mesa = carta
                    color_actual = carta.split()[0]
                
                salta = aplicar_efecto_comodin(carta, mano_pc, mazo, pozo_descarte)
                return carta_mesa, color_actual, salta, f"jugó {carta}"
            else:
                print("Jugada inválida.")
        else:
            print("Selección incorrecta.")

def turno_pc_completo(mano_pc, mano_jugador, mazo, pozo_descarte, carta_mesa, color_actual):
    print("\n--- TURNO PC ---")
    
    for carta in mano_pc:
        if es_jugada_valida(carta, carta_mesa, color_actual):
            mano_pc.remove(carta)
            pozo_descarte.append(carta_mesa)
            
            if "+4" in carta or "Cambio de color" in carta:
                color_actual = random.choice(["Rojo","Amarillo","Verde","Azul"])
                carta_mesa = f"{color_actual} Comodín {carta}"
                print(f"La PC cambió el color a: {color_actual}")
            else:
                carta_mesa = carta
                color_actual = carta.split()[0]
                
            salta = aplicar_efecto_comodin(carta, mano_jugador, mazo, pozo_descarte)
            return carta_mesa, color_actual, salta, f"jugó {carta}"
    
    print("La PC no tiene cartas válidas y tiene que comer.")
    rellenar_mazo_si_vacio(mazo, pozo_descarte)
    if mazo:
        carta = mazo.pop()
        mano_pc.append(carta)
    return carta_mesa, color_actual, False, "robó carta"

# ==========================================
# 4. JUEGO PRINCIPAL
# ==========================================
def jugar_uno():
    print("¡UNO TERMINAL!")
    
    log = iniciar_log()
    turno_num = 1
    
    mazo = crearmazo()
    mano_jugador, mano_pc = repartir_manos(mazo)
    pozo_descarte = []
    
    carta_mesa = mazo.pop()
    while "+4" in carta_mesa or "Cambio de color" in carta_mesa:
        mazo.insert(0, carta_mesa)
        carta_mesa = mazo.pop()
        
    color_actual = carta_mesa.split()[0]
    turno = 0  # 0 = Jugador, 1 = PC
    
    while mano_jugador and mano_pc:
        if turno == 0:
            carta_mesa, color_actual, salta, accion = turno_jugador(mano_jugador, mano_pc, mazo, pozo_descarte, carta_mesa, color_actual)
            registrar_turno(log, turno_num, "Jugador", accion, mano_jugador, mano_pc, carta_mesa)
            turno_num += 1
            
            # Si hay salto, el turno NO cambia (sigue siendo 0)
            if not salta: 
                turno = 1
        else:
            carta_mesa, color_actual, salta, accion = turno_pc_completo(mano_pc, mano_jugador, mazo, pozo_descarte, carta_mesa, color_actual)
            registrar_turno(log, turno_num, "PC", accion, mano_jugador, mano_pc, carta_mesa)
            turno_num += 1
            
            # Si hay salto, el turno NO cambia (sigue siendo 1)
            if not salta: 
                turno = 0
    
    if not mano_jugador:
        print("\n🏆 ¡GANASTE! 🏆")
        log["ganador"] = "Jugador"
    else:
        print("\n🤖 ¡PERDISTE! La PC ganó. 🤖")
        log["ganador"] = "PC"
    
    guardar_log(log)

# ==========================================
if __name__ == "__main__":
    jugar_uno()
