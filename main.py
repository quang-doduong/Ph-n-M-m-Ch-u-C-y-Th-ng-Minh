# main.py
import customtkinter as ctk
from pages import LoginPage, GroupInfoPage, DashboardPage, EditPlantPage

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("green") 

class SmartPotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart Plant Pot - IOT Dashboard")
        self.geometry("900x600")
        self.minsize(800, 500)

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

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = SmartPotApp()
    app.mainloop()