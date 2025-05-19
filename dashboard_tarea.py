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
st.markdown("---")

# Gráfico 2: Ingresos por Línea de Producto
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
# Gráfico 3: Distribución de Calificaciones de Clientes con Plotly (sin numpy)
# Gráfico: Histograma con separación + conteos en barras
st.subheader("⭐ Distribución de Calificaciones de Clientes")

if 'Rating' in df_filtrado.columns:
    import plotly.express as px
    import plotly.graph_objects as go

    col = "Rating"
    data = df_filtrado[col].dropna()

    # Estadísticas
    mean = data.mean()
    median = data.median()
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)

    # Histograma con conteos
    fig_hist = px.histogram(
        df_filtrado, 
        x="Rating", 
        nbins=12,
        opacity=0.75,
        color_discrete_sequence=['royalblue'],
        labels={"Rating": "Calificación"},
        text_auto=True  # <- Mostrar número encima
    )

    # Líneas estadísticas
    fig_hist.add_vline(x=mean, line_dash="dash", line_color="red", annotation_text=f"Media: {mean:.2f}", annotation_position="top right")
    fig_hist.add_vline(x=median, line_dash="dash", line_color="green", annotation_text=f"Mediana: {median:.2f}", annotation_position="top left")
    fig_hist.add_vline(x=q1, line_dash="dot", line_color="orange", annotation_text=f"Q1: {q1:.2f}", annotation_position="bottom right")
    fig_hist.add_vline(x=q3, line_dash="dot", line_color="orange", annotation_text=f"Q3: {q3:.2f}", annotation_position="bottom left")

    # Layout
    fig_hist.update_layout(
        title='Distribución de Calificaciones de Clientes',
        xaxis_title='Calificación',
        yaxis_title='Frecuencia',
        template='plotly_dark',
        bargap=0.2,
        title_x=0.5
    )

    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")
# Gráfico 4: Boxplot de Total por Tipo de Cliente
if 'Customer type' in df_filtrado.columns and 'Total' in df_filtrado.columns:
    import plotly.graph_objects as go

    tipos = df_filtrado['Customer type'].unique()
    fig_box = go.Figure()

    colores = {
        'Member': '#DAA520',  # dark yellow
        'Normal': '#20B2AA'   # light sea green
    }

    for tipo in tipos:
        grupo = df_filtrado[df_filtrado['Customer type'] == tipo]['Total']
        fig_box.add_trace(go.Box(
            y=grupo,
            name=tipo,
            boxmean='sd',
            marker_color=colores.get(tipo, 'gray'),
            fillcolor=colores.get(tipo, 'gray'),
             line_color='white',
            whiskerwidth=1.5
        ))

    
    fig_box.update_layout(
        title='Distribución del Gasto Total por Tipo de Cliente',
        yaxis_title='Gasto Total ($)',
        xaxis_title='Tipo de Cliente',
        template='plotly_dark',
        title_x=0.5
    )

    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.warning("Las columnas 'Customer type' y/o 'Total' no se encuentran en los datos.")
st.markdown("---")
# Reflexión final
st.markdown("### 💬 Reflexión")
st.markdown("""
Gracias a la interactividad del dashboard, el usuario puede explorar distintos periodos de tiempo y visualizar 
patrones temporales en las ventas, tales como horas de mayor actividad, días más rentables, y distribución 
de transacciones. Esta visualización mejora la toma de decisiones operativas y comerciales.
""")
