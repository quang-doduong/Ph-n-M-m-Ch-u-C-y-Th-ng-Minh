# modules.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import iot_socket

EMOJIS = {"EXCELLENT": "🤩", "OK": "🙂", "BAD": "😟", "CRITICAL": "😱"}

class InfoModule(ctk.CTkFrame):
    """Module hiển thị thông tin cây cơ bản"""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        

        name = controller.current_plant_name
        info = controller.current_plant_info
        
        info_text = f"Tên cây đang trồng: {name}\nĐộ ẩm yêu cầu: {info.get('DoAm', '--')}\nÁnh sáng: {info.get('AnhSang', '--')}\nMực nước: {info.get('MucNuoc', '--')}\nKiểm tra mỗi: {info.get('ThoiGianKiemTra', '--')}"
        
        ctk.CTkLabel(self, text=info_text, font=("Arial", 18, "bold")).pack(pady=20)
        ctk.CTkButton(self, text="Đổi loại cây khác", command=lambda: controller.show_frame("EditPlantPage")).pack(pady=10)

class SuggestionModule(ctk.CTkFrame):
    """Module Gợi ý chỗ đặt dựa trên Sensor"""
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text=f"Trạng thái hiện tại: {EMOJIS['EXCELLENT']}", font=("Arial", 20)).pack(pady=10)
        
        self.lbl_sensor = ctk.CTkLabel(self, text="Nhấn nút để lấy dữ liệu cảm biến...", text_color="yellow", font=("Arial", 16))
        self.lbl_sensor.pack(pady=20)
        
        btn_fetch = ctk.CTkButton(self, text="Đọc cảm biến qua IOT Socket", command=self.fetch_data)
        btn_fetch.pack(pady=10)
        
        # Tự động lấy dữ liệu lần đầu
        self.fetch_data()

    def fetch_data(self):
        data = iot_socket.read_sensors()
        display_text = f"☀️ Ánh sáng: {data['light_lux']} lux\n💧 Độ ẩm đất: {data['soil_moisture']}%\n🚰 Mực nước bình: {data['water_level']}"
        self.lbl_sensor.configure(text=display_text)

class PlantHPModule(ctk.CTkFrame):
    """Module hiển thị Streak/Sinh tồn"""
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Lấy dữ liệu từ Socket
        streak_data = iot_socket.read_streak()
        days = streak_data["streak_days"]
        hp = streak_data["hp_percent"]
        status = streak_data["status"]

        ctk.CTkLabel(self, text=f"🔥 Streak: {days} ngày liên tiếp không để cây héo!", font=("Arial", 18, "bold")).pack(pady=20)
        
        lbl_hp = ctk.CTkLabel(self, text=f"Tình trạng sức khỏe: {status} ({int(hp*100)}%)", font=("Arial", 14))
        lbl_hp.pack(pady=(10, 5))
        
        # Đổi màu thanh máu dựa trên %
        color = "green" if hp > 0.6 else ("orange" if hp > 0.4 else "red")
        
        pb = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate", width=400, height=20, progress_color=color)
        pb.pack(pady=10)
        pb.set(hp)

class HoverPlantChart(ctk.CTkFrame):
    """Module vẽ biểu đồ Matplotlib siêu mượt"""
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Lấy dữ liệu lịch sử từ Socket
        hist_data = iot_socket.read_history()
        days = hist_data["days"]
        light = hist_data["light_history"]
        moisture = hist_data["moisture_history"]

        # Thiết lập figure matplotlib nền tối
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b') # Màu nền trùng với CustomTkinter
        ax.set_facecolor('#2b2b2b')

        # Vẽ đường
        ax.plot(days, light, marker='o', color='#f1c40f', label='Ánh sáng (lux)', linewidth=2)
        ax.plot(days, moisture, marker='s', color='#3498db', label='Độ ẩm (%)', linewidth=2)

        # Cấu hình biểu đồ
        ax.set_title("Dữ liệu môi trường 7 ngày qua", color='white', pad=10)
        ax.legend(loc="upper left", frameon=False)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Nhúng vào CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)