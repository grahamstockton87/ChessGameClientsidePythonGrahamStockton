import vec2


class Tile:
    def __init__(self, pos: vec2, state: bool, scale:int):
        self.pos = pos
        self.state = state
        self.square_size = scale

    #def draw_tiles(self, screen) -> None:
    #    # Blit the image on the screen at the calculated position
    #    pygame.draw.rect(screen, self.color, (self.pos.x, self.pos.y, self.square_size, self.square_size))



