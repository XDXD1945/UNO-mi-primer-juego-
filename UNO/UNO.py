import random

# ==========================================
# 1. GENERACIÓN Y REPARTO DE CARTAS
# ==========================================
def crearmazo():
    colores = ["Rojo", "Amarillo", "Verde", "Azul"]
    numeros = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    comodines = ["+2", "Reversa", "bloqueo"]
    comodines_supremos = ["+4", "Cambio de color"]
    
    mazo_nuevo = []
    # Cartas normales
    for color in colores:
        for numero in numeros:
            mazo_nuevo.append(f"{color} {numero}")
    # Comodines de color
    for color in colores:
        for comodin in comodines:
            mazo_nuevo.append(f"{color} {comodin}")
    # Comodines supremos (4 de cada uno)
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
        print("\n¡Se acabaron las cartas para comer! Revolviendo el pozo de descarte...")
        mazo.extend(pozo_descarte)
        pozo_descarte.clear()
        random.shuffle(mazo)

def es_jugada_valida(carta_elegida, carta_mesa):
    if "+4" in carta_elegida or "Cambio de color" in carta_elegida:
        return True
    if "+4" in carta_mesa or "Cambio de color" in carta_mesa:
        return True
        
    detalles_elegida = carta_elegida.split()
    detalles_mesa = carta_mesa.split()
    
    return detalles_elegida[0] == detalles_mesa[0] or detalles_elegida[1] == detalles_mesa[1]

def aplicar_efecto_comodin(carta_jugada, mano_rival, mazo, pozo_descarte):
    if "+2" in carta_jugada:
        print("¡Toma 2! El rival roba 2 cartas.")
        for _ in range(2):
            rellenar_mazo_si_vacio(mazo, pozo_descarte)
            if mazo: mano_rival.append(mazo.pop())
    elif "+4" in carta_jugada:
        print("¡SÚPER GOLPE! El rival roba 4 cartas.")
        for _ in range(4):
            rellenar_mazo_si_vacio(mazo, pozo_descarte)
            if mazo: mano_rival.append(mazo.pop())
    elif "bloqueo" in carta_jugada or "Reversa" in carta_jugada:
        print("¡Turno saltado! Juegas otra vez.")
        return True 
    return False

# ==========================================
# 3. INTERFAZ Y TURNOS
# ==========================================
def mostrar_interfaz(mano_jugador, mano_pc, carta_mesa):
    print("\n" + "="*40)
    print(f"Cartas de la PC: {len(mano_pc)}") 
    print("-"*40)
    print(f"CARTA EN LA MESA: [ {carta_mesa} ]")
    print("-"*40)
    print("TUS CARTAS:")
    for indice, carta in enumerate(mano_jugador):
        print(f" {indice} -> {carta}")
    print("="*40 + "\n")

def turno_jugador(mano_jugador, mano_pc, mazo, pozo_descarte, carta_mesa):
    print("\n--- TU TURNO ---")
    mostrar_interfaz(mano_jugador, mano_pc, carta_mesa)
    
    while True:
        opcion = input("Elige el número de tu carta, o escribe 'comer': ").strip()
        
        if opcion.lower() == "comer":
            rellenar_mazo_si_vacio(mazo, pozo_descarte)
            if mazo:
                nueva_carta = mazo.pop()
                mano_jugador.append(nueva_carta)
                print(f"Robaste: {nueva_carta}")
            return carta_mesa, False
            
        if opcion.isdigit() and 0 <= int(opcion) < len(mano_jugador):
            carta_elegida = mano_jugador[int(opcion)]
            
            if es_jugada_valida(carta_elegida, carta_mesa):
                print(f"\nJugaste: {carta_elegida}")
                mano_jugador.remove(carta_elegida)
                pozo_descarte.append(carta_mesa)
                
                if "+4" in carta_elegida or "Cambio de color" in carta_elegida:
                    nuevo_color = input("Elige nuevo color (Rojo, Amarillo, Verde, Azul): ").strip().capitalize()
                    if nuevo_color not in ["Rojo", "Amarillo", "Verde", "Azul"]: nuevo_color = "Rojo"
                    carta_mesa = f"{nuevo_color} Comodín"
                else:
                    carta_mesa = carta_elegida
                
                salta_rival = aplicar_efecto_comodin(carta_elegida, mano_pc, mazo, pozo_descarte)
                return carta_mesa, salta_rival
            else:
                print("Esa carta no coincide con la mesa.")
        else:
            print("Número o comando inválido.")

def turno_pc_completo(mano_pc, mano_jugador, mazo, pozo_descarte, carta_mesa):
    print("\n--- TURNO DE LA PC ---")
    
    for carta in mano_pc:
        if es_jugada_valida(carta, carta_mesa):
            print(f"La PC jugó: {carta}")
            mano_pc.remove(carta)
            pozo_descarte.append(carta_mesa)
            
            if "+4" in carta or "Cambio de color" in carta:
                nuevo_color = random.choice(["Rojo", "Amarillo", "Verde", "Azul"])
                print(f"La PC cambió el color a: {nuevo_color}")
                carta_mesa = f"{nuevo_color} Comodín"
            else:
                carta_mesa = carta
                
            salta_jugador = aplicar_efecto_comodin(carta, mano_jugador, mazo, pozo_descarte)
            return carta_mesa, salta_jugador
            
    # Si no tiene cartas válidas, come
    rellenar_mazo_si_vacio(mazo, pozo_descarte)
    if mazo:
        nueva_carta = mazo.pop()
        mano_pc.append(nueva_carta)
        print("La PC no tenía cartas válidas y robó una.")
    return carta_mesa, False

# ==========================================
# 4. BUCLE PRINCIPAL DEL JUEGO
# ==========================================
def jugar_uno():
    print("¡BIENVENIDO AL UNO EN TERMINAL, MIERDA!")
    mazo = crearmazo()
    mano_jugador, mano_pc = repartir_manos(mazo)
    pozo_descarte = []
    
    # Aseguramos que la primera carta de la mesa no sea un comodín supremo para empezar limpios
    carta_mesa = mazo.pop()
    while "+4" in carta_mesa or "Cambio de color" in carta_mesa:
        mazo.insert(0, carta_mesa)
        carta_mesa = mazo.pop()
        
    turno = 0 # 0 = Jugador, 1 = PC
    
    while len(mano_jugador) > 0 and len(mano_pc) > 0:
        if turno == 0:
            carta_mesa, salta_pc = turno_jugador(mano_jugador, mano_pc, mazo, pozo_descarte, carta_mesa)
            if not salta_pc: turno = 1
        else:
            carta_mesa, salta_jugador = turno_pc_completo(mano_pc, mano_jugador, mazo, pozo_descarte, carta_mesa)
            if not salta_jugador: turno = 0
            
    if len(mano_jugador) == 0:
        print("\n¡GANASTE EL JUEGO, MIERDA! 🏆")
    else:
        print("\nLa PC te ganó. Más suerte para la próxima. 🤖")

# Arrancar el juego
if __name__ == "__main__":
    jugar_uno()
