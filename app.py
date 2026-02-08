import streamlit as st
from fpdf import FPDF
from datetime import datetime

# 1. Configuración básica
st.set_page_config(page_title="Facturador", layout="wide")

# 2. Título sencillo (sin estilos raros para evitar el TypeError)
st.title("Generador de Facturas")

# --- CABECERA (Nº Factura y Fecha) ---
col_n, col_f = st.columns(2)
with col_n:
    num_factura = st.text_input("Numero de Factura", "2026-0001")
with col_f:
    fecha_factura = st.text_input("Fecha de Emision", datetime.now().strftime("%d/%m/%Y"))

st.divider()

# --- DATOS JUNTOS (Emisor y Cliente) ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Emisor")
    mi_nombre = st.text_input("Mi Nombre", "DI ESTEFANO")
    mi_nif = st.text_input("Mi NIF", "B71537948")
    mi_iban = st.text_input("Mi IBAN", "ES00...")
with c2:
    st.subheader("Cliente")
    c_nombre = st.text_input("Nombre Cliente", "ADANIA RESIDENCIAL S.L.")
    c_nif = st.text_input("NIF Cliente", "B31114051")

# --- TABLA DE TRABAJOS ---
if 'filas' not in st.session_state: st.session_state.filas = 3
st.write("### Detalle")
datos = []
for i in range(st.session_state.filas):
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1: d = st.text_input(f"Descripcion {i+1}", key=f"d{i}")
    with col2: m = st.number_input(f"Cant", key=f"m{i}", min_value=0.0)
    with col3: p = st.number_input(f"Precio", key=f"p{i}", min_value=0.0)
    if d: datos.append({"d": d, "s": m*p})

total = sum(f["s"] for f in datos) * 0.85

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Numero: {num_factura} | Fecha: {fecha_factura}", 0, 1)
    pdf.cell(0, 10, f"Total a pagar: {total:.2f} EUR", 0, 1)
    pdf.cell(0, 10, f"IBAN: {mi_iban}", 0, 1)
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.divider()
# Botón de descarga
st.download_button("DESCARGAR PDF", data=crear_pdf(), file_name=f"Factura_{num_factura}.pdf")
