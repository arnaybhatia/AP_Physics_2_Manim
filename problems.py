import numpy as np
from manim import *

# --- Helper functions / Constants ---
WIEN_CONSTANT = 2.898e-3  # m*K
WIEN_CONSTANT_STR = "2.898 \\times 10^{-3} \\, \\text{m} \\cdot \\text{K}"
GREEN_WAVELENGTH_NM = 550
GREEN_WAVELENGTH_M = GREEN_WAVELENGTH_NM * 1e-9

BULB_GLOW_COLORS = [
    (0, BLACK), (1000, RED_E), (2000, RED_D), (3000, ORANGE),
    (4000, YELLOW_E), (4800, YELLOW_D),
    (5000, interpolate_color(YELLOW_D, GREEN_D, 0.5)),
    (5100, interpolate_color(YELLOW_D, GREEN_D, 0.7)), (5270, GREEN_C)
]

def get_bulb_color(temperature):
    temp_values = [t for t, c in BULB_GLOW_COLORS]
    color_values = [c for t, c in BULB_GLOW_COLORS]
    if temperature <= temp_values[0]: return color_values[0]
    if temperature >= temp_values[-1]: return color_values[-1]
    for i in range(len(temp_values) - 1):
        if temp_values[i] <= temperature < temp_values[i+1]:
            t_ratio = (temperature - temp_values[i]) / (temp_values[i+1] - temp_values[i])
            return interpolate_color(color_values[i], color_values[i+1], t_ratio)
    return color_values[-1]

class Bulb(VGroup):
    def __init__(self, glass_color=GRAY_B, filament_color=DARK_GRAY, base_color=GRAY, glow_opacity=0.7, **kwargs):
        super().__init__(**kwargs)
        self.glass_outer_radius = 0.8; self.neck_height = 0.4; self.base_height = 0.5
        self.neck_radius = 0.3; self.base_radius = 0.35
        bulb_shape = Circle(radius=self.glass_outer_radius, color=glass_color, fill_opacity=0.1, stroke_width=2)
        bulb_shape.stretch_to_fit_height(1.5).move_to(UP * (self.neck_height / 2 + 1.5 / 2))
        neck = Rectangle(width=self.neck_radius * 2, height=self.neck_height, color=glass_color, fill_opacity=0.1, stroke_width=2).next_to(bulb_shape, DOWN, buff=0)
        base = Rectangle(width=self.base_radius * 2, height=self.base_height, color=base_color, fill_opacity=1, stroke_width=1.5).next_to(neck, DOWN, buff=0)
        filament_y_pos = bulb_shape.get_center()[1]
        self.filament = Line(LEFT * 0.2 + filament_y_pos * UP, RIGHT * 0.2 + filament_y_pos * UP, color=filament_color, stroke_width=3)
        self.glow = Circle(radius=self.glass_outer_radius * 0.95, fill_opacity=glow_opacity, stroke_width=0).move_to(bulb_shape.get_center()).set_fill(BLACK)
        self.add(self.glow, bulb_shape, neck, base, self.filament)

    def set_glow_color(self, color):
        self.glow.set_fill(color); self.filament.set_color(color if color != BLACK else DARK_GRAY)

class PracticeProblemScene(Scene):
    """Scene 1: Problem Setup and Calculation - Larger Text, Fewer Transitions"""
    def construct(self):
        self.camera.background_color = BLACK
        frame_width = self.camera.frame_width
        frame_height = self.camera.frame_height

        title_fs = 50
        question_fs = 40
        text_fs = 36
        math_fs = 42
        
        title_problem = Tex("Let's Try a Practice Problem!", font_size=title_fs).to_edge(UP, buff=0.4)
        q_text_str = "What temperature is needed for a light bulb to emit green light?"
        question = Tex(q_text_str, font_size=question_fs, tex_environment="flushleft")
        question.set_width(frame_width - 1.0).next_to(title_problem, DOWN, buff=0.4)
        recall_chart = Tex("Green light implies $\\lambda \\approx 550 \\, \\text{nm}$.", font_size=text_fs)
        recall_chart.next_to(question, DOWN, buff=0.4, aligned_edge=LEFT)
        wien_law_intro = Tex("Apply Wien's Displacement Law:", font_size=text_fs)
        wien_law_intro.next_to(recall_chart, DOWN, buff=0.4, aligned_edge=LEFT)
        wien_law_formula = MathTex("T = {b \\over \\lambda_{max}}", font_size=math_fs)
        wien_law_formula.next_to(wien_law_intro, DOWN, buff=0.35)
        b_constant_text = MathTex(f"b = {WIEN_CONSTANT_STR}", font_size=text_fs - 2)
        b_constant_text.next_to(wien_law_formula, DOWN, buff=0.35)
        problem_setup_group = VGroup(
            title_problem, question, recall_chart,
            wien_law_intro, wien_law_formula, b_constant_text
        )
        
        max_height_part1 = frame_height * 0.95
        if problem_setup_group.get_height() > max_height_part1: # Removed include_invisible
            problem_setup_group.scale_to_fit_height(max_height_part1)
        problem_setup_group.move_to(ORIGIN)

        self.play(Write(title_problem), run_time=0.7)
        self.play(Write(question), run_time=1.2)
        self.play(Write(recall_chart), run_time=0.7)
        self.play(Write(wien_law_intro), run_time=0.7)
        self.play(Write(wien_law_formula), run_time=0.7)
        self.play(Write(b_constant_text), run_time=0.7)
        self.wait(1.5)

        calc_title = Tex("Calculation", font_size=title_fs).to_edge(UP, buff=0.4)
        sub_intro_text = Tex("Given $\\lambda_{max} = 550 \\, \\text{nm} = 550 \\times 10^{-9} \\, \\text{m}$", font_size=text_fs)
        sub_intro_text.next_to(calc_title, DOWN, buff=0.5)
        substituted_formula = MathTex(
            "T = {", WIEN_CONSTANT_STR, "\\over", f"550 \\times 10^{{-9}} \\, \\text{{m}}", "}",
            font_size=math_fs
        )
        substituted_formula.next_to(sub_intro_text, DOWN, buff=0.4)
        calculated_temp_val = WIEN_CONSTANT / GREEN_WAVELENGTH_M
        result_temp = MathTex(f"T \\approx {calculated_temp_val:.0f} \\, \\text{{K}}", font_size=math_fs + 2, color=YELLOW)
        result_temp.next_to(substituted_formula, DOWN, buff=0.5)
        calculation_group = VGroup(calc_title, sub_intro_text, substituted_formula, result_temp)
        
        max_height_part2 = frame_height * 0.9
        if calculation_group.get_height() > max_height_part2: # Removed include_invisible
            calculation_group.scale_to_fit_height(max_height_part2)
        calculation_group.move_to(ORIGIN)

        self.play(FadeOut(problem_setup_group, shift=UP*0.3), run_time=0.5)
        self.wait(0.1)
        self.play(Write(calc_title))
        self.play(Write(sub_intro_text))
        self.play(Write(substituted_formula))
        self.play(Write(result_temp))
        self.wait(2.5)

        outro_text_str = "Theory clear. Does it work in real life?"
        outro_text = Tex(outro_text_str, font_size=question_fs).center()
        self.play(FadeOut(calculation_group, shift=UP*0.3), run_time=0.5)
        self.wait(0.1)
        self.play(Write(outro_text), run_time=1.2)
        self.wait(2)
        
        self.play(FadeOut(outro_text))
        self.wait(0.5)

class AnalysisScene(Scene):
    """Scene 2: Analysis and Conclusion - Larger Text, Sequential Frames, Better Fit"""
    def construct(self):
        self.camera.background_color = BLACK
        frame_width = self.camera.frame_width
        frame_height = self.camera.frame_height

        title_fs = 48
        header_fs = 38
        text_fs = 32
        small_text_fs = 26
        math_fs = 36

        top_margin = 0.4
        bottom_margin = 0.4
        side_margin = 0.5

        def create_and_present_frame(main_title_text, elements_for_frame, prev_elements_to_fade=None):
            if prev_elements_to_fade:
                self.play(FadeOut(prev_elements_to_fade, shift=UP * 0.3), run_time=0.5)
                self.wait(0.1)

            current_title = Tex(main_title_text, font_size=title_fs).to_edge(UP, buff=top_margin)
            self.play(Write(current_title), run_time=0.7)
            self.wait(0.2)

            content = VGroup(*elements_for_frame)
            content.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
            
            for el in content:
                if isinstance(el, Tex) and el.width > frame_width - 2 * side_margin: # Use .width property
                     el.set_width(frame_width - 2 * side_margin)
            content.arrange(DOWN, buff=0.35, aligned_edge=LEFT)

            content.next_to(current_title, DOWN, buff=0.3)
            content.move_to(np.array([0, content.get_center()[1], 0]))

            available_h = frame_height - current_title.height - top_margin - bottom_margin # Use .height property
            if content.height > available_h: # Use .height property
                content.scale_to_fit_height(available_h)
                content.next_to(current_title, DOWN, buff=0.3)
                content.move_to(np.array([0, content.get_center()[1], 0]))

            for i, element in enumerate(elements_for_frame):
                 anim_time = max(0.5, element.width / 15 if hasattr(element, "width") and element.width > 0 else 0.5)
                 if isinstance(element, VGroup) and not any(isinstance(sub_el, Tex) or isinstance(sub_el, MathTex) for sub_el in element.submobjects if sub_el is not None):
                     self.play(FadeIn(element, scale=0.7, shift=UP*0.1), run_time=anim_time*0.8)
                 else:
                     self.play(Write(element), run_time=anim_time)
                 self.wait(0.2)
            
            self.wait(2.0)
            return VGroup(current_title, content)

        # --- Frame 1: Percentage Error ---
        theoretical_T = 5270
        estimated_T_visual = 5100
        error_formula_intro = Tex("Comparing visual estimate to theory:", font_size=text_fs)
        error_formula = MathTex("\\text{Error} = \\frac{|\\text{Est.} - \\text{Theory}|}{\\text{Theory}} \\times 100\\%", font_size=math_fs)
        error_values = MathTex(f"= \\frac{{|{estimated_T_visual}\\text{{K}} - {theoretical_T}\\text{{K}}|}}{{{theoretical_T}\\text{{K}}}} \\times 100\\%", font_size=math_fs-2)
        error_result_val = (abs(estimated_T_visual - theoretical_T) / theoretical_T) * 100
        error_result = MathTex(f"\\approx {error_result_val:.2f}\\%", font_size=math_fs, color=YELLOW)
        frame1_elements = [error_formula_intro, error_formula, error_values, error_result]
        f1_group = create_and_present_frame("Percentage Error Analysis", frame1_elements)

        # --- Frame 2: Sources of Discrepancy - Range Explanation ---
        green_range_title = Tex("A. Color-Wavelength is a Range:", font_size=header_fs)
        green_range_text_str = "Visible green spans wavelengths (e.g., ~520nm to ~565nm), not a single point."
        green_range_text = Tex(green_range_text_str, font_size=text_fs, tex_environment="flushleft")
        
        green_spectrum_bar = VGroup()
        bar_width = 1.5; bar_height = 0.6
        colors_wavelengths = [
            (ManimColor("#98FB98"), "~520nm"),
            (GREEN_B, "~540nm"), 
            (ManimColor("#3CB371"), "~565nm")
        ]
        for i, (m_color, wl) in enumerate(colors_wavelengths):
            rect = Rectangle(width=bar_width, height=bar_height, fill_color=m_color, fill_opacity=0.9, stroke_width=1, stroke_color=GRAY)
            r,g,b = m_color.to_rgb(); lum = 0.2126*r + 0.7152*g + 0.0722*b
            label = Tex(wl, font_size=small_text_fs-4, color=BLACK if lum > 0.5 else WHITE).move_to(rect.get_center())
            green_spectrum_bar.add(VGroup(rect, label))
        green_spectrum_bar.arrange(RIGHT, buff=0.15)
        frame2_elements = [green_range_title, green_range_text, green_spectrum_bar]
        f2_group = create_and_present_frame("Sources of Discrepancy (1/2)", frame2_elements, prev_elements_to_fade=f1_group)
        
        # --- Frame 3: Sources of Discrepancy - Estimation Subjectivity ---
        estimation_title = Tex("B. Visual Estimation is Subjective:", font_size=header_fs)
        estimation_text_str = "Precisely judging color shades by eye (e.g., 'yellow-to-green') introduces uncertainty."
        estimation_text = Tex(estimation_text_str, font_size=text_fs, tex_environment="flushleft")
        
        bulb_demo = Bulb(glow_opacity=0.7).scale(0.9)
        bulb_demo.set_glow_color(interpolate_color(YELLOW_D, GREEN_D, 0.5))
        q_marks = Tex("??", font_size=60, color=RED_C)
        estimation_label = Tex("Subjective Observation", font_size=small_text_fs, color=BLUE_C)
        visual_group = VGroup(bulb_demo, q_marks, estimation_label).arrange(DOWN, buff=0.3)
        frame3_elements = [estimation_title, estimation_text, visual_group]
        f3_group = create_and_present_frame("Sources of Discrepancy (2/2)", frame3_elements, prev_elements_to_fade=f2_group)

        # --- Frame 4: Final Conclusion ---
        final_conclusion_text_str = "Experimental estimation, while subject to variations, generally aligns with Wien's Law."
        final_conclusion_text = Tex(final_conclusion_text_str, font_size=text_fs, tex_environment="flushleft")
        checkmark = Tex("\\checkmark", font_size=80, color=GREEN_C)
        frame4_elements = [final_conclusion_text, checkmark]
        f4_group = create_and_present_frame("Conclusion", frame4_elements, prev_elements_to_fade=f3_group)

        self.play(FadeOut(f4_group))
        self.wait(1)