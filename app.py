from dash import Dash, dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import os

# 📌 Cargar los datos simulados
data = pd.read_csv("data/large_simulated_equipment_data_with_centrals.csv")

# 📌 Manejar valores nulos y asegurar datos correctos
data.fillna("Unknown", inplace=True)
data['Production_Variance'] = data.groupby('Month')['Equipment'].transform(lambda x: x.nunique() * (0.8 + 0.4 * np.random.rand()))

# 📌 Convertir columnas clave a string para evitar errores de NoneType
data[['Step', 'Technician', 'Month', 'Type', 'Result']] = data[['Step', 'Technician', 'Month', 'Type', 'Result']].astype(str)

# 📌 Inicializar la aplicación Dash
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Necesario para Gunicorn en Railway

# 📌 Layout del Dashboard
app.layout = html.Div([
    html.H1("Digital Twin: Aeronautical Sensor Manufacturing", style={'textAlign': 'center'}),

    # 🔹 Filtros interactivos
    html.Div([
        html.Label("Select Step: "),
        dcc.Dropdown(
            id='step-dropdown',
            options=[{'label': step, 'value': step} for step in sorted(data["Step"].unique())] + [{'label': 'All', 'value': 'All'}],
            value='All',
            placeholder="Select Step"
        ),

        html.Label("Select Technician: "),
        dcc.Dropdown(
            id='technician-dropdown',
            options=[{'label': tech, 'value': tech} for tech in sorted(data["Technician"].unique()[:12])] + [{'label': 'All', 'value': 'All'}],
            value='All',
            placeholder="Select Technician"
        ),

        html.Label("Select Month: "),
        dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': month, 'value': month} for month in sorted(data["Month"].unique())] + [{'label': 'All', 'value': 'All'}],
            value='All',
            placeholder="Select Month"
        ),

        html.Label("Select Sensor Type: "),
        dcc.Dropdown(
            id='sensor-dropdown',
            options=[{'label': sensor, 'value': sensor} for sensor in sorted(data["Type"].unique())] + [{'label': 'All', 'value': 'All'}],
            value='All',
            placeholder="Select Sensor Type"
        ),
    ], style={'width': '40%', 'display': 'inline-block', 'padding': '10px'}),

    # 🔹 Gráficos
    dcc.Graph(id='time-comparison-graph'),
    dcc.Graph(id='result-distribution-graph'),
    dcc.Graph(id='monthly-production-graph')
])

# 📌 Callbacks para actualizar los gráficos
@app.callback(
    Output('time-comparison-graph', 'figure'),
    Output('result-distribution-graph', 'figure'),
    Output('monthly-production-graph', 'figure'),
    Input('step-dropdown', 'value'),
    Input('technician-dropdown', 'value'),
    Input('month-dropdown', 'value'),
    Input('sensor-dropdown', 'value')
)
def update_graphs(step, technician, month, sensor_type):
    filtered_data = data.copy()
    
    # 🔹 Aplicar filtros
    if step != 'All':
        filtered_data = filtered_data[filtered_data["Step"] == step]
    if technician != 'All':
        filtered_data = filtered_data[filtered_data["Technician"] == technician]
    if month != 'All':
        filtered_data = filtered_data[filtered_data["Month"] == month]
    if sensor_type != 'All':
        filtered_data = filtered_data[filtered_data["Type"] == sensor_type]
    
    # 🔹 Validar si hay datos disponibles
    if filtered_data.empty:
        return (
            px.bar(x=["No Data"], y=[0], title="No data available"),
            px.histogram(x=["No Data"], title="No data available"),
            px.bar(x=["No Data"], y=[0], title="No data available")
        )
    
    # 🔹 Gráfico 1: Comparación de tiempos estimados vs reales
    fig1 = px.bar(
        filtered_data, x="Step", y=["Estimated_Time", "Real_Time"],
        barmode="group", title="Real vs Estimated Time by Step",
        labels={"value": "Time (minutes)", "variable": "Time Type"},
        color_discrete_map={"Estimated_Time": "#1F77B4", "Real_Time": "#FF7F0E"}
    )
    
    # 🔹 Gráfico 2: Distribución de resultados (Pass vs Fail)
    fig2 = px.histogram(
        filtered_data, 
        x="Result", 
        color="Result",  # Usamos "Result" para asignar colores a Pass y Fail
        title="Result Distribution by Sensor Type",
        color_discrete_map={"Pass": "green", "Fail": "red"}  # Asigna colores específicos
    )

    # 🔹 Gráfico 3: Producción por mes con variación
    monthly_data = filtered_data.groupby("Month")["Production_Variance"].sum().reset_index()
    fig3 = px.bar(
        monthly_data, x="Month", y="Production_Variance", 
        title="Production by Month with Variance", text_auto=True,
        color="Production_Variance", color_continuous_scale="Viridis"
    )

    return fig1, fig2, fig3

# 📌 Ejecutar la aplicación en Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto que asigna Railway
    app.run_server(debug=False, host="0.0.0.0", port=port)

