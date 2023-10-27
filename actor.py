import pygame

from vec2 import vec2


def clip(num, scale):  # clips number to 0 if less than 100
    if isinstance(num, int):
        return (num // scale) * scale if num >= 0 else ((num // scale) - 1) * scale
    elif isinstance(num, vec2):
        return vec2((num.x // scale) * scale if num.x >= 0 else ((num.x // scale) - 1) * scale,
                    (num.y // scale) * scale if num.y >= 0 else ((num.y // scale) - 1) * scale)


def game_pos_to_grid(x, scale):
    return int(x / scale)


def actor_at_tile(tile, actors_list, scale):
    for actor_x in actors_list:  # for every Actor
        clipped_actor_pos = vec2(clip(actor_x.pos.x, scale), clip(actor_x.pos.y, scale))
        if clipped_actor_pos.x == tile.pos.x and clipped_actor_pos.y == tile.pos.y:
            return actor_x


def get_direction(starting_tile, destination_tile, scale):
    return vec2(
        int((destination_tile.pos.x - starting_tile.pos.x) / scale),
        int((destination_tile.pos.y - starting_tile.pos.y) / scale)
    )


class Actor:
    def __init__(self, pos: vec2, image_path, behavior: int, white: bool, scale: int):

        self.pos = pos  # gmae chords (100,100)
        self.moving = False
        self.behavior = behavior  # 1=pawn,2=rooke,3=knight,4=bishop,5=queen,6=king
        self.first_move = True
        self.white = white
        self.direction = vec2(0, 0)  # non negative
        self.pawn_can_take = False
        self.number_of_tiles_moved = vec2(0, 0)  # includes negative
        self.gameDone = False
        self.type_string_name = self.get_type_string_name()
        self.can_castle = False
        self.can_move = False
        self.id = 0

        self.tile_pos = vec2(0, 0)
        self.has_moved = False

        # image
        self.image_path = image_path
        self.image = pygame.image.load(self.image_path)
        self.scale = scale
        self.image = pygame.transform.scale(self.image, (scale, scale))
        self.rect = self.image.get_rect()

    def get_type_string_name(self):
        type_strings = ["Pawn", "Rook", "Knight", "Bishop", "Queen", "King"]
        return type_strings[self.behavior - 1]

    def __str__(self):
        return f"({self.get_type_string_name()})"

    def update_image(self):
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (100, 100))

    def draw_actor(self):
        pygame.display.get_surface().blit(self.image, (self.pos.x, self.pos.y))

    def is_inside_box(self, box: vec2) -> object:
        if self.pos.x <= box.x < self.pos.x + 100 and self.pos.y <= box.y < self.pos.y + 100:
            return True
        else:
            return False

    def on_mouse_click(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.is_inside_box(vec2(mouse_x, mouse_y)):
            self.pos = vec2(mouse_x - 50, mouse_y - 50)

    def snap_to_tile(self, tiles_list):
        for i in range(8):
            for g in range(8):
                if self.is_inside_box(tiles_list[i][g].pos + 50):
                    self.pos = tiles_list[i][g].pos
                    tiles_list[i][g].state = True

    def actors_tile(self, tiles_list):
        return tiles_list[clip(self.pos.x, self.scale)][clip(self.pos.x, self.scale)]  # returns the tile from Actor pos

    def return_to_tile(self, starting_tile):
        self.moving = False
        self.pos = starting_tile.pos

    def move_to_tile(self, destination_tile):
        self.moving = False
        self.pos = destination_tile.pos
        self.has_moved = True

    def take_actor(self, starting_tile, destination_tile, actors_list, actor_dead_list_white, actor_dead_list_black, scale):
        actor_to_remove = actor_at_tile(destination_tile, actors_list, scale)  # Get the associated Actor from the tile
        if actor_to_remove.white:
            actor_dead_list_white.append(actor_to_remove.behavior)
            # print(actor_to_remove.get_type_string_name())
        else:
            actor_dead_list_black.append(actor_to_remove.behavior)
            # print(actor_to_remove.get_type_string_name())

        actors_list.remove(actor_to_remove)
        self.move_to_tile(destination_tile)
        starting_tile.state = False
        if actor_to_remove.behavior == 6:
            self.gameDone = True
        self.has_moved = True
        return actor_dead_list_white, actor_dead_list_black

    def operate(self, operate_list):

        starting_tile, destination_tile, actors_list, tiles_list, actor_dead_list_white, actor_dead_list_black, \
            destination_actor, god_mode, scale = operate_list
        self.has_moved = False
        if self.can_castle:
            self.moving = False
            last = starting_tile.pos.x
            if self.number_of_tiles_moved.x > 1:
                self.moving = False
                self.pos.x = destination_tile.pos.x - 100
                destination_actor.pos.x = last + 100
                self.snap_to_tile(tiles_list)
            else:
                self.moving = False
                self.pos.x = destination_tile.pos.x + 200
                destination_actor.pos.x = last - 100
                self.snap_to_tile(tiles_list)
            self.can_castle = False
            #    target_actor.pos.x = self.pos.x + 100
        elif self.behavior == 3 or self.path_is_clear(starting_tile, tiles_list):  # if path is clear or knight
            if destination_tile.state:  # If the tile is occupied
                target_actor = actor_at_tile(destination_tile, actors_list, scale)
                # If the target Actor is on the same side
                if target_actor.white == self.white:
                    self.return_to_tile(starting_tile)  # Can't take own pawn
                else:  # If the target Actor is an opponent
                    if self.behavior == 1:  # Special rules for pawn
                        if abs(self.direction.x) == abs(self.direction.y):  # If pawn can take diagonally
                            actor_dead_list_white, actor_dead_list_black = self.take_actor(starting_tile, destination_tile, actors_list, actor_dead_list_white,
                                                                                           actor_dead_list_black, scale)

                        else:  # If move isn't diagonal, can't take, return to tile
                            self.return_to_tile(starting_tile)
                    else:  # If not a pawn, take in the direction
                        actor_dead_list_white, actor_dead_list_black = self.take_actor(starting_tile, destination_tile, actors_list, actor_dead_list_white,
                                                                                       actor_dead_list_black, scale)
            else:  # If the tile is empty
                if self.behavior == 1 and abs(self.direction.x) == abs(self.direction.y):  # Pawn's diagonal move
                    self.return_to_tile(starting_tile)
                elif abs(self.direction.x) > 0 or abs(self.direction.y) > 0:  # Non-diagonal move
                    starting_tile.state = False
                    self.move_to_tile(destination_tile)
                    self.first_move = False
        else:  # If the path isn't clear
            self.return_to_tile(starting_tile)
        return actor_dead_list_white, actor_dead_list_black, self.gameDone

    def path_is_clear(self, old_tile, tiles_list):
        if self.behavior == 3 or self.pawn_can_take:  # void path clear if Actor is knight(3)
            return True
        else:
            testing_tile = None
            if self.direction.x == self.direction.y:  # if move is diagnol
                for i in range(self.direction.y):  # iterate for length in moved
                    if self.number_of_tiles_moved.x < 0 and self.number_of_tiles_moved.y < 0:  # -x-y
                        testing_tile = tiles_list[game_pos_to_grid(old_tile.pos.x, self.scale) - i][
                            game_pos_to_grid(old_tile.pos.y, self.scale) - i]
                    elif self.number_of_tiles_moved.x < 0 < self.number_of_tiles_moved.y:  # -x+y
                        testing_tile = tiles_list[game_pos_to_grid(old_tile.pos.x, self.scale) - i][
                            game_pos_to_grid(old_tile.pos.y, self.scale) + i]
                    elif self.number_of_tiles_moved.x > 0 and self.number_of_tiles_moved.y > 0:  # +x+y
                        testing_tile = tiles_list[game_pos_to_grid(old_tile.pos.x, self.scale) + i][
                            game_pos_to_grid(old_tile.pos.y, self.scale) + i]
                    elif self.number_of_tiles_moved.x > 0 > self.number_of_tiles_moved.y:  # +x-y
                        testing_tile = tiles_list[game_pos_to_grid(old_tile.pos.x, self.scale) + i][
                            game_pos_to_grid(old_tile.pos.y, self.scale) - i]
                    if testing_tile is not None and testing_tile.state:  # check if tile in search is occupied
                        self.return_to_tile(old_tile)
                        return False
                return True

            else:  # non diaganol
                if self.direction.x == 0:  # moving on y scale
                    for i in range(self.direction.y):  # iterate for every tile in direction and path
                        if self.number_of_tiles_moved.y > 0:  # +y
                            testing_tile = tiles_list[game_pos_to_grid(old_tile.pos.x, self.scale)][
                                game_pos_to_grid(old_tile.pos.y, self.scale) + i]
                        elif self.number_of_tiles_moved.y < 0:  # -y
                            testing_tile = tiles_list[game_pos_to_grid(old_tile.pos.x, self.scale)][
                                game_pos_to_grid(old_tile.pos.y, self.scale) - i]
                        if testing_tile is not None and testing_tile.state:  # check if tile in search is occupied
                            self.return_to_tile(old_tile)
                            return False
                elif self.direction.y == 0:  # moving on x dimension
                    for i in range(self.direction.x):  # iterate for every tile in direction and path
                        if self.number_of_tiles_moved.x > 0:  # +x
                            testing_tile = tiles_list[game_pos_to_grid(old_tile.pos.x, self.scale) + i][
                                game_pos_to_grid(old_tile.pos.y, self.scale)]
                        elif self.number_of_tiles_moved.x < 0:  # -x
                            testing_tile = tiles_list[game_pos_to_grid(old_tile.pos.x, self.scale) - i][
                                game_pos_to_grid(old_tile.pos.y, self.scale)]
                        if testing_tile is not None and testing_tile.state:  # check if tile in search is occupied
                            self.return_to_tile(old_tile)
                            return False
                return True

    def upgrade_to_queen(self):
        self.behavior = 5
        if self.white:
            self.image_path = "Images/pieces-new/w_queen_png_shadow_1024px.png"
        else:
            self.image_path = "Images/pieces-new/b_queen_png_shadow_1024px.png"

        self.update_image()

    def actor_to_json(self):
        return {"id": self.id, "pos": {"x": self.tile_pos.x, "y": self.tile_pos.y}}
