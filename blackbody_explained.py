import numpy as np
from manim import *

# Define approximate colors for temperatures (adjust as needed)
# Using ManimColor objects directly
TEMP_COLORS = [
    (300, DARK_GRAY),      # Room temperature starting point
    (500, ManimColor.from_rgb([0.4, 0, 0])),  # Deep Red
    (800, RED_E),          # Dull Red
    (1000, RED_D),         # Bright Red
    (1200, ORANGE),        # Orange
    (1400, YELLOW_E),      # Yellow
    (1600, YELLOW_D),      # Brighter Yellow
    (2500, WHITE),         # Approaching White (requires higher temps)
]

# Wien's displacement constant (m*K)
B_Wien = 2.898e-3

# Simplified function for visual spectrum shape (peak shift focus)
# Represents Intensity vs Wavelength (in nm)
# REMOVED internal np.clip for intensity to allow dynamic axis scaling
def pseudo_planck(wavelength_nm, T_kelvin):
    if T_kelvin <= 0: # Avoid division by zero or negative temps
        return np.zeros_like(wavelength_nm)
    lambda_m = wavelength_nm * 1e-9 # Convert nm to m
    lambda_max_m = B_Wien / T_kelvin
    # Use a skewed distribution peaking near lambda_max
    # This is NOT the real Planck law, but visually demonstrates the shift
    peak_nm = lambda_max_m * 1e9
    # Simple Gaussian-like shape, scaled and shifted
    # Use a slightly wider spread for better visualization
    intensity = np.exp(-((wavelength_nm - peak_nm)**2) / (2 * (peak_nm * 0.4)**2))
    # Scale intensity roughly with T^4 (Stefan-Boltzmann) - very approximate
    intensity *= (T_kelvin / 1000)**4
    return intensity # Return raw intensity


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
        nail.set_fill(DARK_GRAY) # Ensure initial fill matches color

        temp_label = Tex("Temperature: ", font_size=30)
        temp_value = DecimalNumber(
            300, # Start at room temp (approx 300K)
            num_decimal_places=0,
            unit=" K",
            font_size=30
        )
        temp_display = VGroup(temp_label, temp_value).arrange(RIGHT).next_to(nail, DOWN, buff=0.5)

        self.play(FadeIn(explanation1))
        self.play(Create(nail), Write(temp_display))
        self.wait(1)

        # Animate heating and color change
        for i in range(1, len(TEMP_COLORS)):
            target_temp, target_color = TEMP_COLORS[i]
            # Calculate animation time - make it proportional to temperature change
            # Ensure previous temp is fetched correctly
            previous_temp = temp_value.get_value()
            anim_time = 1.0 + abs(target_temp - previous_temp) / 500 # Use abs for safety
            if anim_time <= 0: anim_time = 0.5 # Ensure positive run_time

            self.play(
                temp_value.animate.set_value(target_temp),
                nail.animate.set_fill(target_color), # Animate fill color
                run_time=anim_time
            )
            self.wait(0.7)

        self.wait(2)

        explanation2 = Tex(
            "Color shifts: ",
            "Red", " $\\rightarrow$ ",
            "Orange", " $\\rightarrow$ ",
            "Yellow", " $\\rightarrow$ ",
            "White",
            " as T increases",
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

        # --- Physics: Blackbody Spectrum ---
        spectrum_title = Tex("Blackbody Spectrum", font_size=48).to_edge(UP)
        spectrum_expl = Tex("Intensity of radiation vs. Wavelength", font_size=32).next_to(spectrum_title, DOWN, buff=0.2)

        # --- Calculate dynamic Y range BEFORE creating Axes ---
        temps_to_plot = [1000, 1500, 2500, 4000] # K
        colors_to_plot = [RED_D, ORANGE, YELLOW_D, WHITE]
        max_intensity = 0
        # Check wavelengths around the visible spectrum and potential peaks
        wavelengths_for_peak_check = np.linspace(100, 2500, 300) # Wider range, more points
        for T in temps_to_plot:
             intensities = pseudo_planck(wavelengths_for_peak_check, T)
             # Filter out potential NaNs or Infs if pseudo_planck is complex
             valid_intensities = intensities[np.isfinite(intensities)]
             if len(valid_intensities) > 0:
                 max_intensity = max(max_intensity, np.max(valid_intensities))

        # Add some buffer and determine a reasonable step size
        y_max_limit = max_intensity * 1.2 # 20% buffer
        if y_max_limit <= 0: y_max_limit = 10 # Default max if no intensity

        # Aim for about 4-6 major ticks. Round step up to a nice number.
        if y_max_limit < 20:
            y_step = np.ceil(y_max_limit / 5 / 2) * 2 # Round up to nearest 2
        elif y_max_limit < 100:
            y_step = np.ceil(y_max_limit / 5 / 5) * 5 # Round up to nearest 5
        else:
            y_step = np.ceil(y_max_limit / 5 / 10) * 10 # Round up to nearest 10

        if y_step == 0: y_step = 1 # Avoid step=0
        # Adjust max limit to be a multiple of the step size for nice ticks
        y_max_limit = np.ceil(y_max_limit / y_step) * y_step
        # --- End of Y range calculation ---


        # Axes: Wavelength (nm) vs Relative Intensity
        # Remove the unsupported 'margin' parameter
        axes = Axes(
            x_range=[200, 1500, 200], # Wavelength in nm
            y_range=[0, y_max_limit, y_step], # USE DYNAMIC Y RANGE
            x_length=9.5,  # Slightly smaller x_length to leave room for label
            y_length=5.5,  # Slightly taller y-axis
            axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": 0}},
            tips=False,
            x_axis_config={"include_tip": False},
            y_axis_config={"include_tip": False},
        ).add_coordinates() # Add coordinates after initialization
        
        # Shift the entire axes further right to make more room for label
        axes.shift(RIGHT * 0.7)  # Increased from 0.3 to 0.7
        
        x_label = axes.get_x_axis_label(r"\lambda \text{ (nm)}")
        
        # Use a vertical orientation for the y-axis label to save horizontal space
        y_label = Tex(r"\text{Intensity}", font_size=28).rotate(90 * DEGREES)
        
        # Position it further left with more buffer
        y_label.next_to(axes.y_axis, LEFT, buff=0.7)  # Increased buffer
        y_label.shift(UP * 0.5)  # Center it vertically
        
        axes_labels = VGroup(x_label, y_label)

        self.play(Write(spectrum_title), Write(spectrum_expl))
        self.play(Create(axes), Write(axes_labels))
        self.wait(1)

        # Plot spectra for different temperatures
        plots = VGroup()
        peak_dots = VGroup()
        temp_labels = VGroup()

        for i, T in enumerate(temps_to_plot):
            # Calculate peak wavelength for this temperature
            lambda_max_m = B_Wien / T
            lambda_max_nm = lambda_max_m * 1e9

            # FIX: Plot without clamping intensity, axis range handles it now
            plot = axes.plot(
                lambda wl: pseudo_planck(wl, T),
                x_range=[axes.x_range[0], axes.x_range[1]], # Use axis range
                color=colors_to_plot[i],
                use_smoothing=True
            )
            plots.add(plot)

            # Add a dot at the peak wavelength
            # FIX: Calculate peak intensity without clamping
            peak_intensity = pseudo_planck(lambda_max_nm, T)
            # Ensure the point is within the calculated graph bounds before converting
            # (handles cases where peak lambda is outside x_range)
            if axes.x_range[0] <= lambda_max_nm <= axes.x_range[1]:
                 peak_point = axes.c2p(lambda_max_nm, peak_intensity)

                 # Ensure dot is visible even if intensity is low, but don't clamp high
                 if axes.p2c(peak_point)[1] < 0.5: # If peak is too low on graph
                     peak_point = axes.c2p(lambda_max_nm, 0.5)

                 peak_dot = Dot(point=peak_point, color=colors_to_plot[i], radius=0.08)
                 peak_dots.add(peak_dot)

                 # Improved label placement
                 # Try placing slightly above and to the right/left of the peak
                 label_offset_x = 100 if T <= 2000 else -100 # Right for low T, left for high T
                 label_offset_y = 0.1 * y_max_limit # Offset based on axis height
                 label_pos = peak_point + RIGHT * label_offset_x * axes.x_length / (axes.x_range[1]-axes.x_range[0]) + UP * label_offset_y

                 # Basic check to prevent labels going too far off screen (can be refined)
                 if axes.p2c(label_pos)[0] < axes.x_range[0] + 50: label_pos[0] += 1
                 if axes.p2c(label_pos)[0] > axes.x_range[1] - 50: label_pos[0] -= 1
                 if axes.p2c(label_pos)[1] > axes.y_range[1] - 0.2: label_pos[1] -= 0.5

                 temp_label_text = MathTex(f"{T} K", color=colors_to_plot[i], font_size=28).move_to(label_pos)
                 temp_labels.add(temp_label_text)

                 self.play(
                     Create(plot, run_time=2),
                     FadeIn(peak_dot, scale=0.5),
                     Write(temp_label_text)
                 )
                 self.wait(1.0) # Slightly shorter wait
            else:
                 # If peak is outside x_range, just draw the plot without dot/label
                 self.play(Create(plot, run_time=2))
                 self.wait(1.0)


        # Fix the LaTeX error by escaping the ampersand (&) character
        spectrum_summary = Tex(r"Higher T \(\implies\) Higher Intensity \& Peak shifts to shorter \(\lambda\)", 
                              font_size=30).next_to(axes, DOWN, buff=0.4)
        self.play(Write(spectrum_summary))
        self.wait(3)

        planck_text = Tex("Classical physics failed. Planck proposed quantized energy.", font_size=30).next_to(spectrum_summary, DOWN, buff=0.5)
        self.play(FadeIn(planck_text))
        self.wait(2)

        # Clear spectrum elements
        self.play(
            FadeOut(axes), FadeOut(axes_labels), FadeOut(plots), FadeOut(peak_dots),
            FadeOut(temp_labels), FadeOut(spectrum_title), FadeOut(spectrum_expl),
            FadeOut(spectrum_summary), FadeOut(planck_text)
        )
        self.wait(0.5)


        # --- Real World Examples ---
        examples_title = Tex("Real-World Examples", font_size=48).to_edge(UP)
        self.play(Write(examples_title))

        # Incandescent Bulb
        bulb_filament = Line(LEFT*0.5, RIGHT*0.5, color=YELLOW_D, stroke_width=6).shift(UP*1.5)
        bulb_glass = Circle(radius=1.0, color=WHITE).surround(bulb_filament, buffer_factor=1.5)
        bulb_base = Rectangle(width=0.6, height=0.4, color=GRAY).next_to(bulb_glass, DOWN, buff=-0.05)
        bulb = VGroup(bulb_filament, bulb_glass, bulb_base)
        bulb_text = Tex("Incandescent Bulb: Hot filament glows", font_size=30).next_to(bulb, DOWN)

        # Stars
        star1 = Star(n=5, outer_radius=0.5, color=RED_D, fill_opacity=1).shift(DOWN*1.5 + LEFT*2)
        star1_text = Tex("Cooler Star (Red)", font_size=28).next_to(star1, DOWN, buff=0.1)
        star2 = Star(n=5, outer_radius=0.6, color=YELLOW_E, fill_opacity=1).shift(DOWN*1.5)
        star2_text = Tex("Medium Star (Yellow)", font_size=28).next_to(star2, DOWN, buff=0.1)
        star3 = Star(n=5, outer_radius=0.7, color=BLUE_C, fill_opacity=1).shift(DOWN*1.5 + RIGHT*2)
        star3_text = Tex("Hotter Star (Blue)", font_size=28).next_to(star3, DOWN, buff=0.1)
        stars = VGroup(star1, star2, star3)
        stars_text = VGroup(star1_text, star2_text, star3_text)

        self.play(FadeIn(bulb, scale=0.5), Write(bulb_text))
        self.wait(1.5)
        self.play(Create(stars), Write(stars_text))
        self.wait(3)

        self.play(FadeOut(examples_title), FadeOut(bulb), FadeOut(bulb_text), FadeOut(stars), FadeOut(stars_text))
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
        self.play(*[FadeOut(mob) for mob in self.mobjects]) # Fade out everything
        self.wait(1)

