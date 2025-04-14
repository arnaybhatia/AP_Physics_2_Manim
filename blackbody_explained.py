import numpy as np
from manim import *

# Define a list of colors and corresponding temperatures.
# This is used to visualize the color change as the temperature increases.
TEMP_COLORS = [
    (300, DARK_GRAY),      # Starting color at room temperature (300K).
    (500, ManimColor.from_rgb([0.4, 0, 0])),  # Deep red.  Using ManimColor for precise color control.
    (800, RED_E),          # Dull red.
    (1000, RED_D),         # Bright red.
    (1200, ORANGE),        # Orange.
    (1400, YELLOW_E),      # Yellow.
    (1600, YELLOW_D),      # Brighter Yellow.
    (2500, WHITE),         # Approaching white (requires higher temperatures).
]

# Wien's displacement constant in meter-Kelvin (m*K). This is a fundamental constant
# used in Wien's Law to calculate the peak wavelength of blackbody radiation.
B_Wien = 2.898e-3

# This function calculates the intensity of blackbody radiation as a function of
# wavelength and temperature.  It's a simplified version focused on the peak shift.
# The function returns the intensity at a given wavelength, for a given temperature.
def pseudo_planck(wavelength_nm, T_kelvin):
    # Convert the input wavelength to a NumPy array. This ensures that the
    # function can handle a range of wavelengths efficiently.
    wavelength_nm = np.asarray(wavelength_nm)

    # Handle the case where temperature is zero or negative. In this scenario,
    # there is no blackbody radiation, so we return an array of zeros with the
    # same shape as the wavelength array.
    if T_kelvin <= 0:
        return np.zeros_like(wavelength_nm)

    # Convert wavelength from nanometers to meters.
    lambda_m = wavelength_nm * 1e-9

    # Calculate the peak wavelength (in meters) using Wien's displacement law.
    lambda_max_m = B_Wien / T_kelvin

    # Convert the peak wavelength to nanometers.
    peak_nm = lambda_max_m * 1e9

    # Define the width of the distribution, to better match real blackbody curves.
    left_width = peak_nm * 0.3
    right_width = peak_nm * 0.6

    # Create boolean arrays to separate the wavelengths into two regions:
    # wavelengths less than the peak, and wavelengths greater than the peak.
    left_side = wavelength_nm <= peak_nm
    right_side = wavelength_nm > peak_nm

    # Initialize an array to store the intensity values.  The shape matches
    # the input wavelength array.
    intensity = np.zeros_like(wavelength_nm)

    # Calculate the intensity for wavelengths less than or equal to the peak.
    # The formula is a Gaussian-like distribution.  The left side (shorter wavelengths)
    # falls off more sharply.
    intensity[left_side] = np.exp(-((wavelength_nm[left_side] - peak_nm)**2) / (2 * left_width**2))

    # Calculate the intensity for wavelengths greater than the peak.  The right
    # side (longer wavelengths) has a gentler falloff.
    intensity[right_side] = np.exp(-((wavelength_nm[right_side] - peak_nm)**2) / (2 * right_width**2))

    # Scale the intensity, roughly, with T^4. This approximates the Stefan-Boltzmann law,
    # which states that the total power radiated is proportional to T^4. This is a
    # simplified approximation for visual purposes.
    intensity *= (T_kelvin / 1000)**4

    # Return the raw intensity values.  The dynamic axis scaling in the Manim
    # scene will handle the final display scaling.
    return intensity

class BlackbodyRadiationExplained(Scene):
    def construct(self):
        # --- Title Scene ---

        # Create the title text object.  Set the font size to 60.
        title = Tex("Blackbody Radiation", font_size=60)

        # Create the subtitle text object and position it below the title.
        subtitle = Tex("From Heat to Light", font_size=40).next_to(title, DOWN, buff=0.3)

        # Create the introductory text and position it below the subtitle.
        intro_text = Tex(
            "All objects emit radiation based on their temperature.",
            font_size=32
        ).next_to(subtitle, DOWN, buff=0.5)

        # Play animations to display the title, subtitle, and introductory text.
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.play(FadeIn(intro_text, shift=UP))

        # Wait for 2 seconds.
        self.wait(2)

        # Fade out the title, subtitle, and introductory text.
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(intro_text))

        # Wait for a short period.
        self.wait(0.5)

        # --- Simulated Experiment ---

        # Create the explanation text for the heating experiment.
        explanation1 = Tex("Let's heat an object, like an iron nail:", font_size=36).to_edge(UP)

        # Create a rectangle to represent the iron nail. Set the initial color.
        nail = Rectangle(width=3, height=0.3, color=DARK_GRAY, fill_opacity=1).round_corners(0.1)
        nail.set_fill(DARK_GRAY)

        # Create the temperature label.
        temp_label = Tex("Temperature: ", font_size=30)

        # Create the temperature value display.
        temp_value = DecimalNumber(
            300, # Start at room temp (approx 300K)
            num_decimal_places=0,
            unit=" K",
            font_size=30
        )

        # Group the temperature label and value together.
        temp_display = VGroup(temp_label, temp_value).arrange(RIGHT).next_to(nail, DOWN, buff=0.5)

        # Display the explanation text and the iron nail, with its temperature display.
        self.play(FadeIn(explanation1))
        self.play(Create(nail), Write(temp_display))

        # Wait a moment.
        self.wait(1)

        # Animate the heating of the nail and the corresponding color changes.
        for i in range(1, len(TEMP_COLORS)): # Start from index 1 to show color changes
            # Extract target temperature and color.
            target_temp, target_color = TEMP_COLORS[i]

            # Calculate animation time based on the temperature change.  This makes
            # the animation duration proportional to the temperature difference.
            previous_temp = temp_value.get_value()
            anim_time = 1.0 + abs(target_temp - previous_temp) / 500  # Use abs for safety
            if anim_time <= 0:
                anim_time = 0.5  # Ensure positive run_time

            # Animate the temperature display and the color of the nail.
            self.play(
                temp_value.animate.set_value(target_temp), # Update temperature
                nail.animate.set_fill(target_color),      # Change nail color
                run_time=anim_time                        # Set animation time
            )

            # Wait a short time between each temperature step.
            self.wait(0.7)

        # Wait a longer time after the heating animation.
        self.wait(2)

        # Create the explanation text for the color shifts.
        explanation2 = Tex(
            "Color shifts: ",
            "Red", " $\\rightarrow$ ",
            "Orange", " $\\rightarrow$ ",
            "Yellow", " $\\rightarrow$ ",
            "White",
            " as T increases",
            font_size=32
        )

        # Set the colors for specific text elements to match the color changes.
        explanation2[1].set_color(RED_D)
        explanation2[3].set_color(ORANGE)
        explanation2[5].set_color(YELLOW_D)
        explanation2[7].set_color(WHITE)

        # Position the color shift explanation below the temperature display.
        explanation2.next_to(temp_display, DOWN, buff=0.5)

        # Display the color shift explanation.
        self.play(Write(explanation2))

        # Wait a moment.
        self.wait(2)

        # Fade out the nail, temperature display, and explanations.
        self.play(
            FadeOut(nail), FadeOut(temp_display), FadeOut(explanation1), FadeOut(explanation2)
        )

        # Wait a short time.
        self.wait(0.5)

        # --- Physics: Wien's Law ---

        # Create the title for Wien's Displacement Law.
        wien_title = Tex("Wien's Displacement Law", font_size=48).to_edge(UP)

        # Create the formula for Wien's Law.
        wien_formula = MathTex(r"\lambda_{max} = \frac{b}{T}", font_size=60)

        # Create an explanation of Wien's Law.
        wien_explanation = Tex(
            r"Peak wavelength (\(\lambda_{max}\)) is inversely proportional to Temperature (T).",
            font_size=32
        ).next_to(wien_formula, DOWN, buff=0.5)

        # Create an implication of Wien's Law.
        wien_implication = Tex(
            r"Higher T \(\implies\) Shorter \(\lambda_{max}\) (shifts towards blue/white)",
            font_size=32
        ).next_to(wien_explanation, DOWN, buff=0.3)

        # Display the title, formula, explanation, and implication.
        self.play(Write(wien_title))
        self.play(Write(wien_formula))
        self.play(FadeIn(wien_explanation, shift=UP))
        self.play(FadeIn(wien_implication, shift=UP))

        # Wait a moment.
        self.wait(3)

        # Fade out the Wien's Law elements.
        self.play(
            FadeOut(wien_title), FadeOut(wien_formula),
            FadeOut(wien_explanation), FadeOut(wien_implication)
        )

        # Wait a moment.
        self.wait(0.5)

        # --- Physics: Blackbody Spectrum ---

        # Create the title for the blackbody spectrum section.
        spectrum_title = Tex("Blackbody Spectrum", font_size=48).to_edge(UP)

        # Create an explanation of the blackbody spectrum.
        spectrum_expl = Tex("Intensity of radiation vs. Wavelength", font_size=32).next_to(spectrum_title, DOWN, buff=0.2)

        # Define a list of temperatures to plot.
        temps_to_plot = [1000, 1500, 2500, 4000] # K

        # Define a list of colors for the plots, matching the temperatures.
        colors_to_plot = [RED_D, ORANGE, YELLOW_D, WHITE]

        # --- Calculate dynamic Y range BEFORE creating Axes ---

        # Determine the maximum intensity value to set the y-axis range dynamically.
        max_intensity = 0

        # Define the wavelengths to check for the peak.
        wavelengths_for_peak_check = np.linspace(50, 2500, 300) # Start lower (50nm)

        # Iterate through the temperatures and calculate the intensities
        for T_check in temps_to_plot:
            # Calculate intensities for the current temperature
            intensities = pseudo_planck(wavelengths_for_peak_check, T_check)
            # Filter out any invalid intensity values (e.g., due to numerical errors)
            valid_intensities = intensities[np.isfinite(intensities)]
            # Find the maximum intensity value
            if len(valid_intensities) > 0:
                max_intensity = max(max_intensity, np.max(valid_intensities))

        # Calculate a buffer for the maximum intensity. This ensures that the
        # plots don't reach the edge of the graph.  Increase the buffer.
        y_max_limit = max_intensity * 1.4 # Increased buffer to 40%

        # Handle cases where there's no radiation.
        if y_max_limit <= 0:
            y_max_limit = 10  # Default max if no intensity

        # Determine the y-axis step size for tick marks.  Aim for roughly 4-6 major ticks.
        if y_max_limit < 1:
            y_step = 0.2 # Handle small intensity cases
        elif y_max_limit < 10:
            y_step = np.ceil(y_max_limit / 5) # Round step up
        elif y_max_limit < 100:
            y_step = np.ceil(y_max_limit / 5 / 5) * 5 # Round up to nearest 5
        else:
            # Ensure step is significant enough for large ranges
            power_of_10 = 10**np.floor(np.log10(y_max_limit/5))
            y_step = np.ceil(y_max_limit / 5 / power_of_10) * power_of_10

        # Avoid step size of zero.
        if y_step == 0:
            y_step = 1

        # Adjust the maximum y-axis limit to be a multiple of the step size. This
        # makes the tick marks cleaner.
        y_max_limit = np.ceil(y_max_limit / y_step) * y_step

        # --- End of Y range calculation ---

        # Create the axes for the plot, with the x-axis as wavelength (nm) and
        # the y-axis as intensity.
        axes = Axes(
            x_range=[200, 1500, 200], # Wavelength in nm, start at 200nm
            y_range=[0, y_max_limit, y_step], # USE DYNAMIC Y RANGE
            x_length=9.5,
            y_length=5.5,
            axis_config={"include_numbers": True},
            tips=False,
            x_axis_config={"include_tip": False},
            y_axis_config={"include_tip": False},
        ).add_coordinates()

        # Shift the axes slightly to the right to create more space for labels.
        axes.shift(RIGHT * 0.7)  # Increased from 0.3 to 0.7

        # Create the x-axis label.
        x_label = axes.get_x_axis_label(r"\lambda \text{ (nm)}")

        # Create the y-axis label and rotate it for better readability.
        y_label = Tex(r"\text{Intensity}", font_size=28).rotate(90 * DEGREES)

        # Position the y-axis label to the left of the y-axis, with some buffer.
        y_label.next_to(axes.y_axis, LEFT, buff=0.7) # Increased buffer
        y_label.shift(UP * 0.5) # Center it vertically

        # Group the axis labels together.
        axes_labels = VGroup(x_label, y_label)

        # Display the title, explanation, axes, and labels.
        self.play(Write(spectrum_title), Write(spectrum_expl))
        self.play(Create(axes), Write(axes_labels))

        # Wait a moment.
        self.wait(1)

        # Create a VGroup to hold all the plots.
        plots = VGroup()

        # Create a VGroup to hold the dots marking the peak wavelengths.
        peak_dots = VGroup()

        # Create a VGroup to hold the temperature labels for the plots.
        temp_labels = VGroup()

        # Iterate through the list of temperatures.
        for i, T in enumerate(temps_to_plot):
            # Calculate the peak wavelength for the current temperature using
            # Wien's displacement law.
            lambda_max_m = B_Wien / T
            lambda_max_nm = lambda_max_m * 1e9

            # Plot the blackbody spectrum for the current temperature.
            # The lambda argument is a lambda function that takes a wavelength
            # in nanometers and returns the corresponding intensity.
            plot = axes.plot(
                lambda wl: pseudo_planck(wl, T), # Pass temperature T
                x_range=[axes.x_range[0], axes.x_range[1]], # Use axis range
                color=colors_to_plot[i],
                use_smoothing=True # Smooth the curve
            )
            # Add the plot to the plots VGroup.
            plots.add(plot)

            # Add a dot at the peak wavelength.
            # Calculate the peak intensity using the `pseudo_planck` function.
            peak_intensity = pseudo_planck(lambda_max_nm, T)

            # Check if the peak wavelength is within the x-axis range.
            if axes.x_range[0] <= lambda_max_nm <= axes.x_range[1]:
                # Check if the peak intensity is within the y-axis range before converting.
                if axes.y_range[0] <= peak_intensity <= axes.y_range[1]:
                     peak_point = axes.c2p(lambda_max_nm, peak_intensity)
                else:
                    # If peak intensity is outside calculated dynamic range, clamp it
                    peak_intensity_clamped = np.clip(peak_intensity, axes.y_range[0], axes.y_range[1])
                    peak_point = axes.c2p(lambda_max_nm, peak_intensity_clamped)

                # Create a dot at the peak wavelength.
                peak_dot = Dot(point=peak_point, color=colors_to_plot[i], radius=0.08)

                # Add the dot to the peak_dots VGroup.
                peak_dots.add(peak_dot)

                # Calculate the offset for the label to avoid overlap.
                label_offset_y = 0.15 * y_max_limit if i % 2 else -0.15 * y_max_limit

                # Position the label to the left or right, depending on peak.
                if lambda_max_nm < (axes.x_range[0] + axes.x_range[1]) / 2:
                    label_offset_x = 150  # Right side for left peaks
                else:
                    label_offset_x = -150  # Left side for right peaks

                # Determine the position for the temperature label.
                label_pos = peak_point + RIGHT * label_offset_x * axes.x_length / (axes.x_range[1]-axes.x_range[0]) + UP * label_offset_y

                # Ensure label stays within axes bounds
                label_pos[0] = max(label_pos[0], axes.x_range[0] * axes.x_axis.unit_size + axes.x_axis.get_start()[0] + 0.5)
                label_pos[0] = min(label_pos[0], axes.x_range[1] * axes.x_axis.unit_size + axes.x_axis.get_start()[0] - 0.5)
                label_pos[1] = max(label_pos[1], axes.y_range[0] * axes.y_axis.unit_size + axes.y_axis.get_start()[1] + 0.2)
                label_pos[1] = min(label_pos[1], axes.y_range[1] * axes.y_axis.unit_size + axes.y_axis.get_start()[1] - 0.2)

                # Create the temperature label.
                temp_label_text = MathTex(f"{T} K", color=colors_to_plot[i], font_size=28).move_to(label_pos)

                # Add the label to the temp_labels VGroup.
                temp_labels.add(temp_label_text)

                # Animate the creation of the plot, the dot, and the temperature label.
                self.play(
                    Create(plot, run_time=2),
                    FadeIn(peak_dot, scale=0.5),
                    Write(temp_label_text)
                )
                self.wait(1.0)  # Slightly shorter wait time

            else:
                # If peak is outside x_range, just draw the plot without dot/label
                self.play(Create(plot, run_time=2))
                self.wait(1.0)

        # Create a summary text explaining the blackbody spectrum.  The r"" string
        # is used for raw strings, to avoid having to escape backslashes.
        spectrum_summary = Tex(r"Higher T \(\implies\) Higher Intensity \& Peak shifts to shorter \(\lambda\)",
                              font_size=30).next_to(axes, DOWN, buff=0.4)

        # Display the summary text.
        self.play(Write(spectrum_summary))

        # Wait a moment.
        self.wait(3)

        # Add a text explaining why classical physics failed.
        planck_text = Tex("Classical physics failed. Planck proposed quantized energy.", font_size=30).next_to(spectrum_summary, DOWN, buff=0.5)

        # Display Planck's text
        self.play(FadeIn(planck_text))

        # Wait a moment.
        self.wait(2)

        # Fade out the spectrum elements.
        self.play(
            FadeOut(axes), FadeOut(axes_labels), FadeOut(plots), FadeOut(peak_dots),
            FadeOut(temp_labels), FadeOut(spectrum_title), FadeOut(spectrum_expl),
            FadeOut(spectrum_summary), FadeOut(planck_text)
        )

        # Wait a moment.
        self.wait(0.5)

        # --- Real World Examples ---

        # Create the title for the real-world examples section.
        examples_title = Tex("Real-World Examples", font_size=48).to_edge(UP)

        # Display the title.
        self.play(Write(examples_title))

        # --- Incandescent Bulb ---

        # Create the filament for the incandescent bulb.
        bulb_filament = Line(LEFT*0.5, RIGHT*0.5, color=YELLOW_D, stroke_width=6).shift(UP*1.5)

        # Create the glass bulb around the filament.
        bulb_glass = Circle(radius=1.0, color=WHITE).surround(bulb_filament, buffer_factor=1.5)

        # Create the base of the bulb.
        bulb_base = Rectangle(width=0.6, height=0.4, color=GRAY).next_to(bulb_glass, DOWN, buff=-0.05)

        # Group the bulb elements.
        bulb = VGroup(bulb_filament, bulb_glass, bulb_base)

        # Create the text for the incandescent bulb example.
        bulb_text = Tex("Incandescent Bulb: Hot filament glows", font_size=30).next_to(bulb, DOWN)

        # --- Stars ---

        # Define the vertical position for the stars.
        star_y_pos = DOWN * 1.5

        # Define the buffer value for spacing.
        star_buff = 0.3

        # Increased horizontal spacing between the stars.
        star_h_spacing = 3.5

        # Create the first star (cooler star).
        star1 = Star(n=5, outer_radius=0.5, color=RED_D, fill_opacity=1).shift(star_y_pos + LEFT*star_h_spacing)

        # Create the text for the first star.
        star1_text = Tex("Cooler Star (Red)", font_size=28).next_to(star1, DOWN, buff=star_buff)

        # Create the second star (medium temperature).
        star2 = Star(n=5, outer_radius=0.6, color=YELLOW_E, fill_opacity=1).shift(star_y_pos)

        # Create the text for the second star.
        star2_text = Tex("Medium Star (Yellow)", font_size=28).next_to(star2, DOWN, buff=star_buff)

        # Create the third star (hotter star).
        star3 = Star(n=5, outer_radius=0.7, color=BLUE_C, fill_opacity=1).shift(star_y_pos + RIGHT*star_h_spacing)

        # Create the text for the third star.
        star3_text = Tex("Hotter Star (Blue)", font_size=28).next_to(star3, DOWN, buff=star_buff)

        # Group the stars together.
        stars = VGroup(star1, star2, star3)

        # Group the star text together.
        stars_text = VGroup(star1_text, star2_text, star3_text)

        # Display the incandescent bulb and its text.
        self.play(FadeIn(bulb, scale=0.5), Write(bulb_text))

        # Wait a moment.
        self.wait(1.5)

        # Animate the stars and their labels.
        self.play(Create(stars), Write(stars_text))

        # Wait.
        self.wait(3)

        # Fade out the real-world examples.
        self.play(FadeOut(examples_title), FadeOut(bulb), FadeOut(bulb_text), FadeOut(stars), FadeOut(stars_text))

        # Wait a moment.
        self.wait(0.5)

        # --- Conclusion ---

        # Create the first part of the conclusion text.
        conclusion = Tex("Blackbody radiation connects temperature, color, and light,", font_size=36)

        # Create the second part of the conclusion text.
        conclusion2 = Tex("a key concept in physics.", font_size=36).next_to(conclusion, DOWN)

        # Create the final thanks text.
        final_thanks = Tex("Thanks for watching!", font_size=40).next_to(conclusion2, DOWN, buff=0.8)

        # Display the conclusion and thanks.
        self.play(Write(conclusion))
        self.play(Write(conclusion2))

        # Wait a moment.
        self.wait(1.5)
        self.play(FadeIn(final_thanks))

        # Wait.
        self.wait(3)

        # Fade out all the objects in the scene.
        self.play(*[FadeOut(mob) for mob in self.mobjects])

        # Wait one second at the end.
        self.wait(1)
