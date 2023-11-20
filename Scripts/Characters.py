
from ursina import Entity, Sprite
from ursina import time as Time

from ursina import destroy as Destroy

from .World import Scene
from .Interface import Ui


class Gun:

    def __init__(self, entity) -> None:

        self.ui = Ui()
        self.entity = entity

        self.DRAG = 9
        self.SPEED = 6
        self.VELOCITY = 15
        self.MAX_RANGE = 8
        self.SHOTGUN_CAPACITY = 4

        self.bullets = []
        self.total_ammo = 20
        self.total_ammo_mag = self.SHOTGUN_CAPACITY
        self.direction = "Right"

        self.get_gun_pos = lambda: (self.entity.x, -1.5)
        self.ui.render_ammo(self.total_ammo)
        self.ui.render_mag_capacity(self.total_ammo_mag)

    def reload(self):

        # RELOAD IF SUFFICIENT AMMO AVAILABLE
        if self.total_ammo >= self.SHOTGUN_CAPACITY:

            # RELOAD GUN
            self.total_ammo -= self.SHOTGUN_CAPACITY
            self.total_ammo_mag = self.SHOTGUN_CAPACITY

            # UPDATE AMMO ON SCREEN
            self.ui.update_ammo(self.total_ammo)
            self.ui.update_mag_capacity(self.total_ammo_mag)

    def spawn_bullet(self):

        if self.total_ammo_mag > 0:

            # TRACK THE BULLET DATA
            self.bullets.append(
                {
                    "direction":    self.direction,
                    "speed":        self.VELOCITY,
                    "bullet":       Entity(
                        model="quad",
                        scale=(0.2, 0.1),
                        position=(
                            self.get_gun_pos()[0],
                            self.get_gun_pos()[1]
                        ),
                        always_on_top=True,
                    )
                }
            )

            self.total_ammo_mag -= 1

            self.ui.update_mag_capacity(self.total_ammo_mag)
            self.animate_bullet()

    def animate_bullet(self):

        bullets: list[dict] = self.bullets.copy()

        for index, bullet in enumerate(bullets):

            #   ANIMATE BULLETS
            # CALCULATE TRAJECTORY
            if bullet["speed"] > self.SPEED:
                bullet["speed"] -= self.DRAG * Time.dt

            # ANIMATE TRAJECTORY
            if bullet["direction"] == "Right":
                bullet["bullet"].x += bullet["speed"] * Time.dt
            else:
                bullet["bullet"].x -= bullet["speed"] * Time.dt

            #   DESTROY BULLETS
            # BULLET DISTANCE FROM CHARACTER
            if abs(bullet["bullet"].x - self.entity.x) >= self.MAX_RANGE:
                Destroy(bullet["bullet"])
                self.bullets.pop(index)
                continue

            # COLLISION WITH ENEMY

            # TODO: CHECK COLLISION WITH ENEMIES


class Character(Scene):

    def __init__(self, entity: Entity, sky: Sprite, ground: Sprite) -> None:
        super().__init__()

        self.ui = Ui()
        self.ui.render_health(100)

        # ENGINE ENTITY OBJECT
        self.sky:    Sprite = sky
        self.ground: Sprite = ground
        self.entity: Entity = entity
        self.gun:       Gun = Gun(self.entity)

        self.animation_timer = 0

        self.speed = 1.3
        self.state = "idle"
        self.direction = "Right"
        self.elapsed_loop_duration = 0
        self.is_gun_triggered = False

        self.last_fire_frame = 0
        self.fire_cooldown = 0.5

        self.texture = {
            "Right": {
                "idle":       {i: f"Assets/Animation/Char/Idle/Right/{i}.png" for i in range(6)},
                "run":        {i: f"Assets/Animation/Char/Run/Right/{i}.png" for i in range(8)},
                "fire":       {i: f"Assets/Animation/Char/Attack/Fire/Right/{i}.png" for i in range(12)},
                "reload":     {i: f"Assets/Animation/Char/Attack/Reload/Right/{i}.png" for i in range(12)},
                "aim":        {0: f"Assets/Animation/Char/Attack/Fire/Right/0.png"}
            },

            "Left": {
                "idle":       {i: f"Assets/Animation/Char/Idle/Left/{i}.png" for i in range(6)},
                "run":        {i: f"Assets/Animation/Char/Run/Left/{i}.png" for i in range(8)},
                "fire":       {i: f"Assets/Animation/Char/Attack/Fire/Left/{i}.png" for i in range(12)},
                "reload":     {i: f"Assets/Animation/Char/Attack/Reload/Left/{i}.png" for i in range(12)},
                "aim":        {0: f"Assets/Animation/Char/Attack/Fire/Left/0.png"}
            }
        }

        # DELAY BETWEEN EACH TEXTURE FRAME
        self.animation_delay = {
            "aim":          0.44,
            "idle":         0.08,
            "run":          0.08,
            "fire":         0.03,
            "reload":       0.12,
        }

    def update_texture(self, loop=True) -> bool:

        # IF PASSED THE ANIMATION DURATION
        if self.elapsed_frames >= self.animation_delay.get(self.state):

            self.elapsed_frames = 0

            self.entity.texture = self.texture.get(
                self.direction
            ).get(self.state).get(self.current_frame)

            total_frames = len(
                self.texture.get(
                    self.direction
                ).get(self.state)
            )

            # LOOP ANIMATION, WHILE DURATION NOT EXCEEDED
            if loop:

                self.current_frame = (
                    self.current_frame+1
                ) % total_frames

            else:

                # REACHED LAST FRAME IN THE ANIMATION
                if self.current_frame >= total_frames:

                    match self.state:
                        case "fire" | "reload":
                            self.state = "aim"
                            self.current_frame = 0
                            self.elapsed_loop_duration = 0
                            return

                self.current_frame += 1

    def animate(self):

        self.gun.direction = self.direction
        self.gun.animate_bullet()

        """
            The state spans across multiple frames
            one case may repeat many times.
            
            If-statement to limit unnecessary repeatition
        """
        match self.state:

            case "idle":
                self.update_texture()

            case "run":

                # INCREASE CHAR X UNTIL ORIGIN
                if self.direction == "Right":

                    if self.entity.x <= 0:
                        self.entity.x += self.speed * Time.dt
                    else:
                        # UPDATE GROUND / SKY POSITION
                        self.ground.x -= self.speed * Time.dt
                        self.sky.x -= (self.speed/2) * Time.dt

                # DECREASE CHAR X UNTIL COLLISION WITH SCREEN
                else:
                    self.entity.x -= self.speed * Time.dt

                self.update_texture()

            case "fire":

                # FIRE A BULLET
                if self.gun.total_ammo_mag > 0:

                    self.update_texture(loop=False)

                    # SPAWN ONE BULLET ON TRIGGER
                    if self.is_gun_triggered:
                        self.gun.spawn_bullet()
                        self.is_gun_triggered = False

                # MAG IS EMPTY, RELOAD
                elif self.gun.total_ammo_mag == 0 and self.gun.total_ammo >= self.gun.SHOTGUN_CAPACITY:
                    self.animation_timer = 0
                    self.state = "reload"

            case "aim":

                # RENDER FIRST FRAME FROM FIREING STATE = AIMING
                self.entity.texture = self.texture.get(self.direction).get(
                    "fire"
                ).get(0)

                self.animation_timer += Time.dt
                if self.animation_timer >= 60 * 1.4 * Time.dt:

                    # BACK TO IDLE
                    self.state = "idle"

            case "reload":

                self.animation_timer += Time.dt
                if self.animation_timer >= 60 * 1.4 * Time.dt:

                    # RELOAD AMMO ONCE RELOADING-ANIMATION ENDED
                    if self.gun.total_ammo_mag != self.gun.SHOTGUN_CAPACITY:
                        self.gun.reload()
                        self.state = "aim"
                        return

                self.update_texture(loop=False)
