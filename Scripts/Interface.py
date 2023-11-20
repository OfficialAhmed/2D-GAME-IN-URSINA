from ursina import Text
from ursina import color as Color


class Ui:

    __ammo:           Text = None
    __health:         Text = None
    __gun_capacity:   Text = None

    def _render_text(self, text, x, y) -> Text:

        return Text(
            text=text,
            font="Assets/Font/CUPHEAD.ttf",
            origin=(0, 0),
            position=(x, y),
            color=Color.black,
            always_on_top=True
        )

    def render_ammo(self, total):
        self.__ammo = self._render_text(f"Ammo: {total}", -0.8, 0.35)

    def render_health(self, total):
        self.__health = self._render_text(f"Life: {total}", -0.8, 0.4)

    def render_mag_capacity(self, total):
        self.__gun_capacity = self._render_text(f"\ {total}", -0.69, 0.35)

    def update_ammo(self, total):
        if self.__ammo:
            self.__ammo.text = f"Ammo: {total}"

    def update_health(self, total):
        if self.__health:
            self.__health.text = f"Life: {total}"

    def update_mag_capacity(self, total):
        if self.__gun_capacity:
            self.__gun_capacity.text = f"\ {total}"
