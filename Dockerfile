# Usa una imagen base de Python
FROM python:3.10

# Configura el directorio de trabajo
WORKDIR /app

# Copia todos los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que correrá el servidor
EXPOSE 5000

# Comando para ejecutar la app en Railway
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:5000"]
