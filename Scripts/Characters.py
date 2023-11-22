from ursina import Entity, Audio
from ursina import time as Time

from ursina import destroy as Destroy

from .World import Fps
from .Interface import Ui


class Gun:

    # _____   CONSTANTS   ____________
    DRAG = 9                # BULLET DEDUCTION SPEED
    SPEED = 6               # BULLET LIMIT SPEED
    VELOCITY = 15           # BULLET STARTING SPEED
    MAX_RANGE = 7           # BULLET DISTANCE
    SHOTGUN_CAPACITY = 4    # MAGAZINE CAPACITY

    def __init__(self, entity) -> None:

        self.ui = Ui()
        self.entity = entity

        self.bullets = []
        self.total_ammo = 20
        self.total_ammo_mag = self.SHOTGUN_CAPACITY
        self.direction = "Right"

        self.get_gun_pos = lambda: (
            self.entity.x, -2.25
        )

        self.shoot_sound = Audio("Assets/Sound/Gun/Shotgun/shoot.mp3", False)
        self.empty_sound = Audio("Assets/Sound/Gun/Shotgun/empty.mp3", False)
        self.reload_sound = Audio("Assets/Sound/Gun/Shotgun/reload.mp3", False)
        self.loaded_sound = Audio("Assets/Sound/Gun/Shotgun/loaded.mp3", False)

        self.ui.render_ammo(self.total_ammo)
        self.ui.render_mag_capacity(self.total_ammo_mag)

    def reload(self):

        # RELOAD IF SUFFICIENT AMMO AVAILABLE
        if self.total_ammo >= self.SHOTGUN_CAPACITY:

            # RELOAD GUN
            self.total_ammo -= self.SHOTGUN_CAPACITY
            self.total_ammo_mag = self.SHOTGUN_CAPACITY

            # UPDATE AMMO ON SCREEN (UI)
            self.ui.update_ammo(self.total_ammo)
            self.ui.update_mag_capacity(self.total_ammo_mag)

    def spawn_bullet(self):

        # TRACK THE BULLET DATA TO ANIMATE INDIVIDUALLY
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
            # BULLET DISTANCE FROM CHARACTER REACHED MAX
            if abs(bullet["bullet"].x - self.entity.x) >= self.MAX_RANGE:
                Destroy(bullet["bullet"])
                self.bullets.pop(index)
                continue

            # COLLISION WITH ENEMY

            # TODO: CHECK COLLISION WITH ENEMIES


class Character(Fps):

    # _____   CONSTANTS   ____________
    SPEED = 1.7

    def __init__(self, entity: Entity) -> None:
        super().__init__()

        self.ui = Ui()
        self.ui.render_health(100)

        # ENGINE ENTITY OBJECT
        self.entity: Entity = entity
        self.gun:       Gun = Gun(self.entity)

        self.aiming_timer = 0               # TO HOLD DURATION OF THE AIMING FRAME
        self.is_animating = False           # TO DETERMINE WHETHER ANIMATION LOOP ENDED
        self.is_gun_triggered = False       # TO DISABLE MULTIPLE SHOOTING

        self.state = "idle"
        self.direction = "Right"
        self.elapsed_loop_duration = 0

        self.last_fire_frame = 0
        self.fire_cooldown = 0.3

        self.total_textures = {
            "idle":     5,
            "run":      7,
            "fire":     11,
            "reload":   11,
            "aim":      1
        }

        self.texture = {
            "Right": {
                "idle":       {i: f"Assets/Animation/Char/Idle/Right/{i}.png" for i in range(self.total_textures.get("idle")+1)},
                "run":        {i: f"Assets/Animation/Char/Run/Right/{i}.png" for i in range(self.total_textures.get("run")+1)},
                "fire":       {i: f"Assets/Animation/Char/Attack/Fire/Right/{i}.png" for i in range(self.total_textures.get("fire")+1)},
                "reload":     {i: f"Assets/Animation/Char/Attack/Reload/Right/{i}.png" for i in range(self.total_textures.get("reload")+1)},
                "aim":        {0: f"Assets/Animation/Char/Attack/Fire/Right/0.png"}
            },

            "Left": {
                "idle":       {i: f"Assets/Animation/Char/Idle/Left/{i}.png" for i in range(self.total_textures.get("idle")+1)},
                "run":        {i: f"Assets/Animation/Char/Run/Left/{i}.png" for i in range(self.total_textures.get("run")+1)},
                "fire":       {i: f"Assets/Animation/Char/Attack/Fire/Left/{i}.png" for i in range(self.total_textures.get("fire")+1)},
                "reload":     {i: f"Assets/Animation/Char/Attack/Reload/Left/{i}.png" for i in range(self.total_textures.get("reload")+1)},
                "aim":        {0: f"Assets/Animation/Char/Attack/Fire/Left/0.png"}
            }
        }

        # DELAY BETWEEN EACH TEXTURE FRAME
        # SOME AFFECT THE STATE SPEED, OTHER AFFECT THE ANIMATION SPEED ONLY
        self.texture_delay = {
            "idle":         0.08,       # IDLE ANIMATION SPEED
            "run":          0.08,       # RUNNING ANIMATION SPEED
            "fire":         0.03,       # FIRING SPEED
            "reload":       0.17,       # RELOADING SPEED
        }

    def update_texture(self):

        # AIMING IS ONE FRAME NOT AN ANIMATION
        if self.state == "aim":
            return

        if self.elapsed_frames >= self.texture_delay.get(self.state):

            # CHANGE TEXTURE
            self.entity.texture = self.texture.get(
                self.direction
            ).get(self.state).get(self.current_frame)

            self.elapsed_frames = 0
            total_frames = self.total_textures.get(self.state)

            if self.current_frame < total_frames:
                self.is_animating = True

            # REACHED LAST ANIMATION FRAME, CHANGE STATE
            else:
                match self.state:
                    case "fire" | "reload":
                        self.state = "aim"
                        self.current_frame = 0
                        self.elapsed_loop_duration = 0
                        self.is_animating = False

            self.current_frame += 1

    def update_texture_loop(self):

        # IF PASSED THE ANIMATION DURATION
        if self.elapsed_frames >= self.texture_delay.get(self.state):

            self.elapsed_frames = 0

            # CHANGE TEXTURE
            self.entity.texture = self.texture.get(
                self.direction
            ).get(self.state).get(self.current_frame)

            total_frames = self.total_textures.get(self.state)

            # LOOP ANIMATION FRAMES
            self.current_frame = (self.current_frame+1) % total_frames

    def update(self):

        self.gun.direction = self.direction
        self.gun.animate_bullet()

        """
            The state spans across multiple frames
            one case may repeat many times.
            
            If-statement to limit unnecessary repeatition
        """
        match self.state:

            case "idle":

                # REPEAT IDLE ANIMATION
                self.update_texture_loop()

            case "run":

                speed = self.SPEED * Time.dt

                if self.direction == "Left":
                    self.entity.x -= speed

                elif self.entity.x <= 0:
                    self.entity.x += speed

                self.update_texture_loop()

            case "fire":

                self.aiming_timer = 0

                # FIRE A BULLET IF MAGAZINE NOT EMPTY
                if self.gun.total_ammo_mag > 0:

                    # SYNC BULLET AND FIRING ANIMATION

                    # IF NO ANIMATION PLAYED, SPAWN ONE BULLET
                    if self.is_gun_triggered and not self.is_animating:
                        self.update_texture()
                        self.gun.spawn_bullet()
                        self.gun.shoot_sound.play()
                        self.is_gun_triggered = False

                # MAG IS EMPTY, RELOAD
                elif self.gun.total_ammo >= self.gun.SHOTGUN_CAPACITY:
                    self.aiming_timer = 0
                    self.state = "reload"
                    self.gun.reload_sound.play()

                # NO MORE AMMO, KEEP AIMING
                elif self.gun.total_ammo == 0:
                    self.gun.empty_sound.play()
                    self.state = "aim"

                self.update_texture()

            case "reload":

                self.update_texture()

                # RELOAD AMMO ONCE RELOADING-ANIMATION ENDED
                if self.gun.total_ammo_mag != self.gun.SHOTGUN_CAPACITY:
                    if not self.is_animating:
                        self.gun.loaded_sound.play()
                        self.gun.reload()

            case "aim":

                self.aiming_timer += Time.dt
                self.entity.texture = self.texture.get(
                    self.direction).get("aim").get(0)

                # PAUSE ANIMATION FOR SOME TIME THEN BACK TO IDLE
                if self.aiming_timer >= 60 * 1.1 * Time.dt:
                    self.state = "idle"

    def position_on_origin(self):

        # WHILE RUNNING AND REACHED MIDDLE SCREEN
        return True if self.entity.x > 0 and self.state == "run" else False
