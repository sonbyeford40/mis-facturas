import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Facturador Pro", layout="wide")

# --- INTERFAZ ---
st.title("📄 Generador de Facturas Profesional")

with st.sidebar:
    st.header("⚙️ Ajustes")
    moneda = st.selectbox("Moneda", ["€", "$", "S/.", "Mex$", "CLP"], index=0)
    iva_p = st.number_input("IVA %", min_value=0, value=0)
    usa_ret = st.toggle("Aplicar Retención (IRPF)", value=True)
    ret_p = st.number_input("Retención %", min_value=0, value=15) if usa_ret else 0

with st.expander("👤 Datos de Emisor y Cliente", expanded=False):
    col_e, col_c = st.columns(2)
    with col_e:
        mi_nombre = st.text_input("Mi Nombre", "DI ESTEFANO")
        mi_nif = st.text_input("Mi NIF", "B71537948")
        mi_dir = st.text_area("Mi Dirección", "Paseo Río Iratí Nº11 - 2do A")
        mi_iban = st.text_input("IBAN para el cobro", "ES00...")
    with col_c:
        c_nombre = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
        c_nif = st.text_input("NIF Cliente", "B31114051")
        c_dir = st.text_input("Dirección Cliente", "Galar 31191")

st.divider()

# --- FILAS DINÁMICAS ---
if 'n_filas' not in st.session_state: st.session_state.n_filas = 4

st.subheader("📝 Conceptos")
filas_data = []

for i in range(st.session_state.n_filas):
    c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
    with c1:
        d = st.text_input(f"Descripción {i+1}", key=f"d{i}", placeholder="Ej: Colocación de Perforado...")
    with c2:
        u = st.selectbox(f"Unidad", ["m²", "Ud", "ml", "kg"], key=f"u{i}")
    with c3:
        m = st.number_input(f"Cant.", min_value=0.0, step=0.1, key=f"m{i}")
    with c4:
        p = st.number_input(f"Precio", min_value=0.0, step=0.01, key=f"p{i}")
    if d:
        filas_data.append({"desc": d, "uni": u, "cant": m, "pre": p, "sub": m*p})

# Botones (SOLO SE VEN EN LA APP, NO EN EL PDF)
c_b1, c_b2, _ = st.columns([1, 1, 4])
with c_b1:
    if st.button("➕ Añadir"):
        st.session_state.n_filas += 1
        st.rerun()
with c_b2:
    if st.button("➖ Quitar") and st.session_state.n_filas > 1:
        st.session_state.n_filas -= 1
        st.rerun()

# --- CÁLCULOS ---
subtotal = sum(f["sub"] for f in filas_data)
monto_iva = subtotal * (iva_p / 100)
monto_ret = subtotal * (ret_p / 100)
total_neto = subtotal + monto_iva - monto_ret

st.divider()
st.subheader(f"TOTAL: {total_neto:.2f} {moneda}")

nota_legal = st.text_area("Nota legal", "Operación exenta de IVA según Art. 20 Ley 37/1992.")

# --- GENERADOR PDF MEJORADO ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'C')
    pdf.ln(5)
    
    # Cabecera
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 5, "EMISOR", 0, 0)
    pdf.cell(95, 5, "CLIENTE", 0, 1)
    pdf.set_font("Arial", '', 10)
    y_antes = pdf.get_y()
    pdf.multi_cell(90, 5, f"{mi_nombre}\nNIF: {mi_nif}\n{mi_dir}")
    pdf.set_y(y_antes)
    pdf.set_x(105)
    pdf.multi_cell(90, 5, f"{c_nombre}\nNIF: {c_nif}\n{c_dir}")
    pdf.ln(10)

    # TABLA UNIFICADA (Sin cuadros separados)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 8, " Descripción", 1, 0, 'L', True)
    pdf.cell(20, 8, "Unidad", 1, 0, 'C', True)
    pdf.cell(20, 8, "Cant.", 1, 0, 'C', True)
    pdf.cell(30, 8, "Precio", 1, 0, 'C', True)
    pdf.cell(30, 8, "Total", 1, 1, 'C', True)

    pdf.set_font("Arial", '', 9)
    for f in filas_data:
        # Dibujamos las celdas de la fila
        pdf.cell(90, 7, f" {f['desc']}", 1)
        pdf.cell(20, 7, f"{f['uni']}", 1, 0, 'C')
        pdf.cell(20, 7, f"{f['cant']}", 1, 0, 'C')
        pdf.cell(30, 7, f"{f['pre']:.2f} {moneda}", 1, 0, 'C')
        pdf.cell(30, 7, f"{f['sub']:.2f} {moneda}", 1, 1, 'R')

    # TOTALES E IBAN (Todo en un bloque visible)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_x(130)
    pdf.cell(40, 7, "Subtotal:", 0)
    pdf.cell(30, 7, f"{subtotal:.2f} {moneda}", 0, 1, 'R')
    
    pdf.set_x(130)
    pdf.cell(40, 7, f"IVA ({iva_p}%):", 0)
    pdf.cell(30, 7, f"{monto_iva:.2f} {moneda}", 0, 1, 'R')
    
    if usa_ret:
        pdf.set_x(130)
        pdf.cell(40, 7, f"IRPF (-{ret_p}%):", 0)
        pdf.cell(30, 7, f"-{monto_ret:.2f} {moneda}", 0, 1, 'R')
    
    pdf.set_x(130)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, "TOTAL NETO:", 'T')
    pdf.cell(30, 10, f"{total_neto:.2f} {moneda}", 'T', 1, 'R')

    # IBAN REUBICADO Y VISIBLE ABAJO DE LOS TOTALES
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 0, 128) # Azul oscuro para que resalte
    pdf.cell(0, 10, f"IBAN PARA EL PAGO: {mi_iban}", 0, 1, 'L')
    
    # Nota legal
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'I', 8)
    pdf.ln(5)
    pdf.multi_cell(0, 5, f"Notas: {nota_legal}")

    return pdf.output(dest='S').encode('latin-1', 'replace')

st.download_button("📥 Descargar Factura PDF", data=crear_pdf(), file_name="Factura.pdf")
