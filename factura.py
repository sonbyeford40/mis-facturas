import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Facturador Internacional", layout="wide")

# --- INTERFAZ DE USUARIO ---
st.title("🚀 Facturador Profesional Global")

with st.sidebar:
    st.header("🌍 Configuración Regional")
    moneda = st.selectbox("Moneda", ["€", "$", "S/.", "Mex$", "CLP", "Bs."], index=0)
    st.info("Configura los impuestos y la moneda aquí.")

with st.expander("👤 Datos de Emisor y Cliente", expanded=False):
    col_e, col_c = st.columns(2)
    with col_e:
        st.markdown("**Mis Datos (Emisor)**")
        mi_nombre = st.text_input("Nombre/Empresa", "DI ESTEFANO")
        mi_nif = st.text_input("Identificación (NIF/DNI/RUC)", "B71537948")
        mi_dir = st.text_area("Dirección Física", "Paseo Río Iratí Nº11 - 2do A")
        mi_iban = st.text_input("Cuenta de Pago (IBAN/Zelle/CBU)", "ES00...")
    with col_c:
        st.markdown("**Datos del Cliente**")
        c_nombre = st.text_input("Razón Social", "ADANIA RESIDENCIAL S.L.")
        c_nif = st.text_input("Identificación Cliente", "B31114051")
        c_dir = st.text_input("Dirección Cliente", "Galar 31191")

st.divider()

# --- GESTIÓN DE FILAS (HASTA 50) ---
if 'n_filas' not in st.session_state: st.session_state.n_filas = 4

st.subheader("📝 Detalle de Servicios y Mediciones")
filas_data = []

for i in range(st.session_state.n_filas):
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
    with c1:
        d = st.text_input(f"Descripción del trabajo {i+1}", key=f"d{i}")
    with c2:
        u = st.selectbox(f"Unidad {i+1}", ["m²", "Ud", "ml", "kg", "m³", "h", "Global"], key=f"u{i}")
    with c3:
        m = st.number_input(f"Cantidad {i+1}", min_value=0.0, step=0.1, key=f"m{i}")
    with c4:
        p = st.number_input(f"Precio ({moneda}) {i+1}", min_value=0.0, step=0.01, key=f"p{i}")
    
    if d:
        filas_data.append({"desc": d, "uni": u, "cant": m, "pre": p, "sub": m*p})

# Botones de control de filas
col_b1, col_b2, _ = st.columns([1, 1, 4])
with col_b1:
    if st.button("➕ Añadir Línea") and st.session_state.n_filas < 50:
        st.session_state.n_filas += 1
        st.rerun()
with col_b2:
    if st.button("➖ Quitar Línea") and st.session_state.n_filas > 1:
        st.session_state.n_filas -= 1
        st.rerun()

st.divider()

# --- IMPUESTOS Y DESGLOSE ---
col_iva, col_irpf = st.columns(2)
with col_iva:
    iva_p = st.number_input("IVA / Tax %", min_value=0, max_value=100, value=0)
with col_irpf:
    usa_ret = st.toggle("¿Aplicar Retención (IRPF/Otros)?", value=True)
    ret_p = st.number_input("Retención %", min_value=0, max_value=100, value=15) if usa_ret else 0

# Cálculos
subtotal = sum(f["sub"] for f in filas_data)
monto_iva = subtotal * (iva_p / 100)
monto_ret = subtotal * (ret_p / 100)
total_neto = subtotal + monto_iva - monto_ret

# Mostrar resultados en la app
st.subheader("💰 Resumen de la Factura")
c_r1, c_r2, c_r3, c_r4 = st.columns(4)
c_r1.metric("Subtotal", f"{subtotal:.2f} {moneda}")
c_r2.metric(f"IVA ({iva_p}%)", f"{monto_iva:.2f} {moneda}")
c_r3.metric(f"Retención (-{ret_p}%)", f"-{monto_ret:.2f} {moneda}")
c_r4.subheader(f"TOTAL: {total_neto:.2f} {moneda}")

nota_legal = st.text_area("Nota legal al pie", "Operación exenta de IVA según Art. 20 Ley 37/1992 (Inversión Sujeto Pasivo).")

# --- GENERACIÓN DEL PDF ---
def generar_pdf_global():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FACTURA PROFESIONAL", 0, 1, 'C')
    pdf.ln(5)
    
    # Bloque de datos
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 5, "EMISOR / PROVIDER", 0, 0)
    pdf.cell(95, 5, "CLIENTE / CUSTOMER", 0, 1)
    
    pdf.set_font("Arial", '', 10)
    y_actual = pdf.get_y()
    pdf.multi_cell(90, 5, f"{mi_nombre}\nID: {mi_nif}\n{mi_dir}")
    pdf.set_y(y_actual)
    pdf.set_x(105)
    pdf.multi_cell(90, 5, f"{c_nombre}\nID: {c_nif}\n{c_dir}")
    pdf.ln(10)

    # Tabla de contenidos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(85, 8, "Descripción", 1, 0, 'L', True)
    pdf.cell(20, 8, "Unidad", 1, 0, 'C', True)
    pdf.cell(25, 8, "Cant.", 1, 0, 'C', True)
    pdf.cell(30, 8, "Precio", 1, 0, 'C', True)
    pdf.cell(30, 8, "Total", 1, 1, 'C', True)

    pdf.set_font("Arial", '', 9)
    for f in filas_data:
        pdf.cell(85, 7, f["desc"], 1)
        pdf.cell(20, 7, f["uni"], 1, 0, 'C')
        pdf.cell(25, 7, f"{f['cant']}", 1, 0, 'C')
        pdf.cell(30, 7, f"{f['pre']:.2f} {moneda}", 1, 0, 'C')
        pdf.cell(30, 7, f"{f['sub']:.2f} {moneda}", 1, 1, 'R')

    # Totales desglosados
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pos_x = 130
    pdf.set_x(pos_x)
    pdf.cell(40, 7, "Subtotal:", 0)
    pdf.cell(30, 7, f"{subtotal:.2f} {moneda}", 1, 1, 'R')
    
    pdf.set_x(pos_x)
    pdf.cell(40, 7, f"IVA ({iva_p}%):", 0)
    pdf.cell(30, 7, f"{monto_iva:.2f} {moneda}", 1, 1, 'R')
    
    if usa_ret:
        pdf.set_x(pos_x)
        pdf.cell(40, 7, f"Retención (-{ret_p}%):", 0)
        pdf.cell(30, 7, f"-{monto_ret:.2f} {moneda}", 1, 1, 'R')
    
    pdf.ln(2)
    pdf.set_x(pos_x)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(255, 255, 200)
    pdf.cell(40, 10, "TOTAL NETO:", 0)
    pdf.cell(30, 10, f"{total_neto:.2f} {moneda}", 1, 1, 'R', True)

    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, f"FORMA DE PAGO / CUENTA: {mi_iban}", 0, 1)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, f"\nNOTAS: {nota_legal}")

    return pdf.output(dest='S').encode('latin-1', 'replace')

if st.download_button("📩 Descargar Factura PDF", data=generar_pdf_global(), file_name="Factura_Internacional.pdf"):
    st.balloons()
