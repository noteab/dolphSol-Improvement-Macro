from customtkinter import *
import webbrowser

DEFAULT_FONT = "Segoe UI"
DEFAULT_FONT_BOLD = "Segoe UI Semibold"

class UpdateWindow(CTk):
    def __init__(self, update, current_version, latest_version, is_beta):
        super().__init__()
        self.geometry("260x190")
        
        if is_beta == True:
            self.geometry("500x210")
            self.title("Beta Notice")
            beta_notice_label = CTkLabel(master=self, text="You are using an alpha/beta version of MACRO NAME. Please be advised that this version may be unstable.", font=CTkFont(DEFAULT_FONT, size=17, weight="normal"), wraplength=450).pack()
        
        if update == True:
            self.title("You can update!")
            self.resizable(False, False)

            update_label = CTkLabel(master=self, text=f"You can update!", font=CTkFont(DEFAULT_FONT_BOLD, size=30, weight="bold")).pack()

            h2 = CTkFont(DEFAULT_FONT, size=17, weight="bold")
            current_version_label = CTkLabel(master=self, text=f"Your current version: v{current_version}", font=h2).pack()
            latest_version_label = CTkLabel(master=self, text=f"Latest version: v{latest_version}", font=h2).pack()
            github_link_button = CTkButton(master=self, text="Download", font=h2, command=self.github_link_button_event).pack(pady=10, ipady=20, ipadx=50)

    def github_link_button_event():
        webbrowser.open("https://github.com/noteab/dolphSol-Improvement-Macro/releases/latest")
        exit()