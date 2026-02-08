import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Facturador Compacto", layout="wide")

# --- INTERFAZ APP ---
st.title("📄 Generador de Factura Compacta")

with st.sidebar:
    st.header("⚙️ Ajustes")
    moneda = st.selectbox("Moneda", ["EUR", "USD", "SOL"], index=0)
    iva_p = st.number_input("IVA %", min_value=0, value=0)
    usa_ret = st.toggle("¿Retención IRPF?", value=True)
    ret_p = st.number_input("Retención %", min_value=0, value=15) if usa_ret else 0

with st.expander("👤 Datos Rápidos", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        mi_nombre = st.text_input("Mi Nombre", "DI ESTEFANO")
        mi_nif = st.text_input("Mi NIF", "B71537948")
        mi_dir = st.text_input("Mi Dirección", "Paseo Río Iratí Nº11 - 2do A")
        mi_iban = st.text_input("IBAN", "ES00...")
    with c2:
        c_nombre = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
        c_nif = st.text_input("NIF Cliente", "B31114051")
        c_dir = st.text_input("Dirección Cliente", "Galar 31191")

if 'n_filas' not in st.session_state: st.session_state.n_filas = 4

st.write("### 🧱 Detalle de Trabajos")
filas_data = []
for i in range(st.session_state.n_filas):
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    with col1: d = st.text_input(f"Desc {i+1}", key=f"d{i}")
    with col2: u = st.selectbox(f"Und", ["m2", "Ud", "ml", "kg"], key=f"u{i}")
    with col3: m = st.number_input(f"Cant", min_value=0.0, step=0.1, key=f"m{i}")
    with col4: p = st.number_input(f"P.Unit", min_value=0.0, step=0.01, key=f"p{i}")
    if d: filas_data.append({"desc": d, "uni": u, "cant": m, "pre": p, "sub": m*p})

btn1, btn2, _ = st.columns([1, 1, 4])
with btn1:
    if st.button("➕"): st.session_state.n_filas += 1; st.rerun()
with btn2:
    if st.button("➖") and st.session_state.n_filas > 1: st.session_state.n_filas -= 1; st.rerun()

subtotal = sum(f["sub"] for f in filas_data)
m_iva = subtotal * (iva_p / 100)
m_ret = subtotal * (ret_p / 100)
total_neto = subtotal + m_iva - m_ret

# --- FUNCIÓN PDF COMPACTO ---
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(10, 10, 10)
    
    # Cabecera Compacta
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "FACTURA DE TRABAJOS", 0, 1, 'C')
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(95, 4, "EMISOR", 0, 0)
    pdf.cell(95, 4, "RECEPTOR", 0, 1)
    
    pdf.set_font("Arial", '', 9)
    pdf.cell(95, 4, f"{mi_nombre} (NIF: {mi_nif})", 0, 0)
    pdf.cell(95, 4, f"{c_nombre} (NIF: {c_nif})", 0, 1)
    pdf.cell(95, 4, f"{mi_dir}", 0, 0)
    pdf.cell(95, 4, f"{c_dir}", 0, 1)
    pdf.ln(5)

    # Tabla sin espacios
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(90, 6, " Descripcion", 1, 0, 'L', True)
    pdf.cell(20, 6, "Und", 1, 0, 'C', True)
    pdf.cell(20, 6, "Cant", 1, 0, 'C', True)
    pdf.cell(30, 6, "Precio", 1, 0, 'C', True)
    pdf.cell(30, 6, "Total", 1, 1, 'C', True)

    pdf.set_font("Arial", '', 9)
    for f in filas_data:
        pdf.cell(90, 6, f" {f['desc']}", 1)
        pdf.cell(20, 6, f"{f['uni']}", 1, 0, 'C')
        pdf.cell(20, 6, f"{f['cant']}", 1, 0, 'C')
        pdf.cell(30, 6, f"{f['pre']:.2f}", 1, 0, 'C')
        pdf.cell(30, 6, f"{f['sub']:.2f}", 1, 1, 'R')

    # Totales e IBAN pegados
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_x(130)
    pdf.cell(40, 5, "Subtotal:", 0)
    pdf.cell(30, 5, f"{subtotal:.2f} {moneda}", 0, 1, 'R')
    pdf.set_x(130)
    pdf.cell(40, 5, f"IVA {iva_p}%:", 0)
    pdf.cell(30, 5, f"{m_iva:.2f} {moneda}", 0, 1, 'R')
    if usa_ret:
        pdf.set_x(130)
        pdf.cell(40, 5, f"IRPF -{ret_p}%:", 0)
        pdf.cell(30, 5, f"-{m_ret:.2f} {moneda}", 0, 1, 'R')
    
    pdf.set_x(130)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(40, 8, "TOTAL NETO:", 'T')
    pdf.cell(30, 8, f"{total_neto:.2f} {moneda}", 'T', 1, 'R')

    pdf.ln(2)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, f"PAGO (IBAN): {mi_iban}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.download_button("📩 DESCARGAR PDF", data=generar_pdf(), file_name="Factura_Compacta.pdf")
