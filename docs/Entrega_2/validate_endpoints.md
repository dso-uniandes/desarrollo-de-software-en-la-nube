# Validación de Endpoints - Cumplimiento de Requisitos Funcionales

Para la segunda entrega del proyecto, hemos validado el correcto funcionamiento de todos los endpoints definidos en la primera entrega mediante pruebas automatizadas con **Newman**. Los resultados confirman que nuestra aplicación web cumple completamente con los requisitos funcionales previamente establecidos.

---

## 🎯 Requisitos Funcionales Validados

### **Endpoints Principales**
- **Autenticación**: `POST /api/auth/signup`, `POST /api/auth/login`
- **Gestión de Videos**: `POST /api/videos/upload`, `GET /api/videos`, `GET /api/videos/{id}`, `DELETE /api/videos/{id}`
- **Sistema de Votación**: `POST /api/public/videos/{id}/vote`, `GET /api/videos/{id}/votes`, `GET /api/public/videos`
- **Rankings**: `GET /api/public/rankings`, `GET /api/public/rankings?city={ciudad}`

---

## 🔧 Metodología de Validación

**Herramientas**: Newman CLI con colección Cloud-ANB (25 requests, 61 assertions)

**Comando ejecutado**:
```bash
newman run collections/Cloud-ANB.postman_collection.json --environment collections/postman_environment.json
```

**Configuración**: URL cambiada a IP pública del EC2 para pruebas en producción

---

## ✅ Resultados de Validación

### **Métricas Generales**
- **25 requests ejecutados** ✅
- **61 de 61 assertions pasaron** ✅ (100% de éxito)

### **Validaciones por Funcionalidad**
- ✅ **Autenticación**: Registro, login y JWT funcionando correctamente
- ✅ **Gestión de Videos**: Carga, validación de formatos, procesamiento asíncrono
- ✅ **Sistema de Votación**: Votación en videos procesados, estadísticas correctas
- ✅ **Rankings**: Cálculo por votos, filtrado por ciudad, paginación
- ✅ **Integración**: Kafka, Worker FFmpeg, PostgreSQL coordinados correctamente

---

## 📊 Evidencia de Cumplimiento

<img alt="image" src="https://github.com/user-attachments/assets/440817f6-3455-4616-9ad8-c29938a5eda9" />

---

## 🎉 Conclusión

**La aplicación web cumple al 100% con los requisitos funcionales establecidos en la primera entrega.** 

Las pruebas automatizadas con Newman han validado exitosamente todos los endpoints y flujos de trabajo completos (registro → login → upload → procesamiento → votación → ranking), confirmando que nuestra implementación en la nube mantiene toda la funcionalidad original mientras añade las mejoras de escalabilidad requeridas.

