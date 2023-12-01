
from Interface import Ui
from World import Collidable

from ursina import Sprite
from ursina import time as Time
from ursina import destroy as Destroy
from ursina import load_texture as LoadTexture


class Item(Collidable):

    CHEST_RENDER_LIMIT = 2
    POPUP_DURATION = 160

    def __init__(self, ui: Ui) -> None:
        super().__init__()

        self.frame = {
            "chest": 0
        }

        self.texture_delay = {
            "chest": 0.1
        }

        self.TOTAL_TEXTURES = {
            "chest": 8
        }

        self.TEXTURE = {
            "chest": {i: LoadTexture(f"Assets/Animation/Items/Chest/{i}.png") for i in range(self.TOTAL_TEXTURES.get("chest"))}
        }

        self.ui = ui
        self.chests = []
        self.items_to_animate = []
        self.items_to_despawn = []

        self.chests.append(self._render_chest(-3))

        self.item_popup = None
        self.elapsed_frames = 0

    def _render_chest(self, x_pos) -> Sprite:

        return Sprite(
            name="chest",
            texture=self.TEXTURE.get("chest").get(0),
            scale=2,
            collider="circle",
            position=(x_pos, -2.73),
            always_on_top=True
        )

    def _animate(self):

        for item in self.items_to_animate.copy():
            if self.elapsed_frames >= self.texture_delay.get(item.name):

                self.elapsed_frames = 0

                current_frame = self.frame.get(item.name)
                total_frames = self.TOTAL_TEXTURES.get(item.name) - 1

                if current_frame < total_frames:        # MORE FRAMES LEFT TO ANIMATE

                    item.texture = self.TEXTURE.get(
                        item.name
                    ).get(current_frame)

                    self.frame[item.name] += 1

                else:                                   # REACHED LAST ANIMATION FRAME
                    
                    # RENDER POPUP TEXT ABOVE PLAYER
                    self.item_popup = self.ui.render_popup(
                        "Ammo: 10", 0, -0.15, 1
                    )

                    # RESET CURRNET STATE FRAME COUNTER
                    self.frame[item.name] = 0
                    self.items_to_animate.remove(item)

    def spawn_chest(self, x_pos: int):

        if len(self.chests) < self.CHEST_RENDER_LIMIT:
            self.chests.append(
                self._render_chest(x_pos)
            )

    def open_chest_at(self, player_x_pos):

        for chest in self.chests.copy():

            # IF CENTER OF THE PLAYER TOUCHING THE CHEST
            chest_pos = chest.position.x
            if player_x_pos >= chest_pos - 0.5:
                if player_x_pos <= chest_pos + 0.5:
                    self.items_to_animate.append(chest)
                    self.items_to_despawn.append(chest)
                    self.chests.remove(chest)

    def update(self):

        self.elapsed_frames += Time.dt

        for frame in self.frame.items():
            if frame != 0:
                self._animate()

        # DESPAWN ITEMS
        for item in self.items_to_despawn.copy():

            # ITEM FINISHED ANIMATION
            if self.frame.get(item.name) == 0:
                if not self.is_item_in_view(item.position.x):
                    self.flagged_delete.append(item)
                    self.items_to_despawn.remove(item)

        # HANDLE POPUP TEXT
        if self.item_popup:
            if self.elapsed_frames >= self.POPUP_DURATION * Time.dt:
                self.elapsed_frames = 0
                Destroy(self.item_popup)
                self.item_popup = None
