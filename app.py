import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
import io
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cloudev-econt Pro", page_icon="🏦", layout="wide")

# --- CSS PERSONALIZADO ---
st.markdown(f"""
    <style>
    .stButton>button {{ background-color: #27ae60; color: white; border-radius: 8px; width: 100%; }}
    .main-title {{ color: #2c3e50; font-family: 'Montserrat', sans-serif; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES CORE ---
def enviar_mail(excel_data, total, ok, err, tasa):
    remitente = st.secrets["email_user"]
    password = st.secrets["email_password"]
    destinatarios = ["socio@cloudev-econt.cl"] # Lista predeterminada
    
    msg = MIMEMultipart()
    msg['Subject'] = f"📊 Reporte Cloudev-econt: {datetime.now().strftime('%d/%m/%Y')}"
    
    html = f"<h3>Resumen Cloudev-econt</h3><p>Procesados: {ok}</p><p>Errores: {err}</p><p>Efectividad: {tasa:.1f}%</p>"
    msg.attach(MIMEText(html, 'html'))
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(excel_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Auditoria.xlsx"')
    msg.attach(part)
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(remitente, password)
            server.send_message(msg)
        return True
    except: return False

# --- INTERFAZ ---
st.title("🏦 Cloudev-econt")
st.subheader("Lleva tu contabilidad al siguiente nivel")

with st.sidebar:
    st.header("🎨 Marca")
    st.info("Configuración de Cloudev-econt activa")

archivos = st.file_uploader("Cargar Cartolas Itaú", accept_multiple_files=True)

if st.button("🚀 PROCESAR Y NOTIFICAR"):
    if archivos:
        # Simulación de proceso
        df_ok = pd.DataFrame([{"Cuenta": "110401", "Debe": 1000, "Haber": 0}])
        df_err = pd.DataFrame([{"Archivo": "error.pdf", "Motivo": "Ilegible"}])
        
        # Gráfico
        fig = px.pie(values=[len(df_ok), len(df_err)], names=['Éxito', 'Revisión'], color_discrete_sequence=['#27ae60', '#e74c3c'])
        st.plotly_chart(fig)
        
        # Generar Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_ok.to_excel(writer, sheet_name='Procesados')
            df_err.to_excel(writer, sheet_name='Errores')
        
        # Enviar
        if enviar_mail(output.getvalue(), 1, 1, 1, 50.0):
            st.success("✅ Proceso completado y reporte enviado por email.")
    else:
        st.warning("Sube archivos primero.")