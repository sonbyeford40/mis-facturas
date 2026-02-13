import streamlit as st
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Facturador Pro", layout="wide")

# --- CABECERA ---
c1, c2 = st.columns(2)
with c1:
    num_f = st.text_input("Nº Factura", "2026-0001")
with c2:
    fec_f = st.text_input("Fecha", datetime.now().strftime("%d/%m/%Y"))

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

# --- TABLA ---
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

st.write("---")
col_imp, col_tot = st.columns(2)
with col_imp:
    p_iva = st.number_input("IVA (%)", value=21.0)
    p_irpf = st.number_input("IRPF (%)", value=15.0)
    txt_legal = st.text_area("Cláusula Legal", value="Operación sujeta a la Ley 37/1992 del IVA.")

base = sum(it["t"] for it in items)
val_iva = base * (p_iva / 100)
val_irpf = base * (p_irpf / 100)
total = base + val_iva - val_irpf

with col_tot:
    st.write(f"Base Imponible: {base:.2f} EUR")
    st.write(f"IVA ({p_iva}%): {val_iva:.2f} EUR")
    st.write(f"IRPF ({p_irpf}%): -{val_irpf:.2f} EUR")
    st.markdown(f"### TOTAL: {total:.2f} EUR")

# --- GENERADOR DE PDF ---
def crear_pdf():
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Función interna para evitar errores de caracteres
        def s(texto):
            return str(texto).encode('latin-1', 'replace').decode('latin-1')

        # Diseño del PDF
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "FACTURA", 0, 1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 7, s(f"Nº: {num_f} | Fecha: {fec_f}"), 0, 1, 'R')
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(95, 7, "EMISOR", 0, 0); pdf.cell(95, 7, "CLIENTE", 0, 1)
        
        pdf.set_font("Arial", '', 10)
        y_pos = pdf.get_y()
        pdf.multi_cell(90, 5, s(f"{mi_nom}\nNIF: {mi_nif}\n{mi_dir}"))
        pdf.set_xy(105, y_pos)
        pdf.multi_cell(90, 5, s(f"{cl_nom}\nNIF: {cl_nif}\n{cl_dir}"))
        
        pdf.ln(15)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(100, 8, "Descripcion", 1, 0, 'C', True)
        pdf.cell(25, 8, "Cant", 1, 0, 'C', True)
        pdf.cell(30, 8, "Precio", 1, 0, 'C', True)
        pdf.cell(35, 8, "Total", 1, 1, 'C', True)
        
        pdf.set_font("Arial", '', 9)
        for it in items:
            pdf.cell(100, 7, s(it["d"]), 1)
            pdf.cell(25, 7, s(it["m"]), 1, 0, 'C')
            pdf.cell(30, 7, f"{it['p']:.2f}", 1, 0, 'R')
            pdf.cell(35, 7, f"{it['t']:.2f}", 1, 1, 'R')

        pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(140, 7, "Base Imponible:", 0, 0, 'R')
        pdf.cell(50, 7, f"{base:.2f} EUR", 0, 1, 'R')
        pdf.cell(140, 7, s(f"IVA ({p_iva}%):"), 0, 0, 'R')
        pdf.cell(50, 7, f"{val_iva:.2f} EUR", 0, 1, 'R')
        pdf.cell(140, 7, s(f"IRPF ({p_irpf}%):"), 0, 0, 'R')
        pdf.cell(50, 7, f"-{val_irpf:.2f} EUR", 0, 1, 'R')
        pdf.cell(140, 10, "TOTAL:", 0, 0, 'R')
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(50, 10, f"{total:.2f} EUR", 1, 1, 'R')

        # Sección Legal e IBAN
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 8)
        pdf.multi_cell(0, 5, s(txt_legal))
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 10, s(f"IBAN: {mi_iba}"), 0, 1)

        # Retornar como bytes directamente
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        return str(e)

# --- BOTÓN DE DESCARGA CON SEGURIDAD ---
if items:
    try:
        pdf_data = crear_pdf()
        if isinstance(pdf_data, bytes):
            st.download_button(
                label="📩 DESCARGAR FACTURA PDF",
                data=pdf_data,
                file_name=f"Factura_{num_f}.pdf",
                mime="application/pdf"
            )
        else:
            st.error(f"Error al generar el PDF: {pdf_data}")
    except:
        st.error("Error crítico en la generación.")
else:
    st.warning("Debes completar al menos una fila de descripción.")
