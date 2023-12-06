
from .World import Collidable

from ursina import Sprite, Text
from ursina import time as Time
from ursina import destroy as Destroy
from random import randint as Randint


class Item(Collidable):

    CHEST_RENDER_LIMIT = 2
    POPUP_DURATION = 160

    # SHARED TO ALL CHILDRENS
    items_to_animate = []
    items_to_despawn = []

    def __init__(self) -> None:
        super().__init__()

        self.item_popup = None
        self.elapsed_frames = 0

    def _render(self, name, x_pos, texture, y_pos=-2.73, scale=2) -> Sprite:

        return Sprite(
            name=name,
            texture=texture,
            scale=scale,
            collider="circle",
            position=(x_pos, y_pos),
            always_on_top=True
        )

    def _animate(self):

        for item in self.items_to_animate.copy():       # NEEDED TO ANIMATE ALL ITEMS SIMULTANEOUSLY

            if self.elapsed_frames >= self.TEXTURE_DELAY:

                self.elapsed_frames = 0
                current_frame = self.frame
                total_frames = self.TOTAL_TEXTURES - 1

                if current_frame < total_frames:        # MORE FRAMES LEFT TO ANIMATE

                    item.texture = self.TEXTURE.get(current_frame)
                    self.frame += 1

                else:                                   # REACHED LAST ANIMATION FRAME

                    # RESET CURRNET STATE FRAME COUNTER
                    self.frame = 0
                    self.items_to_animate.remove(item)
                    self.item_popup = self.get_popup()

    def update(self):

        self.elapsed_frames += Time.dt

        # ANIMATE REQUIRED ITEMS
        if self.items_to_animate:
            self._animate()

        # DESPAWN ITEMS
        for item in self.items_to_despawn.copy():

            # ITEM NOT ON SCREEN
            if not self.is_item_in_view(item.position.x):
                self.flagged_delete.append(item)
                self.items_to_despawn.remove(item)

        # HANDLE POPUP TEXT
        if self.item_popup:

            if self.elapsed_frames >= self.POPUP_DURATION * Time.dt:
                self.elapsed_frames = 0
                Destroy(self.item_popup)
                self.item_popup = None


class Chest(Item):

    frame = 0       # TO DETERMINE CURRENT FRAME TEXTURE
    chests = []

    TEXTURE_DELAY = 0.1
    TOTAL_TEXTURES = 8
    TEXTURE = {
        i: f"Assets/Animation/Items/Chest/{i}.png" for i in range(TOTAL_TEXTURES)
    }

    def __init__(self) -> None:
        super().__init__()

        self.chests.append(self.render(-3))

    def render(self, x_pos) -> Sprite:
        return self._render("chest", x_pos, self.TEXTURE.get(0))

    def spawn(self, x_pos: int):

        # LIMIT SPAWNED CHESTS
        if len(self.chests) < self.CHEST_RENDER_LIMIT:
            self.chests.append(
                self.render(x_pos)
            )

    def open_at(self, player_x_pos):

        # DETERMINE THE CHEST COLLIDING WITH PLAYER POS
        for chest in self.chests.copy():

            # IF CENTER OF THE PLAYER TOUCHING THE CHEST
            chest_pos = chest.position.x

            if player_x_pos >= chest_pos - 0.5 and player_x_pos <= chest_pos + 0.5:
                self.items_to_animate.append(chest)
                self.items_to_despawn.append(chest)
                self.chests.remove(chest)

    def get_popup(self) -> Text:
        """
            RENDER TEXT OBJECT OF THE GAINED AMMO AND RETURN IT TO BE ABLE TO DESTROY LATER
        """

        # GAIN RANDOM AMMO
        ammo = Randint(2, 7)

        # INCREASE PLAYER TOTAL AMMO
        for player in self.entities:
            if player.entity.name == "player":
                player.pick_ammo(ammo)
                return player.popup(f"{ammo} Ammo")
