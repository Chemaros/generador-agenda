import streamlit as st
from html2image import Html2Image
import base64
import zipfile
import io
from PIL import Image, ImageChops # NUEVO: Librerías para recortar la imagen

# 1. Configuración básica de la página web
st.set_page_config(page_title="Generador de Agenda", page_icon="📅")

st.title("Generador de Agenda - PSOE Salamanca")
st.write("Rellena el formulario a continuación para generar la imagen de la agenda.")

# 2. Creamos el formulario web
with st.form("formulario_agenda"):
    st.subheader("Datos Generales")
    fecha = st.text_input("Fecha de la Agenda (ej: MIÉRCOLES, 29 DE ABRIL):")
    
    logo_file = st.file_uploader("Subir logo opcional (PNG o JPG):", type=["png", "jpg", "jpeg"])
    
    col_a, col_b = st.columns(2)
    with col_a:
        num_eventos = st.number_input("Número total de eventos:", min_value=1, value=1, step=1)
    with col_b:
        eventos_por_pag = st.number_input("Eventos por página:", min_value=1, value=4, step=1)
    
    st.subheader("Detalles de los Eventos")
    eventos_datos = []
    
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
    with st.spinner("Maquetando y calculando el tamaño de las imágenes..."):
        fecha_texto = fecha.upper()
        
        etiqueta_logo = ""
        if logo_file is not None:
            encoded_string = base64.b64encode(logo_file.read()).decode()
            etiqueta_logo = f'<img src="data:image/png;base64,{encoded_string}" style="max-width: 150px; margin-bottom: 10px;"><br>'

        paginas_de_eventos = [eventos_datos[i:i + int(eventos_por_pag)] for i in range(0, len(eventos_datos), int(eventos_por_pag))]

        hti = Html2Image(custom_flags=['--no-sandbox', '--disable-gpu'])
        archivo_zip_en_memoria = io.BytesIO()
        
        with zipfile.ZipFile(archivo_zip_en_memoria, "w") as zip_file:
            
            for indice_pag, pagina_actual in enumerate(paginas_de_eventos):
                html_eventos = ""
                
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

                # Plantilla HTML/CSS con la nueva "Caja Inteligente" (#wrapper)
                html_completo = f"""
                <html>
                <head>
                    <style>
                        ::-webkit-scrollbar {{ display: none; }}
                        
                        body {{ 
                            font-family: 'Arial', sans-serif; 
                            margin: 0; 
                            padding: 0; 
                            background-color: #FFFFFF;
                        }}
                        
                        /* Esta caja controla la altura. Mínimo 1200px, pero crece si hace falta */
                        #wrapper {{
                            width: 800px;
                            min-height: 1200px;
                            display: flex;
                            flex-direction: column;
                            background-color: #FFFFFF;
                        }}
                        
                        .header {{ background-color: #e30613; color: white; padding: 20px; font-size: 28px; font-weight: bold; text-align: center; }}
                        
                        .container {{ 
                            padding: 40px; 
                            flex-grow: 1; /* Empuja el footer hacia abajo */
                            text-align: center;
                        }}
                        
                        .evento {{ margin-bottom: 40px; }}
                        .hora-titulo {{ color: #e30613; font-size: 22px; margin-bottom: 5px; font-weight: bold; }}
                        .descripcion {{ color: #707070; font-size: 20px; margin-bottom: 5px; }}
                        .lugar {{ color: #000; font-size: 18px; }}
                        
                        .footer {{ 
                            border-top: 2px solid #e30613; 
                            padding: 20px 20px 40px 20px; /* Margen extra inferior para que respire */
                            display: flex; 
                            justify-content: space-around; 
                            align-items: flex-end; 
                            background-color: #FFFFFF; 
                        }}
                        .bloque-izquierdo {{ text-align: center; }}
                    </style>
                </head>
                <body>
                    <div id="wrapper">
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
                    </div>
                </body>
                </html>
                """
                
                ruta_salida = f'agenda_pag_{indice_pag + 1}.jpg'
                
                # 1. Tomamos una captura GIGANTE (4000px) para que nada se corte
                hti.screenshot(html_str=html_completo, save_as=ruta_salida, size=(800, 4000))
                
                # --- NUEVO SISTEMA DE RECORTE CON PILLOW ---
                # Abrimos la foto gigante generada
                img = Image.open(ruta_salida).convert("RGB")
                
                # Creamos un lienzo completamente blanco del mismo tamaño para comparar
                fondo_blanco = Image.new("RGB", img.size, (255, 255, 255))
                
                # Calculamos la diferencia entre la foto y el lienzo blanco
                # Esto nos dice dónde están todos los píxeles que NO son blancos (nuestros textos y bordes)
                diferencia = ImageChops.difference(img, fondo_blanco)
                caja_delimitadora = diferencia.getbbox()
                
                if caja_delimitadora:
                    # caja_delimitadora[3] nos da la posición Y del último píxel con color (el final del footer)
                    alto_del_contenido = caja_delimitadora[3] + 20 # Sumamos 20px para no cortar el margen blanco final
                    
                    # Decidimos la altura final: Si el contenido es menor a 1200, usamos 1200. Si es mayor, usamos la altura del contenido.
                    alto_final = max(1200, alto_del_contenido)
                    
                    # Recortamos la imagen usando esas coordenadas y la sobrescribimos
                    img_recortada = img.crop((0, 0, 800, alto_final))
                    img_recortada.save(ruta_salida)
                # -------------------------------------------
                
                # Guardar en el ZIP la imagen ya recortada a su tamaño perfecto
                with open(ruta_salida, "rb") as file:
                    zip_file.writestr(ruta_salida, file.read())
                    
    st.success("¡Imágenes adaptadas y generadas correctamente!")
    
    st.download_button(
        label="📥 Descargar Agendas (Archivo ZIP)",
        data=archivo_zip_en_memoria.getvalue(),
        file_name="agendas_generadas.zip",
        mime="application/zip"
    )
