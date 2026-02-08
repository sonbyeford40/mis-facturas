import streamlit as st
from fpdf import FPDF
from datetime import datetime

# 1. DISEÑO SERIO (Sin cohete y compacto)
st.set_page_config(page_title="Factura", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} [data-testid="stHeader"] {display:none;}</style>""", unsafe_allow_index=True)

# --- CABECERA (Nº Factura y Fecha arriba) ---
c_n, c_f = st.columns(2)
with c_n:
    num_f = st.text_input("Factura Numero", "2026-0001")
with c_f:
    fecha_f = st.text_input("Fecha", datetime.now().strftime("%d/%m/%Y"))

st.divider()

# --- DATOS EMISOR Y CLIENTE (JUNTOS) ---
col1, col2 = st.columns(2)
with col1:
    st.write("**EMISOR**")
    mi_nom = st.text_input("Nombre", "DI ESTEFANO")
    mi_nif = st.text_input("NIF", "B71537948")
    mi_dir = st.text_input("Direccion", "Paseo Rio Irati 11")
    mi_iban = st.text_input("IBAN Pago", "ES00...")
with col2:
    st.write("**CLIENTE**")
    cl_nom = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
    cl_nif = st.text_input("NIF Cliente", "B31114051")
    cl_dir = st.text_input("Direccion Cliente", "Galar 31191")

# --- TABLA DE TRABAJOS ---
if 'filas' not in st.session_state: st.session_state.filas = 3
items = []
st.write("### Detalle")
for i in range(st.session_state.filas):
    ca, cb, cc = st.columns([5, 1, 1])
    with ca: d = st.text_input(f"Trabajo {i+1}", key=f"d{i}")
    with cb: m = st.number_input(f"Cant", key=f"m{i}")
    with cc: p = st.number_input(f"Precio", key=f"p{i}")
    if d: items.append({"d": d, "t": m*p})

total = sum(it["t"] for it in items) * 0.85 

# --- GENERADOR DE PDF (SEGURO SIN SIMBOLOS) ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'C')
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"Numero: {num_f} | Fecha: {fecha_f}", 0, 1, 'R')
    pdf.ln(10)
    pdf.cell(0, 10, f"TOTAL NETO A PAGAR: {total:.2f} EUR", 0, 1)
    pdf.cell(0, 10, f"PAGO (IBAN): {mi_iban}", 0, 1)
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.divider()
# BOTON DE DESCARGA (SIN ICONOS PARA EVITAR EL ERROR)
st.download_button("DESCARGAR FACTURA PDF", data=crear_pdf(), file_name="Factura.pdf")
