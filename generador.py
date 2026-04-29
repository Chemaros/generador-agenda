import tkinter as tk
from tkinter import messagebox
from html2image import Html2Image
import base64
import os

class AgendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Agenda - PSOE Salamanca")
        self.eventos_datos = []
        
        # --- Campos de la Agenda ---
        tk.Label(root, text="Fecha de la Agenda (ej: MIÉRCOLES, 29 DE ABRIL):").pack(pady=5)
        self.ent_fecha = tk.Entry(root, width=50)
        self.ent_fecha.pack(pady=5)
        
        tk.Label(root, text="Número de eventos:").pack(pady=5)
        self.ent_num = tk.Entry(root, width=10)
        self.ent_num.pack(pady=5)
        
        # Botón para crear los campos de texto
        tk.Button(root, text="Configurar Eventos", command=self.crear_campos_eventos).pack(pady=10)
        
        # Contenedor para scroll si hay muchos eventos
        self.frame_eventos = tk.Frame(root)
        self.frame_eventos.pack()

    def crear_campos_eventos(self):
        # Limpiar campos previos
        for widget in self.frame_eventos.winfo_children():
            widget.destroy()
        self.eventos_inputs = []
        
        try:
            n = int(self.ent_num.get())
        except:
            messagebox.showerror("Error", "Introduce un número válido")
            return

        for i in range(n):
            frame = tk.LabelFrame(self.frame_eventos, text=f"Evento {i+1}")
            frame.pack(pady=5, fill="x")
            
            tk.Label(frame, text="Hora y Título (Rojo):").grid(row=0, column=0)
            h = tk.Entry(frame, width=40)
            h.grid(row=0, column=1)
            
            tk.Label(frame, text="Descripción (Gris):").grid(row=1, column=0)
            d = tk.Text(frame, width=40, height=3)
            d.grid(row=1, column=1)
            
            tk.Label(frame, text="Lugar (Negrita):").grid(row=2, column=0)
            l = tk.Entry(frame, width=40)
            l.grid(row=2, column=1)
            
            self.eventos_inputs.append((h, d, l))
            
        tk.Button(self.root, text="Generar JPG", command=self.generar_imagen, bg="red", fg="white").pack(pady=20)

    def generar_imagen(self):
        fecha = self.ent_fecha.get().upper()
        html_eventos = ""
        
        # --- Carga automática del logo ---
        etiqueta_logo = ""
        nombre_archivo_logo = "logo.png" 
        
        if os.path.exists(nombre_archivo_logo):
            try:
                with open(nombre_archivo_logo, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                    etiqueta_logo = f'<img src="data:image/png;base64,{encoded_string}" style="max-width: 150px; margin-bottom: 10px;"><br>'
            except Exception as e:
                print("No se pudo cargar el logo:", e)

        # Construir el HTML de cada evento
        for h, d, l in self.eventos_inputs:
            # La hora y título siguen forzándose a mayúsculas
            hora_titulo = h.get().upper()
            
            # La descripción respeta el formato original
            desc = d.get("1.0", tk.END).strip()
            
            # --- CAMBIO REALIZADO AQUÍ ---
            # Se ha eliminado el .upper() para respetar mayúsculas y minúsculas originales en el Lugar
            lugar = l.get().strip()
            
            html_eventos += f"""
            <div class="evento">
                <div class="hora-titulo">{hora_titulo}</div>
                <div class="descripcion">{desc}</div>
                <div class="lugar">LUGAR: <strong>{lugar}</strong></div>
            </div>
            """

        # Plantilla CSS actualizada
        html_completo = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; width: 800px; margin: 0; padding: 0; text-align: center; background-color: #FFFFFF; }}
                .header {{ background-color: #e30613; color: white; padding: 20px; font-size: 28px; font-weight: bold; }}
                .container {{ padding: 40px; }}
                .evento {{ margin-bottom: 40px; }}
                .hora-titulo {{ color: #e30613; font-size: 22px; margin-bottom: 5px; font-weight: bold; }}
                .descripcion {{ color: #707070; font-size: 20px; margin-bottom: 5px; }}
                .lugar {{ color: #000; font-size: 18px; }}
                .footer {{ border-top: 2px solid #e30613; margin-top: 50px; padding: 20px; display: flex; justify-content: space-around; align-items: flex-end; background-color: #FFFFFF; }}
                .bloque-izquierdo {{ text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">AGENDA {fecha} DE 2026</div>
            <div class="container">
                {html_eventos}
            </div>
            <div class="footer">
                <div class="bloque-izquierdo">
                    {etiqueta_logo}
                    <div style="color: #e30613; font-weight: bold;">socialistasdesalamanca.es</div>
                </div>
                <div style="font-size: 24px; font-weight: bold; color: #e30613;">IMPULSANDO la Salamanca del Futuro</div>
            </div>
        </body>
        </html>
        """
        
        # Convertir HTML a Imagen JPG
        hti = Html2Image(custom_flags=['--no-sandbox', '--disable-gpu'])
        hti.screenshot(html_str=html_completo, save_as='agenda_generada.jpg', size=(800, 1200))
        messagebox.showinfo("Éxito", "Imagen 'agenda_generada.jpg' creada correctamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AgendaApp(root)
    root.mainloop()