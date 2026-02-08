import streamlit as st
from fpdf import FPDF

# Configuración básica
st.set_page_config(page_title="Factura", layout="wide")

# Título simple
st.write("# Factura Profesional")

# Datos de prueba rápidos
col1, col2 = st.columns(2)
with col1:
    emisor = st.text_input("Emisor", "DI ESTEFANO")
    iban = st.text_input("IBAN", "ES00...")
with col2:
    cliente = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")

# Función para crear el PDF sin errores de símbolos
def crear_pdf_limpio():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(40, 10, "FACTURA")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(40, 10, f"Emisor: {emisor}")
    pdf.ln(10)
    pdf.cell(40, 10, f"IBAN: {iban}")
    return pdf.output(dest="S").encode("latin-1", "replace")

st.divider()

# ESTE BOTÓN APARECERÁ SI PEGAS ESTE CÓDIGO NUEVO
st.download_button(
    label="📩 DESCARGAR FACTURA PDF",
    data=crear_pdf_limpio(),
    file_name="factura.pdf",
    mime="application/pdf"
)
