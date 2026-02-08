import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Facturador Pro", layout="wide")

# --- INICIO DEL CÓDIGO ACTUALIZADO ---
st.title("📄 Generador de Facturas Profesional")

# Datos fijos para que no los tengas que escribir siempre
with st.expander("👤 Configuración Emisor y Cliente", expanded=False):
    col_e, col_c = st.columns(2)
    with col_e:
        nombre_emisor = st.text_input("Mi Nombre", "DI ESTEFANO")
        nif_emisor = st.text_input("Mi NIF", "B71537948")
        dir_emisor = st.text_area("Mi Dirección", "Paseo Río Iratí Nº11 - 2do A")
        iban = st.text_input("Mi IBAN", "ES00...")
    with col_c:
        nombre_clie = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
        nif_clie = st.text_input("NIF Cliente", "B31114051")
        dir_clie = st.text_input("Dirección Cliente", "Galar 31191")

st.divider()

# --- FILAS DINÁMICAS (Hasta 50) ---
if 'n_filas' not in st.session_state:
    st.session_state.n_filas = 4

st.subheader("🛒 Servicios y Mediciones")
filas_data = []

for i in range(st.session_state.n_filas):
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        d = st.text_input(f"Descripción {i+1}", key=f"d{i}")
    with c2:
        m = st.number_input(f"Metros {i+1}", min_value=0.0, step=0.1, key=f"m{i}")
    with c3:
        p = st.number_input(f"Precio {i+1}", min_value=0.0, step=0.01, key=f"p{i}")
    if d:
        filas_data.append({"desc": d, "mts": m, "pre": p, "sub": m*p})

col_b1, col_b2, _ = st.columns([1, 1, 4])
with col_b1:
    if st.button("➕ Añadir Fila") and st.session_state.n_filas < 50:
        st.session_state.n_filas += 1
        st.rerun()
with col_b2:
    if st.button("➖ Quitar Fila") and st.session_state.n_filas > 1:
        st.session_state.n_filas -= 1
        st.rerun()

st.divider()

# --- IMPUESTOS Y TOTALES ---
c_iva, c_irpf = st.columns(2)
with c_iva:
    iva_p = st.selectbox("IVA %", [0, 4, 10, 21], index=0)
with c_irpf:
    usa_irpf = st.toggle("Aplicar Retención IRPF (15%)", value=True)
    irpf_p = 15 if usa_irpf else 0

subtotal = sum(f["sub"] for f in filas_data)
iva_tot = subtotal * (iva_p/100)
irpf_tot = subtotal * (irpf_p/100)
total_final = subtotal + iva_tot - irpf_tot

st.subheader(f"Total a Percibir: {total_final:.2f} €")

nota_pie = st.text_area("Nota Legal / IVA 0%", "Operación exenta de IVA según Art. 20 Ley 37/1992.")

# --- FUNCIÓN PARA EL PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'C')
    pdf.ln(5)
    
    # Cabeceras emisor/receptor
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 5, f"EMISOR: {nombre_emisor}", 0, 0)
    pdf.cell(95, 5, f"CLIENTE: {nombre_clie}", 0, 1)
    pdf.cell(95, 5, f"NIF: {nif_emisor}", 0, 0)
    pdf.cell(95, 5, f"NIF: {nif_clie}", 0, 1)
    pdf.multi_cell(0, 5, f"DIR: {dir_emisor}")
    pdf.ln(10)

    # Tabla de productos
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 8, "Descripción", 1)
    pdf.cell(30, 8, "Cant/Mts", 1)
    pdf.cell(30, 8, "Precio", 1)
    pdf.cell(30, 8, "Total", 1, 1)

    pdf.set_font("Arial", '', 9)
    for f in filas_data:
        pdf.cell(100, 7, f["desc"], 1)
        pdf.cell(30, 7, f"{f['mts']}", 1)
        pdf.cell(30, 7, f"{f['pre']:.2f}", 1)
        pdf.cell(30, 7, f"{f['sub']:.2f}", 1, 1)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(160, 7, "SUBTOTAL:", 0, 0, 'R')
    pdf.cell(30, 7, f"{subtotal:.2f}€", 1, 1, 'R')
    if usa_irpf:
        pdf.cell(160, 7, "IRPF (-15%):", 0, 0, 'R')
        pdf.cell(30, 7, f"-{irpf_tot:.2f}€", 1, 1, 'R')
    pdf.cell(160, 10, "TOTAL NETO:", 0, 0, 'R')
    pdf.cell(30, 10, f"{total_final:.2f}€", 1, 1, 'R')

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, f"IBAN: {iban}", 0, 1)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, nota_pie)

    return pdf.output(dest='S').encode('latin-1')

if st.download_button("Descargar Factura PDF", data=crear_pdf(), file_name="Factura.pdf"):
    st.success("¡PDF Generado!")
