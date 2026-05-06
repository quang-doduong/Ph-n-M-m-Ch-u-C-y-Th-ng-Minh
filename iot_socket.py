import serial
import serial.tools.list_ports
import time

# ================= KHO LƯU TRỮ DỮ LIỆU THỰC TẾ =================
# Loại bỏ 100% dữ liệu ảo. Khởi tạo trạng thái mặc định an toàn để không sập UI.
sensor_cache = {
    "light_lux": "Không có",
    "air_humidity": "Không có",
    "soil_moisture": "Không có",
    "touch_sensor": "Không có"
}

# Đồ thị yêu cầu mảng số để không sập. Mặc định là mảng số 0.
history_cache = {
    "days": ["Lần 1", "Lần 2", "Lần 3", "Lần 4", "Lần 5", "Lần 6", "Lần 7"],
    "light_history": [0, 0, 0, 0, 0, 0, 0],
    "moisture_history": [0, 0, 0, 0, 0, 0, 0]
}

# Trạng thái sinh tồn tính dựa trên cảm biến thật (Độ ẩm đất)
streak_cache = {
    "streak_days": 0,
    "hp_percent": 0.0,
    "status": "Mất kết nối"
}

ser = None
last_update_time = 0

def auto_connect():
    """Tự động quét và kết nối với ESP32 (Plug & Play) mà không cần cấu hình cứng COM"""
    global ser
    # Nếu đang có kết nối ổn định thì giữ nguyên
    if ser is not None and ser.is_open:
        return True
    
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            # Nhận diện chip nạp của ESP32 (Thường là CH340, CP210x, hoặc USB Serial)
            if "CH340" in port.description or "CP210" in port.description or "Serial" in port.description:
                ser = serial.Serial(port.device, 9600, timeout=1)
                time.sleep(2) # Chờ phần cứng ESP32 reset và ổn định tín hiệu
                return True
        except:
            continue
            
    # Nếu không bắt được bằng định danh, thử cắm đại vào cổng thiết bị phần cứng đầu tiên
    if len(ports) > 0:
        try:
            ser = serial.Serial(ports[0].device, 9600, timeout=1)
            time.sleep(2)
            return True
        except:
            pass
            
    return False

def update_data():
    """Hàm lõi: Quản lý đọc dữ liệu thật từ Hardware mỗi 60 giây"""
    global ser, last_update_time
    global sensor_cache, history_cache, streak_cache
    
    current_time = time.time()
    
    # Chỉ giao tiếp Serial mỗi 60 giây để tuân thủ luật loát (load) 1 phút/lần
    if current_time - last_update_time >= 10: # 10 giây thử
        # Nếu cắm dây (Plug)
        if auto_connect():
            try:
                ser.reset_input_buffer()
                # Python nhận dữ liệu và giải mã
                raw_data = ser.readline().decode('utf-8').strip()
                
                if raw_data:
                    values = raw_data.split(',')
                    if len(values) == 4:
                        # 1. Cập nhật dữ liệu cảm biến (Realtime)
                        sensor_cache["light_lux"] = values[0]
                        sensor_cache["air_humidity"] = values[1]
                        sensor_cache["soil_moisture"] = values[2]
                        sensor_cache["touch_sensor"] = values[3]
                        
                        # 2. Cập nhật mảng Biểu đồ thật (Dịch trái mảng và nạp giá trị mới vào cuối)
                        try:
                            l_val = float(values[0])
                            m_val = float(values[2])
                            
                            history_cache["light_history"].pop(0)
                            history_cache["light_history"].append(l_val)
                            
                            history_cache["moisture_history"].pop(0)
                            history_cache["moisture_history"].append(m_val)
                        except ValueError:
                            pass # Bỏ qua nếu ESP gửi dính ký tự rác, bảo vệ UI không bị lỗi sập
                            
                        # 3. Tính toán Hệ thống Sinh tồn/Streak dựa trên độ ẩm đất thực tế
                        try:
                            soil = float(values[2])
                            if 40 <= soil <= 80: # Đất có độ ẩm lý tưởng
                                streak_cache["hp_percent"] = 1.0
                                streak_cache["status"] = "Tuyệt vời"
                                streak_cache["streak_days"] += 1
                            elif soil < 40: # Quá khô
                                streak_cache["hp_percent"] = 0.3
                                streak_cache["status"] = "Thiếu nước"
                                streak_cache["streak_days"] = 0
                            else: # Quá ẩm (Úng nước)
                                streak_cache["hp_percent"] = 0.5
                                streak_cache["status"] = "Úng nước"
                                streak_cache["streak_days"] = 0
                        except ValueError:
                            pass
                            
                        # Chốt thời gian cập nhật thành công
                        last_update_time = current_time
                        return 
            except Exception:
                # Đóng cổng nếu bị rút dây đột ngột
                ser.close()
                ser = None
        
        # --- Kịch bản: Rút dây (Unplug) hoặc Mất tín hiệu ---
        sensor_cache = {k: "Không có dữ liệu" for k in sensor_cache}
        streak_cache["hp_percent"] = 0.0
        streak_cache["status"] = "Rút cáp/Mất kết nối"
        
        # Lưu ý: history_cache KHÔNG bị ghi đè thành chữ "Không có dữ liệu" 
        # để mảng biểu đồ giữ nguyên được chỉ số cũ, hoặc rớt về 0 tuỳ thuộc, bảo vệ UI khỏi lỗi sập đồ thị.
        
        last_update_time = current_time

# ================= CÁC HÀM XUẤT ĐỂ MODULES.PY GỌI =================
# Cả 3 hàm đều gọi qua một lõi update_data để dữ liệu đồng bộ chính xác thời gian với nhau.

def read_sensors():
    update_data()
    return sensor_cache

def read_history():
    update_data()
    return history_cache

def read_streak():
    update_data()
    return streak_cache