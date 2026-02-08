import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Facturador Profesional", layout="wide")

# Título
st.title("Generador de Facturas")

# --- CABECERA COMPACTA ---
col_n, col_f = st.columns(2)
with col_n:
    num_factura = st.text_input("Nº Factura", "2026-0001")
with col_f:
    fecha_factura = st.text_input("Fecha", datetime.now().strftime("%d/%m/%Y"))

st.divider()

# --- BLOQUE ÚNICO DE DATOS (EMISOR Y CLIENTE JUNTOS) ---
st.write("### Información de Facturación")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**EMISOR**")
    mi_nombre = st.text_input("Mi Nombre", "DI ESTEFANO")
    mi_nif = st.text_input("Mi NIF", "B71537948")
    mi_dir = st.text_input("Mi Dirección", "Paseo Rio Irati 11")
    mi_iban = st.text_input("Mi IBAN", "ES00...")
with c2:
    st.markdown("**CLIENTE**")
    c_nombre = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
    c_nif = st.text_input("NIF Cliente", "B31114051")
    c_dir = st.text_input("Dirección Cliente", "Galar 31191")

st.divider()

# --- TABLA DE ARTÍCULOS ---
if 'n_filas' not in st.session_state:
    st.session_state.n_filas = 3

datos_tabla = []
for i in range(st.session_state.n_filas):
    ca, cb, cc, cd = st.columns([4, 1, 1, 1])
    with ca: d = st.text_input(f"Descripción", key=f"d_{i}")
    with cb: u = st.text_input(f"Unid", value="Ud", key=f"u_{i}")
    with cc: m = st.number_input(f"Cant", min_value=0.0, key=f"m_{i}")
    with cd: p = st.number_input(f"Precio", min_value=0.0, key=f"p_{i}")
    if d:
        datos_tabla.append({"d": d, "u": u, "m": m, "p": p, "t": m * p})

if st.button("➕ Añadir fila"):
    st.session_state.n_filas += 1
    st.rerun()

# --- IMPUESTOS Y TOTALES ---
st.divider()
col_i1, col_i2 = st.columns(2)
with col_i1:
    p_iva = st.number_input("IVA %", value=21)
    p_irpf = st.number_input("IRPF % (Retención)", value=15)

base_imponible = sum(item["t"] for item in datos_tabla)
cuota_iva = base_imponible * (p_iva / 100)
cuota_irpf = base_imponible * (p_irpf / 100)
total_final = base_imponible + cuota_iva - cuota_irpf

with col_i2:
    st.write(f"Base Imponible: {base_imponible:.2f} EUR")
    st.write(f"IVA ({p_iva}%): +{cuota_iva:.2f} EUR")
    st.write(f"IRPF ({p_irpf}%): -{cuota_irpf:.2f} EUR")
    st.write(f"### TOTAL A COBRAR: {total_final:.2f} EUR")

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 8, f"Factura: {num_factura} | Fecha: {fecha_factura}", 0, 1, 'R')
    
    # Datos juntos para ahorrar espacio
    pdf.ln(5)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 7, " DATOS DEL EMISOR", 0, 0, 'L', True)
    pdf.cell(95, 7, " DATOS DEL CLIENTE", 0, 1, 'L', True)
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(95, 5, mi_nombre, 0, 0); pdf.cell(95, 5, c_nombre, 0, 1)
    pdf.cell(95, 5, f"NIF: {mi_nif}", 0, 0); pdf.cell(95, 5, f"NIF: {c_nif}", 0, 1)
    pdf.cell(95, 5, mi_dir, 0, 0); pdf.cell(95, 5, c_dir, 0, 1)

    # Tabla
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(100, 8, "Descripción", 1, 0, 'C', True)
    pdf.cell(30, 8, "Cant", 1, 0, 'C', True)
    pdf.cell(30, 8, "Precio", 1, 0, 'C', True)
    pdf.cell(30, 8, "Total", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 9)
    for item in datos_tabla:
        pdf.cell(100, 7, item["d"], 1)
        pdf.cell(30, 7, str(item["m"]), 1, 0, 'C')
        pdf.cell(30, 7, f"{item['p']:.2f}", 1, 0, 'C')
        pdf.cell(30, 7, f"{item['t']:.2f}", 1, 1, 'C')

    # Desglose
    pdf.ln(5)
    pdf.cell(130, 6, "", 0)
    pdf.cell(30, 6, "Base Imponible:", 0, 0, 'R')
    pdf.cell(30, 6, f"{base_imponible:.2f}", 1, 1, 'R')
    pdf.cell(130, 6, "", 0)
    pdf.cell(30, 6, f"IVA {p_iva}%:", 0, 0, 'R')
    pdf.cell(30, 6, f"{cuota_iva:.2f}", 1, 1, 'R')
    pdf.cell(130, 6, "", 0)
    pdf.cell(30, 6, f"IRPF {p_irpf}%:", 0, 0, 'R')
    pdf.cell(30, 6, f"-{cuota_irpf:.2f}", 1, 1, 'R')
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(130, 8, "", 0)
    pdf.cell(30, 8, "TOTAL NETO:", 0, 0, 'R')
    pdf.cell(30, 8, f"{total_final:.2f} EUR", 1, 1, 'R')

    # TEXTO LEGAL LEY DEL IVA
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    texto_legal = "Operación sujeta a la Ley 37/1992 del Impuesto sobre el Valor Añadido (IVA). En caso de inversión del sujeto pasivo, se aplica el artículo 84.Uno.2º de dicha Ley."
    pdf.multi_cell(0, 5, texto_legal)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, f"FORMA DE PAGO (IBAN): {mi_iban}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.divider()
st.download_button("📩 DESCARGAR FACTURA PDF", data=crear_pdf(), file_name=f"Factura_{num_factura}.pdf")
