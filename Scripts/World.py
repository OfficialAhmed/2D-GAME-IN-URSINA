"""

    ALL CLASSES DO NOT INHERIT FROM OTHER SCRIPTS
    
"""

from ursina import Sprite
from ursina import time as Time


class Fps:
    """
        FRAME MANIPULATION
    """

    def __init__(self) -> None:
        self.current_frame = 0
        self.elapsed_frames = 0
        
    def item_on_screen(self):
        print(Camera.world_position_getter())
    


class Collidable:
    """
        ENTITIES CAN BE COLLIDED WITH OTHER OBJECTS STORED HERE
    """

    entities = []           # ENTITIES CAN BE CHECKED FOR COLLISION
    flagged_delete = []     # ENTITIES TO BE DELETED


class Scene:

    ANIMATION_SPEED = 1.8

    def __init__(self, Sprite: Sprite) -> None:
        self.sky = Sprite(
            "Assets/Animation/Stage/sky.png",
            scale=3.5,
            position=(-1, 0)
        )

        self.moon = Sprite(
            "Assets/Animation/Stage/moon.png",
            scale=2.5,
            position=(-3.5, 2),
            always_on_top=True
        )

        self.far_clouds = Sprite(
            "Assets/Animation/Stage/far_clouds.png",
            scale=2,
            position=(0, 0),
            always_on_top=True
        )

        self.clouds = Sprite(
            "Assets/Animation/Stage/clouds.png",
            scale=2,
            position=(6, -0.7),
            always_on_top=True
        )

        self.far_mountains = Sprite(
            "Assets/Animation/Stage/far_mountains.png",
            scale=2,
            position=(-1, -1),
            always_on_top=True
        )

        self.mountains = Sprite(
            "Assets/Animation/Stage/mountains.png",
            scale=2,
            position=(9, -1),
            always_on_top=True
        )

        self.trees = Sprite(
            "Assets/Animation/Stage/trees.png",
            scale=2,
            position=(25, -1.3),
            always_on_top=True
        )

        self.ground = Sprite(
            "Assets/Animation/Stage/ground.png",
            scale=3,
            position=(79.2, -2),
            always_on_top=True
        )

        self.animation_direction = "right"

        self.animation_delay = {
            "trees":         5,
            "mountains":     10,
            "far_mountains": 15,
            "clouds":        20,
            "far_clouds":    25,
            "sky":           33,
        }

    def update(self):
        """
            UPDATES THE POSITION OF THE BACKGROUND
        """

        speed = self.ANIMATION_SPEED * Time.dt

        # DIRECTION BASED ON THE WIDTH OF THE BACKGROUND "sky"
        if self.sky.x <= -3.5:
            self.animation_direction = "left"
        elif self.sky.x >= 3.5:
            self.animation_direction = "right"

        self.trees.x -= speed / self.animation_delay.get("trees")
        self.mountains.x -= speed / self.animation_delay.get("mountains")
        self.far_mountains.x -= speed / \
            self.animation_delay.get("far_mountains")

        # UPDATE POSITIONS BASED ON THE DIRECTION
        # MOVE BACKGROUND TOWARDS THE LEFT
        if self.animation_direction == "right":
            self.sky.x -= speed / self.animation_delay.get("sky")
            self.far_clouds.x -= speed / self.animation_delay.get("far_clouds")
            self.clouds.x -= speed / self.animation_delay.get("clouds")

        # MOVE BACKGROUND TOWARDS THE RIGHT
        else:
            self.sky.x += speed / self.animation_delay.get("sky")
            self.far_clouds.x += speed / self.animation_delay.get("far_clouds")
            self.clouds.x += speed / self.animation_delay.get("clouds")
