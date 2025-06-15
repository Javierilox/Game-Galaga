import pygame
import random
import os
import tkinter as tk
from tkinter import filedialog
import threading
import time

# --- Configurar ventana Tkinter oculta para elegir archivo ---
tk_root = tk.Tk()
tk_root.withdraw()

# Inicializar Pygame
pygame.init()
info = pygame.display.Info()
ANCHO, ALTO = info.current_w, info.current_h
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("Freedom Invasion")

# Rutas de recursos
IMAGENES = "imagenes"
SONIDOS = "sonidos"
MUSICA_PREDETERMINADA = os.path.join("Musica de Fondo", "AGE_2.mp3")
SEED_START_SOUND = os.path.join(SONIDOS, "seed mode.wav")
SEED_THEME_MUSIC = os.path.join("Musica de Fondo", "Gundam Wing.mp3")

# Variables globales música
ruta_musica_actual = None
musica_original = None

def cargar_imagen(nombre):
    return pygame.image.load(os.path.join(IMAGENES, nombre)).convert_alpha()

def cargar_sonido(nombre):
    return pygame.mixer.Sound(os.path.join(SONIDOS, nombre))

# Menú para elegir música, puede usarse tanto en inicio como en pausa
def menu_elegir_musica():
    global ruta_musica_actual
    opciones = ["Usar música predeterminada", "Elegir música desde el PC", "Cancelar"]
    seleccion = 0
    fuente = pygame.font.Font(None, 60)
    fuente_titulo = pygame.font.Font(None, 80)

    seleccionando = True
    while seleccionando:
        pantalla.fill((0, 0, 30))
        texto_titulo = fuente_titulo.render("Selecciona la música", True, (255, 255, 255))
        pantalla.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, ALTO // 2 - 200))

        for i, opcion in enumerate(opciones):
            color = (255, 255, 0) if i == seleccion else (255, 255, 255)
            texto = fuente.render(opcion, True, color)
            pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, ALTO // 2 - 80 + i * 70))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                elif evento.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                elif evento.key == pygame.K_RETURN:
                    if seleccion == 0:
                        ruta_musica_actual = MUSICA_PREDETERMINADA
                        seleccionando = False
                    elif seleccion == 1:
                        archivo = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg *.flac")])
                        if archivo:
                            ruta_musica_actual = archivo
                        seleccionando = False
                    else:  # Cancelar
                        pygame.quit()
                        exit()
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

# Menú pausa con opción para reanudar o cambiar música
def menu_pausa():
    fuente = pygame.font.Font(None, 50)
    fuente_titulo = pygame.font.Font(None, 80)
    pausa = True
    while pausa:
        pantalla.fill((0, 0, 0))
        texto_titulo = fuente_titulo.render("Juego en Pausa", True, (255, 255, 255))
        texto_reanudar = fuente.render("P - Reanudar", True, (255, 255, 255))
        texto_cambiar_musica = fuente.render("M - Cambiar Música", True, (255, 255, 255))
        texto_salir = fuente.render("Esc - Salir del juego", True, (255, 255, 255))

        pantalla.blit(texto_titulo, (ANCHO // 2 - texto_titulo.get_width() // 2, ALTO // 2 - 150))
        pantalla.blit(texto_reanudar, (ANCHO // 2 - texto_reanudar.get_width() // 2, ALTO // 2 - 40))
        pantalla.blit(texto_cambiar_musica, (ANCHO // 2 - texto_cambiar_musica.get_width() // 2, ALTO // 2 + 40))
        pantalla.blit(texto_salir, (ANCHO // 2 - texto_salir.get_width() // 2, ALTO // 2 + 120))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_p:
                    pausa = False
                elif evento.key == pygame.K_m:
                    menu_elegir_musica()
                    if ruta_musica_actual:
                        pygame.mixer.music.load(ruta_musica_actual)
                        pygame.mixer.music.play(-1)
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        pygame.time.Clock().tick(10)

# Cargar recursos
disparo_sonido = cargar_sonido("laser.wav")
explosion_sonido = cargar_sonido("explosion.wav")
fondo = pygame.transform.scale(cargar_imagen("fondo_1.png"), (ANCHO, ALTO))
jugador_normal_img = pygame.transform.scale(cargar_imagen("A1_1.png"), (int(ANCHO * 0.06), int(ALTO * 0.1)))
jugador_seed_activacion_img = pygame.transform.scale(cargar_imagen("SEED_MODE.png"), (int(ANCHO * 0.06), int(ALTO * 0.1)))
jugador_seed_img = pygame.transform.scale(cargar_imagen("Strike_Freedom.png"), (int(ANCHO * 0.06), int(ALTO * 0.1)))
enemigo_img = pygame.transform.scale(cargar_imagen("E1_1.png"), (int(ANCHO * 0.06), int(ALTO * 0.1)))
bala_img = pygame.transform.scale(cargar_imagen("B1_1.png"), (int(ANCHO * 0.015), int(ALTO * 0.04)))

JUGADOR_ANCHO, JUGADOR_ALTO = jugador_normal_img.get_size()
ENEMIGO_ANCHO, ENEMIGO_ALTO = enemigo_img.get_size()
BALA_ANCHO, BALA_ALTO = bala_img.get_size()

jugador_img = jugador_normal_img
jugador_x = ANCHO // 2
jugador_y = ALTO - JUGADOR_ALTO - 10
jugador_vel = 8

puntaje = 0
oleada = 1
OLEADA_ENEMIGOS = 6
enemigos = []

balas = []
bala_vel = 20
bala_cooldown = 0

# Seed Mode
total_seed_usos = 3
seed_mode_usos = total_seed_usos
seed_mode_activado = False
seed_mode_tiempo = 0
ultimo_seed_uso = -40

fuente_pequena = pygame.font.Font(None, 36)

def mostrar_puntaje():
    texto = fuente_pequena.render(f"Puntaje: {puntaje}  Oleada: {oleada}  SEED (Presiona Z): {seed_mode_usos}/{total_seed_usos}", True, (255, 255, 255))
    pantalla.blit(texto, (10, 10))

def colision(x1, y1, x2, y2):
    return ((x1 - x2)**2 + (y1 - y2)**2) < 30**2

def nueva_oleada(cantidad):
    lista = []
    for _ in range(cantidad):
        x = random.randint(0, ANCHO - ENEMIGO_ANCHO)
        y = random.randint(50, 150)
        velocidad = 3 + 0.5 * (oleada - 1)
        lista.append([x, y, velocidad, 40])
    return lista

def activar_seed_mode():
    global seed_mode_activado, seed_mode_tiempo, seed_mode_usos, jugador_img, ultimo_seed_uso, musica_original
    if seed_mode_usos > 0 and not seed_mode_activado and time.time() - ultimo_seed_uso >= 40:
        seed_mode_activado = True
        seed_mode_usos -= 1
        seed_mode_tiempo = time.time()
        ultimo_seed_uso = seed_mode_tiempo

        jugador_img = jugador_seed_activacion_img

        musica_original = ruta_musica_actual
        pygame.mixer.music.stop()

        pygame.mixer.Sound(SEED_START_SOUND).play()

        def cambiar_a_seed():
            global jugador_img
            jugador_img = jugador_seed_img
            pygame.mixer.music.load(SEED_THEME_MUSIC)
            pygame.mixer.music.play(-1)

        threading.Timer(5, cambiar_a_seed).start()

# Ejecutar menú inicio para elegir música
menu_elegir_musica()
if not ruta_musica_actual:
    ruta_musica_actual = MUSICA_PREDETERMINADA
pygame.mixer.music.load(ruta_musica_actual)
pygame.mixer.music.play(-1)

enemigos = nueva_oleada(OLEADA_ENEMIGOS)

reloj = pygame.time.Clock()
ejecutando = True
while ejecutando:
    pantalla.blit(fondo, (0, 0))

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                ejecutando = False
            if evento.key == pygame.K_z:
                activar_seed_mode()
            if evento.key == pygame.K_p:
                menu_pausa()

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and jugador_x > 0:
        jugador_x -= jugador_vel
    if teclas[pygame.K_RIGHT] and jugador_x < ANCHO - JUGADOR_ANCHO:
        jugador_x += jugador_vel

    if teclas[pygame.K_SPACE] and bala_cooldown == 0:
        if oleada >= 2:
            balas.append([jugador_x + JUGADOR_ANCHO // 4 - BALA_ANCHO // 2, jugador_y])
            balas.append([jugador_x + 3 * JUGADOR_ANCHO // 4 - BALA_ANCHO // 2, jugador_y])
        else:
            balas.append([jugador_x + JUGADOR_ANCHO // 2 - BALA_ANCHO // 2, jugador_y])
        disparo_sonido.play()
        bala_cooldown = 15

    if bala_cooldown > 0:
        bala_cooldown -= 1

    nuevas_balas = []
    for b in balas:
        if b is None:
            continue
        bx, by = b
        by -= bala_vel
        if by > 0:
            pantalla.blit(bala_img, (bx, by))
            nuevas_balas.append([bx, by])
    balas = nuevas_balas

    enemigos_a_eliminar = []
    for idx, enemigo in enumerate(enemigos):
        enemigo[0] += enemigo[2]
        if enemigo[0] <= 0 or enemigo[0] >= ANCHO - ENEMIGO_ANCHO:
            enemigo[2] *= -1
            enemigo[1] += enemigo[3]

        for bidx, b in enumerate(balas):
            if b and colision(enemigo[0], enemigo[1], b[0], b[1]):
                explosion_sonido.play()
                enemigos_a_eliminar.append(idx)
                balas[bidx] = None
                puntaje += 1
                break

        pantalla.blit(enemigo_img, (enemigo[0], enemigo[1]))

    enemigos = [e for i, e in enumerate(enemigos) if i not in enemigos_a_eliminar]
    balas = [b for b in balas if b is not None]

    if len(enemigos) == 0:
        oleada += 1
        enemigos = nueva_oleada(OLEADA_ENEMIGOS + oleada - 1)

    if seed_mode_activado and time.time() - seed_mode_tiempo > 40:
        seed_mode_activado = False
        jugador_img = jugador_normal_img
        pygame.mixer.music.load(musica_original)
        pygame.mixer.music.play(-1)

    pantalla.blit(jugador_img, (jugador_x, jugador_y))
    mostrar_puntaje()
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
