import customtkinter as ctk
from PIL import Image, ImageSequence, ImageOps
from Admin.admin_dashboard import AdminDashboard
from Admin.admin_record import AdminRecord
from Admin.admin_add_record import AdminAddRecord
from Admin.admin_edit_record import AdminEditRecord
from Admin.admin_owner import AdminOwner
from Admin.admin_add_owner import AdminAddOwner
from Admin.admin_edit_owner import AdminEditOwner
from Admin.admin_security import AdminSecurity
from Admin.admin_add_security import AdminAddSecurity
from Admin.admin_edit_security import AdminEditSecurity
from Admin.admin_setting import AdminSetting
from Admin.admin_interface import AdminInterface
from firebase_config import firebase_db

class AdminMainMenu(ctk.CTkFrame):
    def __init__(self, master, user_id, user_name, navigate_to_login, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.user_id = user_id
        self.user_name = user_name
        self.navigate_to_login = navigate_to_login
        # === Side Panel ===
        self.sidebar_collapsed = False
        self.sidebar_width_expanded = 260
        self.sidebar_width_collapsed = 110
        self.side_panel = ctk.CTkFrame(self, height=1, width=self.sidebar_width_expanded, fg_color="#bfd5ff", corner_radius=0)
        self.side_panel.pack(side="left", fill="y")

        # -- Logo section --
        self.logo_frame = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        self.logo_frame.pack(pady=(25, 0), padx=(15, 0), anchor="nw", fill="x")
        self.logo_size_expanded = (150, 69)
        self.logo_size_collapsed = (50, 50)
        pil_logo = Image.open("Pic/Logo.png")
        pil_collapse_logo = Image.open("Pic/collapse_logo.png")
        self.logo_image_expanded = ctk.CTkImage(pil_logo, size=self.logo_size_expanded)
        self.logo_image_collapsed = ctk.CTkImage(pil_collapse_logo, size=self.logo_size_collapsed)
        self.logo_lbl = ctk.CTkLabel(
            self.logo_frame,
            image=self.logo_image_expanded,
            text="",
            fg_color="transparent"
        )
        self.logo_lbl.pack(side="left")
        # Collapse/Expand button
        self.collapse_btn = ctk.CTkButton(
            self.logo_frame,
            text="⮜",
            width=15, height=15,
            fg_color="#2c3e50",
            command=self.toggle_sidebar,
            font=ctk.CTkFont(size=18, weight="bold"),
            hover_color="#1a232e"
        )
        self.collapse_btn.pack(side="right", padx=(0,10))

        # Navigation Buttons
        nav_items = [
            ("Dashboard", "Pic/dashboard_static.png", "Pic/dashboard.gif"),
            ("Records", "Pic/record_static.png", "Pic/record.gif"),
            ("Owner", "Pic/owner_static.png", "Pic/owner.gif"),
            ("Security Personnel", "Pic/security_static.png", "Pic/security.gif"),
            ("Admin", "Pic/admin_static.png", "Pic/admin.gif"),
            ("Blacklist", "Pic/blacklist_static.png", "Pic/blacklist.gif"),
        ]
        self.nav_buttons = {}
        self.nav_icon_size_expanded = (32, 32)
        self.nav_icon_size_collapsed = (40, 40)
        self.nav_static_images = {}
        self.nav_gif_frames = {}
        for text, static_path, gif_path in nav_items:
            static_image = ctk.CTkImage(Image.open(static_path), size=self.nav_icon_size_expanded)
            gif_frames = self.load_gif_frames(gif_path, self.nav_icon_size_expanded)
            self.nav_static_images[text] = {
                'expanded': static_image,
                'collapsed': ctk.CTkImage(Image.open(static_path), size=self.nav_icon_size_collapsed)
            }
            self.nav_gif_frames[text] = {
                'expanded': gif_frames,
                'collapsed': self.load_gif_frames(gif_path, self.nav_icon_size_collapsed)
            }
            def make_hover_animation(button, frames):
                return lambda e: self.start_button_animation(button, frames) if not button.is_selected else None

            def make_leave_animation(button, frames):
                return lambda e: self.stop_button_animation(button, frames)

            btn = ctk.CTkButton(
                self.side_panel,
                text=text,
                image=gif_frames[0],
                compound="left",
                fg_color="transparent",
                font=ctk.CTkFont(size=14),
                anchor="w",
                command=lambda t=text: self.show_page(t),
                corner_radius=8,
                height=50
            )
            btn.pack(fill="x", pady=8, padx=10)
            btn.configure(
                hover_color="#cce0ff",
                text_color="#2c3e50",
            )
            btn.static_image = static_image
            btn.gif_frames = gif_frames
            btn.is_selected = False
            btn._original_text = text
            btn.bind("<Enter>", make_hover_animation(btn, gif_frames))
            btn.bind("<Leave>", make_leave_animation(btn, gif_frames))
            self.nav_buttons[text] = btn

        self.side_panel.pack_propagate(False)
        ctk.CTkLabel(self.side_panel, text="", fg_color="transparent").pack(expand=True, pady=20)

        # Notifications & Logout
        self.logout_gif_frames = []
        self.logout_gif_frames_expanded = []
        self.logout_gif_frames_collapsed = []
        gif = Image.open("Pic/logout.gif")
        for frame in ImageSequence.Iterator(gif):
            frame_exp = frame.convert("RGBA").resize((32, 32))
            frame_col = frame.convert("RGBA").resize((40, 40))
            padded_frame_exp = ImageOps.expand(frame_exp, border=(5, 0, 0, 0), fill=(0, 0, 0, 0))
            padded_frame_col = ImageOps.expand(frame_col, border=(5, 0, 0, 0), fill=(0, 0, 0, 0))
            self.logout_gif_frames_expanded.append(ctk.CTkImage(padded_frame_exp, size=(32, 32)))
            self.logout_gif_frames_collapsed.append(ctk.CTkImage(padded_frame_col, size=(40, 40)))
        self.logout_gif_frames = self.logout_gif_frames_expanded

        self.logout_btn = ctk.CTkButton(
            self.side_panel,
            text="Log out",
            image=self.logout_gif_frames[0],
            fg_color="transparent",
            anchor="w",
            font=ctk.CTkFont(size=14),
            command=self.logout,
            corner_radius=8,
            hover_color="#ff8080",
            text_color="#2c3e50",
            height=50
        )
        self.logout_btn.pack(fill="x", pady=8, padx=10)
        self.logout_btn.bind("<Enter>", lambda e: self.start_logout_animation())
        self.logout_btn.bind("<Leave>", lambda e: self.stop_logout_animation())
        self.logout_animating = False
        self.current_logout_frame = 0

        # Bottom Profile Area & Settings
        self.profile_frame = ctk.CTkFrame(
            self.side_panel,
            fg_color="#bfd5ff",
            corner_radius=0
        )
        self.profile_frame.pack(pady=(15, 10), padx=8, fill="x")

        self.avatar_gif_frames = []
        self.avatar_gif_frames_expanded = []
        self.avatar_gif_frames_collapsed = []
        gif = Image.open("Pic/avatar.gif")
        for frame in ImageSequence.Iterator(gif):
            frame_exp = frame.convert("RGBA").resize((45, 45))
            frame_col = frame.convert("RGBA").resize((40, 40))
            self.avatar_gif_frames_expanded.append(ctk.CTkImage(frame_exp, size=(45, 45)))
            self.avatar_gif_frames_collapsed.append(ctk.CTkImage(frame_col, size=(50, 50)))
        self.avatar_gif_frames = self.avatar_gif_frames_expanded

        self.avatar_lbl = ctk.CTkLabel(
            self.profile_frame,
            image=self.avatar_gif_frames[0],
            text="",
            fg_color="transparent"
        )
        self.avatar_lbl.pack(side="left", padx=2)
        self.avatar_animating = False
        self.current_avatar_frame = 0
        self.avatar_lbl.bind("<Enter>", lambda e: self.start_avatar_animation())
        self.avatar_lbl.bind("<Leave>", lambda e: self.stop_avatar_animation())

        self.name_lbl = ctk.CTkLabel(
            self.profile_frame,
            text=f"{self.user_id}\n{self.user_name}",
            justify="left",
            text_color="#1a3e72",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.name_lbl.pack(side="left")

        self.settings_gif_frames = []
        gif = Image.open("Pic/setting.gif")
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert("RGBA").resize((25, 25))
            self.settings_gif_frames.append(ctk.CTkImage(frame, size=(25, 25)))

        self.settings_btn = ctk.CTkButton(
            self.profile_frame,
            image=self.settings_gif_frames[0],
            text="",
            fg_color="transparent",
            hover_color="#bfd5ff",
            width=40, height=40,
            command=lambda: self.show_page("Settings")
        )
        self.settings_btn.image = self.settings_gif_frames[0]
        self.settings_btn.pack(side="right", pady=(5, 0))
        self.settings_btn.bind("<Enter>", lambda e: self.start_settings_animation())
        self.settings_btn.bind("<Leave>", lambda e: self.stop_settings_animation())
        self.settings_animating = False
        self.current_settings_frame = 0

        # Content Area
        self.content_frame = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=0)
        self.content_frame.pack(side="right", expand=True, fill="both")
        self.show_page("Dashboard")

    def get_selected_nav(self):
        for text, btn in self.nav_buttons.items():
            if btn.is_selected:
                return text
        return None

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        new_width = self.sidebar_width_collapsed if self.sidebar_collapsed else self.sidebar_width_expanded
        self.side_panel.configure(width=new_width)
        if self.sidebar_collapsed:
            self.logo_lbl.configure(image=self.logo_image_collapsed)
        else:
            self.logo_lbl.configure(image=self.logo_image_expanded)

        for text, btn in self.nav_buttons.items():
            if self.sidebar_collapsed:
                btn.configure(text="", image=self.nav_gif_frames[text]['collapsed'][0])
                btn.static_image = self.nav_static_images[text]['collapsed']
                btn.gif_frames = self.nav_gif_frames[text]['collapsed']
                btn.bind("<Enter>", lambda e, b=btn: self.start_button_animation(b, b.gif_frames))
                btn.bind("<Leave>", lambda e, b=btn: self.stop_button_animation(b, b.gif_frames))
            else:
                btn.configure(text=btn._original_text, image=self.nav_gif_frames[text]['expanded'][0])
                btn.static_image = self.nav_static_images[text]['expanded']
                btn.gif_frames = self.nav_gif_frames[text]['expanded']
                btn.bind("<Enter>", lambda e, b=btn: self.start_button_animation(b, b.gif_frames))
                btn.bind("<Leave>", lambda e, b=btn: self.stop_button_animation(b, b.gif_frames))

        if self.sidebar_collapsed:
            self.logout_btn.configure(text="", image=self.logout_gif_frames_collapsed[0])
            self.logout_gif_frames = self.logout_gif_frames_collapsed
            self.avatar_lbl.configure(image=self.avatar_gif_frames_collapsed[0])
            self.avatar_gif_frames = self.avatar_gif_frames_collapsed
            self.avatar_lbl.pack(side="left", padx=6)
        else:
            self.logout_btn.configure(text="Log out", image=self.logout_gif_frames_expanded[0])
            self.logout_gif_frames = self.logout_gif_frames_expanded
            self.avatar_lbl.configure(image=self.avatar_gif_frames_expanded[0])
            self.avatar_gif_frames = self.avatar_gif_frames_expanded

        self.name_lbl.configure(text="" if self.sidebar_collapsed else f"{self.user_id}\n{self.user_name}")

        if self.sidebar_collapsed:
            self.settings_btn.pack_forget()
        else:
            self.settings_btn.pack(side="right", pady=(5, 0))

        self.collapse_btn.configure(text="⮞" if self.sidebar_collapsed else "⮜")

        self.highlight_nav(self.get_selected_nav())

    def highlight_nav(self, name):
        for text, btn in self.nav_buttons.items():
            if text == name:
                btn.is_selected = True

                btn.configure(
                    image=btn.static_image,
                    fg_color="#6a9ef5",
                    text_color="white",
                    hover_color="#6a9ef5",
                    font=ctk.CTkFont(size=15, weight="bold")
                )
                btn._animating = False
            else:
                btn.is_selected = False
                btn.configure(
                    image=btn.gif_frames[0],
                    fg_color="transparent",
                    text_color="#2c3e50",
                    hover_color="#cce0ff",
                    font=ctk.CTkFont(size=14, weight="normal")
                )

    def show_page(self, page_name: str):
        self.clear_main_content()
        if page_name == "Dashboard":
            admin_doc = firebase_db.get_admin(self.user_id)
            admin_name = admin_doc.get('admin_name', self.user_name) if admin_doc else self.user_name
            AdminDashboard(self.content_frame, user_id=self.user_id).pack(fill="both", expand=True)
        elif page_name == "Records":
            AdminRecord(
                self.content_frame,
                self.user_id,
                self.user_name,
                navigate_to=self.show_record_subpage
            ).pack(fill="both", expand=True)
        elif page_name == "Owner":
            AdminOwner(
                self.content_frame,
                self.user_id,
                self.user_name,
                navigate_to=self.show_owner_subpage
            ).pack(fill="both", expand=True)
        elif page_name == "Security Personnel":
            AdminSecurity(
                self.content_frame,
                self.user_id,
                self.user_name,
                navigate_to=self.show_security_subpage
            ).pack(fill="both", expand=True)
        elif page_name == "Admin":
            AdminInterface(
                self.content_frame,
                self.user_id,
                self.user_name,
                navigate_to_login=self.navigate_to_login,
                navigate_to=self.show_admin_subpage
            ).pack(fill="both", expand=True)
        elif page_name == "Blacklist":
            from Admin.admin_blacklist import AdminBlacklist
            AdminBlacklist(self.content_frame, self.user_id, self.user_name, self.navigate_to_login).pack(fill="both", expand=True)
        elif page_name == "Settings":
            AdminSetting(self.content_frame, self.user_id, self.user_name).pack(fill="both", expand=True)
        else:
            header = ctk.CTkLabel(
                self.content_frame,
                text=page_name,
                font=ctk.CTkFont(size=24, weight="bold"),
                fg_color="transparent",
                text_color='black',
                anchor="w"
            )
            header.pack(padx=20, pady=20, anchor="nw")
        if page_name in self.nav_buttons:
            self.highlight_nav(page_name)
            self.highlight_settings(False)
        elif page_name == "Settings":
            self.highlight_nav(None)
            self.highlight_settings(True)
        else:
            self.highlight_nav(None)
            self.highlight_settings(False)

    def highlight_settings(self, is_selected):
        if is_selected:
            self.settings_btn.configure(
                fg_color="#6a9ef5",
                hover_color="#6a9ef5",
                text_color="white"
            )
        else:
            self.settings_btn.configure(
                fg_color="transparent",
                hover_color="#bfd5ff",
                text_color="#2c3e50"
            )

    def start_settings_animation(self):
        if len(self.settings_gif_frames) <= 1:
            return
        self.settings_animating = True
        self.current_settings_frame = 0

        if hasattr(self, '_settings_animation_task'):
            self.after_cancel(self._settings_animation_task)
        self.animate_settings()

    def stop_settings_animation(self):
        self.settings_animating = False

        if hasattr(self, '_settings_animation_task'):
            self.after_cancel(self._settings_animation_task)
        self.settings_btn.configure(image=self.settings_gif_frames[0])

    def animate_settings(self):
        if not self.settings_animating:
            return
        self.current_settings_frame = (self.current_settings_frame + 1) % len(self.settings_gif_frames)
        self.settings_btn.configure(image=self.settings_gif_frames[self.current_settings_frame])

        self._settings_animation_task = self.after(50, self.animate_settings)

    def start_logout_animation(self):
        if len(self.logout_gif_frames) <= 1:
            return
        self.logout_animating = True
        self.current_logout_frame = 0

        if hasattr(self, '_logout_animation_task'):
            self.after_cancel(self._logout_animation_task)
        self.animate_logout()

    def stop_logout_animation(self):
        self.logout_animating = False

        if hasattr(self, '_logout_animation_task'):
            self.after_cancel(self._logout_animation_task)
        self.logout_btn.configure(image=self.logout_gif_frames[0])

    def animate_logout(self):
        if not self.logout_animating:
            return
        self.current_logout_frame = (self.current_logout_frame + 1) % len(self.logout_gif_frames)
        self.logout_btn.configure(image=self.logout_gif_frames[self.current_logout_frame])

        self._logout_animation_task = self.after(50, self.animate_logout)

    def load_gif_frames(self, gif_path, size):
        frames = []
        gif = Image.open(gif_path)
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert("RGBA").resize(size)
            frames.append(ctk.CTkImage(frame, size=size))
        return frames

    def start_button_animation(self, button, frames):
        if not button.is_selected:
            button._animating = True
            button._current_frame = 0

            if hasattr(button, '_animation_task'):
                self.after_cancel(button._animation_task)
            self.animate_button(button, frames)

    def stop_button_animation(self, button, frames):
        button._animating = False

        if hasattr(button, '_animation_task'):
            self.after_cancel(button._animation_task)
        if not button.is_selected:
            button.configure(image=frames[0])

    def animate_button(self, button, frames):
        if not getattr(button, '_animating', False):
            return
        button._current_frame = (button._current_frame + 1) % len(frames)
        button.configure(image=frames[button._current_frame])
        delay = 80

        button._animation_task = self.after(delay, lambda: self.animate_button(button, frames))

    def start_avatar_animation(self):
        if len(self.avatar_gif_frames) <= 1:
            return
        self.avatar_animating = True
        self.current_avatar_frame = 0

        if hasattr(self, '_avatar_animation_task'):
            self.after_cancel(self._avatar_animation_task)
        self.animate_avatar()

    def stop_avatar_animation(self):
        self.avatar_animating = False

        if hasattr(self, '_avatar_animation_task'):
            self.after_cancel(self._avatar_animation_task)
        self.avatar_lbl.configure(image=self.avatar_gif_frames[0])

    def animate_avatar(self):
        if not self.avatar_animating:
            return
        self.current_avatar_frame = (self.current_avatar_frame + 1) % len(self.avatar_gif_frames)
        self.avatar_lbl.configure(image=self.avatar_gif_frames[self.current_avatar_frame])

        self._avatar_animation_task = self.after(50, self.animate_avatar)

    def logout(self):
        self.destroy()
        self.navigate_to_login()

    def show_record_subpage(self, page, **kwargs):
        self.clear_main_content()
        if page == "add_record":
            AdminAddRecord(
                self.content_frame,
                self.user_id,
                self.user_name,
                navigate_to=self.show_record_subpage
            ).pack(fill="both", expand=True)
        elif page == "edit_record":
            record = kwargs.get("record")
            AdminEditRecord(
                self.content_frame,
                self.user_id,
                self.user_name,
                record,
                navigate_to=self.show_record_subpage
            ).pack(fill="both", expand=True)
        else:
            self.show_page("Records")

    def show_owner_subpage(self, page, **kwargs):
        self.clear_main_content()
        if page == "add_owner":
            AdminAddOwner(
                self.content_frame,
                self.user_id,
                self.user_name,
                navigate_to=self.show_owner_subpage,
                navigate_to_login=self.navigate_to_login
            ).pack(fill="both", expand=True)
        elif page == "edit_owner":
            owner = kwargs.get("owner")
            AdminEditOwner(
                self.content_frame,
                self.user_id,
                self.user_name,
                owner,
                navigate_to=self.show_owner_subpage,
                navigate_to_login=self.navigate_to_login
            ).pack(fill="both", expand=True)
        else:
            self.show_page("Owner")

    def show_security_subpage(self, page, **kwargs):
        self.clear_main_content()
        if page == "add_security":
            AdminAddSecurity(
                self.content_frame,
                self.user_id,
                self.user_name,
                navigate_to=self.show_security_subpage,
                navigate_to_login=self.navigate_to_login
            ).pack(fill="both", expand=True)
        elif page == "edit_security":
            security = kwargs.get("security")
            AdminEditSecurity(
                self.content_frame,
                self.user_id,
                self.user_name,
                security,
                navigate_to=self.show_security_subpage,
                navigate_to_login=self.navigate_to_login
            ).pack(fill="both", expand=True)
        else:
            self.show_page("Security Personnel")

    def show_admin_subpage(self, page, **kwargs):
        self.clear_main_content()
        if page == "add_admin":
            from Admin.admin_add_admin import AdminAddAdmin
            AdminAddAdmin(
                self.content_frame,
                self.user_id,
                self.user_name,
                navigate_to=self.show_admin_subpage,
                navigate_to_login=self.navigate_to_login
            ).pack(fill="both", expand=True)
        elif page == "edit_admin":
            from Admin.admin_edit_admin import AdminEditAdmin
            admin = kwargs.get("admin")
            AdminEditAdmin(
                self.content_frame,
                self.user_id,
                self.user_name,
                admin,
                navigate_to=self.show_admin_subpage,
                navigate_to_login=self.navigate_to_login
            ).pack(fill="both", expand=True)
        else:
            self.show_page("Admin")

    def clear_main_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()


