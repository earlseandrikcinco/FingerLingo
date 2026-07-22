import customtkinter as ctk

ctk.set_appearance_mode("dark") #dark mode ata to HAAHAHA
ctk.set_default_color_theme("blue")

app = ctk.CTk()

app.title("FingerLingo")
app.geometry("1000,1000")

label = ctk.CTkLabel(app, text="Welcome to FingerLingo", font=("Roboto", 20))
label.pack(padx=20,pady=20) 

button = ctk.CTkButton(app, text="Let's Learn", command=lambda: print("ts where the magic happens twin"))
button.pack(padx=20,pady=20)

app.mainloop()