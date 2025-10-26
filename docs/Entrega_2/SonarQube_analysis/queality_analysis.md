# 📊 Reporte de Análisis SonarQube – Entrega 2

**Proyecto:** MISW4204-202515-anb-Grupo03-local  
**Rama analizada:** `main`  
**Fecha del análisis:** Última ejecución CI con acción `gitricko/sonarless@v1.3`  
**Estado del análisis:** ✅ Ejecución exitosa  
**Quality Gate:** 🟢 **Aprobado**

---
Antes de las conclusiones, es importante resaltar algunos aspectos clave del proceso de mejora. 
- En la Entrega 1 se contaban 44 pruebas automáticas, mientras que en la Entrega 2 se alcanzaron 64 pruebas. 
- El enfoque principal fue ampliar la cobertura de tests en los módulos `video.py`, `worker.py` y `nfs.py`, incorporando más casos negativos y de integración.
- La reducción significativa de *code smells* no solo se debió a refactorizaciones, sino también a la exclusión de archivos de las rutas `capacity-planning`, `docs`, `collections` y `videos` del análisis de SonarQube, permitiendo así centrar la evaluación en el código fuente principal. Esta exclusión ayudó a que el reporte refleje con mayor precisión la calidad del núcleo del sistema y contribuyó a mejorar la calificación global del *Quality Gate*.

## 🧩 Comparativo General

| Métrica | Entrega 1    | Entrega 2 | Variación                             | Estado                                     |
|----------|--------------|------------|---------------------------------------|--------------------------------------------|
| 🐞 **Bugs** | 0            | 0 | 🟰                                      | ✅ Sin errores funcionales                  |
| 🔒 **Vulnerabilidades** | 0            | 0 | 🟰                                   | ✅ Sin riesgos de seguridad                 |
| ⚠️ **Code Smells** | 22           | 6 | 🔽 **-73%**                           | ✅ Mejoras significativas en mantenibilidad |
| 🧪 **Cobertura de pruebas unitarias** | 25.9 %       | **54.1 %** | 🔼 **+28.2 pts**                      | ⚠️ Se seguirá ampliando                    |
| 🔁 **Duplicación de código** | 2 %          | 0 % | 🔽 Eliminada                          | ✅ Código limpio                            |
| 🚦 **Quality Gate** | 🔴 Rechazado | 🟢 Aprobado | ✅ Cumple todos los umbrales de calidad |

---

## 📈 Análisis Detallado

### **1. Cobertura de pruebas unitarias**
Se incrementó la cobertura del **25.9 % a 54.1 %**, superando el umbral base y duplicando el nivel anterior.  
Este aumento se logró mediante:

- **Nuevas pruebas unitarias y de integración** sobre los módulos críticos:
  - `storeapi/routers/video.py` → validaciones de errores (`HTTPException 400, 404, 500`) y flujo de streaming.
  - `message_broker/worker.py` → simulaciones de procesamiento y validación de logs.
  - `utils/nfs` → pruebas de funciones auxiliares de NFS.
- Se mejoró la **cobertura de ramas (branch coverage)** mediante pruebas negativas y excepciones forzadas.

📌 *Resultado:* el sistema ahora cuenta con más de **60 pruebas automáticas**, cubriendo escenarios de éxito, error y validación de seguridad.

---

### ⚙️ **2. Reducción de code smells**
Los *code smells* se redujeron de **22 a 6** gracias a:

- Eliminación de código duplicado en módulos `video.py` y `worker.py`.  
- Reemplazo de estructuras repetitivas con funciones auxiliares y fixtures reutilizables.
- Mejora en el manejo de excepciones (`try/except` explícitos y logs estructurados).
- Uso de `async/await` con `aiofiles` y contextos asíncronos consistentes.

📌 *Resultado:* mejor mantenibilidad y consistencia en los módulos con mayor complejidad lógica.

---

### 🔐 **3. Seguridad y vulnerabilidades**
No se detectaron vulnerabilidades en el análisis más reciente.  
Se reforzaron las rutas críticas mediante:

- Validaciones explícitas de tipo de archivo y tamaño en `/api/videos/upload`.
- Manejo seguro de archivos temporales (`tempfile` y borrado controlado).
- Validaciones de permisos de usuario en `/api/videos/{id}` y `/api/videos/delete`.

📌 *Resultado:* SonarQube mantiene la calificación **A (1.0)** en seguridad y fiabilidad.

---

### 🔁 **4. Duplicación de código**
La duplicación pasó de **2 % a 0 %**, eliminando redundancias en los tests y funciones repetidas.  
Se consolidaron estructuras de prueba comunes mediante **fixtures en `conftest.py`**.

📌 *Resultado:* código más compacto, con responsabilidades claramente separadas.

---

### 🧭 **5. Estado del Quality Gate**
El proyecto pasó de un estado **Rechazado (Entrega 1)** a **Aprobado (Entrega 2)**.  
Cumple todos los umbrales definidos en la política de calidad del pipeline CI/CD.

| Condición | Umbral | Resultado | Estado |
|------------|---------|------------|---------|
| Bugs = 0 | ✅ | 0 | ✅ |
| Vulnerabilidades = 0 | ✅ | 0 | ✅ |
| Code Smells < 10 | ✅ | 6 | ✅ |
| Duplicación < 3 % | ✅ | 0 % | ✅ |
| Cobertura > 50 % | ⚠️ | 54.1 % | ✅ |
| Quality Gate | OK | OK | 🟢 |

---


## 🧰 **Cambios técnicos aplicados**

| Categoría | Acción tomada | Archivos afectados |
|------------|----------------|--------------------|
| 🧪 Pruebas unitarias | Se añadieron más de 15 nuevos casos para excepciones, flujos negativos y cobertura de streaming | `test_video.py`, `test_workers.py`, `test_nfs.py` |
| 🧹 Limpieza de código | Se eliminaron duplicados y funciones obsoletas | `video.py`, `worker.py`, `cache.py` |
| 🧩 Manejo de errores | Se estandarizaron mensajes de error HTTP 400–500 | `video.py`, `security.py` |
| 🧱 Logging estructurado | Uso uniforme de `logger.exception()` y `logger.warning()` | Todos los módulos principales |
| 📦 CI/CD | Se integró acción `gitricko/sonarless@v1.3` para ejecutar SonarQube en cada PR | `.github/workflows/ci.yml` |

---

## 📋 **Conclusiones**

- Se logró una mejora significativa en la **cobertura de pruebas (+28 p.p.)**.  
- Se redujeron los **code smells en 73 %**, eliminando redundancias y mejorando mantenibilidad.  
- No existen bugs ni vulnerabilidades activas.
- El **Quality Gate se aprobó exitosamente**, evidenciando una evolución positiva en la calidad técnica del código.
