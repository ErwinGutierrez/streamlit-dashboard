# dashboard_tarea.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Título y descripción
st.title("📊 Dashboard Interactivo de Ventas")
st.markdown("""
Este dashboard permite visualizar la evolución de las ventas, con datos limpios y transformados para facilitar el análisis temporal.
Incluye filtros interactivos y múltiples vistas para comprender mejor el comportamiento de las ventas.
""")

# Carga de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data.csv")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce')
    df['Day'] = df['Date'].dt.day_name()
    df['Month'] = df['Date'].dt.month_name()
    df['Hour'] = df['Time'].dt.hour
    return df.dropna()

df = cargar_datos()

# Filtro de fechas
st.subheader("📅 Filtrar por Rango de Fechas")
fecha_min = df['Date'].min()
fecha_max = df['Date'].max()

fecha_inicio, fecha_fin = st.date_input(
    label="Selecciona el rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

df_filtrado = df[(df['Date'] >= pd.to_datetime(fecha_inicio)) & (df['Date'] <= pd.to_datetime(fecha_fin))]

st.markdown("---")

# Gráfico 1: Ventas Totales por Día
st.subheader("📈 Ventas Totales por Día")

ventas_diarias = df_filtrado.groupby('Date')['Total'].sum().reset_index()

fig1 = px.line(
    ventas_diarias,
    x='Date',
    y='Total',
    title='Evolución de las Ventas Totales',
    markers=True,
    labels={'Date': 'Fecha', 'Total': 'Ventas Totales (USD)'},
    template='plotly_white'
)

fig1.update_traces(line_color='darkorange')
fig1.update_layout(title_x=0.5)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Cantidad de Transacciones por Día
st.subheader("🧾 Cantidad de Transacciones por Día")

transacciones = df_filtrado.groupby('Date').size().reset_index(name='Cantidad')

fig2 = px.bar(
    transacciones,
    x='Date',
    y='Cantidad',
    title='Cantidad de Transacciones por Día',
    labels={'Cantidad': 'Número de Transacciones'},
    template='plotly_white'
)

st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Promedio de Ventas por Día de la Semana
st.subheader("📅 Promedio de Ventas por Día de la Semana")

ventas_dia = df_filtrado.groupby('Day')['Total'].mean().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
]).reset_index()

fig3 = px.bar(
    ventas_dia,
    x='Day',
    y='Total',
    title='Promedio de Ventas por Día de la Semana',
    labels={'Total': 'Promedio de Ventas (USD)'},
    template='plotly_white',
    color_discrete_sequence=['#636EFA']
)

st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4: Distribución de Ventas por Hora
st.subheader("⏰ Distribución de Ventas por Hora del Día")

fig4 = px.histogram(
    df_filtrado,
    x='Hour',
    y='Total',
    nbins=24,
    title='Distribución de Ventas por Hora',
    labels={'Hour': 'Hora del Día', 'Total': 'Ventas Totales'},
    template='plotly_white'
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Reflexión final
st.markdown("### 💬 Reflexión")
st.markdown("""
Gracias a la interactividad del dashboard, el usuario puede explorar distintos periodos de tiempo y visualizar 
patrones temporales en las ventas, tales como horas de mayor actividad, días más rentables, y distribución 
de transacciones. Esta visualización mejora la toma de decisiones operativas y comerciales.
""")
