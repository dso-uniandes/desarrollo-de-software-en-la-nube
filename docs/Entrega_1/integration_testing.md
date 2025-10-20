# Pruebas de Integración con Newman

## 🚀 Configuración de Newman

Usamos Newman, que es la herramienta de línea de comandos de Postman. Nos sirve para correr toda la colección de pruebas de forma automática, como si fueran usuarios reales interactuando con la API.

## Colección Cloud-ANB

### Configuración
- **25 requests** cubriendo todos los endpoints
- **61 assertions** (validaciones de respuesta y tiempos)

### Tipos de Pruebas
- **Casos de éxito**: Validación de respuestas correctas
- **Casos de error**: Que las respuestas de error sean las correctas
- **Validación de datos**: Estructura y contenido de respuestas
