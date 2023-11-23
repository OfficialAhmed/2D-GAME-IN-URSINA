from ursina import Sprite, Audio, Keys
from ursina import time as Time

from ursina import destroy as Destroy
from ursina import load_texture as LoadTexture

from .World import Fps
from .Interface import Ui


class Weapon:

    # _____   CONSTANTS   ____________
    DRAG = 9                # BULLET DEDUCTION SPEED
    SPEED = 6               # BULLET LIMIT SPEED
    VELOCITY = 15           # BULLET STARTING SPEED

    def __init__(
        self,
        entity,
        ui,
        capacity,
        total_ammo,
        total_ammo_mag,
        weapon_y_pos,
        max_range
    ) -> None:

        self.ui: Ui = ui
        self.entity = entity

        self.bullets = []
        self.direction = "Right"

        self.capacity = capacity
        self.max_range = max_range
        self.total_ammo = total_ammo
        self.weapon_y_pos = weapon_y_pos
        self.total_ammo_mag = total_ammo_mag

        self.shoot_sound = Audio("Assets/Sound/Gun/Shotgun/shoot.mp3", False)
        self.empty_sound = Audio("Assets/Sound/Gun/Shotgun/empty.mp3", False)
        self.reload_sound = Audio("Assets/Sound/Gun/Shotgun/reload.mp3", False)
        self.loaded_sound = Audio("Assets/Sound/Gun/Shotgun/loaded.mp3", False)

    def reload(self):

        # RELOAD IF SUFFICIENT AMMO AVAILABLE
        if self.total_ammo >= self.capacity:

            # RELOAD GUN
            self.total_ammo -= self.capacity
            self.total_ammo_mag = self.capacity

            # UPDATE AMMO ON SCREEN (UI)
            self.ui.update_ammo(self.total_ammo)
            self.ui.update_mag_capacity(self.total_ammo_mag)

    def spawn_bullet(self):

        # TRACK THE BULLET DATA TO ANIMATE INDIVIDUALLY
        self.bullets.append(
            {
                "direction":    self.direction,
                "speed":        self.VELOCITY,
                "bullet":       Sprite(
                    scale=0.1,
                    position=(
                        self.entity.x,
                        self.weapon_y_pos
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
            if abs(bullet["bullet"].x - self.entity.x) >= self.max_range:
                Destroy(bullet["bullet"])
                self.bullets.pop(index)
                continue

            # COLLISION WITH ENEMY

            # TODO: CHECK COLLISION WITH ENEMIES


class Character(Fps):

    def __init__(self) -> None:
        super().__init__()

        self.SPEED = 1.7

        self.aiming_timer = 0               # TO HOLD DURATION OF THE AIMING FRAME
        self.is_animating = False           # TO DETERMINE WHETHER ANIMATION LOOP ENDED
        self.is_gun_triggered = False       # TO DISABLE MULTIPLE SHOOTING

        self.state = "idle"
        self.direction = "Right"
        self.elapsed_loop_duration = 0

        self.last_fire_frame = 0
        self.fire_cooldown = 0.3

        # DELAY BETWEEN EACH TEXTURE FRAME
        # SOME AFFECT THE STATE SPEED, OTHER AFFECT THE ANIMATION SPEED ONLY
        self.texture_delay = {
            "idle":         0.08,       # IDLE ANIMATION SPEED
            "run":          0.08,       # RUNNING ANIMATION SPEED
            "walk":         0.08,       # WALKING ANIMATION SPEED
            "fire":         0.03,       # FIRING SPEED
            "reload":       0.17,       # RELOADING SPEED
        }

        # OVERWRITTEN BY THE INSTANCE
        self.weapon:            Weapon = None
        self.entity:            Sprite = None
        self.texture:           dict = {}
        self.total_textures:    dict = {}

    def update_texture(self):
        """
            UPDATES THE TEXTURE OF THE CHARACTER IN ONE LOOP ONLY
        """

        # AIMING IS ONE FRAME NOT AN ANIMATION
        if self.state == "aim":
            return

        if self.elapsed_frames >= self.texture_delay.get(self.state):
            self.elapsed_frames = 0

            # CHANGE TEXTURE
            self.entity.texture = self.texture.get(
                self.direction
            ).get(self.state).get(self.current_frame)

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
        """
            UPDATES THE TEXTURE IN REPEAT MODE
        """

        # IF PASSED THE ANIMATION DURATION
        if self.elapsed_frames >= self.texture_delay.get(self.state):

            self.elapsed_frames = 0
            total_frames = self.total_textures.get(self.state)

            # CHANGE TEXTURE
            self.entity.texture = self.texture.get(
                self.direction
            ).get(self.state).get(self.current_frame)

            # LOOP ANIMATION FRAMES
            self.current_frame = (self.current_frame + 1) % total_frames

    def update(self):
        """
            CHECKS THE STATE OF THE CHARACTER AND UPDATE THE ANIMATION
        """

        self.weapon.direction = self.direction
        self.weapon.animate_bullet()

        """
            The state spans across multiple frames
            one case may repeat many times.
            
            If-statement to limit unnecessary repeatition
        """
        match self.state:

            case "idle":

                # REPEAT IDLE ANIMATION
                self.update_texture_loop()

            case "run" | "walk":

                speed = self.SPEED * Time.dt
                if self.state == "walk":
                    speed /= 2

                if self.direction == "Left":
                    self.entity.x -= speed

                elif self.entity.x <= 0:
                    self.entity.x += speed

                self.update_texture_loop()

            case "fire":

                self.aiming_timer = 0

                # FIRE A BULLET IF MAGAZINE NOT EMPTY
                if self.weapon.total_ammo_mag > 0:

                    # SYNC BULLET AND FIRING ANIMATION

                    # IF NO ANIMATION PLAYED, SPAWN ONE BULLET
                    if self.is_gun_triggered and not self.is_animating:
                        self.update_texture()
                        self.weapon.spawn_bullet()
                        self.weapon.shoot_sound.play()
                        self.is_gun_triggered = False

                # MAG IS EMPTY, RELOAD
                elif self.weapon.total_ammo >= self.weapon.capacity:
                    self.aiming_timer = 0
                    self.state = "reload"
                    self.weapon.reload_sound.play()

                # NO MORE AMMO, KEEP AIMING
                elif self.weapon.total_ammo == 0:
                    self.weapon.empty_sound.play()
                    self.state = "aim"

                self.update_texture()

            case "reload":

                self.update_texture()

                # RELOAD AMMO ONCE RELOADING-ANIMATION ENDED
                if self.weapon.total_ammo_mag != self.weapon.capacity:
                    if not self.is_animating:
                        self.weapon.loaded_sound.play()
                        self.weapon.reload()

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


class Player(Character):

    def __init__(self, entity: Sprite, ui: Ui) -> None:
        super().__init__()

        self.entity = entity

        self.MAX_RANGE = 7           # BULLET DISTANCE
        self.SHOTGUN_CAPACITY = 4    # MAGAZINE CAPACITY
        self.WEAPON_Y_POS = -2.1

        self.total_ammo = 20
        self.total_ammo_mag = self.SHOTGUN_CAPACITY

        self.weapon = Weapon(
            entity, ui, self.SHOTGUN_CAPACITY, self.total_ammo, self.total_ammo_mag, self.WEAPON_Y_POS, self.MAX_RANGE
        )

        ui.render_money(50)
        ui.render_armor(100)
        ui.render_health(100)
        ui.render_ammo(self.total_ammo)
        ui.render_mag_capacity(self.total_ammo_mag)

        self.total_textures = {
            "idle":     5,
            "run":      7,
            "fire":     11,
            "reload":   11,
            "aim":      1
        }

        self.texture = {
            "Right": {
                "idle":       {i: LoadTexture(f"Assets/Animation/Char/Idle/Right/{i}.png") for i in range(self.total_textures.get("idle")+1)},
                "run":        {i: LoadTexture(f"Assets/Animation/Char/Run/Right/{i}.png") for i in range(self.total_textures.get("run")+1)},
                "fire":       {i: LoadTexture(f"Assets/Animation/Char/Attack/Fire/Right/{i}.png") for i in range(self.total_textures.get("fire")+1)},
                "reload":     {i: LoadTexture(f"Assets/Animation/Char/Attack/Reload/Right/{i}.png") for i in range(self.total_textures.get("reload")+1)},
                "aim":        {0: LoadTexture(f"Assets/Animation/Char/Attack/Fire/Right/0.png")},
            },
            "Left": {
                "idle":       {i: LoadTexture(f"Assets/Animation/Char/Idle/Left/{i}.png") for i in range(self.total_textures.get("idle")+1)},
                "run":        {i: LoadTexture(f"Assets/Animation/Char/Run/Left/{i}.png") for i in range(self.total_textures.get("run")+1)},
                "fire":       {i: LoadTexture(f"Assets/Animation/Char/Attack/Fire/Left/{i}.png") for i in range(self.total_textures.get("fire")+1)},
                "reload":     {i: LoadTexture(f"Assets/Animation/Char/Attack/Reload/Left/{i}.png") for i in range(self.total_textures.get("reload")+1)},
                "aim":        {0: LoadTexture(f"Assets/Animation/Char/Attack/Fire/Left/0.png")},
            },
        }

    def controller(self, key):

        match key:
            case Keys.right_arrow:
                self.state = "run"
                self.direction = "Right"

            case Keys.right_arrow_up:
                self.state = "idle"

            case Keys.left_arrow:
                self.state = "run"
                self.direction = "Left"

            case Keys.left_arrow_up:
                self.state = "idle"

            case "space":

                # COOLDOWN FIRING
                if (self.last_fire_frame) >= self.fire_cooldown:

                    # CANNOT FIRE WHILE RELOADING
                    if self.state != "reload":

                        self.state = "fire"
                        self.last_fire_frame = 0
                        self.is_gun_triggered = True


class Enemy(Character):

    def __init__(self, entity: Sprite, ui: Ui) -> None:
        super().__init__()

        self.entity = entity

        self.direction = "Right"
        self.state = "idle"
        self.current_frame = 0

        self.total_textures = {
            "idle":     7,
            "walk":     7,
            "run":      7,
            "fire":     11,
            "reload":   11,
            "aim":      1
        }

        self.texture = {
            "Right": {
                "idle":       {i: LoadTexture(f"Assets/Animation/Soldier/Idle/Right/{i}.png") for i in range(self.total_textures.get("idle")+1)},
                "walk":       {i: LoadTexture(f"Assets/Animation/Soldier/Walk/Right/{i}.png") for i in range(self.total_textures.get("walk")+1)},
                # "run":        {i: LoadTexture(f"Assets/Animation/Soldier/Run/Right/{i}.png") for i in range(self.total_textures.get("run")+1)},
                # "fire":       {i: LoadTexture(f"Assets/Animation/Soldier/Attack/Fire/Right/{i}.png") for i in range(self.total_textures.get("fire")+1)},
                # "reload":     {i: LoadTexture(f"Assets/Animation/Soldier/Attack/Reload/Right/{i}.png") for i in range(self.total_textures.get("reload")+1)},
                # "aim":        {0: LoadTexture(f"Assets/Animation/Soldier/Attack/Fire/Right/0.png")},
            },

            "Right": {
                "idle":       {i: LoadTexture(f"Assets/Animation/Soldier/Idle/Left/{i}.png") for i in range(self.total_textures.get("idle")+1)},
                "walk":       {i: LoadTexture(f"Assets/Animation/Soldier/Walk/Left/{i}.png") for i in range(self.total_textures.get("walk")+1)},
                # "run":        {i: LoadTexture(f"Assets/Animation/Soldier/Run/Left/{i}.png") for i in range(self.total_textures.get("run")+1)},
                # "fire":       {i: LoadTexture(f"Assets/Animation/Soldier/Attack/Fire/Left/{i}.png") for i in range(self.total_textures.get("fire")+1)},
                # "reload":     {i: LoadTexture(f"Assets/Animation/Soldier/Attack/Reload/Left/{i}.png") for i in range(self.total_textures.get("reload")+1)},
                # "aim":        {0: LoadTexture(f"Assets/Animation/Soldier/Attack/Fire/Left/0.png")},
            },
        }

        self.weapon = Weapon(
            entity, ui, 5, 10, 2, (1, -1), 5
        )

        self.frames_per_state = 2       # FRAMES LIMIT TO CHANGE STATE
        self.ai_elapsed_frames = 0      # HOLDS FPS FOR THE AI MOVEMENT

    def update_ai(self):

        self.ai_elapsed_frames += Time.dt
        print(self.direction)

        if self.ai_elapsed_frames >= self.frames_per_state:
            if self.state == "idle":
                self.direction = "Left" if self.direction == "Right" else "Right"
                self.state = "walk"

            elif self.state == "walk":
                self.state = "idle"

            self.ai_elapsed_frames = 0

        self.update()

    def controller(self, key):

        match key:
            case Keys.right_arrow:
                self.state = "run"
                self.direction = "Right"

            case Keys.right_arrow_up:
                self.state = "idle"

            case Keys.left_arrow:
                self.state = "run"
                self.direction = "Left"

            case Keys.left_arrow_up:
                self.state = "idle"

            case "space":

                # COOLDOWN FIRING
                if (self.last_fire_frame) >= self.fire_cooldown:

                    # CANNOT FIRE WHILE RELOADING
                    if self.state != "reload":

                        self.state = "fire"
                        self.last_fire_frame = 0
                        self.is_gun_triggered = True

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
