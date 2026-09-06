from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_shadcn_ui as ui
import plotly.graph_objects as go


# ========================================================
# CONFIGURACIÓN GENERAL
# ========================================================

st.set_page_config(
    page_title="M5 Walmart | Forecasting",
    page_icon="📊",
    layout="wide"
)


# ========================================================
# PALETA DE COLORES
# ========================================================

WALMART_BLUE = "#0071CE"
WALMART_DARK_BLUE = "#041E42"
WALMART_YELLOW = "#FFC220"

LIGHT_BLUE = "#E8F3FA"
LIGHT_GRAY = "#F4F6F8"
MEDIUM_GRAY = "#6B7280"
DARK_GRAY = "#374151"
WHITE = "#FFFFFF"


# ========================================================
# ESTILO VISUAL
# ========================================================

st.markdown(
    f"""
    <style>

    /* Fondo general */
    .stApp {{
        background-color: {LIGHT_GRAY};
    }}

    /* Contenedor principal */
    .block-container {{
        padding-top: 5rem;
        padding-bottom: 3rem;
    }}

    /* Título principal */
    .titulo-principal {{
        color: {WALMART_DARK_BLUE};
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }}

    /* Subtítulo */
    .subtitulo {{
        color: {WALMART_BLUE};
        font-size: 1.15rem;
        font-weight: 500;
        margin-bottom: 0.8rem;
    }}

    /* Descripción */
    .descripcion {{
        color: {DARK_GRAY};
        font-size: 1rem;
        line-height: 1.5;
        max-width: 900px;
        margin-bottom: 1.5rem;
    }}

    /* Línea amarilla decorativa */
    .linea-walmart {{
        height: 4px;
        width: 70px;
        background-color: {WALMART_YELLOW};
        border-radius: 4px;
        margin-bottom: 1.2rem;
    }}

     
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------------
# ENCABEZADO
# --------------------------------------------------------

st.markdown(
    f"""
    <div style="
        text-align: center;
        margin-bottom: 0.2rem;
    ">
        <div style="
            color: {WALMART_DARK_BLUE};
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.2;
        ">Segmentación y pronóstico de demanda</div><div style="
            color: {WALMART_BLUE};
            font-size: 1.05rem;
            margin-top: 0.45rem;
        ">M5 Walmart · Machine Learning aplicado a Supply Chain</div><div style="
            width: 70px;
            height: 4px;
            background-color: {WALMART_YELLOW};
            margin: 0.8rem auto 0 auto;
            border-radius: 2px;
        "></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ========================================================
# RUTAS DEL PROYECTO
# ========================================================

RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DATA = RUTA_PROYECTO / "data"
RUTA_PROCESSED = RUTA_DATA / "processed"
RUTA_OUTPUTS = RUTA_PROYECTO / "outputs"


# ========================================================
# CARGA DE DATOS
# ========================================================

@st.cache_data
def cargar_datos():

    # Segmentación de las series SKU + tienda.
    segmentacion = pd.read_csv(
        RUTA_PROCESSED / "segmentacion_sku_tienda.csv"
    )

    # Pronóstico del grupo estacional.
    forecast_estacional = pd.read_csv(
        RUTA_OUTPUTS / "forecast_estacional.csv"
    )

    # Pronóstico del grupo tendencia.
    forecast_tendencia = pd.read_csv(
        RUTA_OUTPUTS / "forecast_tendencia.csv"
    )

    # Pronóstico del grupo sin patrón dominante.
    forecast_sin_patron = pd.read_csv(
        RUTA_OUTPUTS / "forecast_sin_patron.csv"
    )

    # Calendario M5.
    calendar = pd.read_csv(
        RUTA_DATA / "raw" / "calendar.csv"
    )

    calendar["date"] = pd.to_datetime(
        calendar["date"]
    )

    # Demanda real utilizada para evaluar el pronóstico.
    test_real = pd.read_csv(
        RUTA_PROCESSED / "test_real.csv"
    )

    test_real["date"] = pd.to_datetime(
        test_real["date"]
    )

    return (
        segmentacion,
        forecast_estacional,
        forecast_tendencia,
        forecast_sin_patron,
        calendar,
        test_real
    )
# Cargar los datos.
(
    segmentacion,
    forecast_estacional,
    forecast_tendencia,
    forecast_sin_patron,
    calendar,
    test_real
) = cargar_datos()

# Unir los tres archivos de pronóstico.
forecast = pd.concat(
    [
        forecast_estacional,
        forecast_tendencia,
        forecast_sin_patron
    ],
    ignore_index=True
)

# Asegurar el formato correcto de la fecha.
forecast["date"] = pd.to_datetime(forecast["date"])
# ============================================================
# AGREGAR CATEGORÍA Y EVENTO AL PRONÓSTICO
# ============================================================

# Agregar la categoría de cada SKU + tienda.
forecast = forecast.merge(
    segmentacion[
        ["item_id", "store_id", "cat_id"]
    ],
    on=["item_id", "store_id"],
    how="left"
)

# Crear una columna con el nombre del evento.
calendar_eventos = calendar[
    ["date", "event_name_1"]
].copy()

calendar_eventos = calendar_eventos.rename(
    columns={
        "event_name_1": "evento"
    }
)

# Unir el evento correspondiente a cada fecha.
forecast = forecast.merge(
    calendar_eventos,
    on="date",
    how="left"
)

# Cuando no existe evento, mostrar "Sin evento".
forecast["evento"] = forecast["evento"].fillna("Sin evento")
# ============================================================

# ============================================================
# RESUMEN DEL PROYECTO
# ============================================================

st.markdown(
    f"""
    <div style="
        color: {WALMART_DARK_BLUE};
        font-size: 1.45rem;
        font-weight: 650;
        margin-bottom: 1rem;
    ">
        Resumen del proyecto
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    ui.metric_card(
        "Series SKU + tienda",
        f"{len(segmentacion):,}",
        description="30,490 series analizadas"
    )

with col2:
    ui.metric_card(
        "Tiendas",
        "10",
        description="Cobertura del dataset"
    )

with col3:
    ui.metric_card(
        "Observaciones",
        "58M+",
        description="Demanda histórica 2011–2016"
    )

with col4:
    ui.metric_card(
        "Horizonte",
        "28 días",
        description="Pronóstico fuera de muestra"
    )
# ============================================================
# MÉTRICAS DE LOS MODELOS GANADORES
# ============================================================

# Título centrado sobre la tabla.
col_titulo_izq, col_titulo, col_titulo_der = st.columns([1, 2, 1])

with col_titulo:
    st.markdown(
        f"""
        <div style="
            color: {WALMART_DARK_BLUE};
            font-size: 1.45rem;
            font-weight: 650;
            text-align: center;
            margin-bottom: 1rem;
        ">
            Métricas de los modelos ganadores
        </div>
        """,
        unsafe_allow_html=True
    )

metricas = pd.DataFrame({
    "Macrogrupo": [
        "Estacional",
        "Tendencia",
        "Sin patrón dominante"
    ],
    "Modelo": [
        "XGBoost",
        "XGBoost",
        "XGBoost"
    ],
    "MAE": [
        2.3759,
        1.6680,
        0.9648
    ],
    "RMSE": [
        3.9708,
        2.9260,
        2.0633
    ],
    "MAPE": [
        "50.99%",
        "53.42%",
        "57.51%"
    ]
})

# Mostrar la tabla centrada y con un ancho acorde al contenido.
col_izq, col_tabla, col_der = st.columns([1, 2, 1])

with col_tabla:
    st.dataframe(
        metricas,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# EXPLORADOR DE PRONÓSTICOS
# ============================================================

# Título centrado sobre los filtros y la gráfica.
col_titulo_izq, col_titulo, col_titulo_der = st.columns([1, 2, 1])

with col_titulo:
    st.markdown(
        f"""
        <div style="
            color: {WALMART_DARK_BLUE};
            font-size: 1.45rem;
            font-weight: 650;
            text-align: center;
            margin-bottom: 1rem;
        ">
            Explorador de pronósticos
        </div>
        """,
        unsafe_allow_html=True
    )

# Obtener las opciones disponibles directamente de los pronósticos.
opciones_tienda = sorted(
    forecast["store_id"].unique().tolist()
)

opciones_categoria = sorted(
    forecast["cat_id"].unique().tolist()
)

opciones_evento = sorted(
    forecast["evento"].unique().tolist()
)

st.markdown(
    f"""
    <div style="
        color: {MEDIUM_GRAY};
        font-size: 0.95rem;
        text-align: center;
        margin-bottom: 1.2rem;
    ">
        Selecciona una tienda para visualizar la demanda agregada de sus SKU.
        Puedes filtrar por categoría, evento y periodo.
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FILTROS
# ============================================================

col1, col2, col3 = st.columns(3)


# Selector de tienda.
with col1:

    seleccion_tienda = ui.combobox(
        "Tienda",
        opciones_tienda,
        selection_mode="single"
    )


# Selector de categoría.
with col2:

    seleccion_categoria = ui.combobox(
        "Categoría",
        ["Todas"] + opciones_categoria,
        selection_mode="single"
    )


# Selector de evento.
with col3:

    seleccion_evento = ui.combobox(
        "Evento",
        ["Todos"] + opciones_evento,
        selection_mode="single"
    )


# Selector de rango de fechas del horizonte de pronóstico.
fecha_minima = pd.Timestamp("2016-04-25").date()
fecha_maxima = pd.Timestamp("2016-05-22").date()

# Etiqueta del selector de fechas.
st.markdown(
    f"""
    <div style="
        color: {DARK_GRAY};
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 0.5rem;
        margin-bottom: 0.3rem;
    ">
        Rango de fechas
    </div>
    """,
    unsafe_allow_html=True
)

rango_fechas = st.date_input(
    "",
    value=(fecha_minima, fecha_maxima),
    min_value=fecha_minima,
    max_value=fecha_maxima,
    label_visibility="collapsed"
)

# ============================================================
# VISTA: DEMANDA AGREGADA DE UNA TIENDA
# ============================================================

if (
    seleccion_tienda
    and len(rango_fechas) == 2
):

    tienda = seleccion_tienda

    # --------------------------------------------------------
    # FILTRAR LA TIENDA
    # --------------------------------------------------------

    datos_forecast = forecast[
        forecast["store_id"] == tienda
    ].copy()

    datos_real = test_real[
        test_real["store_id"] == tienda
    ].copy()


    # --------------------------------------------------------
    # FILTRO DE CATEGORÍA
    # --------------------------------------------------------

    if (
        seleccion_categoria
        and seleccion_categoria != "Todas"
    ):

        # Filtrar el pronóstico por categoría.
        datos_forecast = datos_forecast[
            datos_forecast["cat_id"] == seleccion_categoria
        ]

        # Obtener los SKU que pertenecen a la categoría.
        sku_categoria = segmentacion[
            segmentacion["cat_id"] == seleccion_categoria
        ][
            ["item_id", "store_id"]
        ].drop_duplicates()

        # Filtrar las ventas reales con los mismos SKU + tienda.
        datos_real = datos_real.merge(
            sku_categoria,
            on=["item_id", "store_id"],
            how="inner"
        )


    

    # --------------------------------------------------------
    # FILTRO DE FECHAS
    # --------------------------------------------------------

    fecha_inicio = pd.to_datetime(
        rango_fechas[0]
    )

    fecha_fin = pd.to_datetime(
        rango_fechas[1]
    )

    datos_forecast = datos_forecast[
        (datos_forecast["date"] >= fecha_inicio)
        & (datos_forecast["date"] <= fecha_fin)
    ]

    datos_real = datos_real[
        (datos_real["date"] >= fecha_inicio)
        & (datos_real["date"] <= fecha_fin)
    ]

    # --------------------------------------------------------
    # AGREGAR TODOS LOS SKU POR DÍA
    # --------------------------------------------------------

    pronostico_diario = (
        datos_forecast
        .groupby(
            "date",
            as_index=False
        )["demanda_pronosticada"]
        .sum()
    )

    real_diario = (
        datos_real
        .groupby(
            "date",
            as_index=False
        )["demanda_real"]
        .sum()
    )


    # --------------------------------------------------------
    # COMBINAR DEMANDA REAL Y PRONOSTICADA
    # --------------------------------------------------------

    datos_grafica = pd.merge(
        real_diario,
        pronostico_diario,
        on="date",
        how="outer"
    ).sort_values("date")


    datos_grafica = datos_grafica.rename(
        columns={
            "demanda_real": "Demanda real",
            "demanda_pronosticada": "Demanda pronosticada"
        }
    )


    # --------------------------------------------------------
    # INFORMACIÓN DE LOS FILTROS
    # --------------------------------------------------------

    categoria_texto = (
        seleccion_categoria
        if seleccion_categoria
        else "Todas"
    )

    evento_texto = (
        seleccion_evento
        if seleccion_evento
        else "Todos"
    )


    # Mostrar de forma compacta la selección activa.
    st.markdown(
        f"""
        <div style="
            background-color: {LIGHT_BLUE};
            border-left: 4px solid {WALMART_BLUE};
            border-radius: 6px;
            padding: 0.65rem 0.9rem;
            margin-top: 0.8rem;
            margin-bottom: 1rem;
            color: {DARK_GRAY};
            font-size: 0.9rem;
        ">
            <strong style="color: {WALMART_DARK_BLUE};">
                Selección actual:
            </strong>
            {tienda} · {categoria_texto} · {evento_texto}
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # GRÁFICA
    # --------------------------------------------------------

        # --------------------------------------------------------
    # TÍTULO DE LA GRÁFICA
    # --------------------------------------------------------

    col_titulo_izq, col_titulo, col_titulo_der = st.columns([1, 2, 1])

    with col_titulo:
        st.markdown(
            f"""
            <div style="
                color: {WALMART_DARK_BLUE};
                font-size: 1.45rem;
                font-weight: 650;
                text-align: center;
                margin-bottom: 1rem;
            ">
                Demanda real vs. pronosticada — {tienda}
            </div>
            """,
            unsafe_allow_html=True
        )
  

    # Crear la gráfica.
    fig = go.Figure()


    # Demanda real.
    fig.add_trace(
        go.Scatter(
            x=datos_grafica["date"],
            y=datos_grafica["Demanda real"],
            mode="lines",
            name="Demanda real"
        )
    )


    # Demanda pronosticada.
    fig.add_trace(
        go.Scatter(
            x=datos_grafica["date"],
            y=datos_grafica["Demanda pronosticada"],
            mode="lines",
            name="Demanda pronosticada"
        )
    )


    # --------------------------------------------------------
    # MARCAR EVENTO SELECCIONADO
    # --------------------------------------------------------

    if (
        seleccion_evento
        and seleccion_evento != "Todos"
    ):

        fechas_evento = calendar[
            calendar["event_name_1"] == seleccion_evento
        ]["date"]

        fechas_evento = fechas_evento[
            (fechas_evento >= fecha_inicio)
            & (fechas_evento <= fecha_fin)
        ]


        for fecha_evento in fechas_evento:

            fig.add_vline(
                x=fecha_evento,
                line_dash="dash",
                annotation_text=seleccion_evento,
                annotation_position="top"
            )


    # Configuración de la gráfica.
    fig.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Unidades",
    hovermode="x unified",
    legend_title="Serie",
    height=500,
    yaxis=dict(
        rangemode="tozero"
    )
)


    st.plotly_chart(
        fig,
        use_container_width=True
    )
    # --------------------------------------------------------
    # RESUMEN DEL PRONÓSTICO
    # --------------------------------------------------------

    demanda_real_total = datos_grafica["Demanda real"].sum()
    demanda_pronosticada_total = datos_grafica["Demanda pronosticada"].sum()

    diferencia = (
        demanda_pronosticada_total - demanda_real_total
    )

    diferencia_pct = (
        diferencia / demanda_real_total * 100
        if demanda_real_total != 0
        else 0
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        ui.metric_card(
            "Demanda real",
            f"{demanda_real_total:,.0f}",
            description="Unidades en el periodo seleccionado"
        )

    with col2:
        ui.metric_card(
            "Pronóstico",
            f"{demanda_pronosticada_total:,.0f}",
            description="Unidades pronosticadas"
        )

    with col3:
        ui.metric_card(
            "Desviación del pronóstico",
            f"{diferencia_pct:+.1f}%",
            description="Pronóstico vs. demanda real"
        )

# --------------------------------------------------------
# FUENTE DE DATOS
# --------------------------------------------------------

st.markdown(
    f"""
    <div style="
        text-align: center;
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
        color: {MEDIUM_GRAY};
        font-size: 0.8rem;
    ">
        Fuente de datos:
        <a
            href="https://doi.org/10.5281/zenodo.10203108"
            target="_blank"
            style="
                color: {WALMART_BLUE};
                text-decoration: none;
                font-weight: 500;
            "
        >
            M5 Forecasting – Accuracy · Zenodo
        </a>
    </div>
    """,
    unsafe_allow_html=True
)