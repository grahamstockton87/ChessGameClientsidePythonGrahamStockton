from vec2 import vec2
from actor import Actor
from Tile import Tile

# GLOBAL VARS__________________________________________________________________________________________________



# GLOBAL VARS__________________________________________________________________________________________________

def initilize_actors_list(scale):
    actors_list = []

    for i in range(8):
        actors_list.append(
            Actor(pos=vec2(i * scale, scale * 6), image_path="Images/pieces-new/w_pawn_png_shadow_1024px.png", behavior=1,
                  white=True, scale=scale))

    actors_list.append(
        Actor(pos=vec2(0, scale * 7), image_path="Images/pieces-new/w_rook_png_shadow_1024px.png", behavior=2, white=True, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale, scale * 7), image_path="Images/pieces-new/w_knight_png_shadow_1024px.png", behavior=3,
              white=True, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 2, scale * 7), image_path="Images/pieces-new/w_bishop_png_shadow_1024px.png", behavior=4,
              white=True, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 3, scale * 7), image_path="Images/pieces-new/w_queen_png_shadow_1024px.png", behavior=5, white=True, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 4, scale * 7), image_path="Images/pieces-new/w_king_png_shadow_1024px.png", behavior=6, white=True, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 5, scale * 7), image_path="Images/pieces-new/w_bishop_png_shadow_1024px.png", behavior=4,
              white=True, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 6, scale * 7), image_path="Images/pieces-new/w_knight_png_shadow_1024px.png", behavior=3,
              white=True, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 7, scale * 7), image_path="Images/pieces-new/w_rook_png_shadow_1024px.png", behavior=2, white=True, scale=scale))

    for i in range(8):
        actors_list.append(
            Actor(pos=vec2(i * scale, scale), image_path="Images/pieces-new/b_pawn_png_shadow_1024px.png", behavior=1,
                  white=False, scale=scale))

    actors_list.append(
        Actor(pos=vec2(0, 0), image_path="Images/pieces-new/b_rook_png_shadow_1024px.png", behavior=2, white=False, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale, 0), image_path="Images/pieces-new/b_knight_png_shadow_1024px.png", behavior=3, white=False, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 2, 0), image_path="Images/pieces-new/b_bishop_png_shadow_1024px.png", behavior=4, white=False, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 3, 0), image_path="Images/pieces-new/b_queen_png_shadow_1024px.png", behavior=5, white=False, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 4, 0), image_path="Images/pieces-new/b_king_png_shadow_1024px.png", behavior=6, white=False, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 5, 0), image_path="Images/pieces-new/b_bishop_png_shadow_1024px.png", behavior=4, white=False, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 6, 0), image_path="Images/pieces-new/b_knight_png_shadow_1024px.png", behavior=3, white=False, scale=scale))
    actors_list.append(
        Actor(pos=vec2(scale * 7, 0), image_path="Images/pieces-new/b_rook_png_shadow_1024px.png", behavior=2, white=False, scale=scale))

    for i in range(len(actors_list)):
        actors_list[i].id = i
    return actors_list


def initialize_tiles_list(scale):
    # Initialize a 2D list of tiles with all elements set to None
    tiles_list = [[None for _ in range(8)] for _ in range(8)]

    # Create the tiles and set their colors based on their positions
    for a in range(8):
        for i in range(8):
            tiles_list[i][a] = Tile(pos=vec2(i * scale, a * scale), state=False, scale=scale)

    return tiles_list


def clip(num, scale):
    return (num // scale) * scale if num >= 0 else ((num // scale) - 1) * scale


def game_pos_to_grid(x):
    return int(x / 100)


def actor_at_tile(tile, actors_list, scale):
    for actor in actors_list:  # for every Actor
        clipped = vec2(clip(actor.pos.x, scale), clip(actor.pos.y, scale))
        # print("Actor: " , cliped, Actor.behavior, "tile: ",tile.pos)
        if clipped.x == tile.pos.x and clipped.y == tile.pos.y:
            return actor


def get_direction(starting_tile, destination_tile):
    return vec2(
        int((destination_tile.pos.x - starting_tile.pos.x) / 100),
        int((destination_tile.pos.y - starting_tile.pos.y) / 100)
    )


def get_actor_index_from_id(actors_list_X, id):
    for index, actor_x in enumerate(actors_list_X):
        if actor_x.id == id:
            return index  # Return the index of the matching Actor in the list


def tile_at(mouse_position, tiles_list):
    return tiles_list[mouse_position.x][mouse_position.y]


def update_board(tiles_list, actors_list, scale):
    for row in tiles_list:
        for tile in row:
            tile.state = False

    # Change status for overlapping positions in tiles and actors
    for actor in actors_list:
        clipped_actor_pos = vec2(int(clip(actor.pos.x, scale) / scale), int(clip(actor.pos.y, scale) / scale))
        if 0 <= clipped_actor_pos.x < len(tiles_list) and 0 <= clipped_actor_pos.y < len(
                tiles_list[clipped_actor_pos.x]):
            tiles_list[clipped_actor_pos.x][clipped_actor_pos.y].state = True


def is_move_valid(starting_actor):
    if starting_actor.number_of_tiles_moved.x == 0 and starting_actor.number_of_tiles_moved.y == 0:
        return False  # if hasnt moved return to tile
    elif starting_actor.behavior == 1:  # PAWN
        if starting_actor.direction.x == 0:
            if (starting_actor.first_move and starting_actor.white and -2 <= starting_actor.number_of_tiles_moved.y < 0) or \
                    (starting_actor.first_move and not starting_actor.white and 0 < starting_actor.number_of_tiles_moved.y <= 2) or \
                    (not starting_actor.first_move and starting_actor.white and -1 <= starting_actor.number_of_tiles_moved.y < 0) or \
                    (not starting_actor.first_move and not starting_actor.white and 0 < starting_actor.number_of_tiles_moved.y <= 1):
                return True
            else:
                return False
        elif starting_actor.direction.x == starting_actor.direction.y:  # If move is diagonal
            starting_actor.pawn_can_take = True
            return True
        else:
            return False

    elif starting_actor.behavior == 2:  #
        if starting_actor.direction.x == 0 or starting_actor.direction.y == 0:
            return True
        else:  # illeagle move
            return False
    elif starting_actor.behavior == 3:  # knight
        if (starting_actor.direction.x == 1 and starting_actor.direction.y == 2) or (
                starting_actor.direction.x == 2 and starting_actor.direction.y == 2) or (
                starting_actor.direction.y == 1 and starting_actor.direction.x == 2):  # move and snap to tile
            return True
        else:  # illeagle move
            return False

    elif starting_actor.behavior == 4:  # bishop diagnol
        if abs(starting_actor.direction.x) == abs(
                starting_actor.direction.y):  # starting_actor.direction.x and y move; and both even
            return True
        else:  # illeagle move
            return False

    elif starting_actor.behavior == 5:  # queen
        if (starting_actor.direction.x == 0 or starting_actor.direction.y == 0) \
                or starting_actor.direction.x == starting_actor.direction.y:
            return True
        else:  # illeagle move
            return False

    elif starting_actor.behavior == 6:  # king
        if starting_actor.direction.x <= 1 and starting_actor.direction.y <= 1:
            return True
        else:  # illeagle move
            return False


def is_inside_box(box_pos: vec2, box_size: vec2, obj_pos: vec2):  # if obj is between bounds
    if box_pos.x <= obj_pos.x < box_pos.x + box_size.x and box_pos.y <= obj_pos.y < box_pos.y + box_size.y:
        return True
    else:
        return False
