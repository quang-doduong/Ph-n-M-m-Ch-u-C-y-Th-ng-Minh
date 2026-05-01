# iot_socket.py
import random

def read_sensors():
    """Dữ liệu realtime cho tab Cảm biến & Gợi ý"""
    return {
        "light_lux": random.randint(200, 1000),
        "soil_moisture": random.randint(10, 90),
        "water_level": random.choice(["Thấp", "Trung bình", "Đầy"])
    }

def read_history():
    """Dữ liệu mảng 7 ngày để vẽ biểu đồ cho tab Dữ liệu trực quan"""
    return {
        "days": ["T2", "T3", "T4", "T5", "T6", "T7", "CN"],
        "light_history": [random.randint(300, 900) for _ in range(7)],
        "moisture_history": [random.randint(20, 80) for _ in range(7)]
    }

def read_streak():
    """Dữ liệu cho hệ thống Sinh tồn/Streak"""
    hp = random.uniform(0.4, 1.0) # Máu ngẫu nhiên từ 40% đến 100%
    return {
        "streak_days": random.randint(1, 30),
        "hp_percent": hp,
        "status": "Tốt" if hp > 0.6 else ("Báo động" if hp < 0.5 else "Bình thường")
    }