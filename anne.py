import numpy as np
from manim import *

# Define a list of colors and corresponding temperatures for cube glow.
TEMP_COLORS_CUBE = [
    (0, RED_E),       # Start red
    (1, RED_D),
    (2, ORANGE),
    (3, YELLOW_E),
    (4, YELLOW_D),
    (5, WHITE)        # End white
]

class Anim1_BlackCubeAbsorption(ThreeDScene):
    """
    Animation 1: Black cube getting hit by various colored light beams,
    absorbs them, then starts to glow from red to white.
    """
    def construct(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES, distance=8)
        self.camera.background_color = BLACK

        # Black Cube
        cube = Cube(side_length=2, fill_color=BLACK, fill_opacity=1, stroke_color=DARK_GRAY)
        cube_label = Tex("Black Body (Cube)", font_size=36).next_to(cube, DOWN, buff=0.5)
        self.play(Create(cube), Write(cube_label))
        self.wait(0.5)

        # Light beams
        beam_colors = [BLUE, GREEN, YELLOW, ORANGE, RED]
        beam_start_points = [
            UP * 3 + LEFT * 3 + OUT * 1,
            UP * 3 + RIGHT * 3 + OUT * 1,
            DOWN * 1 + LEFT * 3 + OUT * 3,
            UP * 1 + RIGHT * 3 + OUT * 3,
            UP * 2 + LEFT * 1 + OUT * 4,
        ]

        beams = VGroup()
        for i, color in enumerate(beam_colors):
            # Target a point on the cube's surface
            target_point_on_cube = cube.get_center() + normalize(beam_start_points[i] - cube.get_center()) * -1 # a bit inside
            
            beam = Arrow(
                beam_start_points[i % len(beam_start_points)],
                target_point_on_cube, # Aim near the center
                stroke_width=8,
                color=color,
                max_tip_length_to_length_ratio=0.2,
                buff=0.1 
            )
            beams.add(beam)

        self.play(LaggedStart(*[GrowArrow(beam) for beam in beams], lag_ratio=0.3))
        self.wait(0.5)

        # Absorb beams
        self.play(LaggedStart(*[beam.animate.become(Dot(beam.get_end(), color=beam.color, radius=0.05)) for beam in beams], lag_ratio=0.2))
        self.play(LaggedStart(*[FadeOut(beam) for beam in beams], lag_ratio=0.1))
        self.wait(0.5)

        # Cube starts to glow
        glow_title = Tex("Cube heats up and glows...", font_size=36).to_edge(UP)
        self.play(ReplacementTransform(cube_label, glow_title))

        temp_tracker = ValueTracker(0)
        
        # Add an outer glow effect - a slightly larger, transparent cube
        outer_glow = Cube(side_length=2.2, fill_opacity=0, stroke_width=0)
        outer_glow.move_to(cube.get_center())
        
        initial_glow_color_idx = 0
        cube.add_updater(lambda m: m.set_fill(
            color=interpolate_color(
                TEMP_COLORS_CUBE[int(temp_tracker.get_value()) % len(TEMP_COLORS_CUBE)][1],
                TEMP_COLORS_CUBE[ (int(temp_tracker.get_value()) + 1) % len(TEMP_COLORS_CUBE)][1],
                temp_tracker.get_value() % 1
            ),
            opacity=1
        ))
        
        outer_glow.add_updater(lambda m: m.set_fill(
             color=interpolate_color(
                TEMP_COLORS_CUBE[int(temp_tracker.get_value()) % len(TEMP_COLORS_CUBE)][1],
                TEMP_COLORS_CUBE[ (int(temp_tracker.get_value()) + 1) % len(TEMP_COLORS_CUBE)][1],
                temp_tracker.get_value() % 1
            ),
            opacity=0.3 # Make outer glow transparent
        ).set_stroke(opacity=0))


        self.add(cube, outer_glow) # Add updaters first, then the mobject if it wasn't there

        self.play(temp_tracker.animate.set_value(len(TEMP_COLORS_CUBE) -1.01), run_time=5, rate_func=linear)
        
        cube.clear_updaters()
        outer_glow.clear_updaters()
        self.wait(2)
        self.play(FadeOut(cube), FadeOut(outer_glow), FadeOut(glow_title))


class Anim2_EMWave(ThreeDScene):
    """
    Animation 2: Two orthogonal E and B waves propagating.
    E-field oscillates vertically, B-field horizontally.
    Both move forward in the z-direction (out of the screen).
    """
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=-100 * DEGREES, distance=10)
        self.camera.background_color = BLACK
        
        axes = ThreeDAxes(
            x_range=[-1, 1, 0.5], x_length=3,
            y_range=[-1, 1, 0.5], y_length=3,
            z_range=[-3, 3, 1], z_length=6,
            axis_config={"include_tip": True, "include_numbers": False}
        )
        x_label = axes.get_x_axis_label("B_x")
        y_label = axes.get_y_axis_label("E_y")
        z_label = axes.get_z_axis_label("z (propagation)")
        labels = VGroup(x_label, y_label, z_label)
        self.add(axes, labels)

        # Parameters for the wave
        wavelength = 2.0
        k = TAU / wavelength  # Wave number
        amplitude = 0.8
        
        time = ValueTracker(0) # For animation of propagation
        omega = 2 * PI # Angular frequency (speed of phase change)

        # E-field wave (oscillates along Y, propagates along Z)
        # (z_pos, E_y, 0 in local wave coords, then rotated)
        # For a wave propagating along Z, E is in XY plane, B is in XY plane.
        # E_y = A * sin(k*z - omega*t)
        # B_x = A * sin(k*z - omega*t) (in phase for EM wave)
        
        e_field_color = BLUE
        b_field_color = GREEN

        # E-field: oscillates along Y, propagates along Z
        e_wave_func = lambda z: [0, amplitude * np.sin(k * z - omega * time.get_value()), z]
        e_wave = always_redraw(
            lambda: ParametricFunction(
                e_wave_func,
                t_range=[-3, 3, 0.1], # z-range
                color=e_field_color,
                stroke_width=3
            )
        )
        e_label = MathTex("E", color=e_field_color).next_to(e_wave, UP, buff=0.2, coor_mask=[0,1,0])


        # B-field: oscillates along X, propagates along Z
        b_wave_func = lambda z: [amplitude * np.sin(k * z - omega * time.get_value()), 0, z]
        b_wave = always_redraw(
            lambda: ParametricFunction(
                b_wave_func,
                t_range=[-3, 3, 0.1], # z-range
                color=b_field_color,
                stroke_width=3
            )
        )
        b_label = MathTex("B", color=b_field_color).next_to(b_wave, RIGHT, buff=0.2, coor_mask=[1,0,0])
        
        # Propagation vector (conceptual)
        prop_arrow_start_z = -3
        prop_arrow_end_z = 3
        propagation_vector = Arrow(
            axes.c2p(0,0,prop_arrow_start_z), axes.c2p(0,0,prop_arrow_end_z), 
            buff=0, color=YELLOW, stroke_width=4
        )
        prop_label = Tex("Propagation (k)", font_size=24, color=YELLOW).next_to(propagation_vector.get_end(), OUT + RIGHT*0.5)


        self.play(Create(e_wave), Create(b_wave), Write(e_label), Write(b_label))
        self.play(GrowArrow(propagation_vector), Write(prop_label))
        self.wait(1)

        # Animate propagation
        self.play(time.animate.set_value(2), run_time=4, rate_func=linear) # 2 full cycles if omega=TAU
        self.wait(1)
        self.play(FadeOut(VGroup(e_wave, b_wave, e_label, b_label, propagation_vector, prop_label, axes, labels)))


class Anim3_StickFigureDance(Scene):
    """
    Animation 3: Two stick figures with linked arm motions.
    """
    def construct(self):
        self.camera.background_color = BLACK

        # Helper to create a stick figure
        def create_stick_figure(color=WHITE):
            head = Circle(radius=0.3, color=color, fill_opacity=1)
            body = Line(UP * 0.3, DOWN * 1, color=color, stroke_width=6) # Body starts from bottom of head
            
            # Arms: shoulder point is top of body
            shoulder_point = body.get_start() 
            arm_length = 0.7
            left_arm = Line(shoulder_point, shoulder_point + LEFT * arm_length + DOWN * 0.2, color=color, stroke_width=5)
            right_arm = Line(shoulder_point, shoulder_point + RIGHT * arm_length + DOWN * 0.2, color=color, stroke_width=5)
            arms = VGroup(left_arm, right_arm)

            # Legs
            hip_point = body.get_end()
            leg_length = 0.8
            left_leg = Line(hip_point, hip_point + LEFT * 0.4 + DOWN * leg_length, color=color, stroke_width=5)
            right_leg = Line(hip_point, hip_point + RIGHT * 0.4 + DOWN * leg_length, color=color, stroke_width=5)
            legs = VGroup(left_leg, right_leg)
            
            figure = VGroup(head, body, arms, legs)
            figure.head = head
            figure.body = body
            figure.arms = arms # VGroup of left_arm, right_arm
            figure.legs = legs
            figure.shoulder_point = shoulder_point
            return figure

        kid1 = create_stick_figure(color=BLUE_A).shift(LEFT * 2.5)
        kid2 = create_stick_figure(color=GREEN_A).shift(RIGHT * 2.5)
        
        self.play(Create(kid1), Create(kid2))
        self.wait(0.5)

        # Animation parameters
        arm_angle_kid1 = ValueTracker(0) # For up-down motion
        arm_angle_kid2 = ValueTracker(0) # For side-to-side motion
        
        # Updaters for arm motion
        # Kid 1: Arms up and down (rotate around shoulder)
        kid1.arms[0].add_updater(lambda m: m.become(
            Line(kid1.shoulder_point, 
                 kid1.shoulder_point + rotate_vector(LEFT*0.7 + DOWN*0.2, arm_angle_kid1.get_value() * np.sin(self.renderer.time * 2*PI*0.5)), # 0.5 Hz
                 color=kid1.arms[0].get_color(), stroke_width=5)
        ))
        kid1.arms[1].add_updater(lambda m: m.become(
            Line(kid1.shoulder_point, 
                 kid1.shoulder_point + rotate_vector(RIGHT*0.7 + DOWN*0.2, -arm_angle_kid1.get_value() * np.sin(self.renderer.time * 2*PI*0.5)),
                 color=kid1.arms[1].get_color(), stroke_width=5)
        ))

        # Kid 2: Arms side to side (rotate around shoulder, different axis)
        # For side-to-side, let's pivot from a slightly different initial pose or use a different rotation logic
        # Simpler: move endpoints horizontally
        kid2_arm_amplitude = 0.5
        kid2.arms[0].add_updater(lambda m: m.put_start_and_end_on(
            kid2.shoulder_point,
            kid2.shoulder_point + DOWN*0.2 + LEFT*0.7 + RIGHT * kid2_arm_amplitude * np.sin(self.renderer.time * 2*PI*0.5 + PI/2) # 90 deg phase offset
        ))
        kid2.arms[1].add_updater(lambda m: m.put_start_and_end_on(
            kid2.shoulder_point,
            kid2.shoulder_point + DOWN*0.2 + RIGHT*0.7 + LEFT * kid2_arm_amplitude * np.sin(self.renderer.time * 2*PI*0.5 + PI/2)
        ))


        self.add(kid1, kid2) # Add them so updaters start
        self.play(arm_angle_kid1.animate.set_value(PI/4), run_time=3, rate_func=linear) # Kid1 starts flailing
        self.wait(0.5)
        
        # Show motion lines (conceptual)
        # Using ShowPassingFlash on a path the hand traces might be too complex for simple stick figures.
        # Instead, let's add simple lines indicating motion.
        motion_label = Tex("Linked Motion & Timing", font_size=30).to_edge(UP)
        self.play(Write(motion_label))

        # Kids move forward together
        self.play(
            kid1.animate.shift(RIGHT * 1.5 + UP*0.2), 
            kid2.animate.shift(RIGHT * 1.5 + UP*0.2),
            arm_angle_kid1.animate.set_value(PI/3), # Continue flailing
            run_time=3
        )
        self.wait(1)

        # Control panel concept: Change speed
        control_text = Tex("Speed Control: Normal", font_size=28).next_to(motion_label, DOWN)
        self.play(Write(control_text))
        self.wait(1)
        
        # Simulate faster speed - this requires changing the frequency in updaters,
        # which is tricky with lambda functions capturing self.renderer.time.
        # A simpler way is to re-define updaters or use a speed factor if ValueTracker was used for time.
        # For this demo, we'll just animate faster for a bit by changing the ValueTracker rate.
        # This part is more illustrative than a true interactive control.
        
        # To truly change speed, the frequency in sin(self.renderer.time * FREQ) needs to change.
        # This is hard with current updater setup. A full "control panel" is beyond scope here.
        # We'll just imply linked motion by them moving together and starting arm motion.
        
        kid1.clear_updaters() # Stop current motion
        kid2.clear_updaters()
        self.play(FadeOut(motion_label), FadeOut(control_text))
        self.wait(1)
        self.play(FadeOut(kid1), FadeOut(kid2))


class Anim4_EMWaveInSpace(ThreeDScene):
    """
    Animation 4: EM wave from earlier propagating through space,
    passing stars or black body objects like the sun.
    """
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-110 * DEGREES, distance=18)
        self.camera.background_color = BLACK
        
        # Parameters for the wave
        wavelength = 3.0
        k = TAU / wavelength
        amplitude = 1.0
        time = ValueTracker(0)
        omega = TAU # Speed of phase change

        # EM Wave (similar to Anim2, but will move as a whole)
        z_range_wave = [-5, 5]
        e_wave_func = lambda z: [amplitude * np.sin(k * z), 0, z] # E along X
        b_wave_func = lambda z: [0, amplitude * np.sin(k * z), z] # B along Y
        
        # Group for the EM wave that will propagate
        em_wave_group = VGroup()
        
        current_e_wave = ParametricFunction(e_wave_func, t_range=z_range_wave, color=BLUE, stroke_width=3)
        current_b_wave = ParametricFunction(b_wave_func, t_range=z_range_wave, color=GREEN, stroke_width=3)
        
        # Rotate to propagate along X axis (E in Y, B in Z)
        current_e_wave.rotate(PI/2, axis=UP).rotate(PI/2, axis=RIGHT) # E along Y
        current_b_wave.rotate(PI/2, axis=UP) # B along Z
        
        em_wave_visual = VGroup(current_e_wave, current_b_wave)
        em_wave_group.add(em_wave_visual)

        # Propagation arrow attached to the wave group
        prop_arrow = Arrow(ORIGIN, RIGHT * (z_range_wave[1]-z_range_wave[0]), color=YELLOW, buff=0)
        em_wave_group.add(prop_arrow)
        em_wave_group.move_to(LEFT * 10) # Start off-screen

        self.add(em_wave_group)

        # Add stars/sun
        sun = Sphere(radius=1.5, center=RIGHT*2+UP*1).set_color(YELLOW_D).set_sheen(0.5,DR)
        star1 = Sphere(radius=0.5, center=LEFT*3+UP*2+OUT*2).set_color(BLUE_B).set_sheen(0.3,UL)
        star2 = Sphere(radius=0.7, center=RIGHT*5+DOWN*2+IN*1).set_color(RED_B).set_sheen(0.3,DL)
        celestial_bodies = VGroup(sun, star1, star2)
        self.play(LaggedStartMap(Create, celestial_bodies, lag_ratio=0.5))

        # Animate EM wave propagating past objects
        # We'll use an updater for the internal oscillation and .animate for group movement
        def wave_updater(mobj, dt):
            # mobj is em_wave_visual here
            new_time = time.get_value() + omega * dt
            time.set_value(new_time) # Update time for next frame
            
            # Recreate waves based on new time for oscillation effect
            # This is phase shift for oscillation, not group movement
            phase_shift = omega * time.get_value()
            
            e_osc_func = lambda z_local: [0, amplitude * np.sin(k * z_local - phase_shift), z_local]
            b_osc_func = lambda z_local: [amplitude * np.sin(k * z_local - phase_shift), 0, z_local] # B along X, E along Y
            
            # If E along Y, B along Z, prop along X:
            # E: (0, A*sin(k*x - phase), x)
            # B: (0, 0, A*sin(k*x - phase), x)
            # This needs careful coordinate definition.
            # Let's simplify: the wave shape is fixed, and the group moves.
            # The "propagation" shown by Anim2 was phase shift. Here it's group movement.
            pass # For now, the wave shape is static within the group as it moves

        # For this animation, let's make the wave appear to move through space.
        # The internal oscillation (phase shift) is less critical than the group's movement.
        
        self.play(em_wave_group.animate.shift(RIGHT * 20), run_time=8, rate_func=linear)
        self.wait(1)
        self.play(FadeOut(em_wave_group), FadeOut(celestial_bodies))


class Anim5_LightInteraction(Scene):
    """
    Animation 5: Light beam interaction with a surface (reflection, absorption, transmission).
    """
    def construct(self):
        self.camera.background_color = BLACK

        # Surface
        surface = Line(LEFT * 3, RIGHT * 3, color=GRAY, stroke_width=5).shift(DOWN*1)
        surface_label = Tex("Surface", font_size=24).next_to(surface, DOWN, buff=0.2)
        self.play(Create(surface), Write(surface_label))

        # Incident Light
        incident_start_point = UP * 2.5 + LEFT * 2.5
        incident_end_point = surface.get_center() + LEFT*0.5 # Hit slightly left of center
        
        incident_ray = Arrow(incident_start_point, incident_end_point, buff=0.1, color=YELLOW, stroke_width=6)
        incident_label = Tex("Incident Light", font_size=28, color=YELLOW).next_to(incident_ray.get_start(), UP+LEFT, buff=0.1)
        
        self.play(GrowArrow(incident_ray), Write(incident_label))
        self.wait(0.5)

        # Point of impact
        impact_point = incident_ray.get_end()
        impact_dot = Dot(impact_point, color=YELLOW, radius=0.08)
        self.play(FadeIn(impact_dot, scale=0.5))

        # Normal line
        normal_line = DashedLine(impact_point, impact_point + UP * 1.5, color=WHITE, stroke_width=2)
        self.play(Create(normal_line))

        # Reflected Ray
        # Angle of incidence = angle of reflection
        incoming_vector = incident_ray.get_vector()
        surface_normal_vector = normalize(UP) # For horizontal surface
        
        # Reflection: R = I - 2 * dot(I, N) * N
        reflected_vector = incoming_vector - 2 * np.dot(incoming_vector, surface_normal_vector) * surface_normal_vector
        reflected_ray = Arrow(impact_point, impact_point + normalize(reflected_vector) * 2.5, buff=0, color=ORANGE, stroke_width=5)
        reflected_label = Tex("Reflected", font_size=24, color=ORANGE).next_to(reflected_ray.get_end(), UP + reflected_vector[0]*RIGHT, buff=0.1)

        self.play(GrowArrow(reflected_ray), Write(reflected_label))
        self.wait(0.5)

        # Absorbed Component
        # Show by dimming incident ray or surface heating up slightly
        absorption_effect = Circle(radius=0.3, color=RED, fill_opacity=0.5).move_to(impact_point)
        absorbed_label = Tex("Absorbed", font_size=24, color=RED).next_to(impact_point, DOWN, buff=0.3)
        
        self.play(FadeIn(absorption_effect, scale=0.1), Write(absorbed_label))
        self.play(FadeOut(absorption_effect, scale=5), FadeOut(absorbed_label, shift=DOWN*0.2), run_time=1) # Quick flash
        self.wait(0.2)

        # Transmitted Ray (if surface is semi-transparent)
        # For simplicity, assume some transmission straight through, but dimmed
        transmitted_vector = incoming_vector # Assuming no refraction for simplicity, or surface is parallel
        transmitted_ray = Arrow(impact_point, impact_point + normalize(transmitted_vector) * 2.0, buff=0, color=LIGHT_GREY, stroke_width=4, stroke_opacity=0.7)
        transmitted_label = Tex("Transmitted", font_size=24, color=LIGHT_GREY).next_to(transmitted_ray.get_end(), DOWN + transmitted_vector[0]*RIGHT, buff=0.1)
        
        # Make surface slightly transparent for this part
        self.play(surface.animate.set_opacity(0.5))
        self.play(GrowArrow(transmitted_ray), Write(transmitted_label))
        self.wait(2)
        
        self.play(
            FadeOut(VGroup(incident_ray, incident_label, impact_dot, normal_line)),
            FadeOut(VGroup(reflected_ray, reflected_label)),
            FadeOut(VGroup(transmitted_ray, transmitted_label)),
            FadeOut(surface), FadeOut(surface_label)
        )
        self.wait(1)

