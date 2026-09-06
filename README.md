# Segmentación y pronóstico de demanda para productos de retail

Proyecto de forecasting aplicado al dataset **M5 Walmart**, utilizando Machine Learning para segmentar series de demanda y generar pronósticos a nivel **SKU + tienda**.

## Objetivo

Identificar diferentes comportamientos de demanda y seleccionar el modelo de forecasting con mejor desempeño para cada grupo.

## Datos

Se utilizaron los datos de **M5 Forecasting – Accuracy**, obtenidos de Zenodo.

* 3,049 SKU
* 10 tiendas
* 30,490 series SKU + tienda
* Historial de demanda de 2011 a 2016
* Horizonte de evaluación: 28 días

## Segmentación de la demanda

La clasificación se realizó a nivel **SKU + tienda**, utilizando indicadores de estacionalidad y tendencia.

### Estacional

* `seasonality\_strength > 0.25` → indica una variabilidad semanal relativamente marcada en el comportamiento de la demanda.
* `acf\_7\_detrended > 0.05` → indica una correlación positiva con la demanda observada 7 días antes, después de retirar el efecto de tendencia.

### Tendencia

* `abs(change\_q1\_q4) > 0.50` → indica un cambio relevante en el nivel de demanda entre el primer y último periodo analizado.
* `trend\_consistency >= 0.67` → indica que al menos dos de los tres cambios entre periodos siguen la misma dirección.

### Sin patrón dominante

Series que no cumplen los criterios anteriores.

Esto no significa que la demanda no tenga comportamiento, sino que **no presenta una señal dominante de estacionalidad o tendencia bajo los criterios definidos**.

Cuando una serie cumplió simultáneamente los criterios de estacionalidad y tendencia, se priorizó **Estacional**, ya que su `seasonality\_score` fue superior a su `trend\_score`.

### Resultado de la segmentación

|Grupo|Series|Proporción|
|-|-:|-:|
|Estacional|413|1.35%|
|Tendencia|2,249|7.38%|
|Sin patrón dominante|27,828|91.27%|
|**Total**|**30,490**|**100%**|

## Metodología de forecasting

Se utilizaron las mismas variables para los experimentos de Machine Learning:

* Rezagos: 7, 14, 21, 28, 35 y 56 días.
* Promedios móviles: 7, 28 y 56 días.
* Variables de calendario: día de la semana, mes y evento.

Los promedios móviles utilizan únicamente información histórica mediante desplazamiento (`shift(1)`), evitando utilizar información futura durante el entrenamiento.

El pronóstico final se genera de forma **recursiva durante 28 días**, utilizando las predicciones anteriores como parte de la información disponible para los días siguientes.

## Modelos

Se evaluaron **Random Forest, XGBoost e HistGradientBoosting**. Como referencia adicional, se utilizó **Seasonal Naive**, un método tradicional de pronóstico.

|Grupo|Modelo|MAE|RMSE|MAPE|
|-|-|-:|-:|-:|
|Estacional|Random Forest|2.4280|4.0458|53.75%|
|Estacional|**XGBoost**|**2.3759**|**3.9708**|**50.99%**|
|Estacional|HistGradientBoosting|2.4011|3.9717|52.10%|
|Estacional|Seasonal Naive|2.9875|5.0712|71.86%|
|Tendencia|Random Forest|—|—|—|
|Tendencia|**XGBoost**|**1.6680**|2.9260|53.42%|
|Tendencia|HistGradientBoosting|1.6915|**2.9246**|**53.33%**|
|Tendencia|Seasonal Naive|2.0554|3.6579|82.67%|
|Sin patrón dominante|Random Forest|—|—|—|
|Sin patrón dominante|**XGBoost**|**0.9648**|2.0633|57.51%|
|Sin patrón dominante|HistGradientBoosting|1.0028|**2.0226**|**54.92%**|
|Sin patrón dominante|Seasonal Naive|1.1525|2.5275|83.27%|

**Nota:** Random Forest fue entrenado para el grupo Estacional. Para Tendencia y Sin patrón dominante, no fue posible completar la evaluación recursiva de Random Forest debido al costo computacional, por lo que no se reportan métricas para esos casos.

## Modelos seleccionados

El criterio principal de selección fue **MAE**, por ser una métrica expresada en unidades y más interpretable para series con demanda baja e intermitente.

Los modelos seleccionados fueron:

* **Estacional → XGBoost**
* **Tendencia → XGBoost**
* **Sin patrón dominante → XGBoost**

**Seasonal Naive** se utilizó únicamente como **benchmark tradicional de referencia** y no forma parte de los modelos finales.

## Evaluación

El entrenamiento utiliza la demanda histórica hasta `d\_1913`.

La evaluación fuera de muestra utiliza como valores reales los días `d\_1914` a `d\_1941`, correspondientes a un horizonte de **28 días**.

Las métricas utilizadas son:

* **MAE:** error absoluto medio, expresado en unidades.
* **RMSE:** error cuadrático medio, que penaliza en mayor medida los errores grandes.
* **MAPE:** error porcentual absoluto medio.

Debido a la presencia de series de baja demanda e intermitencia, **MAE se utiliza como métrica principal**. MAPE puede presentar valores elevados cuando la demanda real es cercana a cero.

## Resultados finales

|Grupo|Modelo final|MAE|RMSE|MAPE|
|-|-|-:|-:|-:|
|Estacional|XGBoost|2.3759|3.9708|50.99%|
|Tendencia|XGBoost|1.6680|2.9260|53.42%|
|Sin patrón dominante|XGBoost|0.9648|2.0633|57.51%|

## Aplicación interactiva

El proyecto incluye una aplicación desarrollada con **Streamlit** para explorar los pronósticos sin necesidad de volver a entrenar los modelos.

La aplicación permite:

* Seleccionar una tienda.
* Filtrar por categoría.
* Filtrar por evento.
* Seleccionar un periodo.
* Comparar demanda real vs. pronosticada.
* Consultar indicadores agregados del periodo seleccionado.

Los pronósticos utilizados por la aplicación fueron calculados previamente y almacenados como archivos de salida.

## Estructura del proyecto

```text
M5 Walmart/
├── app/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
│   ├── xgb\_estacional.joblib
│   ├── xgb\_tendencia.joblib
│   └── xgb\_sin\_patron.joblib
├── notebooks/
│   └── 03\_modelos\_finales.ipynb
├── outputs/
│   ├── forecast\_estacional.csv
│   ├── forecast\_tendencia.csv
│   └── forecast\_sin\_patron.csv
├── requirements.txt
└── README.md
```

Los datos originales de M5 y los archivos intermedios de gran tamaño no se incluyen en el repositorio público.

```

## Consideraciones

* La segmentación es específica para las series **SKU + tienda** del dataset analizado.
* La evaluación corresponde a un horizonte fuera de muestra de 28 días.
* MAPE debe interpretarse con cautela en series de demanda baja o intermitente.
* La aplicación utiliza pronósticos previamente calculados y no realiza reentrenamiento al abrirse.

## Fuente de datos

**M5 Forecasting – Accuracy**

Zenodo: https://doi.org/10.5281/zenodo.10203108

