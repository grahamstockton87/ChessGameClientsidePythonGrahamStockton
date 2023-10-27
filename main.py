import threading
import pygame
from Button import Button
from Text import Text
from actor import actor_at_tile
from actor import get_direction
from globals import tile_at, update_board
from globals import initilize_actors_list, initialize_tiles_list, clip, is_move_valid, is_inside_box, get_actor_index_from_id
from vec2 import vec2
import time
import json
import socket


class Socket:
    def __init__(self):
        self.serverAddress = None
        self.clientSocket = None
        self.online = False
        self.server_address = ('192.168.1.129', 27021)
        #self.server_address = ('23.241.31.105', 27022)
        self.exit_flag = False

    def stop_thread(self):
        self.online = False

    def connect_client_to_server(self):
        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.connect(self.server_address)
            self.online = True
            print("Connected to the server.")
        except Exception as e:
            print("Could not Connect. Entering Offline Mode", e)
            self.online = False

    def run_socket(self):
        global can_start_game
        self.connect_client_to_server()
        global white_turn, player_white, tiles_list, actors_list, game_over, scale
        received_data = None
        data = None
        while self.online:
            try:
                data = self.clientSocket.recv(1024)
            except TimeoutError:
                pass  # Ignore the TimeoutError and continue the loop
            except ConnectionResetError:
                print("Connection reset by server. Server may have gone down or disconnected.")
                self.clientSocket.close()
                self.online = False
                break
            try:
                received_data = data.decode("utf-8")
                if len(received_data) == 1:
                    if received_data[0] == str(0):
                        player_white = False
                        can_start_game = True
                    elif received_data[0] == str(1):
                        player_white = True
                        can_start_game = True
                elif len(received_data) == 4 and received_data == "pass":
                    print("Recieved Data", received_data)
                    self.clientSocket.send("6969696".encode())
                    print("sent")
                else:
                    data_dict = json.loads(received_data)
                    white_turn = bool(data_dict["white_turn"])
                    received_id = data_dict["id"]
                    actor_index = get_actor_index_from_id(actors_list, received_id)
                    if not actors_list[actor_index].has_moved:
                        pos_x = int(data_dict["x"])
                        pos_y = int(data_dict["y"])
                        actor_pos_x = int(data_dict["x"] * scale)
                        actor_pos_y = int(data_dict["y"] * scale)
                        destination_tile = tile_at(vec2(pos_x, pos_y), tiles_list)
                        if destination_tile.state == 1:
                            actor_to_be_removed = actor_at_tile(destination_tile, actors_list, scale)
                            if actor_to_be_removed:
                                actors_list.remove(actor_to_be_removed)
                                if actor_to_be_removed.behavior == 6:
                                    game_over = True
                        actors_list[actor_index].pos.x = actor_pos_x
                        actors_list[actor_index].pos.y = actor_pos_y
                        update_board(tiles_list, actors_list, scale)
            except Exception as e:
                print("Error while parsing JSON:", e, " Data ", received_data)
        time.sleep(0.1)

    def send_server(self, actor_moved):
        if self.online and self.clientSocket is not None:
            actor_moved.tile_pos = actor_moved.pos / scale
            actor_moved_json = {"id": actor_moved.id, "pos": {"x": actor_moved.tile_pos.x, "y": actor_moved.tile_pos.y}}
            # Serialize the list of JSON objects to a JSON-formatted string
            write_json_data = json.dumps(actor_moved_json, indent=4)
            try:
                self.clientSocket.send(write_json_data.encode())
                # print("sent: ", write_json_data.encode())
            except Exception as e:
                print(e)


# -----------------------------FUNCTIONS-----------------------------
# ------------------------------------------PYGAME AND WINDOW SETUP-----------------------------------------------------
white_turn = True
scale = 90
game_over = False
player_white = True
clientSocket = None
can_start_game = False

pygame.init()

actors_list_json = []

actors_list = initilize_actors_list(scale)
tiles_list = initialize_tiles_list(scale=scale)

update_board(tiles_list, actors_list, scale)


# load chess piece images here

# --------------------------------------- MAIN LOOP --------------------------------------------------------------------
def main_loop():
    pygame.mixer.init()

    global tiles_list
    global actors_list
    global white_turn
    global player_white
    global game_over
    global clientSocket
    global can_start_game

    starting_actor = None

    # Load move sound
    move_sound = pygame.mixer.Sound("Audio/pawnmove.mp3")

    # theme sound
    theme_sound = pygame.mixer.Sound("Audio/epic.mp3")
    theme_sound.set_volume(0.1)
    theme_sound.play(10)

    theme_sound2 = pygame.mixer.Sound("Audio/chill.mp3")
    theme_sound2.set_volume(0.1)

    # Set the size of the window
    window_size = (900, 750)
    # screen = pygame.display.set_mode(window_size)
    screen = pygame.display.set_mode(window_size)

    # Set the title of the window
    pygame.display.set_caption("Chess")

    # pygame.display.set_window_position(0, 0)
    # Initialize the clock
    clock = pygame.time.Clock()

    board_background = pygame.image.load("Images/board.png")
    board_background = pygame.transform.scale(board_background, (scale * 8, scale * 8))

    # Turn Text
    turn_font = pygame.font.SysFont("Arial", 50)
    turn_text = "White Turn!"
    turn_text_color = (0, 0, 0)
    turn_text_surface = turn_font.render(turn_text, True, (255, 255, 255))

    move_text = Text(pos=vec2(scale * 8 + 10, 600), text="Move:", font_name="Arial", font_size=60, color=(255, 255, 255))

    start_button = Button(button_size=vec2(300, 300), button_pos=vec2(window_size[0] / 2, window_size[1] / 2), text="START", text_color=(255, 255, 255),
                          font_name="Arial", button_color=(255, 0, 0), font_size=90)

    start_button.center_at(window_size)

    intro_text = Text(pos=vec2(scale * 8 + 10, 200), text="Chess Game by Graham Stockton", font_name="Times New Roman", font_size=90, color=(255, 255, 255))

    white_text = Text(pos=vec2(scale * 8 + 10, 200), text="Player White", font_name="Arial", font_size=35, color=(255, 255, 255))
    black_text = Text(pos=vec2(scale * 8 + 10, 300), text="Player Black", font_name="Arial", font_size=35, color=(0, 0, 0))
    starting_color_text = "none"
    if player_white:
        starting_color_text = "White"
    else:
        starting_color_text = "Black"

    player_turn_start = Text(pos=vec2(scale * 8 + 10, 150), text=starting_color_text, font_name="Arial", font_size=40, color=(255, 255, 255))

    mute_button = Button(button_size=vec2(300, 50), button_pos=vec2(scale * 8 + 10, 400), text="MUTE", text_color=(255, 255, 255), font_name="Arial",
                         button_color=(100, 100, 100), font_size=40)
    god_button = Button(button_size=vec2(300, 50), button_pos=vec2(scale * 8 + 10, 480), text="GOD MODE", text_color=(255, 255, 255), font_name="Arial",
                        button_color=(100, 100, 100), font_size=40)

    # 1=pawn,2=rooke,3=knight,4=bishop,5=queen,6=king

    dead_images_list_white = [pygame.image.load("Images/dead_pieces/w_pawn_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/w_rook_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/w_knight_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/w_bishop_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/w_queen_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/w_king_png_128px.png")]
    dead_images_list_black = [pygame.image.load("Images/dead_pieces/b_pawn_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/b_rook_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/b_knight_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/b_bishop_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/b_queen_png_128px.png"),
                              pygame.image.load("Images/dead_pieces/b_king_png_128px.png")]

    # Resize images and update the lists
    for i in range(len(dead_images_list_white)):
        dead_images_list_white[i] = pygame.transform.scale(dead_images_list_white[i], (35, 35))

    for i in range(len(dead_images_list_black)):
        dead_images_list_black[i] = pygame.transform.scale(dead_images_list_black[i], (35, 35))

    # ---------------------------------CHESS PIECES and TILES SETUP---------------------------------------------------------

    starting_screen = False
    mute = False
    move_valid = False
    starting_tile = None

    actor_dead_list_white = []
    actor_dead_list_black = []

    god_mode = False

    redo_list = []

    game_over_text = Text(pos=vec2(0, 0), text="GAME OVER", font_name="Arial", font_size=200, color=(255, 0, 0))

    while True:
        # Receive data
        x, y = pygame.mouse.get_pos()
        mouse_position = vec2(x, y)
        clipped_mouse = vec2(int(clip(mouse_position.x, scale) / scale), int(clip(mouse_position.y, scale) / scale))
        if white_turn:
            turn_text_surface = turn_font.render("White Turn", True, (255, 255, 255))
        else:
            turn_text_surface = turn_font.render("Black Turn", True, (0, 0, 0))
            # receive_data(clientSocket)
        # Handle event
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.button.collidepoint(event.pos):
                    starting_screen = False
                if is_inside_box(mute_button.button_pos, mute_button.size, mouse_position):
                    mute_button.on = not mute_button.on
                if is_inside_box(god_button.button_pos, god_button.size, mouse_position):
                    god_button.on = not god_button.on

                if not starting_screen and can_start_game:
                    starting_tile = tile_at(clipped_mouse, tiles_list)
                    if starting_tile is not None and starting_tile.state:  # Tile with an Actor
                        starting_actor = actor_at_tile(starting_tile, actors_list, scale)
                        starting_tile.state = False  # Make tile empty
                        if (starting_actor.white and white_turn and player_white) or (not starting_actor.white and not white_turn and not player_white):
                            starting_actor.moving = True
                            starting_actor.can_move = True
                        else:
                            starting_actor.moving = False
                            starting_actor.can_move = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button click
                    if starting_actor is not None and starting_actor.can_move and x <= 800 and y <= 800:
                        destination_tile = tiles_list[clipped_mouse.x][clipped_mouse.y]
                        if destination_tile.pos.x == starting_tile.pos.x and destination_tile.pos.y == starting_tile.pos.y:
                            starting_actor.can_move = False
                            starting_actor.moving = False
                            move_valid = False  # return
                            starting_actor.can_move = False

                        starting_actor.number_of_tiles_moved = get_direction(starting_tile, destination_tile, scale)  # returns
                        starting_actor.direction = vec2(abs(starting_actor.number_of_tiles_moved.x),
                                                        abs(starting_actor.number_of_tiles_moved.y))

                        if starting_actor.can_move:
                            move_valid = is_move_valid(starting_actor)

                        destination_actor = actor_at_tile(destination_tile, actors_list, scale)
                        clipped_tile_pos = starting_tile.pos / scale

                        operate_list = [starting_tile, destination_tile, actors_list, tiles_list, actor_dead_list_white,
                                        actor_dead_list_black, destination_actor, god_mode, scale]

                        if destination_actor is not None:
                            if starting_actor.behavior == 6 and destination_actor.behavior == 2:
                                if not tiles_list[clipped_tile_pos.x + 1][clipped_tile_pos.y].state and not \
                                        tiles_list[clipped_tile_pos.x + 2][clipped_tile_pos.y].state \
                                        or not tiles_list[clipped_tile_pos.x - 1][clipped_tile_pos.y].state and not \
                                        tiles_list[clipped_tile_pos.x - 2][
                                            clipped_tile_pos.y].state \
                                        and not tiles_list[clipped_tile_pos.x - 3][clipped_tile_pos.y].state:
                                    starting_actor.can_castle = True
                                else:
                                    starting_actor.can_castle = False

                        if move_valid or starting_actor.can_castle or god_mode:
                            actor_dead_list_white, actor_dead_list_black, game_over = starting_actor.operate(operate_list)
                            if starting_actor.has_moved:
                                white_turn = not white_turn
                            client_socket.send_server(starting_actor)

                            redo_list.append(starting_actor)
                            if starting_actor.behavior == 1 and (starting_actor.white and starting_actor.pos.y == 0) or (
                                    not starting_actor.white and starting_actor.pos.y == 7):
                                starting_actor.upgrade_to_queen()
                            update_board(tiles_list, actors_list, scale)

                            move_sound.play()
                        else:
                            starting_actor.return_to_tile(starting_tile)  # Illegal move

                        starting_actor.type_string_name = starting_actor.get_type_string_name()
                        tile_pos = (int(destination_tile.pos.x / scale + 1), int(destination_tile.pos.y / scale))

                        move_text.text = "Move: " + starting_actor.type_string_name + str(tile_pos)

                        update_board(tiles_list, actors_list, scale)
                starting_actor = None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                white_turn = not white_turn
                update_board(tiles_list, actors_list, scale)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                white_turn = not white_turn
                update_board(tiles_list, actors_list, scale)

        # BACKGROUND ALBEDO
        screen.fill((8, 69, 25))  # Black

        if mute:
            theme_sound.stop()
            theme_sound2.stop()

        if starting_screen:

            start_button.draw_button(screen)

            intro_text.draw()

            theme_sound.play(1000)
        else:
            theme_sound.stop()

            pygame.display.get_surface().blit(board_background, (0, 0))

            # Update the actors' positions
            actors_list.sort(key=lambda actor: actor.moving)
            for actor in actors_list:
                if actor.moving:
                    actor.pos = vec2(mouse_position.x, mouse_position.y) - vec2(scale / 2, scale / 2)
                actor.draw_actor()

            pygame.display.get_surface().blit(turn_text_surface, (scale * 8 + 10, 10))  # Turn text
            move_text.draw()

            white_text.draw()
            black_text.draw()
            player_turn_start.draw()

            if mute_button.on:
                mute_button.button_text.text = "Mute On"
                mute = True
                server_bool = True
            else:
                mute_button.button_text.text = "Mute Off"
                mute = False

            if god_button.on:
                god_button.button_text.text = "God Mode On"
                god_mode = True
            else:
                god_button.button_text.text = "God Mode Off"
                god_mode = False

            mute_button.draw_button(screen)
            god_button.draw_button(screen)

            for index, x in enumerate(actor_dead_list_white):
                pygame.display.get_surface().blit(dead_images_list_white[x - 1],
                                                  (scale * 8 + white_text.pos.x, white_text.pos.y + 100))

            for index, x in enumerate(actor_dead_list_black):
                pygame.display.get_surface().blit(dead_images_list_black[x - 1],
                                                  (scale * 8 + black_text.pos.x, black_text.pos.y + 100))

            if game_over:
                game_over_text.draw()
        # Limit the frame rate
        clock.tick(60)
        # Update the display
        pygame.display.update()


main_thread = threading.Thread(target=main_loop)
main_thread.daemon = False
main_thread.start()

client_socket = Socket()
socket_thread = threading.Thread(target=client_socket.run_socket)
socket_thread.daemon = True
socket_thread.start()

socket_thread.join()  # Wait for the thread to finish
main_thread.join()
