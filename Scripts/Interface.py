from ursina import Text
from ursina import color as Color


class Ui:

    __ammo:    Text = None
    __health:  Text = None

    def render_ammo(self, total):

        self.__ammo = Text(
            f"Ammo: {total}",
            font="Assets/Font/CUPHEAD.ttf",
            origin=(0, 0),
            position=(-0.8, 0.4),
            color=Color.black,
            always_on_top=True
        )

    def render_health(self, total):
        
        self.__health = Text(
            f"Life: {total}",
            font="Assets/Font/CUPHEAD.ttf",
            origin=(0, 0),
            position=(-0.8, 0.2),
            color=Color.black,
            always_on_top=True
        )
        
    def update_ammo(self, total):

        if self.__ammo:
            self.__ammo.text = f"Ammo: {total}"
            
    def update_health(self, total):

        if self.__health:
            self.__health.text = f"Life: {total}"
