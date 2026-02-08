import streamlit as st
from fpdf import FPDF
from datetime import datetime

# Configuracion seria sin titulos decorativos
st.set_page_config(page_title="Factura", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} [data-testid="stHeader"] {display:none;}</style>""", unsafe_allow_index=True)

# --- CABECERA (Nº Factura y Fecha) ---
col_n, col_f = st.columns(2)
with col_n:
    num_factura = st.text_input("Numero de Factura", "2026-0001")
with col_f:
    fecha_factura = st.text_input("Fecha de Emision", datetime.now().strftime("%d/%m/%Y"))

st.divider()

# --- DATOS EMISOR Y CLIENTE JUNTOS ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Datos del Emisor")
    mi_nombre = st.text_input("Mi Nombre", "DI ESTEFANO")
    mi_nif = st.text_input("Mi NIF", "B71537948")
    mi_dir = st.text_input("Mi Direccion", "Paseo Rio Irati 11")
    mi_iban = st.text_input("Mi IBAN", "ES00...")
with c2:
    st.subheader("Datos del Cliente")
    c_nombre = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
    c_nif = st.text_input("NIF Cliente", "B31114051")
    c_dir = st.text_input("Direccion Cliente", "Galar 31191")

# --- TABLA DE TRABAJOS ---
if 'filas' not in st.session_state: st.session_state.filas = 4
st.write("### Detalle de Trabajos")
datos = []
for i in range(st.session_state.filas):
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    with col1: d = st.text_input(f"Descripcion {i+1}", key=f"d{i}")
    with col2: u = st.selectbox(f"Unid", ["m2", "Ud", "ml"], key=f"u{i}")
    with col3: m = st.number_input(f"Cant", min_value=0.0, key=f"m{i}")
    with col4: p = st.number_input(f"Precio", min_value=0.0, key=f"p{i}")
    if d: datos.append({"d": d, "u": u, "c": m, "p": p, "s": m*p})

# --- CALCULOS ---
subtotal = sum(f["s"] for f in datos)
total = subtotal * 0.85 

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Numero: {num_factura} | Fecha: {fecha_factura}", 0, 1, 'R')
    pdf.ln(10)
    pdf.cell(0, 10, f"TOTAL NETO: {total:.2f} EUR", 0, 1)
    pdf.cell(0, 10, f"IBAN: {mi_iban}", 0, 1)
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.divider()
# EL BOTON AZUL QUE BUSCAS APARECERA AQUI ABAJO
st.download_button("📩 DESCARGAR FACTURA PDF", data=crear_pdf(), file_name=f"Factura_{num_factura}.pdf")
