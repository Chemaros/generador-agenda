import streamlit as st
from html2image import Html2Image
import base64

# 1. Configuración básica de la página web
st.set_page_config(page_title="Generador de Agenda", page_icon="📅")

st.title("Generador de Agenda - PSOE Salamanca")
st.write("Rellena el formulario a continuación para generar la imagen de la agenda.")

# 2. Creamos el formulario web
with st.form("formulario_agenda"):
    st.subheader("Datos Generales")
    fecha = st.text_input("Fecha de la Agenda (ej: MIÉRCOLES, 29 DE ABRIL):")
    
    # Campo para subir el logo directamente desde la web
    logo_file = st.file_uploader("Subir logo opcional (PNG o JPG):", type=["png", "jpg", "jpeg"])
    
    num_eventos = st.number_input("Número de eventos:", min_value=1, value=1, step=1)
    
    st.subheader("Detalles de los Eventos")
    eventos_datos = []
    
    # Generamos los campos de texto según el número de eventos elegidos
    for i in range(int(num_eventos)):
        st.markdown(f"**Evento {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            hora_titulo = st.text_input(f"Hora y Título (Rojo)", key=f"hora_{i}")
            lugar = st.text_input(f"Lugar (Negrita)", key=f"lugar_{i}")
        with col2:
            desc = st.text_area(f"Descripción (Gris)", height=100, key=f"desc_{i}")
        
        # Guardamos los datos de este evento en nuestra lista
        eventos_datos.append({
            "hora": hora_titulo,
            "desc": desc,
            "lugar": lugar
        })
        st.markdown("---") # Línea separadora visual
    
    # Botón principal de la web
    submit_button = st.form_submit_button("Generar Imagen JPG")

# 3. Lógica que se ejecuta al pulsar el botón "Generar Imagen JPG"
if submit_button:
    with st.spinner("Maquetando y generando la imagen..."):
        fecha_texto = fecha.upper()
        html_eventos = ""
        
        # Procesar el logo subido en la web para incrustarlo en el HTML
        etiqueta_logo = ""
        if logo_file is not None:
            encoded_string = base64.b64encode(logo_file.read()).decode()
            etiqueta_logo = f'<img src="data:image/png;base64,{encoded_string}" style="max-width: 150px; margin-bottom: 10px;"><br>'

        # Procesar los textos respetando mayúsculas/minúsculas donde solicitaste
        for ev in eventos_datos:
            h = ev["hora"].upper()
            d = ev["desc"].strip()  # Mantiene mayúsculas y minúsculas
            l = ev["lugar"].strip() # Mantiene mayúsculas y minúsculas
            
            html_eventos += f"""
            <div class="evento">
                <div class="hora-titulo">{h}</div>
                <div class="descripcion">{d}</div>
                <div class="lugar">LUGAR: <strong>{l}</strong></div>
            </div>
            """

        # Diseño final en HTML y CSS
        html_completo = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; width: 800px; margin: 0; padding: 0; text-align: center; overflow: hidden; background-color: #FFFFFF; }}
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
            <div class="header">AGENDA {fecha_texto} DE 2026</div>
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
        
        # 4. IMPORTANTE: Configuración especial para que funcione en el servidor de Streamlit
        hti = Html2Image(custom_flags=['--no-sandbox', '--disable-gpu'])
        ruta_salida = 'agenda_web_generada.jpg'
        
        # Generar la imagen
        hti.screenshot(html_str=html_completo, save_as=ruta_salida, size=(800, 1200))
        
        # Leer la imagen generada para prepararla para la descarga
        with open(ruta_salida, "rb") as file:
            imagen_bytes = file.read()
            
    st.success("¡Imagen generada correctamente! Usa el botón de abajo para guardarla.")
    
    # 5. Botón para que el usuario descargue el JPG a su ordenador
    st.download_button(
        label="📥 Descargar Agenda en JPG",
        data=imagen_bytes,
        file_name="agenda_final.jpg",
        mime="image/jpeg"
    )
