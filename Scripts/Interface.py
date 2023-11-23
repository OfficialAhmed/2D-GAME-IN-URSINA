from ursina import Text, Entity
from ursina import color as Color

class Ui:

    __ammo:           Text = None
    __armor:          Text = None
    __money:          Text = None
    __health:         Text = None
    __gun_capacity:   Text = None

    def __init__(self, Entity: Entity) -> None:
        # HUD BACKGROUND UI
        Entity(
            model="quad",
            texture="Assets/Interface/HUD.png",
            scale=(5.5, 2),
            position=(-4.3, 3.1),
            always_on_top=True
        )

    def _render_text(self, text, x, y) -> Text:

        return Text(
            text=text,
            font="Assets/Font/CUPHEAD.ttf",
            origin=(0, 0),
            position=(x, y),
            color=Color.white,
            always_on_top=True
        )

    def render_ammo(self, total):
        self.__ammo = self._render_text(total, -0.72, 0.29)

    def render_money(self, total):
        self.__money = self._render_text(total, -0.25, 0.45)

    def render_armor(self, total):
        self.__armor = self._render_text(f"{total}%", -0.45, 0.44)

    def render_health(self, total):
        self.__health = self._render_text(f"{total}%", -0.45, 0.36)

    def render_mag_capacity(self, total):
        self.__gun_capacity = self._render_text(f"\{total}", -0.67, 0.29)

    def update_ammo(self, total):
        if self.__ammo:
            self.__ammo.text = total

    def update_money(self, total):
        if self.__money:
            self.__money.text = total

    def update_armor(self, total):
        if self.__armor:
            self.__armor.text = f"{total}%"

    def update_health(self, total):
        if self.__health:
            self.__health.text = f"{total}%"

    def update_mag_capacity(self, total):
        if self.__gun_capacity:
            self.__gun_capacity.text = f"\ {total}"
