import streamlit as st
from fpdf import FPDF
from datetime import datetime

# 1. Configuración de página
st.set_page_config(page_title="Facturador Flexible", page_icon="📊", layout="wide")

# --- CABECERA ---
c1, c2 = st.columns(2)
with c1:
    num_f = st.text_input("Nº Factura", "2026-0001")
with c2:
    fec_f = st.date_input("Fecha", datetime.now()).strftime("%d/%m/%Y")

# --- DATOS ---
st.write("---")
col_e, col_c = st.columns(2)
with col_e:
    st.markdown("**EMISOR**")
    mi_nom = st.text_input("Mi Nombre", "DI ESTEFANO")
    mi_nif = st.text_input("Mi NIF", "B71537948")
    mi_dir = st.text_input("Mi Dirección", "Paseo Rio Irati 11")
    mi_iba = st.text_input("Mi IBAN", "ES00...")
with col_c:
    st.markdown("**CLIENTE**")
    cl_nom = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
    cl_nif = st.text_input("NIF Cliente", "B31114051")
    cl_dir = st.text_input("Dirección Cliente", "Galar 31191")

st.write("---")

# --- TABLA DINÁMICA ---
if 'filas' not in st.session_state: st.session_state.filas = 3
items = []
for i in range(st.session_state.filas):
    ca, cb, cc, cd = st.columns([4, 1, 1, 1])
    with ca: d = st.text_input(f"Descripción {i+1}", key=f"d{i}")
    with cb: u = st.text_input(f"Unid", value="Ud", key=f"u{i}")
    with cc: m = st.number_input(f"Cant", key=f"m{i}", min_value=0.0)
    with cd: p = st.number_input(f"Precio", key=f"p{i}", min_value=0.0)
    if d: items.append({"d": d, "u": u, "m": m, "p": p, "t": m*p})

if st.button("➕ Añadir otra fila"):
    st.session_state.filas += 1
    st.rerun()

# --- IMPUESTOS EDITABLES Y TOTALES ---
st.write("---")
col_imp, col_res = st.columns(2)

with col_imp:
    st.markdown("**Configuración de Impuestos**")
    # Campos para editar los porcentajes
    p_iva = st.number_input("Porcentaje IVA (%)", value=21.0, step=1.0)
    p_irpf = st.number_input("Porcentaje IRPF (%)", value=15.0, step=1.0)
    txt_legal = st.text_area("Cláusula Legal / Notas", 
                             value="Operación sujeta a la Ley 37/1992 del IVA.")

with col_res:
    base = sum(it["t"] for it in items)
    val_iva = base * (p_iva / 100)
    val_irpf = base * (p_irpf / 100)
    total = base + val_iva - val_irpf

    st.write(f"**Base Imponible:** {base:.2f} EUR")
    st.write(f"**IVA ({p_iva}%):** +{val_iva:.2f} EUR")
    st.write(f"**IRPF ({p_irpf}%):** -{val_irpf:.2f} EUR")
    st.markdown(f"## TOTAL A COBRAR: {total:.2f} EUR")

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'L')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"Numero: {num_f}  |  Fecha: {fec_f}", 0, 1, 'R')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 7, "EMISOR", 0, 0); pdf.cell(95, 7, "CLIENTE", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(95, 5, f"{mi_nom}\nNIF: {mi_nif}\n{mi_dir}")
    
    # Tabla
    pdf.ln(10)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(100, 8, "Descripcion", 1, 0, 'C', True)
    pdf.cell(30, 8, "Cant", 1, 0, 'C', True)
    pdf.cell(30, 8, "Precio", 1, 0, 'C', True)
    pdf.cell(30, 8, "Total", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 9)
    for it in items:
        pdf.cell(100, 7, it["d"], 1)
        pdf.cell(30, 7, str(it["m"]), 1, 0, 'C')
        pdf.cell(30, 7, f"{it['p']:.2f}", 1, 0, 'R')
        pdf.cell(30, 7, f"{it['t']:.2f}", 1, 1, 'R')

    # Totales en PDF
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(130, 7, f"Base Imponible:", 0, 0, 'R')
    pdf.cell(60, 7, f"{base:.2f} EUR", 0, 1, 'R')
    pdf.cell(130, 7, f"IVA ({p_iva}%):", 0, 0, 'R')
    pdf.cell(60, 7, f"+{val_iva:.2f} EUR", 0, 1, 'R')
    pdf.cell(130, 7, f"IRPF ({p_irpf}%):", 0, 0, 'R')
    pdf.cell(60, 7, f"-{val_irpf:.2f} EUR", 0, 1, 'R')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(130, 10, "TOTAL A COBRAR:", 0, 0, 'R')
    pdf.cell(60, 10, f"{total:.2f} EUR", 1, 1, 'R')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, f"IBAN: {mi_iba}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.download_button("📩 DESCARGAR FACTURA PDF", data=crear_pdf(), file_name=f"Factura_{num_f}.pdf")
