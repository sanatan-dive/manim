from manim import *

config.pixel_height = 1080
config.pixel_width = 1920
config.frame_rate = 30

class SineWaveAnimation(Scene):
    def construct(self):
        config.frame_width = 16
        config.frame_height = 9

        # Title
        title = Text("Sine Wave Animation", font_size=48)
        title.move_to(UP * 3.5)
        self.play(Write(title))

        # Axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-1.5, 1.5, 0.5],
            x_length=10,
            y_length=3,
            axis_config={"color": BLUE_E},
        )
        axes.move_to(DOWN * 0.5)
        x_label = axes.get_x_axis_label("x", edge=RIGHT, direction=DR, buff=0.5)
        y_label = axes.get_y_axis_label("y", edge=UP, direction=UR, buff=0.5)
        labels = VGroup(x_label, y_label)

        self.play(Create(axes), Write(labels))

        # Sine Wave
        sine_wave = axes.plot(lambda x: np.sin(x), color=GREEN_E, stroke_width=3)
        self.play(Create(sine_wave))

        # Moving Dot
        dot = Dot(axes.c2p(0, np.sin(0)), color=RED_E)
        self.play(Create(dot))

        # Value tracker for x-coordinate
        x_tracker = ValueTracker(0)

        # Updater function for the dot
        def update_dot(mob, dt):
            x_value = x_tracker.get_value()
            mob.move_to(axes.c2p(x_value, np.sin(x_value)))

        dot.add_updater(update_dot)

        # Animate the x_tracker to move the dot along the sine wave
        self.play(x_tracker.animate.set_value(10), run_time=5, rate_func=linear)
        self.wait(1)

        # Remove the updater
        dot.remove_updater(update_dot)
        self.play(FadeOut(dot))

        # Another sine wave with transformation
        sine_wave2 = axes.plot(lambda x: 0.5 * np.sin(2 * x), color=YELLOW_E, stroke_width=3)
        self.play(Transform(sine_wave, sine_wave2))
        self.wait(1)

        # Fade out everything
        self.play(FadeOut(title, axes, sine_wave, labels))
        self.wait(0.5)

        # Footer
        footer = Text("Created with Manim", font_size=24, color=GRAY_E)
        footer.move_to(DOWN * 3.5)
        self.play(Write(footer))
        self.wait(1)
        self.play(FadeOut(footer))