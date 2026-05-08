# modules.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import iot_socket

EMOJIS = {"EXCELLENT": "🤩", "OK": "🙂", "BAD": "😟", "CRITICAL": "😱"}

# mới cập nhật lại
class InfoModule(ctk.CTkFrame):
    """Module hiển thị thông tin cây cơ bản"""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller # Giữ lại controller để dùng cho nút bấm
        
        # 1. KHỞI TẠO KHUNG XƯƠNG (Gán vào biến self.info_label)
        self.info_label = ctk.CTkLabel(self, text="Đang tải dữ liệu...", font=("Arial", 18, "bold"))
        self.info_label.pack(pady=20)
        
        # 2. Nút bấm (Giữ nguyên)
        ctk.CTkButton(self, text="Đổi loại cây khác", command=lambda: controller.show_frame("EditPlantPage")).pack(pady=10)

    def update_ui(self, plant_name, plant_specs):
        # 1. GẮN MÁY NGHE LÉN VÀO ĐÂY:
        print(f"========== DEBUG KÊNH DỮ LIỆU ==========")
        print(f"Tên cây nhận được: {plant_name}")
        print(f"Thông số YAML nhận được: {plant_specs}")
        print(f"========================================")

        # 2. Code cũ của bạn
        info_text = f"Tên cây đang trồng: {plant_name}\nĐộ ẩm yêu cầu: {plant_specs.get('DoAm', '--')}\nÁnh sáng: {plant_specs.get('AnhSang', '--')}\nMực nước: {plant_specs.get('MucNuoc', '--')}\nKiểm tra mỗi: {plant_specs.get('ThoiGianKiemTra', '--')}"
        
        self.info_label.configure(text=info_text)

class SuggestionModule(ctk.CTkFrame):
    def __init__(self, parent, controller): # Thêm controller vào đây
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Giữ nguyên giao diện của bạn
        self.lbl_status = ctk.CTkLabel(self, text="Hệ thống phán xét: Đang đợi lệnh...", font=("Arial", 20, "bold"))
        self.lbl_status.pack(pady=10)
        
        self.lbl_sensor = ctk.CTkLabel(self, text="Chưa có dữ liệu cảm biến", text_color="yellow", font=("Arial", 16))
        self.lbl_sensor.pack(pady=20)
        
        # Nút bấm bây giờ gọi hàm không tham số
        btn_fetch = ctk.CTkButton(self, text="Phán xét sinh tồn ngay", command=self.update_logic)
        btn_fetch.pack(pady=10)

    def update_logic(self):
        """Hàm tự thò tay vào kho lấy dữ liệu để ý nghĩa hóa - Đã thêm giáp bảo vệ"""
        import iot_socket
        
        # 1. LẤY THỰC TẾ
        real_data = iot_socket.sensor_cache
        raw_soil = real_data.get("soil_moisture", 0)
        
        # --- GIÁP BẢO VỆ: Kiểm tra xem có phải là số không ---
        try:
            soil = float(raw_soil) # Cố gắng chuyển sang số
            is_hardware_connected = True
        except (ValueError, TypeError):
            soil = 0
            is_hardware_connected = False # Đánh dấu là chưa cắm phần cứng
        # ----------------------------------------------------

        # 2. LẤY KINH THÁNH
        plant_info = self.controller.shared_data.get("plant_info", {})
        plant_name = self.controller.shared_data.get("selected_plant", "Chưa chọn cây")
        
        try:
            ideal_soil = float(plant_info.get('DoAm', '50%').replace('%', ''))
        except:
            ideal_soil = 50.0

        # 3. PHÁN XÉT
        if not is_hardware_connected:
            msg = "⚠️ HỆ THỐNG: Mất kết nối với chậu cây!"
            color = "gray"
            sensor_detail = "Vui lòng kiểm tra cáp USB hoặc cổng COM"
        else:
            # Logic so sánh như cũ
            if soil < ideal_soil - 15:
                msg = f"CẢNH BÁO: {plant_name} đang KHÁT KHÔ!"
                color = "#E74C3C"
            elif soil > ideal_soil + 15:
                msg = f"CẢNH BÁO: {plant_name} đang bị ÚNG!"
                color = "#3498DB"
            else:
                msg = f"TUYỆT VỜI: {plant_name} đang sống rất tốt!"
                color = "#2ECC71"
            sensor_detail = f"☀️ Ánh sáng: {real_data.get('light_lux')} lux | ☁️ Khí: {real_data.get('air_humidity')}%"

        # 4. HIỂN THỊ
        self.lbl_status.configure(text=msg, text_color=color)
        self.lbl_sensor.configure(text=sensor_detail)

class PlantHPModule(ctk.CTkFrame):
    """Module hiển thị Máu (HP) và Chuỗi ngày sinh tồn (Streak)"""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Nhãn hiển thị HP (Máu cây)
        self.lbl_hp = ctk.CTkLabel(self, text="SỨC SỐNG: --%", font=("Arial", 28, "bold"))
        self.lbl_hp.pack(pady=20)
        
        # Nhãn hiển thị Streak
        self.lbl_streak = ctk.CTkLabel(self, text="🔥 Chuỗi sinh tồn: 0 ngày", font=("Arial", 18))
        self.lbl_streak.pack(pady=10)

    def update_stats(self):
        import iot_socket
        # Hút dữ liệu từ 'ổ cắm' phần cứng
        stats = iot_socket.streak_cache
        hp = stats.get("hp_percent", 100.0)
        days = stats.get("streak_days", 0)
        
        # Phối màu theo lượng máu
        hp_color = "#2ECC71" if hp > 50 else "#F1C40F" if hp > 20 else "#E74C3C"
        
        self.lbl_hp.configure(text=f"SỨC SỐNG: {hp}%", text_color=hp_color)
        self.lbl_streak.configure(text=f"🔥 Chuỗi sinh tồn: {days} ngày")

class HoverPlantChart(ctk.CTkFrame):
    """Module vẽ biểu đồ so sánh Thực tế và Lý tưởng"""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_chart(self):
        import iot_socket
        # 1. LẤY DỮ LIỆU LỊCH SỬ (Thực tế)
        history = iot_socket.history_cache
        days = history["days"]
        data = history["moisture_history"]

        # 2. LẤY NGƯỠNG LÝ TƯỞNG (Kinh thánh)
        plant_info = self.controller.shared_data.get("plant_info", {})
        try:
            ideal_val = float(plant_info.get('DoAm', '50%').replace('%', ''))
        except:
            ideal_val = 50.0

        self.ax.clear()
        # Vẽ đường thực tế (màu xanh dương)
        self.ax.plot(days, data, marker='o', color='#3498DB', label="Độ ẩm thực")
        # ✅ ĐÂY LÀ ĐƯỜNG KINH THÁNH: Vẽ một đường ngang màu xanh lá (Ideal threshold)
        self.ax.axhline(y=ideal_val, color='#2ECC71', linestyle='--', label="Lý tưởng")
        
        self.ax.set_title(f"Biểu đồ sinh tồn: {self.controller.shared_data.get('selected_plant', 'Cây')}")
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()