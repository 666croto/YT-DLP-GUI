import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


class YtDlpApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Mi YT-DLP GUI con Terminal")
    self.root.geometry("600x500")
    self.root.resizable(False, False)

    self.download_path = os.path.expanduser("~")

    # 1. URL
    tk.Label(root, text="Enlace de YouTube (Video o Playlist):").pack(
        anchor="w", padx=20, pady=(15, 5)
    )
    self.url_entry = tk.Entry(root, width=70)
    self.url_entry.pack(padx=20, pady=5)

    # 2. Carpeta de destino
    folder_frame = tk.Frame(root)
    folder_frame.pack(fill="x", padx=20, pady=10)

    tk.Label(folder_frame, text="Carpeta de destino:").pack(side="left")
    self.path_label = tk.Label(
        folder_frame, text=self.download_path, fg="gray", width=45, anchor="w"
    )
    self.path_label.pack(side="left", padx=10)

    btn_browse = tk.Button(
        folder_frame, text="Examinar", command=self.select_folder
    )
    btn_browse.pack(side="right")

    # 3. Botón de descarga
    self.btn_download = tk.Button(
        root,
        text="Descargar en MP3",
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        command=self.start_download_thread,
    )
    self.btn_download.pack(pady=10)

    # 4. Consola / Terminal visual
    tk.Label(root, text="Salida de la terminal:").pack(
        anchor="w", padx=20, pady=(5, 0)
    )
    self.terminal_box = scrolledtext.ScrolledText(
        root, width=70, height=12, bg="black", fg="lightgreen", font=("Consolas", 9)
    )
    self.terminal_box.pack(padx=20, pady=5)

    # 5. Estado
    self.status_label = tk.Label(root, text="Estado: Esperando enlace...", fg="blue")
    self.status_label.pack(pady=5)

  def select_folder(self):
    folder = filedialog.askdirectory()
    if folder:
      self.download_path = folder
      self.path_label.config(text=folder)

  def start_download_thread(self):
    url = self.url_entry.get().strip()
    if not url:
      messagebox.showerror("Error", "Por favor ingresa un enlace válido.")
      return

    self.btn_download.config(state="disabled")
    self.terminal_box.delete("1.0", tk.END)  # Limpiar terminal anterior
    self.status_label.config(text="Estado: Descargando y convirtiendo a MP3...")

    thread = threading.Thread(target=self.run_ytdlp, args=(url,))
    thread.start()

  def run_ytdlp(self, url):
    try:
      command = [
          "yt-dlp",
          "-x",
          "--audio-format",
          "mp3",
          "--audio-quality",
          "0",
          "-P",
          self.download_path,
          url,
      ]

      process = subprocess.Popen(
          command,
          stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT,
          universal_newlines=True,
          encoding="utf-8",
          errors="ignore",
      )

      # Leer la salida línea por línea e insertarla en la terminal visual
      for line in process.stdout:
        self.root.after(0, self.update_terminal, line)

      process.wait()

      if process.returncode == 0:
        self.root.after(
            0,
            lambda: messagebox.showinfo(
                "Éxito", "¡Descarga completada con éxito!"
            ),
        )
        self.root.after(
            0,
            lambda: self.status_label.config(
                text="Estado: Descarga finalizada."
            ),
        )
      else:
        raise Exception("El comando terminó con un código de error.")

    except Exception as e:
      self.root.after(
          0,
          lambda: messagebox.showerror(
              "Error", f"Ocurrió un error durante la descarga:\n{e}"
          ),
      )
      self.root.after(
          0,
          lambda: self.status_label.config(text="Estado: Error en la descarga."),
      )

    finally:
      self.root.after(
          0, lambda: self.btn_download.config(state="normal")
      )

  def update_terminal(self, text):
    self.terminal_box.insert(tk.END, text)
    self.terminal_box.see(tk.END)  # Auto-scroll hacia abajo


if __name__ == "__main__":
  root = tk.Tk()
  app = YtDlpApp(root)
  root.mainloop()