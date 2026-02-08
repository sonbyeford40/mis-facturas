import streamlit as st
from fpdf import FPDF
from datetime import datetime

# 1. Configuración de página ultra-limpia
st.set_page_config(page_title="Factura", layout="wide")

# Ocultar TODO lo que sobra de la web (títulos, menús, iconos)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stHeader"] {display:none;}
    </style>
    """, unsafe_allow_index=True)

# --- ENCABEZADO DIRECTO ---
c_n, c_f = st.columns(2)
with c_n:
    num_factura = st.text_input("Factura Nº", "2026-0001")
with c_f:
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    fecha_factura = st.text_input("Fecha", fecha_hoy)

st.divider()

# --- DATOS COMPACTOS ---
with st.expander("📝 Datos Identificativos", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        mi_nombre = st.text_input("Emisor", "DI ESTEFANO")
        mi_nif = st.text_input("NIF/DNI", "B71537948")
        mi_dir = st.text_input("Dirección", "Paseo Río Iratí Nº11 - 2do A")
        mi_iban = st.text_input("IBAN para el cobro", "ES00...")
    with c2:
        c_nombre = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
        c_nif = st.text_input("NIF Cliente", "B31114051")
        c_dir = st.text_input("Dirección Cliente", "Galar 31191")

# --- TABLA SIN ESPACIOS ---
if 'filas' not in st.session_state: st.session_state.filas = 4

st.write("### Detalle de Trabajos")
datos_tabla = []
for i in range(st.session_state.filas):
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    with col1: d = st.text_input(f"Descripción {i+1}", key=f"d{i}", label_visibility="collapsed")
    with col2: u = st.selectbox(f"Unid", ["m2", "Ud", "ml", "kg"], key=f"u{i}", label_visibility="collapsed")
    with col3: m = st.number_input(f"Cant", min_value=0.0, format="%.2f", key=f"m{i}", label_visibility="collapsed")
    with col4: p = st.number_input(f"Precio", min_value=0.0, format="%.2f", key=f"p{i}", label_visibility="collapsed")
    if d: datos_tabla.append({"d": d, "u": u, "c": m, "p": p, "s": m*p})

b1, b2, _ = st.columns([1, 1, 4])
with b1:
    if st.button("➕ Añadir"): st.session_state.filas += 1; st.rerun()
with b2:
    if st.button("➖ Quitar") and st.session_state.filas > 1: st.session_state.filas -= 1; st.rerun()

# --- CÁLCULOS (Sidebar) ---
iva_p = st.sidebar.number_input("IVA %", value=0)
ret_p = st.sidebar.number_input("Retención %", value=15)
subtotal = sum(f["s"] for f in datos_tabla)
m_iva = subtotal * (iva_p / 100)
m_ret = subtotal * (ret_p / 100)
total = subtotal + m_iva - m_ret

# --- GENERACIÓN DE PDF PROFESIONAL ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Encabezado serio
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(100, 10, "FACTURA", 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.cell(90, 10, f"Numero: {num_factura}  |  Fecha: {fecha_factura}", 0, 1, 'R')
    pdf.ln(5)
    
    # Datos Emisor/Receptor cara a cara
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(95, 6, " EMISOR", 0, 0, 'L', True)
    pdf.cell(5, 6, "", 0, 0)
    pdf.cell(90, 6, " CLIENTE", 0, 1, 'L', True)
    
    pdf.set_font("Arial", '', 9)
    pdf.ln(2)
    pdf.cell(95, 4, f"{mi_nombre} (NIF: {mi_nif})", 0, 0)
    pdf.cell(5, 4, "", 0, 0)
    pdf.cell(90, 4, f"{c_nombre} (NIF: {c_nif})", 0, 1)
    pdf.cell(95, 4, f"{mi_dir}", 0, 0)
    pdf.cell(5, 4, "", 0, 0)
    pdf.cell(90, 4, f"{c_dir}", 0, 1)
    pdf.ln(8)

    # Tabla de Conceptos
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(90, 7, " Descripcion", 1, 0, 'L', True)
    pdf.cell(20, 7, "Ud", 1, 0, 'C', True)
    pdf.cell(20, 7, "Cant", 1, 0, 'C', True)
    pdf.cell(30, 7, "Precio", 1, 0, 'C', True)
    pdf.cell(30, 7, "Total", 1, 1, 'C', True)

    pdf.set_font("Arial", '', 9)
    for f in datos_tabla:
        pdf.cell(90, 6, f" {f['d']}", 1)
        pdf.cell(20, 6, f"{f['u']}", 1, 0, 'C')
        pdf.cell(20, 6, f"{f['c']:.2f}", 1, 0, 'C')
        pdf.cell(30, 6, f"{f['p']:.2f}", 1, 0, 'C')
        pdf.cell(30, 6, f"{f['s']:.2f}", 1, 1, 'R')

    # Bloque de Totales
    pdf.ln(5)
    pdf.set_x(130)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(40, 6, "Subtotal:", 0)
    pdf.cell(30, 6, f"{subtotal:.2f}", 0, 1, 'R')
    pdf.set_x(130)
    pdf.cell(40, 6, f"IVA {iva_p}%:", 0)
    pdf.cell(30, 6, f"{m_iva:.2f}", 0, 1, 'R')
    pdf.set_x(130)
    pdf.cell(40, 6, f"Retencion {ret_p}%:", 0)
    pdf.cell(30, 6, f"-{m_ret:.2f}", 0, 1, 'R')
    
    pdf.set_x(130)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(40, 10, "TOTAL NETO:", 'T')
    pdf.cell(30, 10, f"{total:.2f} EUR", 'T', 1, 'R')

    # IBAN y Notas
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, f"FORMA DE PAGO (IBAN): {mi_iban}", 0, 1)
    pdf.set_font("Arial", 'I', 8)
    pdf.ln(2)
    pdf.multi_cell(0, 4, f"Nota: Operacion exenta de IVA segun Art. 20 Ley 37/1992.")
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.download_button("📩 DESCARGAR FACTURA PDF", data=crear_pdf(), file_name=f"Factura_{num_factura}.pdf")
