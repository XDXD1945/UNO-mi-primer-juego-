import random

def crearmazo():
    colores = ["Rojo", "Amarillo", "Verde", "Azul"]
    numeros = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    comodines = ["+2", "Reversa", "bloqueo"]
    comodines_supremos = ["+4", "Cambio de color"]
    
    mazo_nuevo = [] 

    # 1. Creamos las cartas normales (Color + Número)
    for color in colores:
        for numero in numeros:
            mazo_nuevo.append(f"{color} {numero}")

    # 2. Creamos los comodines con color (Rojo +2, Azul Reversa, etc.)
    for color in colores:
        for comodin in comodines:
            mazo_nuevo.append(f"{color} {comodin}")

    # 3. Creamos los comodines supremos (estos no tienen color propio)
    # En el UNO real hay 4 de cada uno, así que los repetimos 4 veces
    for i in range(4):
        for supremo in comodines_supremos:
            mazo_nuevo.append(supremo)

    return mazo_nuevo


def repartir_manos(mazo):
    random.shuffle(mazo) # Revolvemos el mazo de mierda
    
    mano_jugador = []
    mano_pc = []
    
    # RE TO: Usa un bucle 'for' que se repita 7 veces usando range(7)
    # para meter cartas a la mano_jugador con .append(mazo.pop())
    # Y luego otro bucle igual para la mano_pc.
    for i in range(7):
        mano_jugador.append(mazo.pop())
        
    for i in range(7):
        mano_pc.append(mazo.pop())

    
    return mano_jugador, mano_pc


def mostrar_interfaz(mano_jugador, mano_pc, carta_centro):
    print("\n" + "="*30)
    # Mostramos cuántas cartas tiene la PC (¡sin hacer trampa y mostrar cuáles son!)
    print(f"Cartas de la PC: {len(mano_pc)}") 
    print("-"*30)
    # Mostramos la carta que está en la mesa
    print(f"CARTA EN LA MESA: [ {carta_centro} ]")
    print("-"*30)
    # Mostramos las cartas del jugador con un número para que las elija
    print("TUS CARTAS:")
    for indice, carta in enumerate(mano_jugador):
        print(f"{indice} -> {carta}")
    print("="*30 + "\n")


def es_jugada_valida(carta_elegida, carta_mesa):
    # Si es un comodín supremo, se puede jugar siempre
    if "+4" in carta_elegida or "Cambio de color" in carta_elegida:
        return True
        
    # Separamos las palabras de las cartas para revisar color y tipo
    # "Rojo 7".split() nos da una lista: ["Rojo", "7"]
    detalles_elegida = carta_elegida.split()
    detalles_mesa = carta_mesa.split()
    
    color_elegido = detalles_elegida[0]
    tipo_elegido = detalles_elegida[1]
    
    color_mesa = detalles_mesa[0]
    tipo_mesa = detalles_mesa[1]
    
    # RE TO: Escribe el 'if' que revise si el color_elegido es igual al color_mesa 
    # O SI el tipo_elegido es igual al tipo_mesa. Si se cumple, devuelve True.
    # Si no se cumple nada, devuelve False.
    if color_elegido == color_mesa or tipo_elegido == tipo_mesa:
        return True
        
    return False

# Suponiendo que ya creamos el mazo, repartimos y sacamos la carta_mesa...

jugando = True

while jugando:
    # 1. Mostramos la pantalla
    mostrar_interfaz(mano_jugador, mano_pc, carta_mesa)
    
    # 2. El jugador elige qué hacer
    opcion = input("Elige el número de tu carta para jugarla, o escribe 'comer' para sacar una: ")
    
    if opcion.lower() == "comer":
        if len(mazo) == 0:
            print("¡La baraja se acabó! (Aquí meteremos tu idea de revolver el descarte luego)")
        else:
            nueva_carta = mazo.pop()
            mano_jugador.append(nueva_carta)
            print(f"Robaste: {nueva_carta}")
            
    else:
        # Convertimos la opción en número para sacar la carta de la lista
        indice = int(opcion)
        carta_seleccionada = mano_jugador[indice]
        
        # ¡Usamos tu función mágica!
        if es_jugada_valida(carta_seleccionada, carta_mesa):
            print(f"Jugaste: {carta_seleccionada}")
            carta_mesa = carta_seleccionada # La carta de la mesa cambia
            mano_jugador.remove(carta_seleccionada) # La quitas de tu mano
        else:
            print("¡Esa jugada no vale, no seas tramposo!")
            
    # Condición para ganar
    if len(mano_jugador) == 0:
        print("¡GANASTE EL JUEGO, MIERDA! 🏆")
        jugando = False


def turno_pc(mano_pc, mazo, carta_mesa):
    print("\n--- TURNO DE LA PC ---")
    
    # 1. La PC revisa si tiene alguna carta que pueda jugar
    for carta in mano_pc:
        if es_jugada_valida(carta, carta_mesa):
            print(f"La PC jugó: {carta}")
            carta_mesa = carta          # La carta de la mesa cambia
            mano_pc.remove(carta)       # La PC suelta la carta de su mano
            return carta_mesa           # Terminamos el turno devolviendo la nueva carta de la mesa
            
    # 2. Si el bucle termina y la PC no devolvió nada, significa que no tuvo ninguna carta válida.
    # Le toca comer.
    if len(mazo) > 0:
        nueva_carta = mazo.pop()
        mano_pc.append(nueva_carta)
        print("La PC no tenía cartas válidas y robó una.")
    else:
        print("La PC quería robar, pero el mazo está vacío.")
        
    return carta_mesa # Devolvemos la misma carta de la mesa porque no cambió

def rellenar_mazo_si_vacio(mazo, pozo_descarte):
    if len(mazo) == 0:
        print("\n¡Se acabaron las cartas para comer! Revolviendo el pozo de descarte...")
        
        # Pasamos las cartas del descarte al mazo entero
        mazo.extend(pozo_descarte)
        
        # Limpiamos el pozo de descarte para que quede vacío otra vez
        pozo_descarte.clear()
        
        # Revolvemos el mazo con el truco que ya conoces
        random.shuffle(mazo)


def aplicar_efecto_comodin(carta_jugada, mano_rival, mazo, pozo_descarte):
    # Si la carta tiene un "+2", el rival se traga 2 cartas
    if "+2" in carta_jugada:
        print("¡Toma 2! El rival roba 2 cartas.")
        for _ in range(2):
            rellenar_mazo_si_vacio(mazo, pozo_descarte)
            if mazo: mano_rival.append(mazo.pop())

    # Si es un "+4", el rival se traga 4 cartas
    elif "+4" in carta_jugada:
        print("¡SÚPER GOLPE! El rival roba 4 cartas.")
        for _ in range(4):
            rellenar_mazo_si_vacio(mazo, pozo_descarte)
            if mazo: mano_rival.append(mazo.pop())
            
    # Si es un bloqueo o reversa (en 1 vs 1, la reversa funciona como bloqueo)
    elif "bloqueo" in carta_jugada or "Reversa" in carta_jugada:
        print("¡Turno saltado! Juegas otra vez.")
        return True # Devolvemos True para indicar que se salta el turno del rival
        
    return False # Turno normal, no se salta al rival


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
            return carta_mesa, False # No cambia la mesa, turno normal
            
        # Validar que el usuario no escriba cualquier pendejada y meta un número válido
        if opcion.isdigit() and 0 <= int(opcion) < len(mano_jugador):
            indice = int(opcion)
            carta_elegida = mano_jugador[indice]
            
            if es_jugada_valida(carta_elegida, carta_mesa):
                print(f"Jugaste: {carta_elegida}")
                mano_jugador.remove(carta_elegida)
                pozo_descarte.append(carta_mesa) # La vieja va al descarte
                
                # REGLA DE CAMBIO DE COLOR: Si es comodín supremo, pides el nuevo color
                if "+4" in carta_elegida or "Cambio de color" in carta_elegida:
                    nuevo_color = input("Elige nuevo color (Rojo, Amarillo, Verde, Azul): ").strip().capitalize()
                    # Transformamos la carta de la mesa en ese color para que la PC pueda jugar
                    carta_mesa = f"{nuevo_color} Comodín"
                else:
                    carta_mesa = carta_elegida
                
                # Aplicamos castigos a la PC si usaste un comodín
                salta_rival = aplicar_efecto_comodin(carta_elegida, mano_pc, mazo, pozo_descarte)
                
                return carta_mesa, salta_rival
            else:
                print("Esa carta no coincide con la mesa. ¡Intenta otra!")
        else:
            print("Opción inválida. Pon un número de tu lista.")

# ... (Repartición inicial y preparación de variables) ...

turno = 0 # 0 = Jugador, 1 = PC
jugando = True

while jugando:
    if len(mano_jugador) == 0:
        print("¡GANASTE EL JUEGO, MIERDA! 🏆")
        break
    if len(mano_pc) == 0:
        print("La PC ganó. F por ti. 🤖")
        break

    if turno == 0:
        # Juegas tú. La función nos dice si la mesa cambió y si bloqueaste a la PC
        carta_mesa, salta_pc = turno_jugador(mano_jugador, mano_pc, mazo, pozo_descarte, carta_mesa)
        if not salta_pc:
            turno = 1 # Si no la bloqueaste, ahora le toca a la PC
    else:
        # Juega la PC (A la PC también le aplicamos su función para ver si te bloquea)
        # *Nota: Habría que adaptar el turno_pc de la misma forma que el del jugador*
        carta_mesa, salta_jugador = turno_pc_adaptado(mano_pc, mano_jugador, mazo, pozo_descarte, carta_mesa)
        if not salta_jugador:
            turno = 0 # Si no te bloqueó, te toca a ti
