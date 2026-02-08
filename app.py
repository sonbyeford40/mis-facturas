import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Facturador Pro", layout="wide")

# Título
st.title("Generador de Facturas con IVA e IRPF")

# --- CABECERA ---
col_n, col_f = st.columns(2)
with col_n:
    num_factura = st.text_input("Nº Factura", "2026-0001")
with col_f:
    fecha_factura = st.text_input("Fecha", datetime.now().strftime("%d/%m/%Y"))

st.divider()

# --- DATOS JUNTOS ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Emisor")
    mi_nombre = st.text_input("Mi Nombre", "DI ESTEFANO")
    mi_nif = st.text_input("Mi NIF", "B71537948")
    mi_dir = st.text_input("Mi Dirección", "Paseo Rio Irati 11")
    mi_iban = st.text_input("Mi IBAN", "ES00...")
with c2:
    st.subheader("Cliente")
    c_nombre = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
    c_nif = st.text_input("NIF Cliente", "B31114051")
    c_dir = st.text_input("Dirección Cliente", "Galar 31191")

st.divider()

# --- TABLA DINÁMICA DE ARTÍCULOS ---
st.write("### Artículos / Servicios")
if 'n_filas' not in st.session_state:
    st.session_state.n_filas = 3

datos_tabla = []
for i in range(st.session_state.n_filas):
    ca, cb, cc, cd = st.columns([4, 1, 1, 1])
    with ca: d = st.text_input(f"Descripción", key=f"d_{i}")
    with cb: u = st.text_input(f"Unid", value="Ud", key=f"u_{i}")
    with cc: m = st.number_input(f"Cant", min_value=0.0, step=1.0, key=f"m_{i}")
    with cd: p = st.number_input(f"Precio", min_value=0.0, step=0.01, key=f"p_{i}")
    if d:
        datos_tabla.append({"d": d, "u": u, "m": m, "p": p, "t": m * p})

# Botón para añadir más filas (No saldrá en el PDF)
if st.button("➕ Añadir otra fila"):
    st.session_state.n_filas += 1
    st.rerun()

st.divider()

# --- IMPUESTOS (IVA e IRPF) ---
col_i1, col_i2 = st.columns(2)
with col_i1:
    p_iva = st.number_input("IVA %", value=21)
    p_irpf = st.number_input("IRPF % (Retención)", value=15)

# --- CÁLCULOS ---
base_imponible = sum(item["t"] for item in datos_tabla)
cuota_iva = base_imponible * (p_iva / 100)
cuota_irpf = base_imponible * (p_irpf / 100)
total_final = base_imponible + cuota_iva - cuota_irpf

with col_i2:
    st.write(f"Base Imponible: {base_imponible:.2f}")
    st.write(f"IVA ({p_iva}%): +{cuota_iva:.2f}")
    st.write(f"IRPF ({p_irpf}%): -{cuota_irpf:.2f}")
    st.write(f"### TOTAL A COBRAR: {total_final:.2f} EUR")

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"N. Factura: {num_factura} | Fecha: {fecha_factura}", 0, 1, 'R')
    
    # Bloque datos
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 7, "EMISOR", 0, 0)
    pdf.cell(95, 7, "CLIENTE", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 5, mi_nombre, 0, 0); pdf.cell(95, 5, c_nombre, 0, 1)
    pdf.cell(95, 5, f"NIF: {mi_nif}", 0, 0); pdf.cell(95, 5, f"NIF: {c_nif}", 0, 1)
    pdf.multi_cell(95, 5, mi_dir, 0, 'L');
