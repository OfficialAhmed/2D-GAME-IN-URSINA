"""

    ALL CLASSES DO NOT INHERIT FROM OTHER SCRIPTS
    
"""

from ursina import Sprite
from ursina import time as Time
from ursina import camera as Camera


class Fps:
    """
        FRAME MANIPULATION
    """

    def __init__(self) -> None:
        self.current_frame = 0
        self.elapsed_frames = 0


class Screen:

    def __init__(self) -> None:
        pass

    def is_item_in_view(self, pos_x) -> bool:
        """
            DETERMINE IF THE X-POSITION OF THE ITEM IS WITHIN THE SCREEN VIEW
        """
        center = Camera.world_position_getter().x
        frame_r = center + 7.5
        frame_l = center - 7.5

        return pos_x >= frame_l <= frame_r


class Collidable(Screen):
    """
        ENTITIES CAN BE COLLIDED WITH OTHER OBJECTS STORED HERE
    """

    entities = []           # ENTITIES CAN BE CHECKED FOR COLLISION
    flagged_delete = []     # ENTITIES TO BE DELETED

    def __init__(self) -> None:
        super().__init__()


class Scene:

    ANIMATION_SPEED = 1.8

    def __init__(self, Sprite: Sprite) -> None:

        self.sky = Sprite(
            "Assets/Animation/Stage/sky.png",
            scale=3.5,
            position=(-1, 0)
        )

        self.moon: Sprite = Sprite(
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
            position=(0, -0.7),
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

        self.tree_on_screen = Sprite(
            "Assets/Animation/Stage/Trees/0.png",
            scale=2,
            position=(0, -1.3),
            always_on_top=True
        )
        self.tree_off_screen = Sprite(
            f"Assets/Animation/Stage/Trees/1.png",
            scale=2,
            position=(-22, -1.3),
            always_on_top=True
        )

        self.ground = Sprite(
            "Assets/Animation/Stage/ground.png",
            scale=3,
            position=(79, -2),
            always_on_top=True
        )

        self.last_pos = 0

    def loading_zone(self, player_pos):
        """
            DETERMINE RENDERING ZONE FOR CURRENT TEXTURE: IF PLAYER CLOSER TO THE END OF THE TEXTURE
        """

        return player_pos >= self.tree_on_screen.x + 3 and player_pos <= self.tree_on_screen.x + 4

    def update(self, player_pos):
        """
            UPDATES THE POSITION OF THE BACKGROUND
        """

        if self.loading_zone(player_pos):

            # CHANGE TREE ON SCREEN
            self.tree_off_screen.x = self.tree_on_screen.x + 22
            self.tree_on_screen, self.tree_off_screen = self.tree_off_screen, self.tree_on_screen

        speed = self.ANIMATION_SPEED * Time.dt

        if player_pos <= self.last_pos:     # PLAYER IDLE
            self.clouds.x += 0.06*speed
            self.far_clouds.x += 0.05*speed

        else:                               # PLAYER MOVING LEFT
            speed *= 0.9                    # MATCH PLAYER SPEED
            self.clouds.x += speed
            self.mountains.x += speed
            self.far_clouds.x += speed
            self.far_mountains.x += speed

        # EVERY 5 UNITS GOING LEFT, RESET TEXTURE TO PLAYER POSITION
        if self.far_clouds.x - player_pos >= 5:
            self.clouds.x = player_pos
            self.mountains.x = player_pos
            self.far_clouds.x = player_pos
            self.far_mountains.x = player_pos

        # FIXED POSITION
        self.moon.x = player_pos - 3
        self.sky.x = player_pos - 3

        self.last_pos = player_pos
