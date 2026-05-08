import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import iot_socket

EMOJIS = {"EXCELLENT": "🤩", "OK": "🙂", "BAD": "😟", "CRITICAL": "😱"}

# ========================================================
# 1. MODULE THÔNG TIN CÂY (INFO)
# ========================================================
class InfoModule(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Lấy thông tin từ YAML (đã được pages.py nạp vào shared_data)
        p_info = self.controller.shared_data.get("plant_info", {})

        # Giao diện tĩnh: Các tiêu đề và thông số lý tưởng (Không đổi)
        title = ctk.CTkLabel(self, text="📊 CHỈ SỐ MÔI TRƯỜNG", font=("Arial", 18, "bold"))
        title.pack(pady=(0, 20))

        # --- KHU VỰC CÁC NHÃN SẼ THAY ĐỔI SỐ LIỆU ---
        # Chúng ta găm vào self để hàm update_ui tìm thấy
        self.light_label = self.create_item("💡 Ánh sáng", f"Lý tưởng: {p_info.get('AnhSang', 'N/A')}")
        self.air_label = self.create_item("🌡️ Độ ẩm KK", f"Lý tưởng: {p_info.get('DoAm', 'N/A')}")
        self.soil_label = self.create_item("💧 Độ ẩm đất", f"Mức nước: {p_info.get('MucNuoc', 'N/A')}")
        
        self.update_ui() # Cập nhật số liệu thật ngay lập tức

    def create_item(self, label_text, ideal_text):
        frame = ctk.CTkFrame(self, fg_color="#2C3E50", corner_radius=10)
        frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(frame, text=label_text, font=("Arial", 14, "bold")).pack(side="left", padx=15, pady=10)
        
        # Nhãn chứa giá trị Sensor thật (Biến số)
        val_label = ctk.CTkLabel(frame, text="Đang tải...", font=("Arial", 14), text_color="#F1C40F")
        val_label.pack(side="right", padx=15)
        
        ctk.CTkLabel(frame, text=ideal_text, font=("Arial", 12), text_color="#BDC3C7").pack(side="right", padx=20)
        return val_label

    def update_ui(self):
        """Hàm thay số thần tốc - KHÔNG GIẬT"""
        # Lấy dữ liệu từ kho iot_socket
        light = iot_socket.sensor_cache.get("light_lux", "---")
        air = iot_socket.sensor_cache.get("air_humidity", "---")
        soil = iot_socket.sensor_cache.get("soil_moisture", "---")

        # Cập nhật chữ cho các nhãn đã găm sẵn
        self.light_label.configure(text=f"{light} Lux")
        self.air_label.configure(text=f"{air} %")
        self.soil_label.configure(text=f"{soil} %")

# ========================================================
# 2. MODULE SINH TỒN (STREAK / HP)
# ========================================================
class PlantHPModule(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        ctk.CTkLabel(self, text="💓 TRẠNG THÁI SINH TỒN", font=("Arial", 18, "bold")).pack(pady=10)

        # Thanh máu (HP)
        self.hp_bar = ctk.CTkProgressBar(self, width=400, height=20)
        self.hp_bar.pack(pady=10)
        
        # Các nhãn thông báo
        self.hp_text = ctk.CTkLabel(self, text="HP: 0%", font=("Arial", 16))
        self.hp_text.pack()
        
        self.streak_label = ctk.CTkLabel(self, text="Ngày sinh tồn: 0 ngày", font=("Arial", 25, "bold"), text_color="#E74C3C")
        self.streak_label.pack(pady=20)
        
        self.status_label = ctk.CTkLabel(self, text="Tình trạng: Đang kiểm tra...", font=("Arial", 14))
        self.status_label.pack()

    def update_stats(self):
        """Cập nhật HP và Streak - KHÔNG GIẬT"""
        hp = iot_socket.streak_cache.get("hp_percent", 0.0)
        days = iot_socket.streak_cache.get("streak_days", 0)
        status = iot_socket.streak_cache.get("status", "Bình thường")

        # Ép thanh máu và chữ nhảy số
        self.hp_bar.set(hp)
        self.hp_text.configure(text=f"HP: {int(hp*100)}%")
        self.streak_label.configure(text=f"🔥 {days} NGÀY")
        self.status_label.configure(text=f"Tình trạng: {status}")

# ========================================================
# 3. MODULE BIỂU ĐỒ (CHART)
# ========================================================
class HoverPlantChart(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Khởi tạo Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('#1a1a1a') # Màu nền tối khớp với App
        self.ax.set_facecolor('#1a1a1a')
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.update_ui()

    def update_ui(self):
        """Vẽ lại đường biểu đồ trên khung cũ - KHÔNG GIẬT"""
        self.ax.clear()
        
        # Lấy mảng dữ liệu từ lịch sử
        light_data = iot_socket.history_cache.get("light_history", [0]*7)
        moisture_data = iot_socket.history_cache.get("moisture_history", [0]*7)
        
        # Vẽ biểu đồ
        self.ax.plot(light_data, label="Ánh sáng", color="#F1C40F", linewidth=2)
        self.ax.plot(moisture_data, label="Độ ẩm đất", color="#3498DB", linewidth=2)
        
        self.ax.legend(facecolor='#1a1a1a', labelcolor='white')
        self.ax.tick_params(colors='white')
        
        self.canvas.draw()

# ========================================================
# 4. MODULE GỢI Ý (SUGGESTION)
# ========================================================
class SuggestionModule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.icon_label = ctk.CTkLabel(self, text=EMOJIS["OK"], font=("Arial", 60))
        self.icon_label.pack(pady=20)
        
        self.msg_label = ctk.CTkLabel(self, text="Hệ thống đang phân tích...", font=("Arial", 16))
        self.msg_label.pack()

    def update_ui(self):
        """Cập nhật gợi ý - KHÔNG GIẬT"""
        status = iot_socket.streak_cache.get("status", "Bình thường")
        if "tuyệt" in status.lower():
            self.icon_label.configure(text=EMOJIS["EXCELLENT"])
            self.msg_label.configure(text="Vị trí hiện tại rất tốt cho cây!")
        elif "nước" in status.lower():
            self.icon_label.configure(text=EMOJIS["CRITICAL"])
            self.msg_label.configure(text="Cây đang gặp nguy hiểm, hãy xử lý ngay!")
        else:
            self.icon_label.configure(text=EMOJIS["OK"])
            self.msg_label.configure(text="Mọi thứ đang ổn định.")