import streamlit as st
from fpdf import FPDF
from datetime import datetime

# 1. Configuración de página
st.set_page_config(page_title="Facturador Pro", layout="wide")

# --- CABECERA ---
c1, c2 = st.columns(2)
with c1:
    num_f = st.text_input("Nº Factura", "2026-0001")
with c2:
    fec_f = st.text_input("Fecha", datetime.now().strftime("%d/%m/%Y"))

# --- DATOS COMPACTOS ---
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

# --- CLAUSULA PERSONALIZADA ---
st.write("---")
txt_legal = st.text_area("Cláusula Legal / Notas adicionales", 
                         value="Operación sujeta a la Ley 37/1992 del IVA. En caso de inversión del sujeto pasivo, se aplica el artículo 84.Uno.2 de dicha Ley.")

# --- TOTALES ---
base = sum(it["t"] for it in items)
iva = base * 0.21
irpf = base * 0.15
total = base + iva - irpf

col_res1, col_res2 = st.columns(2)
with col_res2:
    st.write(f"Base Imponible: {base:.2f} EUR")
    st.write(f"IVA (21%): +{iva:.2f} EUR")
    st.write(f"IRPF (15%): -{irpf:.2f} EUR")
    st.write(f"### TOTAL A COBRAR: {total:.2f} EUR")

# --- GENERADOR DE PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FACTURA", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 7, f"Numero: {num_f}  |  Fecha: {fec_f}", 0, 1, 'R')
    
    # Datos
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 7, "EMISOR", 0, 0); pdf.cell(95, 7, "CLIENTE", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 5, mi_nom, 0, 0); pdf.cell(95, 5, cl_nom, 0, 1)
    pdf.cell(95, 5, f"NIF: {mi_nif}", 0, 0); pdf.cell(95, 5, f"NIF: {cl_nif}", 0, 1)
    pdf.cell(95, 5, mi_dir, 0, 0); pdf.cell(95, 5, cl_dir, 0, 1)

    # Tabla
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(100, 8, "Descripcion", 1, 0, 'C', True)
    pdf.cell(30, 8, "Cant", 1, 0, 'C', True)
    pdf.cell(30, 8, "Precio", 1, 0, 'C', True)
    pdf.cell(30, 8, "Total", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 9)
    for it in items:
        pdf.cell(100, 7, it["d"], 1)
        pdf.cell(30, 7, str(it["m"]), 1, 0, 'C')
        pdf.cell(30, 7, f"{it['p']:.2f}", 1, 0, 'C')
        pdf.cell(30, 7, f"{it['t']:.2f}", 1, 1, 'C')

    # Totales
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(130, 7, "", 0)
    pdf.cell(30, 7, "TOTAL EUR:", 0, 0, 'R')
    pdf.cell(30, 7, f"{total:.2f}", 1, 1, 'R')
    
    # CLAUSULA DINÁMICA
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, txt_legal.encode('latin-1', 'replace').decode('latin-1'))
    
    # IBAN
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, f"FORMA DE PAGO (IBAN): {mi_iba}", 0, 1)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

st.download_button("📩 DESCARGAR FACTURA PDF", data=crear_pdf(), file_name=f"Factura_{num_f}.pdf")
