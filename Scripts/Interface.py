from ursina import Text, Entity, Keys
from ursina import color as Color
from ursina import destroy as Destroy


class PauseMenu:

    def __init__(self) -> None:
        self.options = (
            "save",
            "load",
            "back"
        )

        self.option = {
            "back": self.destroy,
            "save": self.save,
            "load": self.load
        }

        self.is_enabled = False
        self.unpause_game = False
        self._current_option = 2

        self.texture = lambda option: f"Assets/Interface/Pause menu/{self.options[option]}.png"

    def controller(self, key):
        """
            HANDLES THE MOVEMENT OF THE MENU OPTIONS
        """
        match key:
            case Keys.up_arrow:
                self.change_option("up")

            case Keys.down_arrow:
                self.change_option("down")

            case Keys.enter:
                return self.select_option()

    def render(self):

        self.is_enabled = True
        self.unpause_game = True
        self.menu = Entity(
            model="quad",
            texture=self.texture(self._current_option),
            scale=(15, 9),
            always_on_top=True
        )

    def destroy(self):
        self.is_enabled = False
        Destroy(self.menu)

    def change_option(self, direction):
        if direction == "up" and self._current_option > 0:
            self._current_option -= 1

        elif direction == "down" and self._current_option < 2:
            self._current_option += 1

        self.menu.texture = self.texture(self._current_option)

    def select_option(self):

        selected_option = self.options[self._current_option]
        self.option.get(selected_option)()      # INVOKE THE METHOD

        if selected_option == "back":
            return True
        else:
            return False

    def save(self):
        # TODO: SAVE CURRENT GAME STATE
        self.destroy()

    def load(self):
        # TODO: LOAD GAME STATE
        self.destroy()


class Ui:

    __ammo:           Text = None
    __armor:          Text = None
    __money:          Text = None
    __health:         Text = None
    __gun_capacity:   Text = None

    def __init__(self, Entity: Entity) -> None:

        # MENUS
        self.pause_menu = PauseMenu()

        # HUD BACKGROUND UI
        Entity(
            model="quad",
            texture="Assets/Interface/HUD.png",
            scale=(5.5, 2),
            position=(-4.3, 3.1),
            always_on_top=True
        )

        # WEAPON ICON
        Entity(
            model="quad",
            texture="Assets/Interface/Icons/Weapons/shotgun.png",
            scale=(1.75, 1.5),
            position=(-5.9, 3.25),
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