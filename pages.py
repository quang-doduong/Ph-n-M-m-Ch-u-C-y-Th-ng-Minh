# pages.py
import customtkinter as ctk
import yaml
import os
from modules import InfoModule, SuggestionModule, PlantHPModule, HoverPlantChart
import unicodedata
from PIL import Image

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

# Mới cập nhật lại thông tin thành viên nhóm trên code
class GroupInfoPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Tiêu đề trang
        ctk.CTkLabel(self, text="ĐỘI NGŨ PHÁT TRIỂN DỰ ÁN", 
                     font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(30, 20))

        # Khung chứa 4 thành viên (chia 2 hàng, 2 cột)
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=50)

        # Danh sách thành viên (Bạn có thể tự sửa text ở đây)
        members = [
            {"name": "Thành viên 1", "role": "Lập trình nhúng / ESP32", "img": "member1.png"},
            {"name": "Thành viên 2", "role": "Thiết kế Giao diện / Python", "img": "member2.png"},
            {"name": "Thành viên 3", "role": "Quản lý Dữ liệu / YAML", "img": "member3.png"},
            {"name": "Thành viên 4", "role": "Hệ thống Thủy lực / Sensor", "img": "member4.png"}
        ]

        for i, m in enumerate(members):
            row = i // 2
            col = i % 2
            self.create_member_card(container, m, row, col)

        ctk.CTkButton(self, text="Quay lại", width=200, height=40,
                      command=lambda: controller.show_frame("LoginPage")).pack(pady=30)

    def create_member_card(self, parent, info, row, col):
        card = ctk.CTkFrame(parent, corner_radius=15, border_width=1)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        # Xử lý ảnh Icon 100*100
        asset_dir = os.path.join(os.path.dirname(__file__), 'asset')
        img_path = os.path.join(asset_dir, info["img"])
        
        try:
            from PIL import Image
            img = Image.open(img_path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            img_label = ctk.CTkLabel(card, image=ctk_img, text="")
            img_label.pack(pady=(15, 5))
        except:
            # Nếu thiếu ảnh, hiện ô xám chuyên nghiệp [cite: 6, 22]
            placeholder = ctk.CTkFrame(card, width=100, height=100, fg_color="#3d3d3d")
            placeholder.pack(pady=(15, 5))
            ctk.CTkLabel(placeholder, text="Avatar").pack(expand=True)

        # Khung chữ thông tin
        ctk.CTkLabel(card, text=info["name"], font=("Arial", 18, "bold")).pack()
        
        # Textbox tùy chọn cho bạn tự gõ sau (dùng CTkLabel cho đẹp hoặc CTkTextbox nếu muốn copy)
        role_label = ctk.CTkLabel(card, text=info["role"], font=("Arial", 14), 
                                  text_color="#3a7ebf", wraplength=200)
        role_label.pack(pady=(0, 15))

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
    
    # cập nhận thông tin sau khi chọn xong ở trang thông tin cây
    def update_display(self): # Mới cập nhật
        """Hàm này sẽ được gọi mỗi khi bạn chọn cây xong"""
        # Lấy dữ liệu từ kho chung của controller
        selected_plant = self.controller.shared_data.get("selected_plant")
        plant_info = self.controller.shared_data.get("plant_info")

        if selected_plant:
            self.name_label.configure(text=f"Cây đang chọn: {selected_plant}")
            # Hiển thị các thông số từ YAML (Độ ẩm, Ánh sáng...)
            info_text = "\n".join([f"{k}: {v}" for k, v in plant_info.items()])
            self.info_label.configure(text=info_text)
        
        # KHAI BÁO CÁC THÀNH PHẦN (Đây là phần bạn bị thiếu dẫn đến lỗi)
        # Nhãn hiển thị tên cây
        self.name_label = ctk.CTkLabel(self, text="Chưa chọn loại cây", font=("Arial", 20, "italic"))
        self.name_label.pack(pady=10)

        # Nhãn hiển thị chi tiết thông số từ YAML
        self.info_label = ctk.CTkLabel(self, text="Hãy vào phần chỉnh sửa để chọn cây", font=("Arial", 14))
        self.info_label.pack(pady=10)

    def update_display(self):
        """Hàm cập nhật thông tin khi quay lại từ trang chọn cây"""
        # Kiểm tra xem shared_data đã có dữ liệu chưa 
        selected_plant = self.controller.shared_data.get("selected_plant")
        plant_info = self.controller.shared_data.get("plant_info")

        if selected_plant:
            self.name_label.configure(text=f"Cây hiện tại: {selected_plant}", font=("Arial", 20, "bold"), text_color="#2ECC71")
            
            # Hiển thị thông số từ YAML (DoAm, AnhSang, MucNuoc...)
            info_text = ""
            for key, val in plant_info.items():
                info_text += f"{key}: {val}\n"
            self.info_label.configure(text=info_text)
# Hàm module con xử lý tên ảnh
def get_safe_filename(name):
    """Ép chuỗi (VD: 'Xương Rồng' -> 'xuong_rong.png')"""
    name = name.lower()
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    return name.replace(' ', '_') + '.png'

# ... (Giữ nguyên LoginPage, GroupInfoPage, DashboardPage của bạn) ...

class EditPlantPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 1. Xác định đường dẫn tuyệt đối an toàn
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data.yaml')
        self.asset_dir = os.path.join(base_dir, 'asset')

        # 2. Đọc file data.yaml
        try:
            with open(data_path, 'r', encoding='utf-8') as file:
                self.plants_data = yaml.safe_load(file)
        except Exception as e:
            self.plants_data = {}
            print(f"Lỗi đọc file data.yaml: {e}")

        # 3. Tạo khung cuộn CTkScrollableFrame
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 4. Hiển thị danh sách từ yaml lên giao diện
        if self.plants_data:
            for plant_name, attributes in self.plants_data.items():
                self.create_plant_row(plant_name, attributes)
        else:
            ctk.CTkLabel(self.scroll_frame, text="Không có dữ liệu cây.", font=("Arial", 16)).pack(pady=20)

    def create_plant_row(self, plant_name, attributes):
        """Tạo một hàng hiển thị cho từng cây kèm ảnh và thông số"""
        row_frame = ctk.CTkFrame(self.scroll_frame)
        row_frame.pack(fill="x", padx=10, pady=10)

        # Xử lý hình ảnh (Tự động chuyển 'ca_chua.png' v.v.)
        filename = get_safe_filename(plant_name)
        img_path = os.path.join(self.asset_dir, filename)

        try:
            # Load ảnh bằng PIL và ép kích thước 200x200
            img = Image.open(img_path)
            plant_img = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
            
            img_label = ctk.CTkLabel(row_frame, image=plant_img, text="")
            # Chống Garbage Collection làm mất ảnh sau hàm init
            img_label.image = plant_img 
            img_label.pack(side="left", padx=10, pady=10)
        except Exception as e:
            # Cơ chế chống sập: Tạo ô Placeholder xám nếu lỗi hoặc thiếu ảnh
            placeholder = ctk.CTkFrame(row_frame, width=200, height=200, fg_color="gray")
            placeholder.pack(side="left", padx=10, pady=10)
            placeholder.pack_propagate(False)
            ctk.CTkLabel(placeholder, text="No Image\n(200x200)").pack(expand=True)

        # Khung chứa thông số YAML
        info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        # Tên cây
        ctk.CTkLabel(info_frame, text=plant_name, font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        # Bóc tách tự động mọi key trong attributes (DoAm, AnhSang...)
        if isinstance(attributes, dict):
            for key, val in attributes.items():
                ctk.CTkLabel(info_frame, text=f"{key}: {val}", font=("Arial", 14)).pack(anchor="w")

        # Nút xác nhận lựa chọn
        select_btn = ctk.CTkButton(
            row_frame, 
            text="Chọn Cây Này", 
            command=lambda p=plant_name: self.on_plant_select(p)
        )
        select_btn.pack(side="right", padx=20)

    def on_plant_select(self, plant_name):
        if plant_name in self.plants_data:
            self.controller.shared_data["selected_plant"] = plant_name
            self.controller.shared_data["plant_info"] = self.plants_data[plant_name]
        
        # Cập nhật hiển thị cho Dashboard trước khi chuyển trang
        if "DashboardPage" in self.controller.frames:
            self.controller.frames["DashboardPage"].update_display()
        
        # Quay về Dashboard
        self.controller.show_frame("DashboardPage")