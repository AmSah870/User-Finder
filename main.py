import tkinter as tk
from tkinter import messagebox
import requests
import json
import os
from PIL import Image, ImageTk
from io import BytesIO

FILE_NAME = "favorites.json"
BG_COLOR = "#0d1117"
TEXT_COLOR = "#c9d1d9"
ACCENT_COLOR = "#58a6ff"
BTN_COLOR = "#238636"

class GitHubFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder & Favorites")
        self.root.geometry("800x650")
        self.root.config(bg=BG_COLOR)
        
        self.current_user_data = None
        self.setup_ui()
        self.load_favorites_from_file()

    def setup_ui(self):
        self.left_frame = tk.Frame(self.root, bg=BG_COLOR, padx=20)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(self.left_frame, text="GitHub Finder", font=("Arial", 20, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=10)

        self.entry = tk.Entry(self.left_frame, font=("Arial", 14), bg="#161b22", fg="white", insertbackground="white")
        self.entry.pack(pady=5, fill=tk.X)

        search_btn = tk.Button(self.left_frame, text="Find User", bg=BTN_COLOR, fg="white", command=self.find_user)
        search_btn.pack(pady=5, fill=tk.X)

        self.avatar_label = tk.Label(self.left_frame, bg=BG_COLOR)
        self.avatar_label.pack(pady=10)

        self.info_label = tk.Label(self.left_frame, text="", font=("Arial", 12), fg=TEXT_COLOR, bg=BG_COLOR, justify="left")
        self.info_label.pack(pady=10)

        self.fav_btn = tk.Button(self.left_frame, text="⭐ Add to Favorites", bg="#21262d", fg=ACCENT_COLOR, state=tk.DISABLED, command=self.add_to_favorites)
        self.fav_btn.pack(pady=5, fill=tk.X)

        self.right_frame = tk.Frame(self.root, bg="#161b22", padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.right_frame, text="Favorites", font=("Arial", 14, "bold"), fg=TEXT_COLOR, bg="#161b22").pack()
        
        self.fav_listbox = tk.Listbox(self.right_frame, width=30, height=25, bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 10))
        self.fav_listbox.pack(pady=10)

    def find_user(self):
        username = self.entry.get().strip()
        if not username:
            messagebox.showwarning("Внимание", "Поле ввода не должно быть пустым!")
            return

        try:
            response = requests.get(f"https://api.github.com/users/{username}")
            if response.status_code != 200:
                messagebox.showerror("Ошибка", "Пользователь не найден")
                return

            data = response.json()
            self.current_user_data = data
            self.display_user(data)
            self.fav_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Проблема с сетью: {e}")

    def display_user(self, data):
        img_res = requests.get(data['avatar_url'])
        img = Image.open(BytesIO(img_res.content)).resize((120, 120))
        photo = ImageTk.PhotoImage(img)
        self.avatar_label.config(image=photo)
        self.avatar_label.image = photo

        info = f"Name: {data.get('name') or 'N/A'}\n" \
               f"Login: {data['login']}\n" \
               f"Repos: {data['public_repos']}\n" \
               f"Followers: {data['followers']}"
        self.info_label.config(text=info)

    def add_to_favorites(self):
        if not self.current_user_data:
            return

        login = self.current_user_data['login']

        existing = self.fav_listbox.get(0, tk.END)
        if login in existing:
            messagebox.showinfo("Инфо", "Пользователь уже в избранном")
            return

        self.fav_listbox.insert(tk.END, login)
        self.save_to_json(self.current_user_data)

    def save_to_json(self, user_data):
        favorites = []
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                favorites = json.load(f)

        favorites.append({
            "login": user_data['login'],
            "name": user_data.get('name'),
            "url": user_data['html_url']
        })

        with open(FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(favorites, f, indent=4, ensure_ascii=False)

    def load_favorites_from_file(self):
        if os.path.exists(FILE_NAME):
            try:
                with open(FILE_NAME, "r", encoding="utf-8") as f:
                    favorites = json.load(f)
                    for user in favorites:
                        self.fav_listbox.insert(tk.END, user['login'])
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubFinder(root)
    root.mainloop()