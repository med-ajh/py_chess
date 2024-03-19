import pygame
import socket
import threading
import pickle

# Constants
WIDTH, HEIGHT = 800, 800
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
FPS = 30

# Chessboard
board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Networking
host = "127.0.0.1"
port = 12345
server_address = (host, port)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Function to receive data from the server
def receive_data():
    while True:
        data, addr = client.recvfrom(4096)
        try:
            received_data = pickle.loads(data)
            handle_received_data(received_data)
        except pickle.UnpicklingError:
            pass

# Function to handle received data
def handle_received_data(received_data):
    if "board" in received_data:
        update_board(received_data["board"])
    elif "message" in received_data:
        print(received_data["message"])

# Function to update the chessboard
def update_board(new_board):
    global board
    board = new_board

# Function to send data to the server
def send_data(data):
    client.sendto(pickle.dumps(data), server_address)

# Main game loop
def game_loop():
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN and my_turn:
                col = event.pos[0] // (WIDTH // 8)
                row = event.pos[1] // (HEIGHT // 8)
                send_data({"type": "move", "from": selected_piece, "to": (row, col)})

        draw_board()
        clock.tick(FPS)
        pygame.display.flip()

# Function to draw the chessboard
def draw_board():
    screen.fill(WHITE)

    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, [col * WIDTH // 8, row * HEIGHT // 8, WIDTH // 8, HEIGHT // 8])

            piece = board[row][col]
            if piece:
                piece_image = pygame.image.load(f"images/{piece}.png")
                piece_image = pygame.transform.scale(piece_image, (WIDTH // 8, HEIGHT // 8))
                screen.blit(piece_image, (col * WIDTH // 8, row * HEIGHT // 8))

# Function to handle move validation
def is_valid_move(piece, from_pos, to_pos):
    # Add your move validation logic here
    return True

# Function to handle the chess game logic
def chess_logic():
    global my_turn
    my_turn = False
    global selected_piece

    while True:
        if my_turn:
            move_input = input("Enter your move (e.g., 'e2 e4'): ").split()
            if len(move_input) == 2:
                from_pos = (int(move_input[0][1]) - 1, ord(move_input[0][0]) - ord("a"))
                to_pos = (int(move_input[1][1]) - 1, ord(move_input[1][0]) - ord("a"))
                piece = board[from_pos[0]][from_pos[1]]

                if is_valid_move(piece, from_pos, to_pos):
                    send_data({"type": "move", "from": from_pos, "to": to_pos})
                    my_turn = False
                else:
                    print("Invalid move. Try again.")
        else:
            pygame.time.wait(100)

# Start the networking thread
network_thread = threading.Thread(target=receive_data)
network_thread.start()

# Start the game loop
game_thread = threading.Thread(target=game_loop)
game_thread.start()

# Start the chess logic thread
chess_logic_thread = threading.Thread(target=chess_logic)
chess_logic_thread.start()

# Initial state
selected_piece = None

# Main loop to handle user input for selecting pieces
while True:
    if not my_turn:
        pygame.time.wait(100)
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            col = event.pos[0] // (WIDTH // 8)
            row = event.pos[1] // (HEIGHT // 8)
            piece = board[row][col]

            if piece and piece.islower():
                selected_piece = (row, col)
                print(f"Selected: {chr(col + ord('a'))}{row + 1}")
            elif selected_piece and is_valid_move(board[selected_piece[0]][selected_piece[1]], selected_piece, (row, col)):
                send_data({"type": "move", "from": selected_piece, "to": (row, col)})
                selected_piece = None
                my_turn = False
