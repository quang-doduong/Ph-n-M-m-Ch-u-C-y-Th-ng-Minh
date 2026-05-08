# main.py
import customtkinter as ctk
from pages import LoginPage, GroupInfoPage, DashboardPage, EditPlantPage
import iot_socket

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("green") 

class SmartPotApp(ctk.CTk):
    def __init__(self):

        super().__init__()
        self.title("Smart Plant Pot - IOT Dashboard")
        self.geometry("900x600")
        self.minsize(800, 500)

        self.continuous_update() # mới cập nhật

        self.shared_data = {
            "selected_plant": None,
            "plant_info": {}
        }


        # --- BỘ NHỚ TRUNG TÂM (Thêm mới) ---
        self.current_plant_name = "Chưa chọn cây"
        self.current_plant_info = {"DoAm": "--", "AnhSang": "--", "MucNuoc": "--", "ThoiGianKiemTra": "--"}

        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (LoginPage, GroupInfoPage, DashboardPage, EditPlantPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def continuous_update(self):
        # 1. Ép hệ thống chọc vào cổng COM để đọc dữ liệu mới nhất
        iot_socket.update_data()
        
        # 2. Nếu đang ở trang Dashboard, ép nó vẽ lại các biểu đồ và nhãn số
        if hasattr(self, 'frames') and "DashboardPage" in self.frames:
            try:
                # Gọi hàm cập nhật hiển thị mà chúng ta đã làm ở các bước trước
                self.frames["DashboardPage"].update_display()
            except Exception:
                pass # Bỏ qua nếu trang chưa sẵn sàng, chống sập App
                
        # 3. ĐÂY LÀ PHÉP MÀU: Hẹn giờ đúng 2 giây (2000ms) sau, tự động chạy lại chính hàm này!
        self.after(2000, self.continuous_update)
        
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "update_display"):
            print(f"--- TRẠM 1: Đã gọi update_display cho {page_name} ---") # THÊM DÒNG NÀY
            frame.update_display()
if __name__ == "__main__":
    app = SmartPotApp()
    app.mainloop()