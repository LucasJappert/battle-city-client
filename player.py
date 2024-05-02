from datetime import datetime
import socket
import pickle
import sys
import pygame
import threading
import random
from enums import MOVEMENTS
import tkinter as tk
from tkinter import simpledialog


# Dirección y puerto del servidor
DEFAULT_SERVER_HOST = '192.168.31.148'
SERVER_PORT = 5555

# Color
GRAY = (55, 55, 55)
BLACK = (0, 0, 0)

# Tamaño de la cuadrícula
GRID_SIZE = 20
CELL_SIZE = 32

# Dimensiones de la ventana
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

def ask_for_text():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana de Tkinter
    user_input = simpledialog.askstring(title="Input", prompt="Ingrese la IP interna host:", initialvalue=DEFAULT_SERVER_HOST)
    return user_input

class GridObject:
    position: tuple[int, int] = (0, 0)
    id: str = "player"
    max_hp: int = 100
    current_hp: int = 100
    
    def __init__(self, position: tuple[int, int] = (0, 0), id: str = "player", max_hp: int = 100, current_hp: int = 100):
        self.position = position
        self.id = id
        self.max_hp = max_hp
        self.current_hp = current_hp
    
class GridBlock:
    grid_object: GridObject | None = None
    position: tuple[int, int] = (0, 0)
    
class Game:
    map_grid: list[list[GridBlock]] = [[GridBlock() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    @staticmethod
    def DRAW_GRID(screen):
        for y, row in enumerate(Game.map_grid):
            for x, cell in enumerate(row):
                color = GRAY if cell.grid_object is None else BLACK
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                
    @staticmethod
    def UPDATE_GRID(x, y, grid_object: GridObject):
        Game.map_grid[y][x].grid_object = grid_object
    
class MyPlayer:
    my_socket: socket.socket | None = None

def main():
    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
    pygame.display.set_caption("Cliente")

    # Inicializar el socket del cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        try:
            text = ask_for_text()
            client_socket.connect((text, SERVER_PORT))
            break
        except Exception as e:
            print(e)
    MyPlayer.my_socket = client_socket

    print("Conexión establecida con el servidor.")
    messages_thread = threading.Thread(target=messages_receiver, args=(client_socket,))
    messages_thread.start()
    
    clock = pygame.time.Clock()

    # Bucle principal del cliente
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                ask_movement(MOVEMENTS.LEFT.value)
            elif keys[pygame.K_d]:
                ask_movement(MOVEMENTS.RIGHT.value)
            elif keys[pygame.K_w]:
                ask_movement(MOVEMENTS.UP.value)
            elif keys[pygame.K_s]:
                ask_movement(MOVEMENTS.DOWN.value)

        # Dibujar la grilla en la pantalla
        screen.fill(GRAY)
        Game.DRAW_GRID(screen)
        # scale_and_blit(screen)
        pygame.display.flip()

        clock.tick(60)

    # Cerrar la conexión al salir
    client_socket.close()
   

def scale_and_blit(screen: pygame.Surface):
    # Escalar la pantalla
    screen_resized = pygame.transform.scale(screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
    # Dibujar la pantalla escalada
    screen.blit(screen_resized, (0, 0))
    # Actualizar la pantalla
    pygame.display.flip()
    
def messages_receiver(client_socket):
    while True:
        try:
            message = client_socket.recv(1024 * 1024)
            # Decodificar los datos recibidos
            decoded_data = pickle.loads(message)
            if "map_grid" in decoded_data:
                Game.map_grid = decoded_data["map_grid"]
            # print(len(decoded_data))
        except socket.error as e:
            print(e)
            return 
    
last_movement: datetime = datetime.now()
def ask_movement(movement: int):
    global last_movement
    if (datetime.now() - last_movement).total_seconds() < 0.1:
        return
    last_movement = datetime.now()
    data = {
        "movement": movement
    }
    MyPlayer.my_socket.send(pickle.dumps(data))


if __name__ == "__main__":
    main()