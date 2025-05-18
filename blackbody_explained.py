import numpy as np
from manim import *

# Constants for Planck's Law (more physically accurate, but can be complex for simple viz)
# H_PLANCK = 6.626e-34  # Planck's constant (J*s)
# C_LIGHT = 3.00e8     # Speed of light (m/s)
# K_BOLTZMANN = 1.38e-23 # Boltzmann constant (J/K)

TEMP_COLORS = [
    (300, DARK_GRAY),
    (800, ManimColor.from_rgb([0.6, 0, 0])),
    (1000, RED_E),
    (1200, RED_D),
    (1500, ORANGE),
    (2000, YELLOW_E),
    (2500, YELLOW_D),
    (3000, WHITE),
    (4000, BLUE_C), # Corrected from LIGHT_BLUE
    (5800, WHITE)
]

B_Wien = 2.898e-3
EPSILON = 1e-9
SIGMA = 5.670374419e-8 # Stefan-Boltzmann constant W/(m^2 K^4)

def pseudo_planck(wavelength_nm_input, T_kelvin):
    # Check if the input wavelength is a scalar
    is_scalar_input = np.isscalar(wavelength_nm_input)
    
    # Convert to NumPy array for vectorized operations
    wavelength_nm = np.asarray(wavelength_nm_input)

    if T_kelvin <= 0:
        # Return 0.0 if scalar input, array of zeros if array input
        return 0.0 if is_scalar_input else np.zeros_like(wavelength_nm, dtype=float)

    lambda_m = wavelength_nm * 1e-9
    lambda_max_m = B_Wien / (T_kelvin + EPSILON)
    peak_nm = lambda_max_m * 1e9

    left_width = peak_nm * 0.3 + EPSILON
    right_width = peak_nm * 0.6 + EPSILON

    # Initialize intensity array (or scalar if input was scalar)
    intensity = np.zeros_like(wavelength_nm, dtype=float)

    # Conditions for left and right side of the peak
    left_side_condition = wavelength_nm <= peak_nm
    right_side_condition = wavelength_nm > peak_nm

    if wavelength_nm.ndim > 0:
        intensity[left_side_condition] = np.exp(-((wavelength_nm[left_side_condition] - peak_nm)**2) / (2 * left_width**2))
        intensity[right_side_condition] = np.exp(-((wavelength_nm[right_side_condition] - peak_nm)**2) / (2 * right_width**2))
    else: 
        if left_side_condition: 
            intensity = np.exp(-((wavelength_nm - peak_nm)**2) / (2 * left_width**2))
        elif right_side_condition: 
            intensity = np.exp(-((wavelength_nm - peak_nm)**2) / (2 * right_width**2))

    # This T^4 scaling is a visual approximation related to Stefan-Boltzmann's P ~ T^4
    # The pseudo_planck function models the *shape* and *peak shift* of the spectral curve.
    # The overall height of the curve in the spectrum plot will visually show the T^4 dependence.
    intensity *= (T_kelvin / 1000)**4 # Keep this for the spectrum plot scaling

    if is_scalar_input:
        return intensity.item() 
    return intensity


class BlackbodyRadiationExplained(Scene):
    def construct(self):
        # --- Title Scene ---
        title = Tex("Blackbody Radiation", font_size=60)
        subtitle = Tex("From Heat to Light", font_size=40).next_to(title, DOWN, buff=0.3)
        intro_text = Tex(
            "All objects emit radiation based on their temperature.",
            font_size=32
        ).next_to(subtitle, DOWN, buff=0.5)
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.play(FadeIn(intro_text, shift=UP))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(intro_text))
        self.wait(0.5)

        # --- Simulated Experiment ---
        explanation1 = Tex("Let's heat an object, like an iron nail:", font_size=36).to_edge(UP)
        nail = Rectangle(width=3, height=0.3, color=DARK_GRAY, fill_opacity=1).round_corners(0.1)
        nail.set_fill(DARK_GRAY) 

        temp_label_text = Tex("Temperature: ", font_size=30)
        temp_value = DecimalNumber(
            300,
            num_decimal_places=0,
            unit=" K",
            font_size=30
        )
        temp_display = VGroup(temp_label_text, temp_value).arrange(RIGHT).next_to(nail, DOWN, buff=0.5)

        self.play(FadeIn(explanation1))
        self.play(Create(nail), Write(temp_display))
        self.wait(1)

        nail_heating_colors = [tc for tc in TEMP_COLORS if tc[0] <= 3000]

        for i in range(len(nail_heating_colors)):
            target_temp, target_color = nail_heating_colors[i]
            if target_temp < temp_value.get_value(): 
                continue
            previous_temp = temp_value.get_value()
            anim_time = 0.5 + abs(target_temp - previous_temp) / 500
            if anim_time <= 0: anim_time = 0.2 
            self.play(
                temp_value.animate.set_value(target_temp),
                nail.animate.set_fill(target_color, opacity=1.0), 
                run_time=anim_time
            )
            self.wait(0.5)
        self.wait(2)

        explanation2 = Tex(
            "Color shifts: ",
            "Red", " $\\rightarrow$ ", "Orange", " $\\rightarrow$ ",
            "Yellow", " $\\rightarrow$ ", "White", " as T increases",
            font_size=32
        )
        explanation2[1].set_color(RED_D)
        explanation2[3].set_color(ORANGE)
        explanation2[5].set_color(YELLOW_D)
        explanation2[7].set_color(WHITE)
        explanation2.next_to(temp_display, DOWN, buff=0.5)
        self.play(Write(explanation2))
        self.wait(2)
        self.play(
            FadeOut(nail), FadeOut(temp_display), FadeOut(explanation1), FadeOut(explanation2)
        )
        self.wait(0.5)

        # --- Physics: Wien's Law ---
        wien_title = Tex("Wien's Displacement Law", font_size=48).to_edge(UP)
        wien_formula = MathTex(r"\lambda_{max} = \frac{b}{T}", font_size=60)
        wien_explanation = Tex(
            r"Peak wavelength (\(\lambda_{max}\)) is inversely proportional to Temperature (T).",
            font_size=32
        ).next_to(wien_formula, DOWN, buff=0.5)
        wien_implication = Tex(
            r"Higher T \(\implies\) Shorter \(\lambda_{max}\) (shifts towards blue/white)",
            font_size=32
        ).next_to(wien_explanation, DOWN, buff=0.3)
        self.play(Write(wien_title))
        self.play(Write(wien_formula))
        self.play(FadeIn(wien_explanation, shift=UP))
        self.play(FadeIn(wien_implication, shift=UP))
        self.wait(3)
        self.play(
            FadeOut(wien_title), FadeOut(wien_formula),
            FadeOut(wien_explanation), FadeOut(wien_implication)
        )
        self.wait(0.5)

        # --- Physics: Stefan-Boltzmann Law ---
        stefan_title = Tex("Stefan-Boltzmann Law", font_size=48).to_edge(UP)
        # P = εσAT^4. For a perfect blackbody, ε=1. Power per unit area is J = σT^4
        stefan_formula = MathTex(r"P = \epsilon \sigma A T^4", font_size=60)
        stefan_formula_simple = MathTex(r"P \propto T^4", font_size=60).next_to(stefan_formula, DOWN, buff=0.7)
        
        stefan_explanation = Tex(
            r"Total power (\(P\)) radiated by an object is proportional to its surface area (\(A\))",
            r"and the fourth power of its absolute temperature (\(T\)).",
            r"(\(\epsilon\) is emissivity, \(\sigma\) is Stefan-Boltzmann constant)",
            font_size=30, tex_environment="flushleft"
        ).next_to(stefan_formula_simple, DOWN, buff=0.5)
        stefan_explanation.set_width(FRAME_WIDTH - 2)


        stefan_implication = Tex(
            r"Hotter objects radiate energy much more intensely.",
            font_size=32
        ).next_to(stefan_explanation, DOWN, buff=0.4)

        self.play(Write(stefan_title))
        self.play(Write(stefan_formula))
        self.play(Write(stefan_formula_simple))
        self.play(FadeIn(stefan_explanation, shift=UP))
        self.play(FadeIn(stefan_implication, shift=UP))
        self.wait(4) # Longer wait for this important law
        self.play(
            FadeOut(stefan_title), FadeOut(stefan_formula), FadeOut(stefan_formula_simple),
            FadeOut(stefan_explanation), FadeOut(stefan_implication)
        )
        self.wait(0.5)


        # --- Physics: Blackbody Spectrum (Modified for Dynamic Axes, Improved Robustness) ---
        # This section remains as it was in your provided code with dynamic axes
        spectrum_title = Tex("Blackbody Spectrum", font_size=48).to_edge(UP)
        spectrum_expl = Tex("Intensity of radiation vs. Wavelength", font_size=32).next_to(spectrum_title, DOWN, buff=0.2)
        self.play(Write(spectrum_title), Write(spectrum_expl))

        temps_to_plot = [1000, 1500, 2500, 4000] 
        plot_colors_map = {
            1000: RED_D, 1500: ORANGE, 2500: YELLOW_D, 4000: WHITE
        }
        
        current_axes_mob = None
        current_x_label_mob = None
        current_y_label_mob = None
        plots_on_screen = VGroup()
        dots_on_screen = VGroup()
        temp_labels_on_screen = VGroup()

        plot_data_accumulator = [] 
        wavelengths_for_axis_scaling = np.linspace(200, 1500, 200)
        fixed_x_range = [200, 1500, 200]

        for T_plot_idx, T_plot in enumerate(temps_to_plot):
            color = plot_colors_map[T_plot]
            plot_function = lambda wl, temp_capture=T_plot: pseudo_planck(wl, temp_capture)
            
            lambda_max_m = B_Wien / (T_plot + EPSILON)
            lambda_max_nm = lambda_max_m * 1e9
            peak_intensity_at_max_wl = pseudo_planck(lambda_max_nm, T_plot)

            plot_data_accumulator.append((T_plot, color, plot_function, lambda_max_nm, peak_intensity_at_max_wl))

            max_intensity_so_far = 0.001 
            for p_data in plot_data_accumulator:
                max_intensity_so_far = max(max_intensity_so_far, p_data[4]) 
                sampled_intensities = p_data[2](wavelengths_for_axis_scaling)
                if isinstance(sampled_intensities, np.ndarray) and sampled_intensities.size > 0:
                    valid_sampled = sampled_intensities[np.isfinite(sampled_intensities)]
                    if valid_sampled.size > 0:
                         max_intensity_so_far = max(max_intensity_so_far, np.max(valid_sampled))

            y_max_limit = max_intensity_so_far * 1.2 
            if y_max_limit <= 0.01 : y_max_limit = 10.0 
            
            if y_max_limit < 1: y_step = 0.2
            elif y_max_limit < 10: y_step = np.ceil(y_max_limit / 5)
            elif y_max_limit < 100: y_step = np.ceil(y_max_limit / 5 / 5) * 5
            else:
                power_of_10 = 10**np.floor(np.log10(y_max_limit/5) if y_max_limit/5 > 0 else 0.1)
                y_step = np.ceil(y_max_limit / 5 / power_of_10) * power_of_10
            if y_step <= 0: y_step = 1.0 
            y_max_limit = np.ceil(y_max_limit / y_step) * y_step
            if y_max_limit == 0 : y_max_limit = y_step * 5

            target_y_range = [0, y_max_limit, y_step]
            target_axes = Axes(
                x_range=fixed_x_range, y_range=target_y_range, x_length=9.5, y_length=5.5,
                axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": 1}},
                tips=False,
            ).add_coordinates().shift(RIGHT * 0.7)
            target_x_label = target_axes.get_x_axis_label(r"\lambda \text{ (nm)}")
            target_y_label = Tex(r"\text{Intensity}", font_size=28).rotate(90 * DEGREES).next_to(target_axes.y_axis, LEFT, buff=0.6)

            all_target_plots = VGroup()
            all_target_dots = VGroup()
            all_target_labels = VGroup()

            for idx, (T, c, pf, l_max_nm, p_int_val) in enumerate(plot_data_accumulator): # Renamed p_int to p_int_val
                plot = target_axes.plot(pf, x_range=[fixed_x_range[0], fixed_x_range[1]], color=c, use_smoothing=True)
                all_target_plots.add(plot)
                current_peak_intensity_for_dot = p_int_val # Use the specific peak intensity for this plot
                if fixed_x_range[0] <= l_max_nm <= fixed_x_range[1] and \
                   target_y_range[0] <= current_peak_intensity_for_dot <= target_y_range[1]:
                    peak_point = target_axes.c2p(l_max_nm, current_peak_intensity_for_dot)
                    dot = Dot(point=peak_point, color=c, radius=0.08)
                    all_target_dots.add(dot)
                    label_text_obj = MathTex(f"{T} K", color=c, font_size=28)
                    label_pos_dir = UP if idx % 2 == 0 else DOWN
                    if l_max_nm > (fixed_x_range[0] + fixed_x_range[1]) *0.75 : label_pos_dir = LEFT + UP*0.5
                    elif l_max_nm < (fixed_x_range[0] + fixed_x_range[1]) *0.25 : label_pos_dir = RIGHT + UP*0.5
                    label_text_obj.next_to(dot, label_pos_dir, buff=0.2)
                    all_target_labels.add(label_text_obj)
            
            current_animations = []
            if current_axes_mob is None: 
                current_axes_mob = target_axes
                current_x_label_mob = target_x_label
                current_y_label_mob = target_y_label
                self.play(Create(current_axes_mob), Write(current_x_label_mob), Write(current_y_label_mob))
                if len(all_target_plots) > 0:
                    current_animations.append(Create(all_target_plots[0]))
                    plots_on_screen.add(all_target_plots[0])
                if len(all_target_dots) > 0:
                    current_animations.append(FadeIn(all_target_dots[0]))
                    dots_on_screen.add(all_target_dots[0])
                if len(all_target_labels) > 0:
                    current_animations.append(Write(all_target_labels[0]))
                    temp_labels_on_screen.add(all_target_labels[0])
            else: 
                current_animations.extend([
                    Transform(current_axes_mob, target_axes),
                    Transform(current_x_label_mob, target_x_label),
                    Transform(current_y_label_mob, target_y_label),
                ])
                for k in range(len(plots_on_screen)):
                    current_animations.append(Transform(plots_on_screen[k], all_target_plots[k]))
                current_animations.append(Create(all_target_plots[-1]))
                plots_on_screen.add(all_target_plots[-1])
                new_dots_to_track = VGroup()
                for k in range(len(all_target_dots)):
                    if k < len(dots_on_screen):
                        current_animations.append(Transform(dots_on_screen[k], all_target_dots[k]))
                        new_dots_to_track.add(dots_on_screen[k])
                    else:
                        current_animations.append(FadeIn(all_target_dots[k]))
                        new_dots_to_track.add(all_target_dots[k])
                for k in range(len(all_target_dots), len(dots_on_screen)):
                    current_animations.append(FadeOut(dots_on_screen[k]))
                dots_on_screen = new_dots_to_track
                new_labels_to_track = VGroup()
                for k in range(len(all_target_labels)):
                    if k < len(temp_labels_on_screen):
                        current_animations.append(Transform(temp_labels_on_screen[k], all_target_labels[k]))
                        new_labels_to_track.add(temp_labels_on_screen[k])
                    else:
                        current_animations.append(Write(all_target_labels[k]))
                        new_labels_to_track.add(all_target_labels[k])
                for k in range(len(all_target_labels), len(temp_labels_on_screen)):
                    current_animations.append(FadeOut(temp_labels_on_screen[k]))
                temp_labels_on_screen = new_labels_to_track
            self.play(*current_animations, run_time=1.5)
            self.wait(0.7)
            
        spectrum_summary = Tex(r"Higher T \(\implies\) Higher Intensity \& Peak shifts to shorter \(\lambda\)",
                               font_size=30).next_to(current_axes_mob if current_axes_mob else self, DOWN, buff=0.7)
        self.play(Write(spectrum_summary))
        self.wait(3)

        planck_text = Tex("Classical physics failed. Planck proposed quantized energy.", font_size=30).next_to(spectrum_summary, DOWN, buff=0.5)
        self.play(FadeIn(planck_text))
        self.wait(2)

        elements_to_fade = VGroup(spectrum_title, spectrum_expl, spectrum_summary, planck_text)
        if current_axes_mob: elements_to_fade.add(current_axes_mob)
        if current_x_label_mob: elements_to_fade.add(current_x_label_mob)
        if current_y_label_mob: elements_to_fade.add(current_y_label_mob)
        elements_to_fade.add(plots_on_screen, dots_on_screen, temp_labels_on_screen)
        
        self.play(FadeOut(elements_to_fade))
        self.wait(0.5)

        # --- Real World Examples ---
        examples_title = Tex("Real-World Examples", font_size=48).to_edge(UP)
        self.play(Write(examples_title))

        bulb_filament = Line(LEFT*0.5, RIGHT*0.5, color=YELLOW_D, stroke_width=6).shift(UP*1.5)
        bulb_glass = Circle(radius=1.0, color=WHITE, stroke_opacity=0.5).surround(bulb_filament, buffer_factor=1.5)
        bulb_base = Rectangle(width=0.6, height=0.4, color=GRAY).next_to(bulb_glass, DOWN, buff=-0.05)
        bulb = VGroup(bulb_filament, bulb_glass, bulb_base)
        bulb_text = Tex("Incandescent Bulb: Hot filament glows", font_size=30).next_to(bulb, DOWN)
        bulb_example_group = VGroup(bulb, bulb_text).shift(LEFT * 3.5)
        self.play(FadeIn(bulb_example_group, scale=0.8))
        self.wait(1.5)
        
        star_y_pos = DOWN * 1.5
        star_buff = 0.3
        star_h_spacing = 3.0 
        star1 = Star(n=5, outer_radius=0.5, color=RED_D, fill_opacity=1).shift(star_y_pos + LEFT*star_h_spacing)
        star1_text = Tex("Cooler Star (Red)", font_size=28).next_to(star1, DOWN, buff=star_buff)
        star2 = Star(n=5, outer_radius=0.6, color=YELLOW_E, fill_opacity=1).shift(star_y_pos)
        star2_text = Tex("Medium Star (Yellow)", font_size=28).next_to(star2, DOWN, buff=star_buff)
        star3 = Star(n=5, outer_radius=0.7, color=BLUE_C, fill_opacity=1).shift(star_y_pos + RIGHT*star_h_spacing)
        star3_text = Tex("Hotter Star (Blue)", font_size=28).next_to(star3, DOWN, buff=star_buff)
        stars = VGroup(star1, star2, star3)
        stars_text = VGroup(star1_text, star2_text, star3_text)
        stars_group = VGroup(stars, stars_text).shift(RIGHT * 3) 
        self.play(Create(stars), Write(stars_text))
        self.wait(3)
        self.play(FadeOut(examples_title), FadeOut(bulb_example_group), FadeOut(stars_group))
        self.wait(0.5)

        # --- Conclusion ---
        conclusion = Tex("Blackbody radiation connects temperature, color, and light,", font_size=36)
        conclusion2 = Tex("a key concept in physics.", font_size=36).next_to(conclusion, DOWN)
        final_thanks = Tex("Thanks for watching!", font_size=40).next_to(conclusion2, DOWN, buff=0.8)
        self.play(Write(conclusion))
        self.play(Write(conclusion2))
        self.wait(1.5)
        self.play(FadeIn(final_thanks))
        self.wait(3)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(1)

# The IncandescentBulbDiffraction class and SunAndSquareScene class would follow here if they are in the same file.
# For this update, I'm only showing the modified BlackbodyRadiationExplained class.

class IncandescentBulbDiffraction(Scene):
    def construct(self):
        title = Tex("Incandescent Bulb \\& Diffraction", font_size=48).to_edge(UP)
        self.play(Write(title))

        # Bulb representation
        bulb_filament = Ellipse(width=0.2, height=0.6, color=DARK_GRAY, fill_opacity=1.0)
        bulb_filament.set_fill(DARK_GRAY)
        bulb_glass = Circle(radius=1.0, color=WHITE, stroke_opacity=0.3).surround(bulb_filament, buffer_factor=2.0)
        bulb_base = Rectangle(width=0.8, height=0.5, color=GRAY).next_to(bulb_glass, DOWN, buff=-0.05)
        bulb_group = VGroup(bulb_glass, bulb_base, bulb_filament).shift(LEFT * 4.5 + UP * 0.5) # Shifted more left

        temp_label_text = Tex("Temp: ", font_size=28)
        temp_value_bulb = DecimalNumber(300, num_decimal_places=0, unit=" K", font_size=28)
        temp_display_bulb = VGroup(temp_label_text, temp_value_bulb).arrange(RIGHT)
        temp_display_bulb.next_to(bulb_group, DOWN, buff=0.3)

        self.play(Create(bulb_group), Write(temp_display_bulb))
        self.wait(0.5)

        # Diffraction grating
        grating = Line(UP * 1.0, DOWN * 1.0, color=GRAY, stroke_width=3).shift(LEFT * 2.0) # Slightly thicker
        grating_label = Tex("Grating", font_size=24).next_to(grating, DOWN, buff=0.2)
        
        # Light rays from bulb to grating
        num_main_rays = 7
        light_path = VGroup()
        # Create rays fanning out towards the grating
        grating_points = [grating.get_start(), grating.get_center(), grating.get_end()]
        if num_main_rays > 3: # Add intermediate points for more rays
            grating_points.insert(1, grating.point_from_proportion(0.25))
            grating_points.insert(3, grating.point_from_proportion(0.75))
            if num_main_rays > 5 :
                 grating_points.insert(1, grating.point_from_proportion(0.1))
                 grating_points.insert(5, grating.point_from_proportion(0.9))


        for i in range(min(num_main_rays, len(grating_points))):
            target_point_on_grating = grating_points[i % len(grating_points)]
            ray = Line(
                bulb_filament.get_center(), 
                target_point_on_grating, 
                stroke_width=1.5, # Slightly thicker
                color=TEMP_COLORS[0][1], # Initial color
                stroke_opacity=0
            )
            light_path.add(ray)

        self.play(Create(grating), Write(grating_label), Create(light_path))
        self.wait(0.5)

        # Screen area for spectrum
        screen_center_x_val = 2.5 
        screen_center_x = RIGHT * screen_center_x_val
        spectrum_base_y = grating.get_center()[1] 
        
        spectrum_defs = [
            {"name": "Violet", "wl": 410, "color": PURPLE_B, "pos_factor": 0.5}, # Adjusted factors for spread
            {"name": "Blue",   "wl": 470, "color": BLUE_D,   "pos_factor": 0.65},
            {"name": "Green",  "wl": 520, "color": GREEN_C,  "pos_factor": 0.85},
            {"name": "Yellow", "wl": 580, "color": YELLOW_C, "pos_factor": 1.05},
            {"name": "Orange", "wl": 610, "color": ORANGE,   "pos_factor": 1.25},
            {"name": "Red",    "wl": 660, "color": RED_D,    "pos_factor": 1.45},
        ]
        
        spectral_lines = VGroup()
        max_bar_height = 2.0 # Slightly taller bars
        bar_width = 0.35    # Slightly wider bars
        
        temps_for_bulb_animation = [300, 800, 1200, 1600, 2000, 2500, 3000, 3500, 4000, 5000] # Extended temps

        # Refined max_possible_intensity_visible calculation
        # Find the global maximum intensity that pseudo_planck will output for visible spectrum at highest animated temp
        global_max_intensity_output = 0.01 # Initialize with a small non-zero value
        for T_check in temps_for_bulb_animation:
            if T_check < 600: continue # Only consider temperatures where some light might be visible
            for spec_def in spectrum_defs:
                intensity_val = pseudo_planck(spec_def["wl"], T_check)
                global_max_intensity_output = max(global_max_intensity_output, float(intensity_val))
        
        max_possible_intensity_visible = global_max_intensity_output # Use this for normalization

        for spec_def in spectrum_defs:
            line_pos_x = screen_center_x_val + spec_def["pos_factor"] * 1.2 # Adjust spread factor if needed
            line = Rectangle(
                width=bar_width, height=max_bar_height, fill_color=spec_def["color"], 
                stroke_width=0, fill_opacity=0.0
            )
            line.move_to(RIGHT * line_pos_x + UP * spectrum_base_y) # Position based on spectrum_base_y
            spectral_lines.add(line)

        self.play(FadeIn(spectral_lines))
        self.wait(0.5)
        
        previous_opacities = [0.0] * len(spectrum_defs)
        temp_color_map = dict(TEMP_COLORS) # For easier lookup

        glow_temp_min = 700.0 # Temperature at which filament starts to visibly glow
        glow_temp_max = max(temps_for_bulb_animation) if temps_for_bulb_animation else 4000.0


        for T_idx, T_current in enumerate(temps_for_bulb_animation):
            target_bulb_color_val = DARK_GRAY 
            for temp_threshold, color_val in TEMP_COLORS:
                if T_current >= temp_threshold:
                    target_bulb_color_val = color_val 
                else:
                    break 

            anim_ops_main = [
                temp_value_bulb.animate.set_value(T_current),
                bulb_filament.animate.set_fill(target_bulb_color_val, opacity=1.0)
            ]
            
            # Animate main light rays from bulb to grating
            ray_opacity_val = 0.0
            if T_current > glow_temp_min:
                # Normalize temperature for glow (0 to 1 range over visible heating)
                normalized_temp_for_glow = (T_current - glow_temp_min) / (glow_temp_max - glow_temp_min + EPSILON)
                ray_opacity_val = np.clip(normalized_temp_for_glow**2.5, 0, 0.8) # Quadratic increase, max 0.8 opacity
            
            anim_ops_main.append(light_path.animate.set_stroke(color=target_bulb_color_val, opacity=ray_opacity_val, width=2.0))

            # Calculate target opacities for spectral lines for this T_current
            current_target_opacities = []
            for i, spec_def in enumerate(spectrum_defs):
                intensity = pseudo_planck(spec_def["wl"], T_current)
                opacity_val = np.clip(float(intensity) / (max_possible_intensity_visible + EPSILON), 0, 1.0)
                current_target_opacities.append(opacity_val)
                anim_ops_main.append(spectral_lines[i].animate.set_fill(opacity=opacity_val))
            
            # Play main animations (bulb, rays, spectral line opacities)
            self.play(*anim_ops_main, run_time=0.8 if T_idx > 0 else 0.4)
            
            # Projection ray flashes for newly prominent spectral lines
            projection_flash_anims = []
            grating_projection_start_point = grating.get_center() + RIGHT * (grating.width/2 + 0.1)

            for i, spec_def in enumerate(spectrum_defs):
                new_opacity = spectral_lines[i].get_fill_opacity() # Get actual opacity after animation
                # Check if it became prominent (e.g. crossed a threshold and increased significantly)
                if new_opacity > 0.05 and (previous_opacities[i] < 0.05 or (new_opacity > previous_opacities[i] + 0.1)):
                    projection_ray = Line(
                        grating_projection_start_point, spectral_lines[i].get_center(),
                        color=spec_def["color"], stroke_width=2
                    )
                    projection_flash_anims.append(ShowPassingFlash(projection_ray.set_stroke(width=2.5), time_width=0.4, run_time=0.4))
                previous_opacities[i] = new_opacity # Update for next iteration
            
            if projection_flash_anims:
                self.play(AnimationGroup(*projection_flash_anims, lag_ratio=0.1)) # Play flashes with a slight lag

            self.wait(0.5 if T_current < 3000 else 0.8) # Wait longer at higher temps

        explanation = Tex(
            "Higher temperature:", "Brighter bulb,", "more intense \\& complete spectrum.", 
            font_size=28, tex_environment="flushleft"
        )
        explanation.set_width(config.frame_width - bulb_group.get_width() - grating.get_width() - 2)
        explanation.next_to(spectral_lines, DOWN, buff=0.5).to_edge(RIGHT, buff=0.5)

        self.play(Write(explanation))
        self.wait(4)

        self.play(
            FadeOut(title), FadeOut(bulb_group), FadeOut(temp_display_bulb),
            FadeOut(grating), FadeOut(grating_label), FadeOut(light_path),
            FadeOut(spectral_lines), FadeOut(explanation)
        )
        self.wait(1)