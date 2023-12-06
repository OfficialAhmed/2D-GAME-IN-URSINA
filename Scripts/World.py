"""

    ALL CLASSES DO NOT INHERIT FROM OTHER SCRIPTS
    
"""

from ursina import Sprite
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

    def __init__(self, Sprite: Sprite) -> None:

        assets = "Assets/Animation/Stage/"

        self.sky_on_screen = Sprite(
            f"{assets}Sky/0.png",
            scale=2,
            position=(0, 1.8)
        )

        self.sky_off_screen = Sprite(
            f"{assets}Sky/0.png",
            scale=2,
            position=(-22, 1.8)
        )

        self.moon: Sprite = Sprite(
            f"{assets}moon.png",
            scale=2.5,
            position=(-3.2, 2),
            always_on_top=True
        )

        self.far_clouds_on_screen = Sprite(
            f"{assets}Clouds/Far/0.png",
            scale=2,
            position=(0, 0),
            always_on_top=True
        )

        self.far_clouds_off_screen = Sprite(
            f"{assets}Clouds/Far/0.png",
            scale=2,
            position=(-22, 0),
            always_on_top=True
        )

        self.clouds_on_screen = Sprite(
            f"{assets}Clouds/0.png",
            scale=2,
            position=(0, -0.7),
            always_on_top=True
        )

        self.clouds_off_screen = Sprite(
            f"{assets}Clouds/0.png",
            scale=2,
            position=(-22, -0.7),
            always_on_top=True
        )

        self.far_mountains_on_screen = Sprite(
            f"{assets}Mountains/Far/0.png",
            scale=2,
            position=(0, -1.3),
            always_on_top=True
        )

        self.far_mountains_off_screen = Sprite(
            f"{assets}Mountains/Far/0.png",
            scale=2,
            position=(-22, -1.3),
            always_on_top=True
        )

        self.mountains_on_screen = Sprite(
            f"{assets}Mountains/0.png",
            scale=2,
            position=(0, -1),
            always_on_top=True
        )

        self.mountains_off_screen = Sprite(
            f"{assets}Mountains/0.png",
            scale=2,
            position=(-22, -1),
            always_on_top=True
        )

        self.tree_on_screen = Sprite(
            f"{assets}Trees/0.png",
            scale=2,
            position=(0, -1.6),
            always_on_top=True
        )

        self.tree_off_screen = Sprite(
            f"{assets}Trees/1.png",
            scale=2,
            position=(-22, -1.6),
            always_on_top=True
        )

        self.ground = Sprite(
            f"{assets}ground.png",
            scale=3,
            position=(79, -2),
            always_on_top=True
        )

    def loading_zone(self, player_pos):
        """
            DETERMINE RENDERING ZONE FOR CURRENT TEXTURE: IF PLAYER CLOSER TO THE END OF THE TEXTURE
        """

        return player_pos >= self.tree_on_screen.x + 3 and player_pos <= self.tree_on_screen.x + 4

    def swap_texture(self):
        """
            WHAT'S OFF-SCREEN BECOMES ON-SCREEN AND VICE VERSA
        """

        self.sky_off_screen.x = self.sky_on_screen.x + 22
        self.tree_off_screen.x = self.tree_on_screen.x + 22
        self.clouds_off_screen.x = self.clouds_on_screen.x + 22
        self.mountains_off_screen.x = self.mountains_on_screen.x + 22
        self.far_clouds_off_screen.x = self.far_clouds_on_screen.x + 22
        self.far_mountains_off_screen.x = self.far_mountains_on_screen.x + 22

        self.sky_on_screen, self.sky_off_screen = self.sky_off_screen, self.sky_on_screen
        self.tree_on_screen, self.tree_off_screen = self.tree_off_screen, self.tree_on_screen
        self.clouds_on_screen, self.clouds_off_screen = self.clouds_off_screen, self.clouds_on_screen
        self.mountains_on_screen, self.mountains_off_screen = self.mountains_off_screen, self.mountains_on_screen
        self.far_clouds_on_screen, self.far_clouds_off_screen = self.far_clouds_off_screen, self.far_clouds_on_screen
        self.far_mountains_on_screen, self.far_mountains_off_screen = self.far_mountains_off_screen, self.far_mountains_on_screen

    def update(self, player_pos):
        """
            UPDATES BACKGROUND
        """

        # FIXED POSITION
        self.moon.x = player_pos - 3

        if self.loading_zone(player_pos):
            self.swap_texture()
