import cmath
import math
import customtkinter as ctk


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def fmt_complex(z: complex) -> str:
    sign = "+" if z.imag >= 0 else "-"
    return f"{z.real:.6g} {sign} {abs(z.imag):.6g}i"


def polar_deg(z: complex) -> tuple[float, float]:
    r = abs(z)
    theta_deg = math.degrees(cmath.phase(z))
    return r, theta_deg


def complex_from_polar_deg(r: float, theta_deg: float) -> complex:
    theta_rad = math.radians(theta_deg)
    return r * complex(math.cos(theta_rad), math.sin(theta_rad))


class ComplexCalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Complex Number Calculator - Premium UI")
        self.geometry("1220x820")
        self.minsize(900, 560)

        # Modern dark palette
        self.colors = {
            "bg": "#0b1220",
            "card": "#131d31",
            "card_soft": "#0f1728",
            "border": "#23314d",
            "text_main": "#e8eef9",
            "text_sub": "#9fb0cf",
            "accent": "#22d3ee",
            "accent_hover": "#06b6d4",
            "danger": "#fb7185",
            "output_bg": "#0a101d",
        }
        self.configure(fg_color=self.colors["bg"])

        # Keep per-tab error labels for better UX (error message visible near input zone)
        self.error_labels: dict[str, ctk.CTkLabel] = {}
        self.current_tab_key = "cartesian"
        # Store output history per textbox to render old/new with different emphasis.
        self.output_history: dict[str, list[str]] = {}
        self.output_history_box: dict[str, ctk.CTkTextbox] = {}

        self._build_header()
        self._build_tabs()
        self._bind_enter_key()

    def _build_header(self):
        # Typography hierarchy: strong title + softer subtitle
        ctk.CTkLabel(
            self,
            text="Complex Number Calculator",
            text_color=self.colors["text_main"],
            font=ctk.CTkFont(size=30, weight="bold"),
        ).pack(anchor="w", padx=24, pady=(20, 0))
        ctk.CTkLabel(
            self,
            text="Professional UI for Cartesian, Polar, Power/Roots, and Exponential operations",
            text_color=self.colors["text_sub"],
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w", padx=24, pady=(4, 14))

    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(
            self,
            command=self._on_tab_change,
            corner_radius=12,
            fg_color=self.colors["card_soft"],
            segmented_button_fg_color=self.colors["card"],
            segmented_button_selected_color=self.colors["accent"],
            segmented_button_selected_hover_color=self.colors["accent_hover"],
            segmented_button_unselected_color=self.colors["card"],
            segmented_button_unselected_hover_color="#1f2b44",
            text_color=self.colors["text_main"],
        )
        self.tabs.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self.tab_cartesian = self.tabs.add("Cartesian")
        self.tab_polar = self.tabs.add("Polar")
        self.tab_power_roots = self.tabs.add("Power & Roots")
        self.tab_exponential = self.tabs.add("Exponential")

        self._build_cartesian_tab()
        self._build_polar_tab()
        self._build_power_roots_tab()
        self._build_exponential_tab()

    def _styled_card(self, parent, is_output: bool = False) -> ctk.CTkFrame:
        return ctk.CTkFrame(
            parent,
            corner_radius=16,
            fg_color=self.colors["output_bg"] if is_output else self.colors["card"],
            border_width=1,
            border_color=self.colors["border"],
        )

    def _scrollable_card(self, parent) -> ctk.CTkScrollableFrame:
        """Input card with built-in scrollbar for small screens."""
        return ctk.CTkScrollableFrame(
            parent,
            corner_radius=16,
            fg_color=self.colors["card"],
            border_width=1,
            border_color=self.colors["border"],
            scrollbar_button_color=self.colors["border"],
            scrollbar_button_hover_color=self.colors["accent"],
        )

    def _build_split_tab(self, tab, tab_key: str, title: str, subtitle: str):
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=16, pady=16)
        container.grid_columnconfigure(0, weight=4)
        container.grid_columnconfigure(1, weight=6)
        container.grid_rowconfigure(1, weight=1)

        # Use a dedicated header frame to avoid overlap/clipping with tab controls.
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=title,
            text_color=self.colors["text_main"],
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text=subtitle,
            text_color=self.colors["text_sub"],
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        left = self._scrollable_card(container)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        right = self._styled_card(container, is_output=True)
        right.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        left.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)

        # Error message area placed right under title in the input card
        self.error_labels[tab_key] = ctk.CTkLabel(
            left,
            text="",
            text_color=self.colors["danger"],
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        self.error_labels[tab_key].pack(fill="x", padx=18, pady=(4, 0))
        return left, right

    def _entry_row(self, parent, label_text: str, placeholder: str = "") -> ctk.CTkEntry:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(
            row,
            text=label_text,
            text_color=self.colors["text_sub"],
            anchor="w",
            font=ctk.CTkFont(size=12),
        ).pack(fill="x")
        entry = ctk.CTkEntry(
            row,
            height=30,
            corner_radius=10,
            placeholder_text=placeholder,
            fg_color="#0f1a2f",
            border_color=self.colors["border"],
            text_color=self.colors["text_main"],
        )
        entry.pack(fill="x", pady=(4, 0))
        return entry

    def _primary_button(self, parent, text: str, command):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=34,
            corner_radius=10,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="#03141a",
            font=ctk.CTkFont(size=12, weight="bold"),
        )

    def _secondary_button(self, parent, text: str, command):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=34,
            corner_radius=10,
            fg_color="#223252",
            hover_color="#2a3f67",
            text_color=self.colors["text_main"],
            font=ctk.CTkFont(size=12),
        )

    def _build_output_area(self, parent, title: str) -> ctk.CTkTextbox:
        ctk.CTkLabel(
            parent,
            text=title,
            text_color=self.colors["text_main"],
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 2))
        ctk.CTkLabel(
            parent,
            text="History",
            text_color=self.colors["text_sub"],
            font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 8))

        parent.grid_rowconfigure(2, weight=2)
        parent.grid_rowconfigure(4, weight=3)

        history_box = ctk.CTkTextbox(
            parent,
            corner_radius=12,
            fg_color="#050a15",
            border_color=self.colors["border"],
            border_width=1,
            text_color="#87a5bd",
            font=ctk.CTkFont(family="Consolas", size=11),
        )
        history_box.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 10))

        ctk.CTkLabel(
            parent,
            text="Latest Result",
            text_color="#22d3ee",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=3, column=0, sticky="w", padx=18, pady=(0, 6))

        latest_box = ctk.CTkTextbox(
            parent,
            corner_radius=12,
            fg_color="#071022",
            border_color=self.colors["accent"],
            border_width=1,
            text_color="#e7fbff",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
        )
        latest_box.grid(row=4, column=0, sticky="nsew", padx=18, pady=(0, 18))
        latest_box.tag_config("center", justify="center")

        key = str(latest_box)
        self.output_history[key] = []
        self.output_history_box[key] = history_box
        return latest_box

    def _build_cartesian_tab(self):
        left, right = self._build_split_tab(
            self.tab_cartesian,
            "cartesian",
            "Cartesian Form",
            "Input z1 = x1 + iy1 and z2 = x2 + iy2",
        )
        self.z1_re = self._entry_row(left, "z1 Real (x1)", "8")
        self.z1_im = self._entry_row(left, "z1 Imag (y1)", "3")
        self.z2_re = self._entry_row(left, "z2 Real (x2)", "9")
        self.z2_im = self._entry_row(left, "z2 Imag (y2)", "-2")

        btns = ctk.CTkFrame(left, fg_color="transparent")
        btns.pack(fill="x", padx=18, pady=(8, 8))
        btns.grid_columnconfigure((0, 1), weight=1)
        actions = [
            ("z1 + z2", self.calc_add, True),
            ("z1 - z2", self.calc_sub, False),
            ("z1 * z2", self.calc_mul, True),
            ("z1 / z2", self.calc_div, False),
            ("Conjugate z1", self.calc_conjugate, False),
            ("|z1| and arg(z1)", self.calc_mod_arg, False),
        ]
        for idx, (text, cmd, is_primary) in enumerate(actions):
            r, c = divmod(idx, 2)
            maker = self._primary_button if is_primary else self._secondary_button
            maker(btns, text, cmd).grid(row=r, column=c, sticky="ew", padx=5, pady=5)

        self._secondary_button(left, "Clear Output", self.clear_cartesian).pack(
            fill="x", padx=18, pady=(0, 18)
        )
        self.cart_result = self._build_output_area(right, "Output: Cartesian Operations")

    def _build_polar_tab(self):
        left, right = self._build_split_tab(
            self.tab_polar,
            "polar",
            "Polar Form",
            "z = r∠theta (degree), with z = r(cos(theta) + i sin(theta))",
        )
        self.p1_r = self._entry_row(left, "z1 radius (r1)", "21")
        self.p1_theta = self._entry_row(left, "z1 angle (theta1, deg)", "23")
        self.p2_r = self._entry_row(left, "z2 radius (r2)", "14")
        self.p2_theta = self._entry_row(left, "z2 angle (theta2, deg)", "15")

        btns = ctk.CTkFrame(left, fg_color="transparent")
        btns.pack(fill="x", padx=18, pady=(8, 8))
        btns.grid_columnconfigure((0, 1), weight=1)
        actions = [
            ("z1 + z2", self.polar_add, True),
            ("z1 - z2", self.polar_sub, False),
            ("z1 * z2", self.polar_mul, True),
            ("z1 / z2", self.polar_div, False),
            ("Polar -> Cartesian z1", self.polar_to_cartesian_z1, False),
            ("Cartesian -> Polar z1", self.cartesian_to_polar_from_tab, False),
        ]
        for idx, (text, cmd, is_primary) in enumerate(actions):
            r, c = divmod(idx, 2)
            maker = self._primary_button if is_primary else self._secondary_button
            maker(btns, text, cmd).grid(row=r, column=c, sticky="ew", padx=5, pady=5)

        self._secondary_button(left, "Clear Output", self.clear_polar).pack(
            fill="x", padx=18, pady=(0, 18)
        )
        self.polar_result = self._build_output_area(right, "Output: Polar Operations")

    def _build_power_roots_tab(self):
        left, right = self._build_split_tab(
            self.tab_power_roots,
            "power_roots",
            "Power & Roots (De Moivre)",
            "Compute z^n and all n-th roots (Polar or Cartesian input)",
        )

        # ── Input mode toggle ──
        self.pr_input_mode = ctk.StringVar(value="polar")
        mode_frame = ctk.CTkFrame(left, fg_color="transparent")
        mode_frame.pack(fill="x", padx=18, pady=(6, 2))
        ctk.CTkLabel(
            mode_frame,
            text="Input Mode:",
            text_color=self.colors["text_sub"],
            font=ctk.CTkFont(size=12),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkSegmentedButton(
            mode_frame,
            values=["Polar", "Cartesian"],
            command=self._on_pr_mode_change,
            selected_color=self.colors["accent"],
            selected_hover_color=self.colors["accent_hover"],
            unselected_color=self.colors["card"],
            unselected_hover_color="#1f2b44",
            text_color="#03141a",
            text_color_disabled=self.colors["text_sub"],
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", fill="x", expand=True)

        # ── Polar inputs ──
        self.pr_polar_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.pr_polar_frame.pack(fill="x")
        self.pr_r = self._entry_row(self.pr_polar_frame, "z radius (r)", "e.g. 8 or sqrt(2)")
        self.pr_theta = self._entry_row(self.pr_polar_frame, "z angle (theta, deg)", "180")

        # ── Cartesian inputs ──
        self.pr_cart_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.pr_x = self._entry_row(self.pr_cart_frame, "z Real (x)", "e.g. 1/2, -8, sqrt(3)")
        self.pr_y = self._entry_row(self.pr_cart_frame, "z Imag (y)", "e.g. 1/2, 0, sqrt(2)")
        # Hidden by default (polar mode first)

        self.pr_n = self._entry_row(left, "n (power/root degree)", "e.g. 6 or 1/6")

        btns = ctk.CTkFrame(left, fg_color="transparent")
        btns.pack(fill="x", padx=18, pady=(8, 8))
        btns.grid_columnconfigure((0, 1), weight=1)
        self._primary_button(btns, "Compute z^n", self.calc_power).grid(
            row=0, column=0, sticky="ew", padx=5, pady=5
        )
        self._primary_button(btns, "Compute all n-th roots", self.calc_roots).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )

        self._secondary_button(left, "Clear Output", self.clear_power_roots).pack(
            fill="x", padx=18, pady=(0, 18)
        )
        self.pr_result = self._build_output_area(right, "Output: Power & Roots")

    def _on_pr_mode_change(self, value: str):
        """Toggle between Polar and Cartesian input in Power & Roots tab."""
        if value == "Cartesian":
            self.pr_input_mode.set("cartesian")
            self.pr_polar_frame.pack_forget()
            self.pr_cart_frame.pack(fill="x", before=self.pr_n.master)
            self.pr_x.focus_set()
        else:
            self.pr_input_mode.set("polar")
            self.pr_cart_frame.pack_forget()
            self.pr_polar_frame.pack(fill="x", before=self.pr_n.master)
            self.pr_r.focus_set()

    def _build_exponential_tab(self):
        left, right = self._build_split_tab(
            self.tab_exponential,
            "exp",
            "Complex Exponential",
            "e^(x + iy) = e^x(cos y + i sin y), where y is in radians",
        )
        self.exp_x = self._entry_row(left, "x (real part)", "0")
        self.exp_y = self._entry_row(left, "y (imag part, rad)", "3.14159")

        btns1 = ctk.CTkFrame(left, fg_color="transparent")
        btns1.pack(fill="x", padx=18, pady=(8, 4))
        btns1.grid_columnconfigure(0, weight=1)
        self._primary_button(btns1, "Compute e^(x+iy)", self.calc_exp_xy).grid(
            row=0, column=0, sticky="ew", padx=5, pady=5
        )

        # ── Separator ──
        sep = ctk.CTkFrame(left, fg_color=self.colors["border"], height=1)
        sep.pack(fill="x", padx=18, pady=(8, 4))
        ctk.CTkLabel(
            left,
            text="z1 & z2  (for  e^z1 , e^z2 , verify property)",
            text_color=self.colors["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(4, 2))

        self.exp_z1_re = self._entry_row(left, "z1 Real (x1)", "1")
        self.exp_z1_im = self._entry_row(left, "z1 Imag (y1)", "2")
        self.exp_z2_re = self._entry_row(left, "z2 Real (x2)", "3")
        self.exp_z2_im = self._entry_row(left, "z2 Imag (y2)", "-1")

        btns2 = ctk.CTkFrame(left, fg_color="transparent")
        btns2.pack(fill="x", padx=18, pady=(8, 8))
        btns2.grid_columnconfigure((0, 1), weight=1)
        self._primary_button(btns2, "Compute e^z1", self.calc_exp_z1).grid(
            row=0, column=0, sticky="ew", padx=5, pady=5
        )
        self._primary_button(btns2, "Compute e^z2", self.calc_exp_z2).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )
        self._secondary_button(btns2, "Verify e^(z1+z2) = e^z1 · e^z2", self.verify_exp_sum_property).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5
        )

        self._secondary_button(left, "Clear Output", self.clear_exp).pack(
            fill="x", padx=18, pady=(0, 18)
        )
        self.exp_result = self._build_output_area(right, "Output: Exponential")

    def _append_result(self, textbox: ctk.CTkTextbox, text: str):
        key = str(textbox)
        history = self.output_history.setdefault(key, [])
        history.append(text)
        self._render_output(textbox)

    def _render_output(self, textbox: ctk.CTkTextbox):
        key = str(textbox)
        history = self.output_history.get(key, [])
        history_box = self.output_history_box.get(key)
        if history_box is None:
            return

        history_box.delete("1.0", "end")
        textbox.delete("1.0", "end")
        if not history:
            return

        for old_result in history[:-1]:
            history_box.insert("end", old_result + "\n")
            history_box.insert("end", "-" * 62 + "\n")

        textbox.insert("end", history[-1] + "\n", "center")
        history_box.see("end")
        textbox.see("end")

    def _set_error(self, tab_key: str, message: str):
        for key, label in self.error_labels.items():
            if key == tab_key:
                label.configure(text=message)
            elif label.cget("text"):
                label.configure(text="")

    def _clear_error(self, tab_key: str):
        self._set_error(tab_key, "")

    def _eval_num(self, val_str: str) -> float:
        """Evaluate a mathematical string like '1/2' or 'sqrt(3)' safely."""
        val_str = val_str.strip()
        if not val_str:
            return 0.0
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        try:
            return float(eval(val_str, {"__builtins__": None}, allowed_names))
        except Exception:
            raise ValueError(f"Invalid numeric input: {val_str}")

    def _read_cartesian(self) -> tuple[complex, complex]:
        x1 = float(self.z1_re.get())
        y1 = float(self.z1_im.get())
        x2 = float(self.z2_re.get())
        y2 = float(self.z2_im.get())
        return complex(x1, y1), complex(x2, y2)

    def _read_polar(self) -> tuple[complex, complex]:
        r1 = float(self.p1_r.get())
        t1 = float(self.p1_theta.get())
        r2 = float(self.p2_r.get())
        t2 = float(self.p2_theta.get())
        return complex_from_polar_deg(r1, t1), complex_from_polar_deg(r2, t2)

    def _safe_run(self, fn, tab_key: str):
        self.current_tab_key = tab_key
        self._clear_error(tab_key)
        try:
            fn()
        except ValueError:
            self._set_error(tab_key, "Please input valid numeric values.")
        except ZeroDivisionError:
            self._set_error(tab_key, "Division by zero is not allowed.")

    def calc_add(self):
        def run():
            z1, z2 = self._read_cartesian()
            self._append_result(self.cart_result, f"z1 + z2 = {fmt_complex(z1 + z2)}")

        self._safe_run(run, "cartesian")

    def calc_sub(self):
        def run():
            z1, z2 = self._read_cartesian()
            self._append_result(self.cart_result, f"z1 - z2 = {fmt_complex(z1 - z2)}")

        self._safe_run(run, "cartesian")

    def calc_mul(self):
        def run():
            z1, z2 = self._read_cartesian()
            self._append_result(self.cart_result, f"z1 * z2 = {fmt_complex(z1 * z2)}")

        self._safe_run(run, "cartesian")

    def calc_div(self):
        def run():
            z1, z2 = self._read_cartesian()
            self._append_result(self.cart_result, f"z1 / z2 = {fmt_complex(z1 / z2)}")

        self._safe_run(run, "cartesian")

    def calc_conjugate(self):
        def run():
            z1, _ = self._read_cartesian()
            self._append_result(self.cart_result, f"conjugate(z1) = {fmt_complex(z1.conjugate())}")

        self._safe_run(run, "cartesian")

    def calc_mod_arg(self):
        def run():
            z1, _ = self._read_cartesian()
            r, theta = polar_deg(z1)
            self._append_result(
                self.cart_result,
                f"|z1| = {r:.6g}, arg(z1) = {theta:.6g} deg\nz1 = {r:.6g}∠{theta:.6g} deg",
            )

        self._safe_run(run, "cartesian")

    def polar_add(self):
        def run():
            z1, z2 = self._read_polar()
            z = z1 + z2
            r, t = polar_deg(z)
            self._append_result(self.polar_result, f"z1 + z2 = {fmt_complex(z)} = {r:.6g}∠{t:.6g} deg")

        self._safe_run(run, "polar")

    def polar_sub(self):
        def run():
            z1, z2 = self._read_polar()
            z = z1 - z2
            r, t = polar_deg(z)
            self._append_result(self.polar_result, f"z1 - z2 = {fmt_complex(z)} = {r:.6g}∠{t:.6g} deg")

        self._safe_run(run, "polar")

    def polar_mul(self):
        def run():
            z1, z2 = self._read_polar()
            z = z1 * z2
            r, t = polar_deg(z)
            self._append_result(self.polar_result, f"z1 * z2 = {fmt_complex(z)} = {r:.6g}∠{t:.6g} deg")

        self._safe_run(run, "polar")

    def polar_div(self):
        def run():
            z1, z2 = self._read_polar()
            z = z1 / z2
            r, t = polar_deg(z)
            self._append_result(self.polar_result, f"z1 / z2 = {fmt_complex(z)} = {r:.6g}∠{t:.6g} deg")

        self._safe_run(run, "polar")

    def polar_to_cartesian_z1(self):
        def run():
            z1, _ = self._read_polar()
            self._append_result(self.polar_result, f"z1 (Cartesian) = {fmt_complex(z1)}")

        self._safe_run(run, "polar")

    def cartesian_to_polar_from_tab(self):
        def run():
            z1, _ = self._read_cartesian()
            r, t = polar_deg(z1)
            self._append_result(self.polar_result, f"z1 (from Cartesian tab) = {r:.6g}∠{t:.6g} deg")

        self._safe_run(run, "polar")

    def clear_polar(self):
        self.output_history[str(self.polar_result)] = []
        self._render_output(self.polar_result)
        self._clear_error("polar")

    def clear_cartesian(self):
        self.output_history[str(self.cart_result)] = []
        self._render_output(self.cart_result)
        self._clear_error("cartesian")

    def _read_pr_complex(self) -> tuple[complex, float, float]:
        """Read the complex number from Power & Roots tab (either mode).
        Returns (z, r, theta_deg)."""
        if self.pr_input_mode.get() == "cartesian":
            x = self._eval_num(self.pr_x.get())
            y = self._eval_num(self.pr_y.get())
            z = complex(x, y)
            r, theta_deg = polar_deg(z)
        else:
            r = self._eval_num(self.pr_r.get())
            theta_deg = self._eval_num(self.pr_theta.get())
            z = complex_from_polar_deg(r, theta_deg)
        return z, r, theta_deg

    def calc_power(self):
        def run():
            z, r, theta_deg = self._read_pr_complex()
            n = self._eval_num(self.pr_n.get())
            res = z ** n
            res_r, res_t = polar_deg(res)
            mode_label = "(Cartesian input)" if self.pr_input_mode.get() == "cartesian" else "(Polar input)"
            n_str = f"{int(n)}" if n.is_integer() else f"{n:.6g}"
            lines = [
                f"{mode_label}  z = {fmt_complex(z)} = {r:.6g}∠{theta_deg:.6g}°",
                f"z^{n_str} = {fmt_complex(res)} = {res_r:.6g}∠{res_t:.6g}°",
            ]
            self._append_result(self.pr_result, "\n".join(lines))

        self._safe_run(run, "power_roots")

    def calc_roots(self):
        def run():
            z, r, theta_deg = self._read_pr_complex()
            n_val = self._eval_num(self.pr_n.get())

            # If user typed a fraction like 1/6 for 6th roots, smartly convert to 6
            if 0 < n_val < 1 and math.isclose(1 / n_val, round(1 / n_val)):
                n_val = round(1 / n_val)
                
            if not float(n_val).is_integer() or n_val <= 0:
                self._set_error("power_roots", "n must be a positive integer (e.g. 6) or a simple fraction (e.g. 1/6).")
                return
            n = int(n_val)

            theta_rad = math.radians(theta_deg)
            mode_label = "(Cartesian input)" if self.pr_input_mode.get() == "cartesian" else "(Polar input)"
            lines = [
                f"{mode_label}  z = {fmt_complex(z)} = {r:.6g}∠{theta_deg:.6g}°",
                f"All {n}-th roots of z:",
            ]
            root_r = r ** (1 / n)
            for k in range(n):
                angle = (theta_rad + 2 * math.pi * k) / n
                root_z = root_r * complex(math.cos(angle), math.sin(angle))
                res_r, res_t = polar_deg(root_z)
                lines.append(f"  k={k}: {fmt_complex(root_z)} = {res_r:.6g}∠{res_t:.6g}°")
            self._append_result(self.pr_result, "\n".join(lines))

        self._safe_run(run, "power_roots")

    def clear_power_roots(self):
        self.output_history[str(self.pr_result)] = []
        self._render_output(self.pr_result)
        self._clear_error("power_roots")

    def _read_exp_z1z2(self) -> tuple[complex, complex]:
        """Read z1 and z2 from the Exponential tab's own inputs."""
        x1 = float(self.exp_z1_re.get())
        y1 = float(self.exp_z1_im.get())
        x2 = float(self.exp_z2_re.get())
        y2 = float(self.exp_z2_im.get())
        return complex(x1, y1), complex(x2, y2)

    def calc_exp_xy(self):
        def run():
            x = float(self.exp_x.get())
            y = float(self.exp_y.get())
            z = complex(x, y)
            res = cmath.exp(z)
            r, t = polar_deg(res)
            self._append_result(
                self.exp_result,
                f"e^({x} + i{y}) = {fmt_complex(res)}\n  = {r:.6g}∠{t:.6g}°",
            )

        self._safe_run(run, "exp")

    def calc_exp_z1(self):
        def run():
            z1, _ = self._read_exp_z1z2()
            res = cmath.exp(z1)
            r, t = polar_deg(res)
            self._append_result(
                self.exp_result,
                f"z1 = {fmt_complex(z1)}\ne^z1 = {fmt_complex(res)}\n  = {r:.6g}∠{t:.6g}°",
            )

        self._safe_run(run, "exp")

    def calc_exp_z2(self):
        def run():
            _, z2 = self._read_exp_z1z2()
            res = cmath.exp(z2)
            r, t = polar_deg(res)
            self._append_result(
                self.exp_result,
                f"z2 = {fmt_complex(z2)}\ne^z2 = {fmt_complex(res)}\n  = {r:.6g}∠{t:.6g}°",
            )

        self._safe_run(run, "exp")

    def verify_exp_sum_property(self):
        def run():
            z1, z2 = self._read_exp_z1z2()
            res1 = cmath.exp(z1 + z2)
            res2 = cmath.exp(z1) * cmath.exp(z2)
            lines = [
                f"z1 = {fmt_complex(z1)},  z2 = {fmt_complex(z2)}",
                f"e^(z1+z2) = {fmt_complex(res1)}",
                f"e^z1 · e^z2 = {fmt_complex(res2)}",
            ]
            if cmath.isclose(res1, res2):
                lines.append("✓ Property holds: e^(z1+z2) == e^z1 · e^z2")
            else:
                lines.append("✗ Property differs due to numeric precision.")
            self._append_result(self.exp_result, "\n".join(lines))

        self._safe_run(run, "exp")

    def clear_exp(self):
        self.output_history[str(self.exp_result)] = []
        self._render_output(self.exp_result)
        self._clear_error("exp")

    # ── UX helpers ──────────────────────────────────────────────

    def _on_tab_change(self):
        """Auto-focus first input field when switching tabs."""
        first_entries = {
            "Cartesian": self.z1_re,
            "Polar": self.p1_r,
            "Power & Roots": self.pr_r,
            "Exponential": self.exp_x,
        }
        current = self.tabs.get()
        entry = first_entries.get(current)
        if entry:
            entry.focus_set()

    def _bind_enter_key(self):
        """Bind Enter key to the primary calculation of the active tab."""
        self.bind("<Return>", self._on_enter)

    def _on_enter(self, event=None):
        tab_actions = {
            "Cartesian": self.calc_add,
            "Polar": self.polar_add,
            "Power & Roots": self.calc_power,
            "Exponential": self.calc_exp_xy,
        }
        current = self.tabs.get()
        action = tab_actions.get(current)
        if action:
            action()


if __name__ == "__main__":
    app = ComplexCalculatorApp()
    app.mainloop()