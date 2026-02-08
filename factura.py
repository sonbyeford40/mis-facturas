import streamlit as st
from fpdf import FPDF
from datetime import datetime

# 1. Configuración compacta y seria
st.set_page_config(page_title="Factura", layout="wide")

# Ocultar decoraciones innecesarias
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} [data-testid="stHeader"] {display:none;}</style>""", unsafe_allow_index=True)

# --- CABECERA (Nº Factura y Fecha) ---
c_n, c_f = st.columns(2)
with c_n:
    num_f = st.text_input("Factura Numero", "2026-0001")
with c_f:
    fecha_f = st.text_input("Fecha", datetime.now().strftime("%d/%m/%Y"))

st.divider()

# --- DATOS EMISOR Y CLIENTE (LADO A LADO) ---
with st.expander("Datos de Facturacion", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        mi_nom = st.text_input("Mi Nombre", "DI ESTEFANO")
        mi_nif = st.text_input("Mi NIF", "B71537948")
        mi_dir = st.text_input("Mi Direccion", "Paseo Rio Irati 11")
        mi_iban = st.text_input("IBAN Pago", "ES00...")
    with col2:
        cl_nom = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
        cl_nif = st.text_input("NIF Cliente", "B31114051")
        cl_dir = st.text_input("Direccion Cliente", "Galar 31191")

# --- TRABAJOS ---
if 'filas' not in st.session_state: st.session_state.filas = 4
st.write("### Detalle de Trabajos")
items = []
for i in range(st.session_state.filas):
    c1, c2, c3, c4 = st.columns([5, 1, 1, 1])
    with c1: d = st.text_input(f"Descripcion {i+1}", key=f"d{i}")
    with c2: u = st.selectbox(f"Unid", ["m2", "Ud", "ml"], key=f"u{i}")
    with c3: m = st.number_input(f"Cant", min_value=0.0, key=f"m{i}")
    with c4: p = st.number_input(f"Precio", min_value=0.0, key=f"p{i}")
    if d: items.append({"d": d, "u": u, "c": m, "p": p, "s": m*p})

# --- TOTALES ---
subtotal = sum(item["s"] for item in items)
iva = st.sidebar.number_input("IVA %", value=0)
ret = st.sidebar.number_input("Retencion %", value=15)
total = subtotal + (subtotal * iva/100) - (subtotal * ret/100)

# --- BOTON DE DESCARGA (SOLO APARECE SI NO HAY ERROR) ---
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"FACTURA: {num_f}", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Fecha: {fecha_f}", 0, 1)
    pdf.ln(5)
    # Tabla simple para ahorrar espacio
    pdf.cell(100, 8, "Descripcion", 1)
    pdf.cell(30, 8, "Total", 1, 1, 'R')
    for it in items:
        pdf.cell(100, 8, it['d'], 1)
        pdf.cell(30, 8, f"{it['s']:.2f}", 1, 1, 'R')
    pdf.ln(5)
    pdf.cell(0, 10, f"TOTAL NETO: {total:.2f} EUR", 0, 1)
    pdf.cell(0, 10, f"IBAN: {mi_iban}", 0, 1)
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.divider()
st.download_button("📩 DESCARGAR FACTURA PDF", data=generar_pdf(), file_name="Factura.pdf")
