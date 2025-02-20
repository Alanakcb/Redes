import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

HOST = '127.0.0.1'
PORT = 5555


class QuizClient:
    def __init__(self, root):
        self.root = root
        self.root.title("QuizBattle - Cliente")

        self.chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15, state=tk.DISABLED)
        self.chat_box.pack(pady=10)

        self.entry = tk.Entry(root, width=40)
        self.entry.pack(pady=5)

        self.send_button = tk.Button(root, text="Enviar", command=self.send_message)
        self.send_button.pack()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar ao servidor: {e}")
            root.quit()
            return

        self.ask_name()

        self.running = True
        threading.Thread(target=self.listen_server, daemon=True).start()

    def ask_name(self):
        name = simpledialog.askstring("Nome", "Digite seu nome:")
        if not name:
            messagebox.showwarning("Aviso", "Nome não pode ser vazio!")
            self.root.quit()
            return

        try:
            self.client.sendall(name.encode())
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar nome: {e}")
            self.root.quit()

    def listen_server(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode()
                if not message:
                    break
                self.update_chat(message)
            except Exception:
                self.update_chat("[Conexão perdida com o servidor]")
                self.running = False
                break

    def update_chat(self, message):
        self.root.after(0, self._safe_update_chat, message)

    def _safe_update_chat(self, message):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, message + "\n")
        self.chat_box.config(state=tk.DISABLED)
        self.chat_box.yview(tk.END)

    def send_message(self):
        message = self.entry.get().strip()
        if message:
            try:
                self.client.sendall(message.encode())
                self.entry.delete(0, tk.END)
            except Exception as e:
                self.update_chat(f"[Erro ao enviar mensagem] {e}")
                self.running = False


if __name__ == "__main__":
    root = tk.Tk()
    client = QuizClient(root)
    root.mainloop()
