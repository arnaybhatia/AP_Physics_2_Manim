import numpy as np
from manim import *

# Define a list of colors and corresponding temperatures for cube glow (not used in Anim2 but kept from original context).
TEMP_COLORS_CUBE = [
    (0, RED_E),       # Start red
    (1, RED_D),
    (2, ORANGE),
    (3, YELLOW_E),
    (4, YELLOW_D),
    (5, WHITE)        # End white
]

class Anim1_BlackCubeAbsorption(Scene):
    """
    Animation 1: Black square getting hit by various colored light beams,
    absorbs them, then starts to glow from red to white.
    """
    def construct(self):
        self.camera.background_color = BLACK

        # Black Square (was Cube)
        square = Square(side_length=2.5, fill_color=BLACK, fill_opacity=1, stroke_color=DARK_GRAY, stroke_width=2)
        square_label = Tex("Black Body (Square)", font_size=36).next_to(square, DOWN, buff=0.5)
        self.play(Create(square), Write(square_label))
        self.wait(0.5)

        # Light beams
        beam_colors = [BLUE_C, GREEN_C, YELLOW_C, ORANGE, RED_C]
        # Adjusted start points for 2D
        beam_start_points = [
            UP * 3 + LEFT * 3.5,
            UP * 3 + RIGHT * 3.5,
            DOWN * 1 + LEFT * 4,
            UP * 1 + RIGHT * 4,
            UP * 3.5 + LEFT * 0,
        ]

        beams = VGroup()
        for i, color in enumerate(beam_colors):
            # Target a point on the square's perimeter or slightly inside
            target_direction = normalize(square.get_center() - beam_start_points[i])
            target_point_on_square = beam_start_points[i] + target_direction * (np.linalg.norm(square.get_center() - beam_start_points[i]) - square.side_length*0.4)


            beam = Arrow(
                beam_start_points[i % len(beam_start_points)],
                target_point_on_square,
                stroke_width=10,
                color=color,
                max_tip_length_to_length_ratio=0.15,
                buff=0.1
            )
            beams.add(beam)

        self.play(LaggedStart(*[GrowArrow(beam) for beam in beams], lag_ratio=0.3, run_time=2))
        self.wait(0.5)

        # Absorb beams
        absorption_animations = []
        for beam in beams:
            impact_dot = Dot(beam.get_end(), color=beam.get_color(), radius=0.1)
            absorption_animations.append(Transform(beam, impact_dot, run_time=0.5))
        
        self.play(LaggedStart(*absorption_animations, lag_ratio=0.15))
        self.play(LaggedStart(*[FadeOut(b) for b in beams], lag_ratio=0.1))
        self.wait(0.5)

        # Square starts to glow
        glow_title = Tex("Square heats up and glows...", font_size=36).to_edge(UP)
        self.play(ReplacementTransform(square_label, glow_title))

        temp_tracker = ValueTracker(0)
        
        # Outer glow effect - a slightly larger, transparent square
        outer_glow = Square(side_length=2.8, fill_opacity=0, stroke_width=0)
        outer_glow.move_to(square.get_center())
        
        square.add_updater(lambda m: m.set_fill(
            color=interpolate_color(
                TEMP_COLORS_CUBE[int(temp_tracker.get_value()) % len(TEMP_COLORS_CUBE)][1],
                TEMP_COLORS_CUBE[min(len(TEMP_COLORS_CUBE)-1, int(temp_tracker.get_value()) + 1)][1],
                temp_tracker.get_value() % 1
            ),
            opacity=1
        ).set_stroke(DARK_GRAY, width=1)) # Corrected from DARK_GREY
        
        outer_glow.add_updater(lambda m: m.set_fill(
             color=interpolate_color(
                TEMP_COLORS_CUBE[int(temp_tracker.get_value()) % len(TEMP_COLORS_CUBE)][1],
                TEMP_COLORS_CUBE[min(len(TEMP_COLORS_CUBE)-1, int(temp_tracker.get_value()) + 1)][1],
                temp_tracker.get_value() % 1
            ),
            opacity=0.3
        ).set_stroke(opacity=0))

        self.add(square, outer_glow) 

        self.play(temp_tracker.animate.set_value(len(TEMP_COLORS_CUBE) -1.001), run_time=5, rate_func=linear)
        
        square.clear_updaters()
        outer_glow.clear_updaters()
        square.set_fill(color=TEMP_COLORS_CUBE[-1][1], opacity=1)
        outer_glow.set_fill(color=TEMP_COLORS_CUBE[-1][1], opacity=0.3)

        self.wait(2)
        self.play(FadeOut(square), FadeOut(outer_glow), FadeOut(glow_title))


class Anim2_OrthogonalOscillations(Scene):
    """
    Animation 2:
    a, E-Field: One wave oscillating vertically on screen, propagating along X.
    b, B-Field: Another wave, also shown oscillating vertically on screen but at a
       different baseline and phase, representing the B-field component that
       oscillates horizontally (e.g., along Z) in 3D space. Both propagate along X.
    """
    def construct(self):
        self.camera.background_color = BLACK
        title_text = Tex("E-Field (Vertical Oscillation), B-Field (Representing Horizontal Oscillation)", font_size=28).to_edge(UP)
        self.play(Write(title_text))

        axes = Axes(
            x_range=[-5, 5, 1], x_length=10, # Propagation axis
            y_range=[-2.5, 2.5, 1], y_length=5, # Screen's vertical axis for plotting waves
            axis_config={"include_tip": True, "include_numbers": True, "stroke_width": 2}
        ).add_coordinates()
        
        x_ax_label = axes.get_x_axis_label(MathTex("x_{prop}", font_size=30), edge=DR, direction=DR)
        # Y-axis label indicates amplitude representation on screen
        y_ax_label = axes.get_y_axis_label(MathTex("Amplitude", font_size=30), edge=UL, direction=UL) 
        
        self.play(Create(axes), Write(x_ax_label), Write(y_ax_label))
        self.wait(0.5)

        wavelength = 3.0  # Adjusted for better visual
        k = TAU / wavelength
        amplitude_E_screen = 1.0  # E-field's amplitude on screen
        amplitude_B_screen = 0.8  # B-field's representation amplitude on screen
        
        time = ValueTracker(0)
        omega = TAU * 0.5  # Angular frequency, adjust for desired speed

        e_field_color = BLUE_D
        b_field_color = GREEN_D

        # E-field: Oscillates vertically on screen.
        # Its actual oscillation is along Y in 3D.
        def e_wave_parametric_function(x_prop_param):
            # y_value is the screen y-coordinate for the E-field wave
            e_y_value = amplitude_E_screen * np.sin(k * x_prop_param - omega * time.get_value())
            return axes.c2p(x_prop_param, e_y_value) # x_prop_param is x-coordinate, e_y_value is y-coordinate

        e_wave = always_redraw(
            lambda: ParametricFunction(
                e_wave_parametric_function,
                t_range=np.array([axes.x_range[0], axes.x_range[1], 0.05]), # t_param is x_prop
                color=e_field_color,
                stroke_width=3.5
            )
        )
        e_label = MathTex("E (Vertical)", color=e_field_color, font_size=30)
        # Anchor point for E-label based on a point on the E-wave
        x_prop_e_label = axes.x_range[0] + 0.75 * (axes.x_range[1] - axes.x_range[0])
        e_label.add_updater(
            lambda mob: mob.next_to(
                e_wave_parametric_function(x_prop_e_label), 
                UR, 
                buff=0.1
            )
        )

        # B-field: Represents horizontal oscillation (e.g., along Z in 3D).
        # Shown on screen as a wave oscillating vertically, but offset and phase-shifted.
        y_baseline_B_screen = -1.2  # Shift B-wave down on screen for visual separation
        
        def b_wave_parametric_function(x_prop_param):
            # b_y_repr is the screen y-coordinate for the B-field representation
            # Using cosine for a 90-degree phase shift relative to sine E-field
            b_y_repr = amplitude_B_screen * np.cos(k * x_prop_param - omega * time.get_value()) 
            return axes.c2p(x_prop_param, y_baseline_B_screen + b_y_repr) # x_prop_param is x, y_baseline + oscillation is y

        b_wave = always_redraw(
            lambda: ParametricFunction(
                b_wave_parametric_function,
                t_range=np.array([axes.x_range[0], axes.x_range[1], 0.05]), # t_param is x_prop
                color=b_field_color,
                stroke_width=3.5
            )
        )
        b_label = MathTex("B (Horizontal)", color=b_field_color, font_size=30)
        # Anchor point for B-label based on a point on the B-wave representation
        x_prop_b_label = axes.x_range[0] + 0.25 * (axes.x_range[1] - axes.x_range[0])
        b_label.add_updater(
            lambda mob: mob.next_to(
                b_wave_parametric_function(x_prop_b_label),
                DL,
                buff=0.1
            )
        )

        self.play(Create(e_wave), Create(b_wave))
        self.add(e_label, b_label) 
        self.wait(0.5)

        # Animate time for a couple of cycles
        num_cycles = 2.5
        animation_duration = num_cycles * (TAU / omega) 
        self.play(time.animate.set_value(time.get_value() + TAU / omega * num_cycles),
                  run_time=animation_duration,
                  rate_func=linear)
        self.wait(1)

        # Clear updaters before fading out
        e_wave.clear_updaters()
        b_wave.clear_updaters()
        e_label.clear_updaters()
        b_label.clear_updaters()
        
        self.play(FadeOut(VGroup(title_text, e_wave, b_wave, e_label, b_label, axes, x_ax_label, y_ax_label)))
        self.wait(0.5)


class Anim3_StickFigureDance(Scene):
    """
    Animation 3: Two stick figures with linked arm motions.
    Arms should remain attached to the shoulders.
    """
    def construct(self):
        self.camera.background_color = BLACK

        # Define a helper function to create a stick figure.
        # This function now ensures that arm attachment points are relative to the body.
        def create_stick_figure(color=WHITE):
            head = Circle(radius=0.3, color=color, fill_opacity=0.8, stroke_color=color, stroke_width=2)
            body_start_point = head.get_bottom() # Relative to head's initial position
            body_end_point = body_start_point + DOWN * 1.0
            body = Line(body_start_point, body_end_point, color=color, stroke_width=6)
            
            # Shoulder point is defined relative to the top of the body.
            # This offset will be applied to the *current* top of the body in updaters.
            shoulder_offset_from_body_top = DOWN * 0.05 
            arm_length = 0.65
            
            # Initial arm vectors (direction and length) relative to the shoulder.
            # These define the resting pose of the arms.
            initial_left_arm_vec = rotate_vector(LEFT * arm_length, -PI/7) 
            initial_right_arm_vec = rotate_vector(RIGHT * arm_length, PI/7)

            # Create initial arms. These will be updated.
            # Calculate initial shoulder point for initial drawing.
            initial_shoulder_point = body.get_start() + shoulder_offset_from_body_top
            left_arm = Line(initial_shoulder_point, initial_shoulder_point + initial_left_arm_vec, color=color, stroke_width=5)
            right_arm = Line(initial_shoulder_point, initial_shoulder_point + initial_right_arm_vec, color=color, stroke_width=5)
            arms = VGroup(left_arm, right_arm)

            hip_point = body.get_end() # Bottom of the body
            leg_length = 0.8
            left_leg = Line(hip_point, hip_point + LEFT * 0.3 + DOWN * leg_length, color=color, stroke_width=5)
            right_leg = Line(hip_point, hip_point + RIGHT * 0.3 + DOWN * leg_length, color=color, stroke_width=5)
            legs = VGroup(left_leg, right_leg)
            
            figure = VGroup(head, body, arms, legs)
            # Store components for easier access, especially for updaters.
            figure.head = head
            figure.body = body # The body Line mobject
            figure.arms = arms # VGroup containing left_arm and right_arm
            figure.legs = legs
            # Store vectors and offsets needed for dynamic arm updates.
            figure.shoulder_offset_from_body_top = shoulder_offset_from_body_top
            figure.initial_left_arm_vec = initial_left_arm_vec 
            figure.initial_right_arm_vec = initial_right_arm_vec
            return figure

        # Create two stick figures.
        kid1 = create_stick_figure(color=BLUE_C).shift(LEFT * 2.5)
        kid2 = create_stick_figure(color=GREEN_C).shift(RIGHT * 2.5)
        
        self.play(LaggedStartMap(Create, VGroup(kid1, kid2), lag_ratio=0.5))
        self.wait(0.5)

        anim_time = ValueTracker(0) # Shared time for animations
        freq = 0.6 # Oscillation frequency of arms

        # Arm animation amplitudes
        kid1_arm_angle_amplitude = PI / 2.8 
        kid2_arm_angle_amplitude = PI / 3.5 

        # Updater for kid1's left arm
        kid1.arms[0].add_updater(lambda m: m.become(
            Line(
                kid1.body.get_start() + kid1.shoulder_offset_from_body_top, # Dynamic shoulder point
                (kid1.body.get_start() + kid1.shoulder_offset_from_body_top) + \
                 rotate_vector(kid1.initial_left_arm_vec, kid1_arm_angle_amplitude * np.sin(anim_time.get_value() * freq * TAU)),
                color=m.get_color(), stroke_width=5
            )
        ))
        # Updater for kid1's right arm
        kid1.arms[1].add_updater(lambda m: m.become(
            Line(
                kid1.body.get_start() + kid1.shoulder_offset_from_body_top, # Dynamic shoulder point
                (kid1.body.get_start() + kid1.shoulder_offset_from_body_top) + \
                 rotate_vector(kid1.initial_right_arm_vec, -kid1_arm_angle_amplitude * np.sin(anim_time.get_value() * freq * TAU)),
                color=m.get_color(), stroke_width=5
            )
        ))

        # Updater for kid2's left arm
        kid2.arms[0].add_updater(lambda m: m.become(
            Line(
                kid2.body.get_start() + kid2.shoulder_offset_from_body_top, # Dynamic shoulder point
                (kid2.body.get_start() + kid2.shoulder_offset_from_body_top) + \
                 rotate_vector(kid2.initial_left_arm_vec, kid2_arm_angle_amplitude * np.sin(anim_time.get_value() * freq * TAU + PI/2)),
                color=m.get_color(), stroke_width=5
            )
        ))
        # Updater for kid2's right arm
        kid2.arms[1].add_updater(lambda m: m.become(
            Line(
                kid2.body.get_start() + kid2.shoulder_offset_from_body_top, # Dynamic shoulder point
                (kid2.body.get_start() + kid2.shoulder_offset_from_body_top) + \
                 rotate_vector(kid2.initial_right_arm_vec, -kid2_arm_angle_amplitude * np.sin(anim_time.get_value() * freq * TAU + PI/2)),
                color=m.get_color(), stroke_width=5
            )
        ))
        
        # Add figures to scene (updaters will now manage arm positions)
        self.add(kid1, kid2) 
        self.play(anim_time.animate.set_value(2), run_time=2/freq, rate_func=linear) 
        
        motion_label = Tex("Linked Timing", font_size=30).to_edge(UP)
        self.play(Write(motion_label))
        
        slow_motion_text = Tex("Slow Motion", font_size=24).next_to(motion_label, DOWN)
        self.play(Write(slow_motion_text))
        current_anim_time = anim_time.get_value()
        self.play(anim_time.animate.set_value(current_anim_time + 1.0), run_time= (1.0/freq) * 2.5, rate_func=linear) 
        self.play(FadeOut(slow_motion_text))

        # Animate figures moving while arms continue to update
        self.play(
            VGroup(kid1, kid2).animate.shift(RIGHT * 3), # Shift the entire VGroup
            anim_time.animate.set_value(anim_time.get_value() + 1.0), # Continue arm animation time
            run_time=(1.0/freq) * 1.5 
        )
        self.wait(1)
        
        panel = RoundedRectangle(width=3.5, height=1.2, corner_radius=0.2, fill_color=DARK_BLUE, fill_opacity=0.7)
        panel_title = Tex("Control Panel", font_size=22).move_to(panel.get_top() + DOWN*0.25)
        slider_text = Tex("Shared Rhythm", font_size=18).next_to(panel_title, DOWN, buff=0.2)
        panel_group = VGroup(panel, panel_title, slider_text).to_corner(DL, buff=0.3)
        self.play(FadeIn(panel_group))
        self.wait(2)

        # Clear updaters before removing figures
        kid1.arms[0].clear_updaters() 
        kid1.arms[1].clear_updaters() 
        kid2.arms[0].clear_updaters() 
        kid2.arms[1].clear_updaters() 

        self.play(FadeOut(motion_label), FadeOut(kid1), FadeOut(kid2), FadeOut(panel_group))
        self.wait(1)


class Anim4_EMWaveInSpace(Scene):
    """
    Animation 4: EM wave propagating through 2D space,
    passing 2D stars/sun.
    """
    def construct(self):
        self.camera.background_color = BLACK
        
        wavelength = 2.0
        k = TAU / wavelength
        amplitude = 0.8 
        
        wave_phase = ValueTracker(0)
        omega = TAU * 0.75

        wave_x_start = -self.camera.frame_width / 2 - 2
        wave_x_end = self.camera.frame_width / 2 + 2
        wave_length = 6

        def create_2d_wave_segment(center_x, current_phase):
            segment = VGroup()
            e_func = lambda x_local: [x_local, amplitude * np.sin(k * x_local - current_phase), 0]
            e_segment = ParametricFunction(
                e_func, t_range=[-wave_length/2, wave_length/2, 0.1], 
                color=BLUE_C, stroke_width=3.5
            )
            segment.add(e_segment)

            num_b_symbols = 15
            x_locals_b = np.linspace(-wave_length/2, wave_length/2, num_b_symbols)
            for x_l in x_locals_b:
                b_val_phase = k * x_l - current_phase + PI/2
                b_strength = np.sin(b_val_phase)
                
                symbol_opacity = np.clip(abs(b_strength) * 0.8 + 0.2, 0.2, 1.0)
                symbol_base_size = 0.06
                
                if b_strength > 0:
                    symbol = Dot(point=[x_l, 0, 0], radius=symbol_base_size * (0.5 + abs(b_strength)*0.5) , color=GREEN_C, fill_opacity=symbol_opacity)
                else:
                    symbol = Tex("X", color=GREEN_C, font_size=12 + 12*abs(b_strength)).move_to([x_l, 0, 0])
                    symbol.set_opacity(symbol_opacity)
                segment.add(symbol)
            
            segment.shift(RIGHT * center_x)
            return segment

        em_wave_packet = create_2d_wave_segment(wave_x_start, wave_phase.get_value())
        em_wave_packet.add_updater(
            lambda mob: mob.become(
                create_2d_wave_segment(
                    mob.get_center()[0], 
                    wave_phase.get_value()
                )
            )
        )
        
        arrow_display_length = 1.5
        propagation_arrow = always_redraw(
            lambda: Arrow(
                em_wave_packet.get_center() + LEFT * arrow_display_length/2,
                em_wave_packet.get_center() + RIGHT * arrow_display_length/2,
                color=YELLOW_D, stroke_width=4, buff=0, max_tip_length_to_length_ratio=0.25
            )
        )
        
        self.add(em_wave_packet, propagation_arrow)

        sun = Circle(radius=1.2, fill_color=YELLOW_D, fill_opacity=1, stroke_width=0).move_to(ORIGIN + UP*0.5)
        star1 = Circle(radius=0.4, fill_color=BLUE_B, fill_opacity=1, stroke_width=0).move_to(RIGHT*3.5+UP*1.5)
        star2 = Circle(radius=0.5, fill_color=RED_B, fill_opacity=1, stroke_width=0).move_to(LEFT*3+DOWN*1.0)
        celestial_bodies = VGroup(sun, star1, star2)
        
        self.play(LaggedStartMap(GrowFromCenter, celestial_bodies, lag_ratio=0.5))
        self.wait(0.5)

        self.play(
            em_wave_packet.animate.move_to(RIGHT * wave_x_end),
            wave_phase.animate.increment_value(TAU * 3),
            run_time=8, 
            rate_func=linear
        )
        self.wait(1)
        
        em_wave_packet.clear_updaters()
        propagation_arrow.clear_updaters()

        self.play(FadeOut(em_wave_packet), FadeOut(propagation_arrow), FadeOut(celestial_bodies))


class Anim5_LightInteraction(Scene):
    """
    Animation 5: Light beam interaction with a surface (reflection, absorption, transmission).
    """
    def construct(self):
        self.camera.background_color = BLACK

        # Corrected color from BLUE_GREY to BLUE_GRAY
        surface_line = Line(LEFT * 3.5, RIGHT * 3.5, color=BLUE_GRAY, stroke_width=6).shift(DOWN*1)
        surface_label = Tex("Surface", font_size=28, color=BLUE_GRAY).next_to(surface_line, DOWN, buff=0.3) # Corrected color
        self.play(Create(surface_line), Write(surface_label))
        self.wait(0.2)

        incident_start = UP * 2.8 + LEFT * 3
        impact_point_on_surface = surface_line.get_center() + LEFT * 0.8
        
        incident_ray = Arrow(incident_start, impact_point_on_surface, buff=0, color=YELLOW_C, stroke_width=7)
        incident_label = Tex("Incident Light", font_size=30, color=YELLOW_C)
        incident_label.next_to(incident_ray.get_start(), UP+LEFT, buff=0.2)
        
        self.play(GrowArrow(incident_ray), Write(incident_label))
        self.wait(0.5)

        impact_dot = Dot(impact_point_on_surface, color=YELLOW_C, radius=0.08)
        self.play(FadeIn(impact_dot, scale=0.7))

        normal = DashedLine(impact_point_on_surface, impact_point_on_surface + UP * 2, color=WHITE, stroke_width=2.5)
        self.play(Create(normal))
        self.wait(0.3)

        incoming_vec = incident_ray.get_vector()
        surface_normal_vec = normalize(UP) 
        reflected_vec_dir = normalize(incoming_vec - 2 * np.dot(incoming_vec, surface_normal_vec) * surface_normal_vec)
        
        reflected_ray = Arrow(impact_point_on_surface, impact_point_on_surface + reflected_vec_dir * 2.5, buff=0, color=ORANGE, stroke_width=6)
        reflected_label = Tex("Reflected", font_size=26, color=ORANGE).next_to(reflected_ray.get_end(), reflected_vec_dir, buff=0.2)

        self.play(GrowArrow(reflected_ray), Write(reflected_label))
        self.wait(0.5)

        absorption_highlight = Circle(radius=0.5, stroke_width=0, fill_color=RED_D, fill_opacity=0).move_to(impact_point_on_surface)
        absorbed_label = Tex("Absorbed", font_size=26, color=RED_D).next_to(impact_point_on_surface, DOWN*1.5 + RIGHT*0.5, buff=0.1)
        
        self.play(
            absorption_highlight.animate.set_fill(opacity=0.6),
            Write(absorbed_label),
            run_time=0.7
        )
        self.play(
            absorption_highlight.animate.set_fill(opacity=0),
            FadeOut(absorbed_label),
            run_time=0.7
        )
        self.remove(absorption_highlight) 
        self.wait(0.2)

        self.play(surface_line.animate.set_stroke(opacity=0.4), run_time=0.3)
        transmitted_vec_dir = normalize(DOWN) 
        if np.abs(incoming_vec[1]) > 0.01: 
            transmitted_vec_dir = normalize(np.array([incoming_vec[0]*0.3, -np.abs(incoming_vec[1]), 0])) 

        transmitted_ray = Arrow(impact_point_on_surface, impact_point_on_surface + transmitted_vec_dir * 2.0, buff=0, color=LIGHT_GRAY, stroke_width=5, stroke_opacity=0.8) # Corrected from LIGHT_GREY
        transmitted_label = Tex("Transmitted", font_size=26, color=LIGHT_GRAY).next_to(transmitted_ray.get_end(), transmitted_vec_dir, buff=0.2) # Corrected from LIGHT_GREY
        
        self.play(GrowArrow(transmitted_ray), Write(transmitted_label))
        self.wait(2)
        
        self.play(
            FadeOut(VGroup(incident_ray, incident_label, impact_dot, normal)),
            FadeOut(VGroup(reflected_ray, reflected_label)),
            FadeOut(VGroup(transmitted_ray, transmitted_label)),
            FadeOut(surface_line), FadeOut(surface_label)
        )
        self.wait(1)

class Anim6_WavelengthToColorChart(Scene):
    """
    Animation 6: Displays a chart mapping visible light wavelengths to colors.
    """
    def construct(self):
        self.camera.background_color = BLACK

        # Title for the chart
        title = Tex("Visible Light Spectrum: Wavelength to Color", font_size=36)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))
        self.wait(0.5)

        # Data for the table: [Wavelength Range (nm), Color Name, Manim Color]
        # These are approximate ranges.
        spectrum_data = [
            ["~700 - 635 nm", "Red", RED],
            ["~635 - 590 nm", "Orange", ORANGE],
            ["~590 - 560 nm", "Yellow", YELLOW],
            ["~560 - 520 nm", "Green", GREEN],
            ["~520 - 490 nm", "Cyan", PURE_BLUE], # Manim doesn't have a direct CYAN, using a blue variant
            ["~490 - 450 nm", "Blue", BLUE],
            ["~450 - 400 nm", "Violet", PURPLE],
        ]

        # Create table entries
        # First row is headers
        table_content = [
            [Tex("Wavelength (nm)", font_size=28, color=WHITE), Tex("Color Name", font_size=28, color=WHITE), Tex("Visual", font_size=28, color=WHITE)]
        ]

        # Populate table rows with data
        for wavelength_range, color_name, manim_color_const in spectrum_data:
            # Create a colored square for the "Visual" column
            color_swatch = Square(side_length=0.5, fill_color=manim_color_const, fill_opacity=1, stroke_width=0)
            table_content.append([
                Tex(wavelength_range, font_size=24),
                Tex(color_name, font_size=24, color=manim_color_const),
                color_swatch
            ])
        
        # Create the table
        # h_buff and v_buff control cell padding
        # include_outer_lines adds a border around the table
        color_table = Table(
            table_content,
            row_labels=[Tex(f"Row {i+1}") for i in range(len(spectrum_data))], # Optional row labels
            col_labels=[Tex("WL"), Tex("Name"), Tex("Vis")], # Optional column labels (not displayed by default with include_outer_lines=True)
            top_left_entry=Tex("Spectrum", font_size=24), # Content for top-left cell if row/col labels are shown
            include_outer_lines=True,
            h_buff=0.7, # Horizontal buffer / padding
            v_buff=0.4  # Vertical buffer / padding
        )
        color_table.scale(0.8) # Scale down if too large
        color_table.next_to(title, DOWN, buff=0.5)

        # Animate the table creation
        self.play(Create(color_table), run_time=3)
        
        # Highlight rows one by one (optional demonstration)
        for i in range(1, len(spectrum_data) + 1): # Iterate through data rows (skip header)
             # Get the cells of the current row (index i, as table_content[0] is header)
            current_row_cells = color_table.get_rows()[i]
            self.play(
                current_row_cells.animate.set_color(YELLOW), # Highlight the text in the row
                # If you want to animate the swatch too, you'd handle it separately or ensure it's part of the cell VGroup
                run_time=0.5
            )
            self.play(
                current_row_cells.animate.set_color(WHITE), # Unhighlight
                 # If swatch was highlighted, revert its color too
                run_time=0.5
            )
        
        self.wait(2)
        self.play(FadeOut(title), FadeOut(color_table))
        self.wait(1)
