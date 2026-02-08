import streamlit as st
from fpdf import FPDF
from datetime import datetime

# 1. Configuración de página
st.set_page_config(page_title="Facturador Profesional", layout="wide")

# Título de la aplicación
st.title("Generador de Facturas")

# --- CABECERA (Nº Factura y Fecha) ---
col_n, col_f = st.columns(2)
with col_n:
    num_factura = st.text_input("Nº Factura (Ej: 2026-0001)", "2026-0001")
with col_f:
    fecha_factura = st.text_input("Fecha de Emisión", datetime.now().strftime("%d/%m/%Y"))

st.divider()

# --- DATOS JUNTOS (Emisor y Cliente lado a lado) ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Datos del Emisor")
    mi_nombre = st.text_input("Mi Nombre/Empresa", "DI ESTEFANO")
    mi_nif = st.text_input("Mi NIF/CIF", "B71537948")
    mi_dir = st.text_input("Mi Dirección", "Paseo Rio Irati 11")
    mi_iban = st.text_input("Mi IBAN para el pago", "ES00...")
with c2:
    st.subheader("Datos del Cliente")
    c_nombre = st.text_input("Nombre del Cliente", "ADANIA RESIDENCIAL S.L.")
    c_nif = st.text_input("NIF del Cliente", "B31114051")
    c_dir = st.text_input("Dirección del Cliente", "Galar 31191")

st.divider()

# --- TABLA DE TRABAJOS ---
st.write("### Detalle de Trabajos / Conceptos")
if 'filas' not in st.session_state:
    st.session_state.filas = 4

datos_tabla = []
for i in range(st.session_state.filas):
    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
    with col1:
        desc = st.text_input(f"Descripción {i+1}", key=f"desc_{i}")
    with col2:
        unid = st.selectbox(f"Unid", ["m2", "Ud", "ml", "h"], key=f"unid_{i}")
    with col3:
        cant = st.number_input(f"Cant", min_value=0.0, step=0.1, key=f"cant_{i}")
    with col4:
        prec = st.number_input(f"Precio", min_value=0.0, step=0.01, key=f"prec_{i}")
    
    if desc:
        subtotal_fila = cant * prec
        datos_tabla.append({"desc": desc, "unid": unid, "cant": cant, "prec": prec, "sub": subtotal_fila})

st.divider()

# --- CÁLCULOS FINALES ---
base_imponible = sum(item["sub"] for item in datos_tabla)
# Ejemplo: Aplicando una retención o descuento del 15% (85% neto)
total_final = base_imponible * 0.85 

col_t1, col_t2 = st.columns(2)
with col_t2:
    st.write(f"**Base Imponible:** {base_imponible:.2f} EUR")
    st.write(f"### **TOTAL NETO A PAGAR: {total_final:.2f} EUR**")

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    pdf.ln(5)
    pdf.cell(0, 8, f"Numero: {num_factura}  |  Fecha: {fecha_factura}", 0, 1, 'R')
    
    # Bloque de datos
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(95, 8, "EMISOR:", 0, 0)
    pdf.cell(95, 8, "CLIENTE:", 0, 1)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 6, mi_nombre, 0, 0)
    pdf.cell(95, 6, c_nombre, 0, 1)
    pdf.cell(95, 6, f"NIF: {mi_nif}", 0, 0)
    pdf.cell(95, 6, f"NIF: {c_nif}", 0, 1)
    pdf.cell(95, 6, mi_dir, 0, 0)
    pdf.cell(95, 6, c_dir, 0, 1)
    
    # Totales
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"TOTAL NETO A PAGAR: {total_final:.2f} EUR", 1, 1, 'C')
    pdf.ln(5)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"FORMA DE PAGO (IBAN): {mi_iban}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.divider()
# Botón de descarga
st.download_button("📩 DESCARGAR FACTURA EN PDF", data=crear_pdf(), file_name=f"Factura_{num_factura}.pdf")
