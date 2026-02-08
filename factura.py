import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Factura", layout="wide")

# Esto quita los menus de arriba para que no estorben
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} [data-testid="stHeader"] {display:none;}</style>""", unsafe_allow_index=True)

# --- CABECERA ---
c_n, c_f = st.columns(2)
with c_n:
    num_factura = st.text_input("Factura Numero", "2026-0001")
with c_f:
    fecha_factura = st.text_input("Fecha", datetime.now().strftime("%d/%m/%Y"))

st.divider()

# --- DATOS ---
with st.expander("Datos Emisor y Cliente", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        mi_nombre = st.text_input("Mi Nombre", "DI ESTEFANO")
        mi_nif = st.text_input("Mi NIF", "B71537948")
        mi_dir = st.text_input("Mi Direccion", "Paseo Rio Irati 11")
        mi_iban = st.text_input("IBAN", "ES00...")
    with c2:
        c_nombre = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
        c_nif = st.text_input("NIF Cliente", "B31114051")
        c_dir = st.text_input("Direccion Cliente", "Galar 31191")

if 'filas' not in st.session_state: st.session_state.filas = 4

# --- TABLA ---
st.write("### Detalle de Trabajos")
datos_tabla = []
for i in range(st.session_state.filas):
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    with col1: d = st.text_input(f"Desc {i+1}", key=f"d{i}")
    with col2: u = st.selectbox(f"Und", ["m2", "Ud", "ml"], key=f"u{i}")
    with col3: m = st.number_input(f"Cant", min_value=0.0, key=f"m{i}")
    with col4: p = st.number_input(f"Precio", min_value=0.0, key=f"p{i}")
    if d: datos_tabla.append({"d": d, "u": u, "c": m, "p": p, "s": m*p})

# --- CALCULOS ---
subtotal = sum(f["s"] for f in datos_tabla)
total = subtotal * 0.85 # Ejemplo con retencion aplicada

# --- EL BOTON MAGICO ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"FACTURA NUMERO: {num_factura}", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Fecha: {fecha_factura}", 0, 1)
    pdf.ln(5)
    pdf.cell(0, 10, f"Total a pagar: {total:.2f} EUR", 0, 1)
    pdf.cell(0, 10, f"IBAN: {mi_iban}", 0, 1)
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.divider()
# ESTE ES EL BOTON QUE DEBES BUSCAR ABAJO DEL TODO
st.download_button("DESCARGAR FACTURA PDF", data=crear_pdf(), file_name="Factura.pdf")
