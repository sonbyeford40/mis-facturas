import streamlit as st
from fpdf import FPDF
from datetime import datetime
import json
import os

# --- CONFIGURACIÓN Y PERSISTENCIA ---
st.set_page_config(page_title="Facturador Pro con Memoria", layout="wide")
PERFIL_FILE = "perfil_emisor.json"

def guardar_perfil(datos):
    with open(PERFIL_FILE, "w") as f:
        json.dump(datos, f)
    st.success("✅ ¡Datos guardados para la próxima vez!")

def cargar_perfil():
    if os.path.exists(PERFIL_FILE):
        with open(PERFIL_FILE, "r") as f:
            return json.load(f)
    return {}

perfil_guardado = cargar_perfil()

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
    st.markdown("### 🏦 MIS DATOS (EMISOR)")
    # Cargamos el valor por defecto desde el JSON si existe
    mi_nom = st.text_input("Mi Nombre/Empresa", perfil_guardado.get("nom", "DI ESTEFANO"))
    mi_nif = st.text_input("Mi NIF", perfil_guardado.get("nif", "B71537948"))
    mi_dir = st.text_input("Mi Dirección", perfil_guardado.get("dir", "Paseo Rio Irati 11"))
    mi_iba = st.text_input("Mi IBAN", perfil_guardado.get("iba", "ES00..."))
    
    if st.button("💾 Guardar mis datos por defecto"):
        datos_a_guardar = {"nom": mi_nom, "nif": mi_nif, "dir": mi_dir, "iba": mi_iba}
        guardar_perfil(datos_a_guardar)

with col_c:
    st.markdown("### 👤 CLIENTE")
    cl_nom = st.text_input("Cliente", "ADANIA RESIDENCIAL S.L.")
    cl_nif = st.text_input("NIF Cliente", "B31114051")
    cl_dir = st.text_input("Dirección Cliente", "Galar 31191")

st.write("---")

# --- TABLA DINÁMICA ---
if 'filas' not in st.session_state: st.session_state.filas = 3
items = []
st.markdown("#### Conceptos")
for i in range(st.session_state.filas):
    ca, cb, cc, cd = st.columns([4, 1, 1, 1])
    with ca: d = st.text_input(f"Descripción", key=f"d{i}")
    with cb: u = st.text_input(f"Unid", value="Ud", key=f"u{i}")
    with cc: m = st.number_input(f"Cant", key=f"m{i}", min_value=0.0, step=1.0)
    with cd: p = st.number_input(f"Precio", key=f"p{i}", min_value=0.0, step=0.01)
    if d: items.append({"d": d, "u": u, "m": m, "p": p, "t": m*p})

if st.button("➕ Añadir concepto"):
    st.session_state.filas += 1
    st.rerun()

# --- IMPUESTOS Y TOTALES ---
st.write("---")
col_l, col_r = st.columns(2)
with col_l:
    p_iva = st.number_input("IVA (%)", value=21.0)
    p_irpf = st.number_input("IRPF (%)", value=15.0)
    txt_legal = st.text_area("Notas / Ley", value="Operación sujeta a la Ley 37/1992 del IVA.")

base = sum(it["t"] for it in items)
val_iva = base * (p_iva / 100)
val_irpf = base * (p_irpf / 100)
total = base + val_iva - val_irpf

with col_r:
    st.write(f"Base Imponible: {base:,.2f} EUR")
    st.write(f"IVA ({p_iva}%): +{val_iva:,.2f} EUR")
    st.write(f"IRPF ({p_irpf}%): -{val_irpf:,.2f} EUR")
    st.markdown(f"## TOTAL: {total:,.2f} EUR")

# --- GENERADOR PDF SEGURO ---
def crear_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    def s(texto): # Limpiador de caracteres para latin-1
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

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
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 8, "Descripcion", 1, 0, 'C', True)
    pdf.cell(25, 8, "Cant", 1, 0, 'C', True)
    pdf.cell(30, 8, "Precio", 1, 0, 'C', True)
    pdf.cell(35, 8, "Total", 1, 1, 'C', True)
    
    for it in items:
        pdf.set_font("Arial", '', 9)
        pdf.cell(100, 7, s(it["d"]), 1)
        pdf.cell(25, 7, s(it["m"]), 1, 0, 'C')
        pdf.cell(30, 7, f"{it['p']:.2f}", 1, 0, 'R')
        pdf.cell(35, 7, f"{it['t']:.2f}", 1, 1, 'R')

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 7, "Base:", 0, 0, 'R')
    pdf.cell(50, 7, f"{base:.2f} EUR", 0, 1, 'R')
    pdf.cell(140, 7, s(f"IVA ({p_iva}%):"), 0, 0, 'R')
    pdf.cell(50, 7, f"{val_iva:.2f} EUR", 0, 1, 'R')
    pdf.cell(140, 7, s(f"IRPF ({p_irpf}%):"), 0, 0, 'R')
    pdf.cell(50, 7, f"-{val_irpf:.2f} EUR", 0, 1, 'R')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "TOTAL A COBRAR:", 0, 0, 'R')
    pdf.cell(50, 10, f"{total:.2f} EUR", 1, 1, 'R')

    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, s(txt_legal))
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, s(f"FORMA DE PAGO (IBAN): {mi_iba}"), 0, 1)

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- BOTÓN DESCARGA ---
if items:
    btn_data = crear_pdf()
    st.download_button(label="📩 DESCARGAR FACTURA PDF", data=btn_data, file_name=f"Factura_{num_f}.pdf", mime="application/pdf")
else:
    st.info("Escribe algo en la descripción para habilitar la descarga.")
