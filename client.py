import socket
import pickle
import pygame

# Dimensiones de la ventana
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Dirección y puerto del servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

# Color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Tamaño de la cuadrícula
GRID_SIZE = 50
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE

def draw_grid(screen, map_grid):
    for y, row in enumerate(map_grid):
        for x, cell in enumerate(row):
            color = WHITE if cell == 0 else BLACK
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cliente")

    # Inicializar el socket del cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    print("Conexión establecida con el servidor.")

    clock = pygame.time.Clock()

    # Bucle principal del cliente
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Recibir datos del servidor
        data = client_socket.recv(1024)
        if not data:
            break

        # Decodificar los datos recibidos
        decoded_data = pickle.loads(data)

        # Obtener la información de la grilla del mapa
        map_grid = decoded_data["map_grid"]

        # Dibujar la grilla en la pantalla
        screen.fill(WHITE)
        draw_grid(screen, map_grid)
        pygame.display.flip()

        clock.tick(60)

    # Cerrar la conexión al salir
    client_socket.close()

if __name__ == "__main__":
    main()
