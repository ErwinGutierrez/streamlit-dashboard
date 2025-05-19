# dashboard_tarea.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Título y descripción
st.title("📊 Dashboard Interactivo de Ventas Equipo 13")
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
# Filtro por línea de producto (si existe esta columna)
if 'Product line' in df.columns:
    st.subheader("📦 Filtrar por Línea de Producto")
    opciones = st.multiselect("Selecciona una o más líneas de producto:", df['Product line'].unique())
    if opciones:
        df_filtrado = df_filtrado[df_filtrado['Product line'].isin(opciones)]
# Filtro por mes
st.subheader("📆 Filtrar por Mes")
meses_unicos = df_filtrado['Month'].unique().tolist()
meses_ordenados = [m for m in ['January', 'February', 'March']
                   if m in meses_unicos]

meses_seleccionados = st.multiselect("Selecciona uno o más meses:", meses_ordenados)

if meses_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['Month'].isin(meses_seleccionados)]
st.markdown("---")
# Métricas clave
st.subheader("📌 Indicadores Clave")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Ventas Totales", f"${df_filtrado['Total'].sum():,.2f}")

with col2:
    promedio_diario = df_filtrado.groupby('Date')['Total'].sum().mean()
    st.metric("📊 Promedio Diario", f"${promedio_diario:,.2f}")

with col3:
    st.metric("🧾 Total Transacciones", f"{len(df_filtrado):,}")

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

# Gráfico 2: Comparación con datos no filtrados
st.subheader("📉 Comparativa General de Ventas Totales (sin filtros)")

ventas_diarias_totales = df.groupby('Date')['Total'].sum().reset_index()

fig2 = px.line(
    ventas_diarias_totales,
    x='Date',
    y='Total',
    title='Evolución General de Ventas Totales',
    markers=True,
    labels={'Date': 'Fecha', 'Total': 'Ventas Totales (USD)'},
    template='plotly_white'
)

fig2.update_traces(line_color='seagreen')
fig2.update_layout(
    xaxis_title='Fecha',
    yaxis_title='Ventas Totales (USD)',
    title_x=0.5
)

st.plotly_chart(fig2, use_container_width=True)
# Gráfico 3: Ingresos por Línea de Producto
st.subheader("📦 Ingresos por Línea de Producto")

# Asegurarse de que la columna existe
if 'Product line' in df_filtrado.columns:
    ventas_por_producto = df_filtrado.groupby('Product line')['Total'].sum().reset_index()
    ventas_por_producto = ventas_por_producto.sort_values(by='Total', ascending=True)

    fig3 = px.bar(
        ventas_por_producto,
        x='Total',
        y='Product line',
        orientation='h',
        title='Ingresos por Línea de Producto',
        labels={'Total': 'Ingresos Totales (USD)', 'Product line': 'Línea de Producto'},
        color='Product line',
        template='plotly_white'
    )

    fig3.update_layout(title_x=0.5)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("La columna 'Product line' no se encuentra en los datos.")

st.markdown("---")

# Reflexión final
st.markdown("### 💬 Reflexión")
st.markdown("""
Gracias a la interactividad del dashboard, el usuario puede explorar distintos periodos de tiempo y visualizar 
patrones temporales en las ventas, tales como horas de mayor actividad, días más rentables, y distribución 
de transacciones. Esta visualización mejora la toma de decisiones operativas y comerciales.
""")
