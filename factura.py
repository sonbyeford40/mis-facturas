import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Facturador Pro", layout="wide")

# Limpieza visual de la web
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>""", unsafe_allow_index=True)

st.title("📄 Generador de Factura con Fecha")

# --- BLOQUE DE CABECERA (Nº Factura y Fecha) ---
with st.expander("👤 Configuración de Factura y Datos", expanded=True):
    col_num, col_fecha = st.columns(2)
    with col_num:
        # Soporta hasta 5000 cifras o cualquier formato de texto largo
        num_factura = st.text_input("Nº de Factura (hasta 5000 cifras)", "2026-0001")
    with col_fecha:
        # Por defecto sale la fecha de hoy, pero puedes cambiarla
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        fecha_factura = st.text_input("Fecha de Emisión", fecha_hoy)
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        mi_nombre = st.text_input("Mi Nombre/Empresa", "DI ESTEFANO")
        mi_nif = st.text_input("Mi NIF", "B71537948")
        mi_dir = st.text_input("Mi Dirección", "Paseo Río Iratí Nº11 - 2do A")
        mi_iban = st.text_input("IBAN para el cobro", "ES00...")
    with c2:
        c_nombre = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
        c_nif = st.text_input("NIF Cliente", "B31114051")
        c_dir = st.text_input("Dirección Cliente", "Galar 31191")

if 'filas' not in st.session_state: st.session_state.filas = 4

st.write("### 🧱 Detalle de Trabajos")
datos_tabla = []
for i in range(st.session_state.filas):
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    with col1: d = st.text_input(f"Descripción {i+1}", key=f"d{i}")
    with col2: u = st.selectbox(f"Und", ["m2", "Ud", "ml", "kg"], key=f"u{i}")
    with col3: m = st.number_input(f"Cant", min_value=0.0, format="%.2f", key=f"m{i}")
    with col4: p = st.number_input(f"Precio", min_value=0.0, format="%.2f", key=f"p{i}")
    if d: datos_tabla.append({"d": d, "u": u, "c": m, "p": p, "s": m*p})

b1, b2, _ = st.columns([1, 1, 4])
with b1:
    if st.button("➕ Añadir"): st.session_state.filas += 1; st.rerun()
with b2:
    if st.button("➖ Quitar") and st.session_state.filas > 1: st.session_state.filas -= 1; st.rerun()

# --- CÁLCULOS ---
iva_p = st.sidebar.number_input("IVA %", value=0)
ret_p = st.sidebar.number_input("Retención IRPF %", value=15)
subtotal = sum(f["s"] for f in datos_tabla)
m_iva = subtotal * (iva_p / 100)
m_ret = subtotal * (ret_p / 100)
total = subtotal + m_iva - m_ret

# --- GENERADOR PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Compacto
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(100, 10, "FACTURA", 0, 0)
    pdf.set_font("Arial", '', 10)
    pdf.cell(90, 10, f"Numero: {num_factura}  |  Fecha: {fecha_factura}", 0, 1, 'R')
    pdf.ln(5)
    
    # Datos Emisor/Receptor
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

    # Tabla
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

    # Totales e IBAN
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

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, f"FORMA DE PAGO (IBAN): {mi_iban}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.download_button("📩 DESCARGAR FACTURA PDF", data=crear_pdf(), file_name=f"Factura_{num_factura}.pdf")
