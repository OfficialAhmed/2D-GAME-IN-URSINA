from ursina import Entity, Sprite
from ursina import time as Time

from ursina import destroy as Destroy

from .World import Scene
from .Interface import Ui


class Bullet:

    def __init__(self, entity) -> None:

        self.ui = Ui()
        self.entity = entity

        self.DRAG = 9
        self.SPEED = 6
        self.VELOCITY = 15
        self.MAX_RANGE = 8

        self.bullets = []
        self.total = 20
        self.direction = "Right"

        self.get_gun_pos = lambda: (self.entity.x, -1.75)
        self.ui.render_ammo(self.total)

    def spawn(self):

        if self.total > 0:

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

            # UPDATE TOTAL AMMO ON SCREEN
            self.total -= 1
            self.ui.update_ammo(self.total)

        self.animate()

    def animate(self):

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

        # ENGINE ENTITY OBJECT
        self.sky:    Sprite = sky
        self.ground: Sprite = ground
        self.entity: Entity = entity
        self.bullet: Bullet = Bullet(self.entity)

        self.aim_timer = 0

        self.speed = 1.29
        self.state = "idle"
        self.direction = "Right"
        self.elapsed_loop_duration = 0

        self.texture = {
            "Right": {
                "aim":          {0: f"Assets/Animation/Char/Attack/Aim/Right/0.png"},
                "idle":         {i: f"Assets/Animation/Char/Idle/Right/{i}.png" for i in range(12)},
                "move":         {i: f"Assets/Animation/Char/Move/Right/{i}.png" for i in range(10)},
                "fire":         {0: f"Assets/Animation/Char/Attack/Fire/Right/0.png"}
            },

            "Left": {
                "aim":          {0: f"Assets/Animation/Char/Attack/Aim/Left/0.png"},
                "idle":         {i: f"Assets/Animation/Char/Idle/Left/{i}.png" for i in range(12)},
                "move":         {i: f"Assets/Animation/Char/Move/Left/{i}.png" for i in range(10)},
                "fire":         {0: f"Assets/Animation/Char/Attack/Fire/Left/0.png"}
            }
        }

        # DELAY BETWEEN EACH TEXTURE FRAME
        self.animation_duration = {
            "aim":          0.14,
            "idle":         0.1,
            "move":         0.08,
            "fire":         0.1
        }

        # DETERMINE AIMING ANIMATION DELAY [IN FRAMES]
        self.expired_fire_state = lambda: self.aim_timer >= 60 * 1.1 * Time.dt

    def update_texture(self, loop=True) -> bool:

        # IF PASSED THE ANIMATION DURATION
        if loop and self.elapsed_frames >= self.animation_duration.get(self.state):
            self.elapsed_frames = 0

            self.entity.texture = self.texture.get(
                self.direction
            ).get(self.state).get(self.current_frame)

            # LOOP ANIMATION, WHILE DURATION NOT EXCEEDED
            self.current_frame = (
                self.current_frame+1
            ) % len(self.texture.get(self.direction).get(self.state))

        elif not loop:

            self.entity.texture = self.texture.get(
                self.direction
            ).get(self.state).get(0)

            # ANIMATION EXPIRED, CHANGE STATE
            if self.elapsed_loop_duration >= self.animation_duration.get(self.state) * Time.dt:

                match self.state:
                    case "fire":
                        self.state = "aim"

    def animate(self):

        self.bullet.direction = self.direction
        self.bullet.animate()

        match self.state:

            case "idle":
                self.update_texture()

            case "move":

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

                # RESET AIMING TIMER
                self.aim_timer = 0

                self.bullet.spawn()

                if self.expired_fire_state():

                    # BACK TO AIMING
                    self.state = "aim"
                    self.current_frame = 0
                    self.elapsed_loop_duration = 0

                else:
                    self.update_texture(loop=False)

            case "aim":

                self.aim_timer += Time.dt

                if self.expired_fire_state():

                    # BACK TO IDLE
                    self.state = "idle"

                else:
                    self.entity.texture = self.texture.get(self.direction).get(
                        "aim"
                    ).get(0)


class Enemy(Scene):
    pass
