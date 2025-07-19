from manim import *
import numpy as np

class BouncingBallSineWave(Scene):
    def construct(self):
        # Define the sine wave
        axes = Axes(
            x_range=[0, 2 * PI, PI / 2],
            y_range=[-1.5, 1.5, 1],
            axis_config={"include_numbers": True},
        )
        sine_wave = axes.plot(lambda x: np.sin(x), color=BLUE)

        # Define the bouncing ball
        ball = Circle(radius=0.2, color=RED, fill_opacity=1.0)
        ball.move_to(axes.c2p(0, 1))  # Start at the peak

        # Initial position and velocity
        x_pos = 0
        y_pos = 1
        velocity = -2  # Initial downward velocity
        gravity = 2

        # Updater function for the ball's position
        def update_ball(mob, dt):
            nonlocal x_pos, y_pos, velocity

            # Update velocity due to gravity
            velocity += gravity * dt

            # Update position
            y_pos += velocity * dt

            # Bounce when reaching the sine wave
            sine_y = np.sin(x_pos)
            if y_pos <= sine_y:
                y_pos = sine_y
                velocity = -velocity * 0.8  # Reverse velocity with some energy loss

            x_pos += 0.5 * dt  # Constant horizontal movement

            # Ensure x_pos stays within the sine wave bounds
            if x_pos > 2 * PI:
                x_pos = 0
                y_pos = 1
                velocity = -2  # Reset

            mob.move_to(axes.c2p(x_pos, y_pos))

        ball.add_updater(update_ball)

        # Add everything to the scene
        self.add(axes, sine_wave, ball)
        self.wait(5)  # Run the animation for 5 seconds
        ball.remove_updater(update_ball)