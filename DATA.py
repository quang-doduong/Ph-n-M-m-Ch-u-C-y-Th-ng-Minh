import yaml
import os
import iot_socket

class AppData:
    def __init__(self):
        self.selected_plant_name = "Chưa chọn cây"
        self.selected_plant_info = {
            "DoAm": "--", 
            "AnhSang": "--", 
            "MucNuoc": "--", 
            "ThoiGianKiemTra": "--"
        }
        self.all_plants = {}
        self.load_yaml()

    def load_yaml(self):
        """Đọc dữ liệu từ data.yaml một cách an toàn"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(base_path, "data.yaml")
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                self.all_plants = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Lỗi đọc file YAML: {e}")

    def set_selected_plant(self, plant_name):
        """Cập nhật cây đang được chọn"""
        if plant_name in self.all_plants:
            self.selected_plant_name = plant_name
            self.selected_plant_info = self.all_plants[plant_name]

    # Các hàm phân phối dữ liệu cho modules.py gọi
    def get_realtime_sensors(self):
        return iot_socket.read_sensors()

    def get_chart_history(self):
        return iot_socket.read_history()

    def get_streak_data(self):
        return iot_socket.read_streak()

# Biến toàn cục để các file khác import
db = AppData()