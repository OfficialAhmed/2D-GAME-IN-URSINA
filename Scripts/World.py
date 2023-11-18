
class Scene:

    def __init__(self) -> None:
        self.current_frame = 0
        self.elapsed_frames = 0

    def stage_1(self) -> dict:
        return {
            "fg": "Assets/Stage/ground.png",
            "bg": "Assets/Stage/background.png",
        }
