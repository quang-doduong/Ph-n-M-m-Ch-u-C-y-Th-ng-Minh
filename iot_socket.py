import serial
import serial.tools.list_ports
import time
ser = None
last_update_time = 0

def auto_connect():
    global ser
    # Nếu đã kết nối rồi thì không làm gì cả
    if ser is not None and ser.is_open:
        return True
        
    try:
        # Tự động quét tất cả các cổng USB đang cắm
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            print("!!! [CỔNG COM]: Không tìm thấy thiết bị nào cắm vào máy tính. Hãy kiểm tra cáp!")
            return False
            
        for port in ports:
            print(f"--- Đang thử bẻ khóa cổng: {port.device} ---")
            try:
                # Thử kết nối với tốc độ 9600
                ser = serial.Serial(port.device, 9600, timeout=1)
                print(f"=== KẾT NỐI THÀNH CÔNG VỚI CHẬU CÂY TẠI {port.device} ===")
                time.sleep(2) # Cho ESP32 2 giây để hoàn hồn sau khi mở cổng
                return True
            except Exception as e:
                # Nếu cổng này bị khóa, báo lỗi chi tiết và thử cổng tiếp theo
                print(f"    [X] Thất bại tại {port.device} (Lý do: {e})")
                
        return False
    except Exception as e:
        print(f"Lỗi hệ thống dò cổng: {e}")
        return False
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

# ser = serial.Serial('COM5', 9600, timeout=1)
last_update_time = 0


'''def auto_connect():
    """Tự động quét và kết nối với mọi mạch ESP32/Arduino (Plug & Play)"""
    global ser
    if ser is not None and ser.is_open:
        return True
        
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        # Bắt các từ khóa thông dụng của ESP32 và Arduino
        if "USB" in port.description or "CH340" in port.description or "CP210" in port.description or "Serial" in port.description:
            try:
                # ÉP BUỘC Baudrate 115200 để khớp với ESP32
                ser = serial.Serial(port.device, baudrate=9600, timeout=1)
                print(f"[THÀNH CÔNG] Đã kết nối ESP32 tại cổng: {port.device}")
                return True
            except Exception as e:
                print(f"[LỖI] Tìm thấy {port.device} nhưng không thể mở: {e}")
                
    print("[CẢNH BÁO] Không tìm thấy chậu cây nào được cắm vào máy tính!")
    return False'''


def update_data():
    global ser, last_update_time
    global sensor_cache, history_cache, streak_cache
    
    current_time = time.time()
    
    # 1. BẬT LẠI DÒNG NÀY ĐỂ XEM TIM CÓ ĐẬP KHÔNG
    print(f"[NHỊP TIM]: Đang kiểm tra cổng COM... (Cách lần trước {current_time - last_update_time:.1f}s)")
    
    if current_time - last_update_time >= 2: 
        # Kiểm tra xem có qua được cửa ải Auto Connect không
        if auto_connect():
            try:
                # Kiểm tra xem có giọt dữ liệu nào không
                if ser.in_waiting > 0:
                    raw_data = ser.readline().decode('utf-8').strip()
                    print(f">>> [PHẦN CỨNG] BẮT ĐƯỢC GÓI TIN: '{raw_data}'")
                    
                    if raw_data:
                        values = raw_data.split(',')
                        if len(values) == 4:
                            sensor_cache["light_lux"] = values[0]
                            sensor_cache["air_humidity"] = values[1]
                            sensor_cache["soil_moisture"] = values[2]
                            sensor_cache["touch_sensor"] = values[3]
                            
                            try:
                                l_val = float(values[0])
                                m_val = float(values[2])
                                history_cache["light_history"].pop(0)
                                history_cache["light_history"].append(l_val)
                                history_cache["moisture_history"].pop(0)
                                history_cache["moisture_history"].append(m_val)
                            except ValueError:
                                pass 
                            
                            last_update_time = current_time
                        else:
                            print(f"    [!] Bỏ qua gói tin thiếu tham số: {raw_data}")
                else:
                    # NẾU CỔNG MỞ MÀ KHÔNG CÓ DỮ LIỆU, IN RA DÒNG NÀY
                    print("--- [CỔNG COM]: Đã kết nối, đang há miệng chờ ESP32 nhưng không thấy gì dội lên!")
                            
            except Exception as e:
                print(f"Lỗi xử lý luồng dữ liệu: {e}")
        else:
            # NẾU KHÔNG KẾT NỐI ĐƯỢC, IN RA DÒNG NÀY
            print("!!! [LỖI]: auto_connect() thất bại, không thể mở cổng!")

def send_command(command):
    """Gửi lệnh điều khiển hoặc ngưỡng dữ liệu xuống ESP32"""
    global ser
    # Kiểm tra xem cổng Serial có đang mở không
    if ser and ser.is_open:
        try:
            # Gửi chuỗi lệnh kèm ký tự xuống dòng \n để ESP32 nhận biết kết thúc lệnh
            full_command = f"{command}\n"
            ser.write(full_command.encode('utf-8'))
            print(f"--- [PYTHON -> ESP32]: Đã gửi lệnh: {command} ---")
            return True
        except Exception as e:
            print(f"Lỗi khi gửi dữ liệu xuống phần cứng: {e}")
    else:
        print("Cảnh báo: Chưa kết nối ESP32, lệnh không thể gửi.")
    return False

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