import numpy as np
from manim import *

class SunAndSquareScene(Scene): # Changed from ThreeDScene to Scene for 2D
    def construct(self):
        # Set a dark background, similar to the image
        self.camera.background_color = BLACK

        # 1. Ground Line
        ground_line = Line(LEFT * 5.5, RIGHT * 5.5, color=WHITE, stroke_width=2)
        # Position it lower on the screen, leaving space for objects
        ground_line.move_to(DOWN * 2.5) 

        # 2. Sun
        sun_center_pos = UP * 2.8 + LEFT * 4.8
        sun_body = Circle(radius=0.7, color=YELLOW_D, fill_opacity=1, stroke_width=0).move_to(sun_center_pos)
        
        sun_rays = VGroup()
        num_rays = 8
        ray_length_short = 0.4
        ray_length_long = 0.8
        ray_width = 8 # Make rays a bit thicker

        for i in range(num_rays):
            angle = (TAU / num_rays) * i + (TAU / (num_rays * 2)) # Offset angle for better appearance
            # Start point slightly outside the sun body for a cleaner look
            start_offset_factor = 1.1 
            start_point = sun_body.get_center() + sun_body.radius * start_offset_factor * np.array([np.cos(angle), np.sin(angle), 0])
            current_ray_length = ray_length_long if i % 2 == 0 else ray_length_short
            end_point = start_point + current_ray_length * np.array([np.cos(angle), np.sin(angle), 0])
            ray = Line(start_point, end_point, color=YELLOW_D, stroke_width=ray_width)
            sun_rays.add(ray)
        
        sun = VGroup(sun_body, sun_rays)

        # 3. Red Square (instead of Cube)
        square_side_length = 1.2
        # Position the square so its bottom edge is on the ground_line
        red_square = Square(side_length=square_side_length, fill_color=RED_C, fill_opacity=0.9, stroke_color=RED_E, stroke_width=3)
        red_square.next_to(ground_line, UP, buff=0) # Place bottom edge on ground_line
        red_square.shift(LEFT * 0.5) # Move it slightly left of center

        # 4. Light beam from Sun to Square
        # Create a Polygon for the beam. Points are defined from sun towards square.
        # Adjust points for a nice visual connection.
        beam_start_width_factor = 0.4
        beam_end_width_factor = 0.6

        # Points near the sun, fanning out slightly
        sun_edge_point = sun_body.get_center() + normalize(red_square.get_top() - sun_body.get_center()) * sun_body.radius
        # Corrected beam_p1 and beam_p2 to use sun_edge_point consistently
        beam_p1 = sun_edge_point + rotate_vector(normalize(red_square.get_center() - sun_body.get_center()), -TAU/32) * beam_start_width_factor 
        beam_p2 = sun_edge_point + rotate_vector(normalize(red_square.get_center() - sun_body.get_center()), TAU/32) * beam_start_width_factor
        
        # Points on the square (top edge)
        beam_p3 = red_square.get_corner(UL) + RIGHT * (square_side_length * (1-beam_end_width_factor)/2 + 0.1) # Adjusted for visual fit
        beam_p4 = red_square.get_corner(UR) + LEFT * (square_side_length * (1-beam_end_width_factor)/2 + 0.1)  # Adjusted for visual fit
        
        light_beam = Polygon(
            beam_p1, beam_p2, beam_p4, beam_p3, # Order matters for polygon vertices
            fill_color=YELLOW,
            fill_opacity=0.25,
            stroke_width=0
        )

        # Animations
        self.play(Create(ground_line), run_time=1)
        self.play(Create(sun), run_time=1)
        self.play(Create(red_square), run_time=1)
        # Animate light beam appearing from sun towards square
        self.play(GrowFromPoint(light_beam, sun_body.get_center()), run_time=0.7)
        # Thermometer creation and animation are removed
        
        self.wait(2)
