import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Listbox, Scrollbar, END
import random
from datetime import datetime, timedelta


class VocabularyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LingvaMaster 🎯")
        self.root.geometry("1000x700")
        self.root.configure(bg="#F5F7FA")

        # Stil ayarları
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#F5F7FA")
        self.style.configure("TButton", font=("Helvetica", 12), padding=10, borderwidth=0)
        self.style.map("TButton",
                       background=[("active", "#4A90E2"), ("!active", "#5E5CED")],
                       foreground=[("active", "white"), ("!active", "white")]
                       )
        self.style.configure("TLabel", background="#F5F7FA", font=("Helvetica", 14))
        self.style.configure("Correct.TButton", background="#C8E6C9", foreground="#1B5E20")
        self.style.configure("Wrong.TButton", background="#FFCDD2", foreground="#B71C1C")
        self.style.configure("Result.TFrame", background="#F5F7FA")

        # Veri yapıları
        self.words = []
        self.load_words()
        self.today_stats = {"correct": 0, "wrong": 0, "completed": False}
        self.streak_days = 0
        self.total_score = 0
        self.load_progress()
        self.load_score()
        self.calculate_streak()

        # Ana arayüz
        self.create_main_frame()
        self.update_progress_display()
        self.update_word_list()

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)

        # Ana Başlık
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(pady=10)

        title_label = ttk.Label(title_frame,
                                text="📚 LingvaMaster",
                                font=("Helvetica", 24, "bold"))
        title_label.pack()

        # Bilgi Çubuğu (Günlük Seri + Puan)
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=5)

        # Günlük Seri (Sol)
        self.streak_label = ttk.Label(header_frame,
                                      text="",
                                      font=("Helvetica", 12, "bold"),
                                      foreground="#FFA500")
        self.streak_label.pack(side=tk.LEFT, padx=10)

        # Puan (Sağ)
        self.score_label = ttk.Label(header_frame,
                                     text=f"🏆 Toplam Puan: {self.total_score}",
                                     font=("Helvetica", 14, "bold"),
                                     foreground="#5E5CED")
        self.score_label.pack(side=tk.RIGHT, padx=20)

        # İlerleme paneli
        self.progress_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.progress_frame.pack(pady=10, fill=tk.X)

        # Kontrol butonları
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="➕ Kelime Ekle", command=self.add_word).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="➖ Kelime Sil", command=self.remove_word).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="🚀 Teste Başla", command=self.start_quiz).pack(side=tk.LEFT, padx=10)

        # Kelime Listesi
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        list_header = ttk.Label(list_frame,
                                text="📖 Kelime Havuzu 📖",
                                font=("Helvetica", 16, "bold"),
                                foreground="#2E86C1",
                                anchor="center")
        list_header.pack(fill=tk.X, pady=5)

        self.listbox = Listbox(list_frame,
                               font=("Helvetica", 12),
                               bg="white",
                               relief=tk.FLAT,
                               selectbackground="#E3F2FD",
                               selectforeground="black",
                               activestyle="none",
                               borderwidth=2,
                               highlightthickness=0)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipadx=10, ipady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bilgileri güncelle
        self.update_streak_display()
        self.update_score_display()

    def load_words(self):
        try:
            with open("kelimeler.txt", "r", encoding="utf-8") as f:
                self.words = [line.strip().split(":") for line in f.readlines()]
        except FileNotFoundError:
            self.words = []

    def update_streak_display(self):
        streak_info = ""
        emoji = "🔥"
        if self.streak_days >= 3:
            emoji = "🥉 Bronz"
        if self.streak_days >= 7:
            emoji = "🥈 Gümüş"
        if self.streak_days >= 14:
            emoji = "🥇 Altın"
        if self.streak_days >= 30:
            emoji = "💎 Platin"

        streak_info = f"{emoji} {self.streak_days} Günlük Seri!"
        self.streak_label.config(
            text=streak_info,
            foreground="#FFA500",  # Turuncu renk kodu
            font=("Helvetica", 12, "bold")  # Kalın yazı stili
        )

    def update_score_display(self):
        self.score_label.config(text=f"🏆 Toplam Puan: {self.total_score}")

    def calculate_streak(self):
        try:
            with open("ilerleme.txt", "r", encoding="utf-8") as f:
                dates = [line.split(",")[0] for line in f.readlines()]
                dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
                dates.sort(reverse=True)

                streak = 0
                current_date = datetime.now().date()
                for d in dates:
                    if d.date() == current_date - timedelta(days=streak):
                        streak += 1
                    else:
                        break
                self.streak_days = streak
        except FileNotFoundError:
            self.streak_days = 0

    def load_score(self):
        try:
            with open("puan.txt", "r", encoding="utf-8") as f:
                self.total_score = int(f.read())
        except FileNotFoundError:
            self.total_score = 0

    def save_score(self):
        with open("puan.txt", "w", encoding="utf-8") as f:
            f.write(str(self.total_score))

    def add_score(self, points):
        self.total_score += points
        self.save_score()
        self.update_score_display()

    def update_word_list(self):
        self.listbox.delete(0, END)
        for word in self.words:
            self.listbox.insert(END, f"{word[0].capitalize():<20} →             {word[1].capitalize()}")

    def update_progress_display(self):
        for widget in self.progress_frame.winfo_children():
            widget.destroy()

        progress_text = f"📅 Günlük İlerleme: {self.today_stats['correct'] + self.today_stats['wrong']}/100\n\n"
        progress_text += f"✅ Doğru: {self.today_stats['correct']}   ❌ Yanlış: {self.today_stats['wrong']}"

        status_label = ttk.Label(self.progress_frame, text=progress_text, font=("Helvetica", 16))
        status_label.pack(pady=15)

        if self.today_stats["completed"]:
            ttk.Label(self.progress_frame, text="🎉 Bugünkü hedef tamamlandı!", foreground="#2ECC71").pack()

    def save_words(self):
        with open("kelimeler.txt", "w", encoding="utf-8") as f:
            for word in self.words:
                f.write(f"{word[0]}:{word[1]}\n")
        self.update_word_list()

    def load_progress(self):
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            with open("ilerleme.txt", "r", encoding="utf-8") as f:
                for line in f.readlines():
                    date, correct, wrong = line.strip().split(",")
                    if date == today:
                        self.today_stats = {
                            "correct": int(correct),
                            "wrong": int(wrong),
                            "completed": (int(correct) + int(wrong)) >= 100
                        }
        except FileNotFoundError:
            pass

    def save_progress(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with open("ilerleme.txt", "a", encoding="utf-8") as f:
            f.write(f"{today},{self.today_stats['correct']},{self.today_stats['wrong']}\n")
        self.calculate_streak()
        self.update_streak_display()

    def add_word(self):
        english = simpledialog.askstring("Kelime Ekle", "İngilizce kelime:")
        turkish = simpledialog.askstring("Kelime Ekle", "Türkçe karşılığı:")
        if english and turkish:
            self.words.append([english.strip().lower(), turkish.strip().lower()])
            self.save_words()
            messagebox.showinfo("Başarılı", "Kelime başarıyla eklendi! 📥")

    def remove_word(self):
        if not self.words:
            messagebox.showwarning("Uyarı", "Kelime havuzu boş! ❗")
            return

        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            del self.words[index]
            self.save_words()
            messagebox.showinfo("Başarılı", "Kelime başarıyla silindi! 📭")
        else:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kelime seçin! ⚠️")

    def start_quiz(self):
        if len(self.words) < 4:
            messagebox.showwarning("Uyarı", "En az 4 kelime eklemelisiniz! ⚠️")
            return

        if self.today_stats["completed"]:
            messagebox.showinfo("Bilgi", "Bugünkü hedef zaten tamamlandı! 🎉")
            return

        self.quiz_window = tk.Toplevel(self.root)
        self.quiz_window.title("Test 🧠")
        self.quiz_window.geometry("600x400")
        self.quiz_window.configure(bg="#F5F7FA")

        self.current_question = 0
        self.correct_answer = ""
        self.setup_question()

    def setup_question(self):
        for widget in self.quiz_window.winfo_children():
            widget.destroy()

        answered = self.today_stats["correct"] + self.today_stats["wrong"]
        if answered >= 100:
            self.today_stats["completed"] = True
            self.save_progress()
            self.update_progress_display()
            ttk.Label(self.quiz_window,
                      text="🎉 Test tamamlandı! Tebrikler! 🎉",
                      font=("Helvetica", 20)).pack(pady=100)
            return

        # Soru bilgilerini hesapla
        current_q_number = answered + 1
        remaining = 100 - current_q_number

        # Rastgele kelime seç
        self.current_word = random.choice(self.words)
        self.correct_answer = self.current_word[1]

        # Yanlış seçenekler
        wrong_answers = random.sample(
            [w[1] for w in self.words if w[1] != self.correct_answer],
            min(3, len(self.words) - 1)
        )

        self.options = wrong_answers + [self.correct_answer]
        random.shuffle(self.options)

        # Soru arayüzü
        self.quiz_frame = ttk.Frame(self.quiz_window)
        self.quiz_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # Soru bilgisi başlığı
        progress_text = f"📝 Soru {current_q_number}/100 (Kalan: {remaining})"
        ttk.Label(self.quiz_frame,
                  text=progress_text,
                  font=("Helvetica", 14, "bold"),
                  foreground="#5E5CED").pack(pady=10)

        ttk.Label(self.quiz_frame,
                  text=f"{self.current_word[0]}",
                  font=("Helvetica", 24, "bold")).pack(pady=20)

        self.answer_buttons = []
        for option in self.options:
            btn = ttk.Button(self.quiz_frame,
                             text=option,
                             command=lambda o=option: self.check_answer(o))
            btn.pack(pady=5, fill=tk.X, padx=50)
            self.answer_buttons.append(btn)

        # Sonuç gösterimi ve ilerleme butonu
        self.result_label = ttk.Label(self.quiz_frame,
                                      text="",
                                      font=("Helvetica", 16))
        self.result_label.pack(pady=15)

        self.next_button = ttk.Button(self.quiz_frame,
                                      text="⏭️ Sonraki Soru",
                                      command=self.next_question,
                                      state=tk.DISABLED)
        self.next_button.pack(pady=10)

    def check_answer(self, selected):
        # Tüm butonları devre dışı bırak
        for btn in self.answer_buttons:
            btn.state(['disabled'])

        # Puan hesapla
        if selected == self.correct_answer:
            self.today_stats["correct"] += 1
            result_text = "🎉 Doğru Cevap! Harikasın! 🎉"
            bg_color = "#E8F5E9"
            self.add_score(2)
        else:
            self.today_stats["wrong"] += 1
            result_text = f"❌ Yanlış Cevap! Doğrusu: {self.correct_answer}"
            bg_color = "#FFEBEE"

        # Günlük hedef kontrolü
        if (self.today_stats["correct"] + self.today_stats["wrong"]) >= 100:
            bonus = 0
            if self.streak_days >= 30:
                bonus = 150
            elif self.streak_days >= 14:
                bonus = 100
            elif self.streak_days >= 7:
                bonus = 50
            elif self.streak_days >= 3:
                bonus = 25

            if bonus > 0:
                self.add_score(bonus)
                messagebox.showinfo("Tebrikler!", f"Günlük hedef tamamlandı! +{bonus} puan kazandınız! 🎉")

        # Sonuç gösterme
        self.result_label.config(text=result_text, background=bg_color)
        self.next_button.state(['!disabled'])
        self.quiz_frame.config(style="Result.TFrame")

        # Doğru cevabı vurgula
        for btn in self.answer_buttons:
            if btn['text'] == self.correct_answer:
                btn.config(style="Correct.TButton")
            elif btn['text'] == selected:
                btn.config(style="Wrong.TButton")

    def next_question(self):
        self.current_question += 1
        self.save_progress()
        self.update_progress_display()
        self.setup_question()


if __name__ == "__main__":
    root = tk.Tk()
    app = VocabularyApp(root)
    root.mainloop()