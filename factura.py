import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Facturador Autónomo", layout="centered")

st.title("📄 Generador de Facturas Profesional")

# --- DATOS DEL EMISOR Y CLIENTE ---
with st.expander("👤 Mis Datos y los de la SL", expanded=True):
    col_e, col_c = st.columns(2)
    with col_e:
        mi_nombre = st.text_input("Mi Nombre/Empresa", "DI ESTEFANO")
        mi_nif = st.text_input("Mi NIF", "B71537948")
        mi_dir = st.text_area("Mi Dirección", "Paseo Río Iratí Nº11 - 2do A")
        mi_iban = st.text_input("IBAN para el cobro", "ES00...")
    with col_c:
        c_nombre = st.text_input("Nombre de la SL", "ADANIA RESIDENCIAL S.L.")
        c_nif = st.text_input("NIF de la SL", "B31114051")
        c_dir = st.text_input("Dirección de la SL", "Galar 31191")

# --- CONCEPTOS ESTILO TU EXCEL ---
st.subheader("🛒 Servicios (Mediciones en m²)")
conceptos = []
c1, c2, c3 = st.columns([3, 1, 1])
d1 = c1.text_input("Descripción", value="Colocación de Perforado D 20")
m1 = c2.number_input("Cant. m²", min_value=0.0, value=0.0)
p1 = c3.number_input("Precio/m² (€)", min_value=0.0, value=0.0)
conceptos.append({"desc": d1, "cant": m1, "prec": p1})

if st.toggle("Añadir otra partida (ej. Golpe de llana)"):
    c1x, c2x, c3x = st.columns([3, 1, 1])
    dx = c1x.text_input("Descripción extra", key="dx")
    mx = c2x.number_input("Cant. m² extra", min_value=0.0, key="mx")
    px = c3x.number_input("Precio/m² extra (€)", min_value=0.0, key="px")
    if dx: conceptos.append({"desc": dx, "cant": mx, "prec": px})

# --- IMPUESTOS Y ARTÍCULO EDITABLE ---
st.divider()
col_iva, col_irpf = st.columns(2)
with col_iva:
    iva_val = st.selectbox("IVA %", [21, 10, 4, 0], index=3) # Por defecto 0%
with col_irpf:
    usa_irpf = st.checkbox("Aplicar Retención IRPF (15%)", value=True)
    irpf_val = 15 if usa_irpf else 0

st.subheader("⚖️ Nota Legal / Artículo IVA (Editable)")
# Texto sugerido si es exento
texto_sugerido = "Operación exenta de IVA según el Art. 20 de la Ley 37/1992." if iva_val == 0 else ""
nota_legal = st.text_area("Este texto aparecerá al pie de la factura:", value=texto_sugerido)

# --- CÁLCULOS ---
subtotal = sum(i["cant"] * i["prec"] for i in conceptos)
total_iva = subtotal * (iva_val / 100)
total_irpf = subtotal * (irpf_val / 100)
total_final = subtotal + total_iva - total_irpf

st.info(f"### TOTAL A COBRAR: {total_final:.2f} €")

# --- FUNCIÓN PARA GENERAR EL PDF ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FACTURA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 5, "EMISOR:", 0)
    pdf.cell(95, 5, "CLIENTE:", ln=1)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(95, 5, f"{mi_nombre}\nNIF: {mi_nif}\n{mi_dir}")
    pdf.set_y(pdf.get_y() - 15)
    pdf.set_x(105)
    pdf.multi_cell(95, 5, f"{c_nombre}\nNIF: {c_nif}\n{c_dir}")
    pdf.ln(15)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(90, 8, "Descripción", 1, 0, 'L', True)
    pdf.cell(30, 8, "Cant. m²", 1, 0, 'C', True)
    pdf.cell(30, 8, "Precio/m²", 1, 0, 'C', True)
    pdf.cell(30, 8, "Importe", 1, 1, 'C', True)
    for item in conceptos:
        if item["cant"] > 0:
            pdf.cell(90, 8, item["desc"], 1)
            pdf.cell(30, 8, f"{item['cant']}", 1, 0, 'C')
            pdf.cell(30, 8, f"{item['prec']:.2f}€", 1, 0, 'C')
            pdf.cell(30, 8, f"{item['cant']*item['prec']:.2f}€", 1, 1, 'C')
    pdf.ln(5)
    pdf.set_x(130)
    pdf.cell(40, 7, "Subtotal:", 0, 0, 'R')
    pdf.cell(30, 7, f"{subtotal:.2f}€", 0, 1, 'R')
    pdf.set_x(130)
    pdf.cell(40, 7, f"IVA ({iva_val}%):", 0, 0, 'R')
    pdf.cell(30, 7, f"{total_iva:.2f}€", 0, 1, 'R')
    if usa_irpf:
        pdf.set_x(130)
        pdf.cell(40, 7, "IRPF (-15%):", 0, 0, 'R')
        pdf.cell(30, 7, f"-{total_irpf:.2f}€", 0, 1, 'R')
    pdf.set_x(130)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, "TOTAL:", 0, 0, 'R')
    pdf.cell(30, 10, f"{total_final:.2f}€", 0, 1, 'R')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, f"IBAN para el pago: {mi_iban}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, nota_legal)
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# --- BOTONES ---
if st.download_button("📥 Descargar PDF para Imprimir", data=crear_pdf(), file_name="Factura.pdf"):
    st.success("¡PDF Generado!")