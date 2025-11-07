# 📊 Reporte de Análisis SonarQube

**Proyecto:** MISW4204-202515-anb-Grupo03-local  
**Rama analizada:** `main`  
**Fecha del análisis:** Última ejecución CI con acción `gitricko/sonarless@v1.3`  
**Estado del análisis:** ✅ Ejecución exitosa  
**Quality Gate:** 🟢 **Aprobado**

---

En esta entrega se consolidan las mejoras iniciadas en la anterior, alcanzando una **cobertura del 67.3 %** y reduciendo los *code smells* a **solo 4**.  
El análisis muestra un sistema más estable, limpio y con una cobertura de pruebas mucho más representativa del flujo real de la aplicación.  

El incremento se debe principalmente a:
- Inclusión de los módulos `message_broker`, `storeapi` y `utils` en la cobertura total.
- Ajustes de exclusiones para focalizar la evaluación en el código relevante.
- Nuevas pruebas automáticas para los componentes de mensajería y almacenamiento.

---

## 🧩 Comparativo General

| Métrica | Entrega 2 | Entrega 3 | Variación | Estado |
|----------|------------|-----------|-----------|---------|
| 🐞 **Bugs** | 0 | 0 | 🟰 | ✅ Sin errores funcionales |
| 🔒 **Vulnerabilidades** | 0 | 0 | 🟰 | ✅ Sin riesgos de seguridad |
| ⚠️ **Code Smells** | 6 | **4** | 🔽 **–33 %** | ✅ Mayor limpieza de código |
| 🧪 **Cobertura de pruebas unitarias** | 54.1 % | **67.3 %** | 🔼 **+13.2 pts** | ⚠️ Excelente avance |
| 🔁 **Duplicación de código** | 0 % | 0 % | 🟰 | ✅ Código limpio |
| 🚦 **Quality Gate** | 🟢 Aprobado | 🟢 Aprobado | 🟰 | ✅ Cumple todos los umbrales |

---

## 📈 Análisis Detallado

### **1. Cobertura de pruebas unitarias**
La cobertura aumentó de **54.1 % a 67.3 %**, consolidando un núcleo de pruebas más completo.  
Las principales mejoras fueron:

- Incorporación de pruebas sobre `message_broker` (Kafka y worker).  
- Validaciones adicionales de errores en `storeapi/database.py` y `utils/ffmpeg.py`.  
- Cobertura de escenarios asíncronos y manejo de excepciones específicas.

📌 *Resultado:* Cobertura sólida, con alto nivel de aseguramiento funcional.

---

### ⚙️ **2. Reducción de code smells**
Los *code smells* bajaron de **6 → 4**, tras refactorizar funciones y eliminar código comentado.

**Principales observaciones restantes (según SonarQube):**
- 🗂 `message_broker/tasks_dispatcher.py`: eliminar código comentado.  
- 🧱 `storeapi/database.py`: definir constante en lugar de literal repetido `"users.id"`.  
- 🎞️ `utils/ffmpeg.py`: ajustar manejo de excepciones y evitar f-string sin campos.  

📌 *Resultado:* solo 4 advertencias menores, todas localizadas y sin impacto funcional.

---

### 🔐 **3. Seguridad y vulnerabilidades**
Nuevamente, **sin vulnerabilidades detectadas**.  
Las reglas de seguridad mantienen calificación **A (1.0)** en todos los indicadores.

📌 *Resultado:* cumplimiento total en seguridad y fiabilidad.

---

### 🔁 **4. Duplicación de código**
Se mantiene en **0 %**, gracias a la reutilización de fixtures y funciones auxiliares comunes.

📌 *Resultado:* alta mantenibilidad y bajo acoplamiento.

---

### 🧭 **5. Estado del Quality Gate**
El proyecto conserva su estado **Aprobado**, cumpliendo todos los umbrales.

| Condición | Umbral | Resultado | Estado |
|------------|---------|------------|---------|
| Bugs = 0 | ✅ | 0 | ✅ |
| Vulnerabilidades = 0 | ✅ | 0 | ✅ |
| Code Smells < 10 | ✅ | 4 | ✅ |
| Duplicación < 3 % | ✅ | 0 % | ✅ |
| Cobertura > 50 % | ✅ | 67.3 % | 🟢 |
| Quality Gate | OK | OK | 🟢 |

---

## 🧰 **Cambios técnicos aplicados**

| Categoría | Acción tomada | Archivos afectados |
|------------|----------------|--------------------|
| 🧪 Pruebas unitarias | Cobertura extendida a módulos de mensajería y utilidades | `test_kafka_consumer.py`, `test_ffmpeg.py`, `test_cache.py` |
| 🧹 Limpieza de código | Eliminación de comentarios y duplicados | `tasks_dispatcher.py`, `ffmpeg.py`, `database.py` |
| ⚙️ Refactorización | Ajuste de nombres de funciones y constantes repetidas | `worker.py`, `database.py` |
| 📦 Configuración de análisis | Nuevas exclusiones refinadas para focos de cobertura | `sonar-project.properties` |

---

## 📋 **Conclusiones**

- La **cobertura total supera el 67 %**, consolidando la estabilidad del backend.  
- Los *code smells* se reducen a un mínimo de **4**, todos de severidad moderada o baja.  
- No hay **bugs ni vulnerabilidades**, manteniendo el nivel de calidad **A**.  
- El proyecto conserva un **Quality Gate aprobado**, demostrando madurez técnica y alta mantenibilidad.

---  
📊 *SonarQube confirma que el backend se encuentra en un estado óptimo, listo para entornos de producción o escalado en AWS.*