import streamlit as st
from html2image import Html2Image
import base64
import zipfile
import io

# 1. Configuración básica de la página web
st.set_page_config(page_title="Generador de Agenda", page_icon="📅")

st.title("Generador de Agenda - PSOE Salamanca")
st.write("Rellena el formulario a continuación para generar la imagen de la agenda.")

# 2. Creamos el formulario web
with st.form("formulario_agenda"):
    st.subheader("Datos Generales")
    fecha = st.text_input("Fecha de la Agenda (ej: MIÉRCOLES, 29 DE ABRIL):")
    
    # Campo para subir el logo
    logo_file = st.file_uploader("Subir logo opcional (PNG o JPG):", type=["png", "jpg", "jpeg"])
    
    col_a, col_b = st.columns(2)
    with col_a:
        num_eventos = st.number_input("Número total de eventos:", min_value=1, value=1, step=1)
    with col_b:
        # NUEVO: Control para decidir cuántos eventos caben en una sola imagen
        eventos_por_pag = st.number_input("Eventos por página (para no cortar la imagen):", min_value=1, value=4, step=1)
    
    st.subheader("Detalles de los Eventos")
    eventos_datos = []
    
    # Generamos los campos de texto
    for i in range(int(num_eventos)):
        st.markdown(f"**Evento {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            hora_titulo = st.text_input(f"Hora y Título (Rojo)", key=f"hora_{i}")
            lugar = st.text_input(f"Lugar (Negrita)", key=f"lugar_{i}")
        with col2:
            desc = st.text_area(f"Descripción (Gris)", height=100, key=f"desc_{i}")
        
        eventos_datos.append({
            "hora": hora_titulo,
            "desc": desc,
            "lugar": lugar
        })
        st.markdown("---")
    
    submit_button = st.form_submit_button("Generar Imágenes JPG")

# 3. Lógica que se ejecuta al pulsar el botón
if submit_button:
    with st.spinner("Maquetando y generando las imágenes..."):
        fecha_texto = fecha.upper()
        
        # Procesar el logo
        etiqueta_logo = ""
        if logo_file is not None:
            encoded_string = base64.b64encode(logo_file.read()).decode()
            etiqueta_logo = f'<img src="data:image/png;base64,{encoded_string}" style="max-width: 150px; margin-bottom: 10px;"><br>'

        # NUEVO: Dividir la lista total de eventos en "páginas" o "trozos"
        # Esto crea una lista de listas. Ej: si hay 10 eventos y caben 4 por pag -> [[4], [4], [2]]
        paginas_de_eventos = [eventos_datos[i:i + int(eventos_por_pag)] for i in range(0, len(eventos_datos), int(eventos_por_pag))]

        # Preparar la herramienta de captura de imágenes
        hti = Html2Image(custom_flags=['--no-sandbox', '--disable-gpu'])
        
        # NUEVO: Crear un "archivo ZIP" virtual en la memoria del servidor
        archivo_zip_en_memoria = io.BytesIO()
        
        # Abrimos ese ZIP para empezar a meterle las fotos
        with zipfile.ZipFile(archivo_zip_en_memoria, "w") as zip_file:
            
            # Repetimos el proceso por cada página que hayamos creado
            for indice_pag, pagina_actual in enumerate(paginas_de_eventos):
                html_eventos = ""
                
                # Procesar los eventos solo de esta página
                for ev in pagina_actual:
                    h = ev["hora"].upper()
                    d = ev["desc"].strip()  
                    l = ev["lugar"].strip() 
                    
                    html_eventos += f"""
                    <div class="evento">
                        <div class="hora-titulo">{h}</div>
                        <div class="descripcion">{d}</div>
                        <div class="lugar">LUGAR: <strong>{l}</strong></div>
                    </div>
                    """

                # Plantilla HTML/CSS (se genera una por cada página)
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
                    <!-- Añadimos (Pág X) al título si hay más de una página -->
                    <div class="header">AGENDA {fecha_texto} DE 2026 {f'(PÁG {indice_pag + 1})' if len(paginas_de_eventos) > 1 else ''}</div>
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
                
                # Nombre único para cada imagen generada
                ruta_salida = f'agenda_pag_{indice_pag + 1}.jpg'
                
                # Tomar la foto a esta página
                hti.screenshot(html_str=html_completo, save_as=ruta_salida, size=(800, 1200))
                
                # Leer la foto y guardarla dentro del archivo ZIP
                with open(ruta_salida, "rb") as file:
                    zip_file.writestr(ruta_salida, file.read())
                    
    st.success("¡Imágenes generadas correctamente! Usa el botón de abajo para guardarlas.")
    
    # 4. Botón para descargar el archivo ZIP con todas las imágenes
    st.download_button(
        label="📥 Descargar Agendas (Archivo ZIP)",
        data=archivo_zip_en_memoria.getvalue(),
        file_name="agendas_generadas.zip",
        mime="application/zip"
    )
