import numpy as np
from manim import *

# Define a list of colors and corresponding temperatures for cube glow
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

        # Black Square
        square = Square(side_length=2.5, fill_color=BLACK, fill_opacity=1, stroke_color=DARK_GRAY, stroke_width=2)
        square_label = Tex("Black Body (Square)", font_size=36).next_to(square, DOWN, buff=0.5)
        self.play(Create(square), Write(square_label))
        self.wait(0.5)

        # Light beams
        beam_colors = [BLUE_C, GREEN_C, YELLOW_C, ORANGE, RED_C]
        beam_start_points = [
            UP * 3 + LEFT * 3.5,
            UP * 3 + RIGHT * 3.5,
            DOWN * 1 + LEFT * 4,
            UP * 1 + RIGHT * 4,
            UP * 3.5 + LEFT * 0,
        ]

        beams = VGroup()
        for i, color in enumerate(beam_colors):
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
        outer_glow = Square(side_length=2.8, fill_opacity=0, stroke_width=0)
        outer_glow.move_to(square.get_center())

        square.add_updater(lambda m: m.set_fill(
            color=interpolate_color(
                TEMP_COLORS_CUBE[int(temp_tracker.get_value()) % len(TEMP_COLORS_CUBE)][1],
                TEMP_COLORS_CUBE[min(len(TEMP_COLORS_CUBE)-1, int(temp_tracker.get_value()) + 1)][1],
                temp_tracker.get_value() % 1
            ),
            opacity=1
        ).set_stroke(DARK_GRAY, width=1))

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


class Anim5_LightInteraction(Scene):
    """
    Animation 5: Light beam interaction with a surface (reflection, absorption, transmission).
    """
    def construct(self):
        self.camera.background_color = BLACK

        surface_line = Line(LEFT * 3.5, RIGHT * 3.5, color=BLUE_D, stroke_width=6).shift(DOWN*1)
        surface_label = Tex("Surface", font_size=28, color=BLUE_D).next_to(surface_line, DOWN, buff=0.3)
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

        transmitted_ray = Arrow(impact_point_on_surface, impact_point_on_surface + transmitted_vec_dir * 2.0, buff=0, color=LIGHT_GRAY, stroke_width=5, stroke_opacity=0.8)
        transmitted_label = Tex("Transmitted", font_size=26, color=LIGHT_GRAY).next_to(transmitted_ray.get_end(), transmitted_vec_dir, buff=0.2)

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
    Animation 6: Displays a refined chart mapping visible light wavelengths to colors,
    built from scratch for a cleaner look.
    """
    def construct(self):
        self.camera.background_color = BLACK

        # Data from the image: [Color Name, Wavelength Range, Manim Color]
        spectrum_data_new = [
            {"name": "Violet", "wavelength": "380-450", "color": ManimColor("#8A2BE2")}, # BlueViolet
            {"name": "Blue", "wavelength": "450-495", "color": ManimColor("#1E90FF")},   # DodgerBlue
            {"name": "Green", "wavelength": "495-570", "color": ManimColor("#90EE90")},   # LightGreen
            {"name": "Yellow", "wavelength": "570-590", "color": ManimColor("#FFD700")},  # Gold / Bright Yellow
            {"name": "Orange", "wavelength": "590-620", "color": ManimColor("#FFA500")},  # Orange
            {"name": "Red", "wavelength": "620-750", "color": ManimColor("#FF4500")},      # OrangeRed / Bright Red
        ]

        # --- Main Title ---
        title_main = Tex("Visible Light Spectrum (Manual Layout)", font_size=32)
        title_main.to_edge(UP, buff=0.6)
        self.play(Write(title_main))
        self.wait(0.3)

        # --- Layout Properties ---
        col_width_color = 3.2
        col_width_wavelength = 2.8
        row_height = 0.65
        total_width = col_width_color + col_width_wavelength

        cell_stroke_width = 1.0
        cell_stroke_color = DARK_GRAY
        header_line_stroke_width = 1.5

        chart_top_y = title_main.get_bottom()[1] - 0.6
        chart_center_x = 0
        start_x_chart = chart_center_x - total_width / 2
        header_y_center = chart_top_y - row_height / 2

        header_font_size = 22
        data_font_size = 18
        # text_color_on_swatch = WHITE # Default to white for text on swatches

        # --- Create Headers ---
        header_color_text = Tex("Color", font_size=header_font_size, color=WHITE)
        header_wavelength_text = Tex("Wavelength (nm)", font_size=header_font_size, color=WHITE)

        header_color_text.move_to(np.array([start_x_chart + col_width_color / 2, header_y_center, 0]))
        header_wavelength_text.move_to(np.array([start_x_chart + col_width_color + col_width_wavelength / 2, header_y_center, 0]))

        header_color_cell_bg = Rectangle(
            width=col_width_color, height=row_height,
            stroke_width=0, fill_opacity=0
        ).move_to(header_color_text.get_center())

        header_wavelength_cell_bg = Rectangle(
            width=col_width_wavelength, height=row_height,
            stroke_width=0, fill_opacity=0
        ).move_to(header_wavelength_text.get_center())

        header_bottom_line = Line(
            start_x_chart * RIGHT + (chart_top_y - row_height) * UP,
            (start_x_chart + total_width) * RIGHT + (chart_top_y - row_height) * UP,
            stroke_width=header_line_stroke_width, color=WHITE
        )
        header_vertical_line = Line(
            (start_x_chart + col_width_color) * RIGHT + chart_top_y * UP,
            (start_x_chart + col_width_color) * RIGHT + (chart_top_y - row_height) * UP,
            stroke_width=header_line_stroke_width, color=WHITE
        )

        header_group = VGroup(
            header_color_cell_bg, header_wavelength_cell_bg,
            header_color_text, header_wavelength_text,
            header_bottom_line, header_vertical_line
        )
        self.play(
            Write(header_color_text),
            Write(header_wavelength_text),
            Create(header_bottom_line),
            Create(header_vertical_line),
            run_time=1.0
        )
        self.wait(0.3)

        all_chart_elements = VGroup(title_main, header_group)

        # --- Create Data Rows ---
        current_row_top_edge_y = chart_top_y - row_height
        animation_group = []

        for i, item in enumerate(spectrum_data_new):
            row_center_y = current_row_top_edge_y - (row_height / 2)

            swatch_cell = Rectangle(
                width=col_width_color,
                height=row_height,
                fill_color=item["color"],
                fill_opacity=1,
                stroke_width=cell_stroke_width,
                stroke_color=cell_stroke_color
            )
            swatch_cell.move_to(np.array([start_x_chart + col_width_color / 2, row_center_y, 0]))

            # Determine text color for good contrast
            # Simple check: if the name is Yellow or Green (typically lighter), use darker text.
            # Your screenshot uses white text for all, which also looks good with the chosen swatch colors.
            text_color_for_this_swatch = WHITE
            if item["name"] in ["Yellow", "Green"] and (item["color"] == ManimColor("#90EE90") or item["color"] == ManimColor("#FFD700")):
                 text_color_for_this_swatch = DARK_GRAY # Or even BLACK

            color_name_text = Tex(item["name"], font_size=data_font_size, color=text_color_for_this_swatch)
            color_name_text.move_to(swatch_cell.get_center())

            wavelength_data_cell = Rectangle(
                width=col_width_wavelength,
                height=row_height,
                fill_opacity=0,
                stroke_width=cell_stroke_width,
                stroke_color=cell_stroke_color
            )
            wavelength_data_cell.move_to(np.array([start_x_chart + col_width_color + col_width_wavelength / 2, row_center_y, 0]))

            wavelength_text = Tex(item["wavelength"], font_size=data_font_size, color=WHITE)
            wavelength_text.move_to(wavelength_data_cell.get_center())

            current_row_group = VGroup(swatch_cell, color_name_text, wavelength_data_cell, wavelength_text)
            all_chart_elements.add(current_row_group)
            animation_group.append(current_row_group)

            current_row_top_edge_y -= row_height

        self.play(LaggedStart(*[FadeIn(row, shift=UP*0.2) for row in animation_group], lag_ratio=0.2, run_time=1.5))

        self.wait(3)
        self.play(FadeOut(all_chart_elements, shift=DOWN*0.5), run_time=1.0)
        self.wait(1)