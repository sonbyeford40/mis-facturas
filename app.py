import streamlit as st
from fpdf import FPDF
from datetime import datetime

# Configuracion de pagina
st.set_page_config(page_title="Facturador", layout="wide")

# Ocultar decoracion innecesaria (quita el cohete)
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} [data-testid="stHeader"] {display:none;}</style>""", unsafe_allow_index=True)

# CABECERA
c1, c2 = st.columns(2)
with c1:
    num_f = st.text_input("Numero Factura", "2026-0001")
with c2:
    fecha_f = st.text_input("Fecha de Emision", datetime.now().strftime("%d/%m/%Y"))

st.divider()

# DATOS JUNTOS (Emisor y Cliente)
col_e, col_c = st.columns(2)
with col_e:
    st.write("**DATOS DEL EMISOR**")
    mi_nom = st.text_input("Nombre", "DI ESTEFANO")
    mi_nif = st.text_input("NIF", "B71537948")
    mi_iban = st.text_input("IBAN Pago", "ES00...")
with col_c:
    st.write("**DATOS DEL CLIENTE**")
    cl_nom = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
    cl_nif = st.text_input("NIF Cliente", "B31114051")

# DETALLE DE TRABAJOS
if 'filas' not in st.session_state: st.session_state.filas = 3
items = []
for i in range(st.session_state.filas):
    ca, cb, cc = st.columns([5, 1, 1])
    with ca: d = st.text_input(f"Trabajo {i+1}", key=f"d{i}")
    with cb: m = st.number_input(f"Cant", key=f"m{i}", min_value=0.0)
    with cc: p = st.number_input(f"Precio", key=f"p{i}", min_value=0.0)
    if d: items.append({"d": d, "t": m*p})

subtotal = sum(it["t"] for it in items)
total = subtotal * 0.85 # Ajuste con retencion

# PDF SEGURO (Sin simbolos que causen UnicodeEncodeError)
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'C')
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"Numero: {num_f} | Fecha: {fecha_f}", 0, 1, 'R')
    pdf.ln(10)
    pdf.cell(0, 10, f"TOTAL NETO A PAGAR: {total:.2f} EUR", 0, 1)
    pdf.cell(0, 10, f"IBAN: {mi_iban}", 0, 1)
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.divider()
# Boton de descarga corregido para evitar el error previo
st.download_button("DESCARGAR FACTURA PDF", data=crear_pdf(), file_name=f"Factura_{num_f}.pdf")
