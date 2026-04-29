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
        # RECUPERADO: Control para decidir cuántos eventos caben en una sola imagen
        eventos_por_pag = st.number_input("Eventos por página:", min_value=1, value=4, step=1)
    
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

        # Dividir la lista total de eventos en páginas según lo que elija el usuario
        paginas_de_eventos = [eventos_datos[i:i + int(eventos_por_pag)] for i in range(0, len(eventos_datos), int(eventos_por_pag))]

        # Preparar la herramienta de captura de imágenes
        hti = Html2Image(custom_flags=['--no-sandbox', '--disable-gpu'])
        
        # Crear un "archivo ZIP" virtual en la memoria
        archivo_zip_en_memoria = io.BytesIO()
        
        with zipfile.ZipFile(archivo_zip_en_memoria, "w") as zip_file:
            
            # Repetimos el proceso por cada página
            for indice_pag, pagina_actual in enumerate(paginas_de_eventos):
                html_eventos = ""
                
                # Procesar los eventos de la página actual
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

                # Plantilla HTML/CSS corregida para que no corte el footer
                html_completo = f"""
                <html>
                <head>
                    <style>
                        /* Ocultamos la barra de desplazamiento visualmente para que no salga en la foto */
                        ::-webkit-scrollbar {{
                            display: none;
                        }}
                        
                        body {{ 
                            font-family: 'Arial', sans-serif; 
                            width: 800px; 
                            min-height: 1200px; /* Altura mínima en lugar de fija */
                            margin: 0; 
                            padding: 0; 
                            text-align: center; 
                            background-color: #FFFFFF;
                            display: flex; 
                            flex-direction: column; 
                        }}
                        
                        .header {{ background-color: #e30613; color: white; padding: 20px; font-size: 28px; font-weight: bold; }}
                        
                        .container {{ 
                            padding: 40px; 
                            flex-grow: 1; /* Empuja el footer hacia abajo de forma natural */
                        }}
                        
                        .evento {{ margin-bottom: 40px; }}
                        .hora-titulo {{ color: #e30613; font-size: 22px; margin-bottom: 5px; font-weight: bold; }}
                        .descripcion {{ color: #707070; font-size: 20px; margin-bottom: 5px; }}
                        .lugar {{ color: #000; font-size: 18px; }}
                        
                        .footer {{ 
                            border-top: 2px solid #e30613; 
                            padding: 20px; 
                            display: flex; 
                            justify-content: space-around; 
                            align-items: flex-end; 
                            background-color: #FFFFFF; 
                        }}
                        .bloque-izquierdo {{ text-align: center; }}
                    </style>
                </head>
                <body>
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
                
                ruta_salida = f'agenda_pag_{indice_pag + 1}.jpg'
                
                # Tomar la foto (mantenemos 800x1200 como proporción estándar)
                hti.screenshot(html_str=html_completo, save_as=ruta_salida, size=(800, 1200))
                
                # Guardar en el ZIP
                with open(ruta_salida, "rb") as file:
                    zip_file.writestr(ruta_salida, file.read())
                    
    st.success("¡Imágenes generadas correctamente! Usa el botón de abajo para guardarlas.")
    
    # 4. Botón para descargar el archivo ZIP
    st.download_button(
        label="📥 Descargar Agendas (Archivo ZIP)",
        data=archivo_zip_en_memoria.getvalue(),
        file_name="agendas_generadas.zip",
        mime="application/zip"
    )
