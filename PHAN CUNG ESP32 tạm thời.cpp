#include <DHT.h>
#include <Preferences.h>

// ================= CẤU HÌNH CHÂN CẮM =================
#define SOIL_PIN 32    // Cảm biến độ ẩm đất (Analog)
#define LDR_PIN 33     // Cảm biến quang trở (Analog)
#define DHT_PIN 13     // Cảm biến DHT11 (Digital)
#define TOUCH_PIN 27   // Cảm biến chạm (Digital)
#define BUZZER_PIN 12  // Còi Buzzer
#define LED_ESP 2      // LED tích hợp trên mạch ESP32

#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);
Preferences prefs;

int plant_threshold = 50; // Ngưỡng độ ẩm lưu trữ
unsigned long last_send = 0;

void setup() {
  Serial.begin(115200); // Chú ý: Python của bạn cũng phải cài baudrate là 115200
  dht.begin();
  
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_ESP, OUTPUT);
  pinMode(TOUCH_PIN, INPUT);

  // Mở "Ký ức" Flash để lấy ngưỡng độ ẩm cũ ra
  prefs.begin("plant_data", false);
  plant_threshold = prefs.getInt("threshold", 50); 
}

void loop() {
  // ================= 1. ĐỌC DỮ LIỆU CẢM BIẾN =================
  int light_val = analogRead(LDR_PIN);
  float hum_val = dht.readHumidity();
  int soil_raw = analogRead(SOIL_PIN);
  int touch_val = digitalRead(TOUCH_PIN);

  // Ép độ ẩm đất về %, giả sử 4095 là khô hoàn toàn, 0 là ngâm nước
  int soil_percent = map(soil_raw, 4095, 0, 0, 100);
  
  // Khống chế số liệu ảo (vượt biên)
  if(soil_percent < 0) soil_percent = 0;
  if(soil_percent > 100) soil_percent = 100;
  if(isnan(hum_val)) hum_val = 0; // Chống sập nếu DHT11 bị lỏng dây

  // ================= 2. GỬI LÊN GIAO DIỆN PYTHON =================
  // ĐÚNG ĐỊNH DẠNG MA: values[0] , values[1] , values[2] , values[3]
  // Ánh sáng , Độ ẩm KK , Độ ẩm đất , Chạm
  if (millis() - last_send > 2000) { // Gửi 2 giây 1 lần để test cho nhanh
    Serial.print(light_val);   Serial.print(",");
    Serial.print(hum_val);     Serial.print(",");
    Serial.print(soil_percent);Serial.print(",");
    Serial.println(touch_val); // Dòng này bắt buộc là println để Python biết đã hết gói tin
    
    last_send = millis();
  }

  // ================= 3. LẮNG NGHE LỆNH TỪ PYTHON (Tự hành) =================
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    
    if (input.startsWith("SET_LIMIT:")) {
      // Bóc tách ngưỡng (VD: SET_LIMIT:20 -> Lấy số 20)
      plant_threshold = input.substring(10).toInt();
      
      // Ghi đè vào bộ nhớ Flash
      prefs.putInt("threshold", plant_threshold); 
      
      // Nháy LED 3 lần để báo "Đã tiếp thu kinh thánh mới"
      for(int i=0; i<3; i++) {
        digitalWrite(LED_ESP, HIGH); delay(100);
        digitalWrite(LED_ESP, LOW); delay(100);
      }
    }
  }

  // ================= 4. PHẢN XẠ KHÔNG ĐIỀU KIỆN (Khi mất kết nối) =================
  // ESP32 vẫn ngầm so sánh với plant_threshold mọi lúc
  if (soil_percent < plant_threshold) {
    digitalWrite(LED_ESP, HIGH); // Bật LED đỏ báo khát nước
  } else {
    digitalWrite(LED_ESP, LOW);
  }
}