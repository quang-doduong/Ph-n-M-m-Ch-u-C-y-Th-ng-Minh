# pages.py
import customtkinter as ctk
import yaml
import os
from modules import InfoModule, SuggestionModule, PlantHPModule, HoverPlantChart

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="🌱 SMART PLANT POT", font=ctk.CTkFont(size=30, weight="bold")).grid(row=1, column=0, pady=20)
        self.entry_username = ctk.CTkEntry(self, placeholder_text="Tên đăng nhập", width=250)
        self.entry_username.grid(row=2, column=0, pady=10)
        self.entry_password = ctk.CTkEntry(self, placeholder_text="Mật khẩu", show="*", width=250)
        self.entry_password.grid(row=3, column=0, pady=10)

        ctk.CTkButton(self, text="Đăng nhập", width=250, command=lambda: controller.show_frame("DashboardPage")).grid(row=4, column=0, pady=10)

        frame_options = ctk.CTkFrame(self, fg_color="transparent")
        frame_options.grid(row=5, column=0, pady=10)
        ctk.CTkButton(frame_options, text="Tạo tài khoản nhanh", width=120, fg_color="transparent", border_width=1, command=self.auto_create_account).grid(row=0, column=0, padx=5)
        ctk.CTkButton(frame_options, text="Thông tin nhóm", width=120, fg_color="transparent", border_width=1, command=lambda: controller.show_frame("GroupInfoPage")).grid(row=0, column=1, padx=5)

    def auto_create_account(self):
        self.entry_username.delete(0, 'end')
        self.entry_password.delete(0, 'end')
        self.entry_username.insert(0, "User_Auto_123")
        self.entry_password.insert(0, "1234")
        self.controller.show_frame("DashboardPage")

class GroupInfoPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Thông tin nhóm làm", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=40)
        ctk.CTkLabel(self, text="Thành viên 1: ...\nThành viên 2: ...\nĐề tài: Chậu cây thông minh IOT", font=("Arial", 16)).pack(pady=20)
        ctk.CTkButton(self, text="Quay lại", command=lambda: controller.show_frame("LoginPage")).pack(pady=20)

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # SIDEBAR
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="My Plant", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=30)
        ctk.CTkButton(self.sidebar_frame, text="🌿 Thông tin cây", command=lambda: self.switch_tab("info", "Thông tin cây")).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="☀️ Cảm biến & Gợi ý", command=lambda: self.switch_tab("suggest", "Dữ liệu Cảm biến Realtime")).grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="💧 Streak/Thành tích", command=lambda: self.switch_tab("streak", "Thành tích sinh tồn")).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="📊 Dữ liệu trực quan", command=lambda: self.switch_tab("chart", "Biểu đồ ánh sáng/độ ẩm")).grid(row=4, column=0, padx=20, pady=10)

        ctk.CTkButton(self.sidebar_frame, text="Đăng xuất", fg_color="gray", command=lambda: controller.show_frame("LoginPage")).grid(row=7, column=0, padx=20, pady=20, sticky="s")

        # MAIN CONTENT
        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.lbl_tab_title = ctk.CTkLabel(self.main_content, text="Chào mừng", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_tab_title.pack(pady=(20, 10))

        self.dynamic_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.dynamic_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.switch_tab("info", "Thông tin cây")

    def clear_dynamic_frame(self):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

    def switch_tab(self, tab_name, title):
        self.clear_dynamic_frame()
        self.lbl_tab_title.configure(text=title)

        if tab_name == "info":
            module = InfoModule(self.dynamic_frame, self.controller)
            module.pack(fill="both", expand=True)
        elif tab_name == "suggest":
            module = SuggestionModule(self.dynamic_frame)
            module.pack(fill="both", expand=True)
        elif tab_name == "streak":
            module = PlantHPModule(self.dynamic_frame)
            module.pack(fill="both", expand=True)
        elif tab_name == "chart":
            module = HoverPlantChart(self.dynamic_frame)
            module.pack(fill="both", expand=True)

class EditPlantPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Lựa Chọn Thông Tin Cây", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 10))
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=600, height=400)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkButton(self, text="Quay lại Dashboard", command=lambda: controller.show_frame("DashboardPage")).pack(pady=20)

        self.load_plant_data()

    def load_plant_data(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            yaml_path = os.path.join(current_dir, "data.yaml")
            
            with open(yaml_path, "r", encoding="utf-8") as file:
                plants = yaml.safe_load(file)
            
            for plant_name, info in plants.items():
                plant_frame = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
                plant_frame.pack(pady=5, padx=5, fill="x")

                info_text = f"🌿 {plant_name}\nĐộ ẩm: {info['DoAm']} | Ánh sáng: {info['AnhSang']} | Mức nước: {info['MucNuoc']}"
                
                ctk.CTkLabel(plant_frame, text=info_text, justify="left", font=("Arial", 14)).pack(side="left", padx=15, pady=10)
                ctk.CTkButton(plant_frame, text="Chọn", width=60, command=lambda n=plant_name, i=info: self.select_plant(n, i)).pack(side="right", padx=15, pady=10)
            
            self.scroll_frame.update_idletasks()
                
        except Exception as e:
            ctk.CTkLabel(self.scroll_frame, text=f"Lỗi tải dữ liệu: {e}", text_color="red").pack()

    def select_plant(self, name, info):
        # 1. Cập nhật dữ liệu vào bộ nhớ trung tâm
        self.controller.current_plant_name = name
        self.controller.current_plant_info = info
        
        # 2. Ép Dashboard tải lại tab "info" để hiển thị cây mới ngay lập tức
        dashboard_frame = self.controller.frames["DashboardPage"]
        dashboard_frame.switch_tab("info", "Thông tin cây")
        
        # 3. Đưa người dùng về trang Dashboard
        self.controller.show_frame("DashboardPage")