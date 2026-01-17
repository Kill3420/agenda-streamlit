import streamlit as st
import mysql.connector
from datetime import datetime, date
import time
import pytz
import os
from PIL import Image

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Agenda Android", layout="centered")
st.title("📱 Agenda Multifunción")

# ---------------- DB MYSQL ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",              # CAMBIA SI TU USUARIO ES OTRO
    password="6234", # CAMBIA ESTO
    database="agenda_db"
)
c = conn.cursor()

# ---------------- FOTOS ----------------
os.makedirs("fotos", exist_ok=True)

# ---------------- MENÚ ----------------
menu = st.sidebar.radio(
    "Menú",
    ["📝 Agenda", "⏰ Reloj", "⏱️ Cronómetro", "⏳ Temporizador", "🌍 Reloj Mundial"]
)

# ==================================================
# 📝 AGENDA
# ==================================================
if menu == "📝 Agenda":
    st.header("📝 Agenda")

    descripcion = st.text_input("Descripción")
    fecha = st.date_input("Fecha", date.today())
    foto = st.file_uploader("Agregar foto", type=["jpg", "png"])

    if st.button("Guardar"):
        nombre_foto = None

        if foto:
            nombre_foto = f"fotos/{int(time.time())}_{foto.name}"
            image = Image.open(foto)
            image.save(nombre_foto)

        c.execute(
            "INSERT INTO agenda (descripcion, fecha, foto) VALUES (%s, %s, %s)",
            (descripcion, fecha, nombre_foto)
        )
        conn.commit()
        st.success("✅ Registro guardado")

    st.divider()
    st.subheader("📋 Registros")

    c.execute("SELECT id, descripcion, fecha, foto FROM agenda ORDER BY id DESC")
    rows = c.fetchall()

    for r in rows:
        col1, col2 = st.columns([1, 3])

        with col1:
            if r[3]:
                st.image(r[3], width=120)
            else:
                st.text("Sin foto")

        with col2:
            st.write(f"📝 **{r[1]}**")
            st.write(f"📅 {r[2]}")

            if st.button("🗑️ Borrar", key=f"del_{r[0]}"):
                c.execute("DELETE FROM agenda WHERE id=%s", (r[0],))
                conn.commit()
                st.experimental_rerun()

        st.divider()


# ==================================================
# ⏰ RELOJ
# ==================================================
elif menu == "⏰ Reloj":
    st.header("⏰ Reloj en tiempo real")
    placeholder = st.empty()

    while True:
        now = datetime.now().strftime("%H:%M:%S")
        placeholder.metric("Hora actual", now)
        time.sleep(1)

# ==================================================
# ⏱️ CRONÓMETRO
# ==================================================
elif menu == "⏱️ Cronómetro":
    st.header("⏱️ Cronómetro")

    if "cronometro" not in st.session_state:
        st.session_state.cronometro = False
        st.session_state.start_time = 0

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Iniciar"):
            st.session_state.cronometro = True
            st.session_state.start_time = time.time()

    with col2:
        if st.button("⏹ Detener"):
            st.session_state.cronometro = False

    if st.session_state.cronometro:
        elapsed = time.time() - st.session_state.start_time
        st.metric("Tiempo", f"{elapsed:.2f} segundos")

# ==================================================
# ⏳ TEMPORIZADOR
# ==================================================
elif menu == "⏳ Temporizador":
    st.header("⏳ Temporizador")

    segundos = st.number_input("Segundos", min_value=1, max_value=3600)

    if st.button("Iniciar temporizador"):
        with st.spinner("⏳ Temporizador activo..."):
            time.sleep(segundos)
        st.success("⏰ Tiempo terminado")

# ==================================================
# 🌍 RELOJ MUNDIAL
# ==================================================
elif menu == "🌍 Reloj Mundial":
    st.header("🌍 Reloj Mundial")

    zonas = [
        "UTC",
        "America/Costa_Rica",
        "America/Mexico_City",
        "America/New_York",
        "Europe/Madrid",
        "Asia/Tokyo"
    ]

    zona = st.selectbox("Zona horaria", zonas)
    hora = datetime.now(pytz.timezone(zona))

    st.metric("Hora", hora.strftime("%H:%M:%S"))
    st.write(hora.strftime("%d/%m/%Y"))
