class vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Vector2D({self.x}, {self.y})"

    def __add__(self, other):
        # Perform addition between two vec2 objects
        if isinstance(other, vec2):
            return vec2(self.x + other.x, self.y + other.y)
        elif isinstance(other, (int, float)):
            return vec2(self.x + other, self.y + other)
        else:
            raise TypeError("Unsupported operand type. Can only add vec2 objects.")

    def __sub__(self, other):
        # Perform subtraction between two vec2 objects
        if isinstance(other, vec2):
            return vec2(self.x - other.x, self.y - other.y)
        else:
            raise TypeError("Unsupported operand type. Can only subtract vec2 objects.")

    def __truediv__(self, other):
        # Perform division between two vec2 objects or divide by a scalar value
        if isinstance(other, vec2):
            return vec2(self.x / other.x, self.y / other.y)
        elif isinstance(other, (int, float)):
            return vec2(int(self.x / other), int(self.y / other))
        else:
            raise TypeError("Unsupported operand type. Can only divide vec2 objects or divide by a scalar value.")

    def __mul__(self, other):
        # Perform division between two vec2 objects or divide by a scalar value
        if isinstance(other, vec2):
            return vec2(self.x * other.x, self.y * other.y)
        elif isinstance(other, (int, float)):
            return vec2(self.x * other, self.y * other)
        else:
            raise TypeError("Unsupported operand type. Can only divide vec2 objects or divide by a scalar value.")

    def to_dict(self):
        return {"x": self.x, "y": self.y}
