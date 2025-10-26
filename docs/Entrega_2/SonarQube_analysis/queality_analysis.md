# 📄 Reporte 2 - Análisis SonarQube

**Proyecto:** MISW4204-202515-anb-Grupo03-local  
**Rama:** main
**Fecha del análisis:** Última ejecución CI (acción `gitricko/sonarless@v1.3`)  
**Quality Gate:** Aprobado

---


## 📊 PRE Métricas principales

| Métrica | Valor | Estado | Interpretación |
|----------|--------|---------|----------------|
| 🐞 **Bugs** | `0` | ✅ | No se detectaron defectos funcionales. |
| 🔒 **Vulnerabilidades** | `0` | ✅ | Sin vulnerabilidades de seguridad. |
| ⚠️ **Code Smells** | `22` | ⚠️ | Leves problemas de mantenibilidad. |
| 🧪 **Cobertura de pruebas unitarias** | `25.9 %` | ⚠️ | Cobertura baja; se recomienda ≥ 70 %. |
| 🧮 **Duplicación de código** | `2 %` | ✅ | Nivel óptimo de duplicación. |
| 🚦 **Quality Gate Status** | `OK` | 🟢 | Cumple todos los umbrales de calidad. |

---

## 📈 Resumen general

- **Análisis completado exitosamente.**
- **Cobertura de pruebas:** 25.9 % → requiere mejora significativa.
- **Sin bugs ni vulnerabilidades.**
- **Duplicación de código mínima (2 %).**
- **Excelente mantenibilidad (rating A).**
- **13 hotspots de seguridad** que deben revisarse, aunque no representan vulnerabilidades activas.
- **Quality Gate aprobado.**

---

## 🧭 Conclusiones y recomendaciones

1. ✅ **La aplicación cumple con los criterios de calidad base.**  
   No existen vulnerabilidades ni errores críticos que afecten el funcionamiento o la seguridad.

2. ⚠️ **Aumentar la cobertura de pruebas unitarias.**  
   - Incluir casos de prueba para endpoints principales (`/api/videos/upload`, `/api/public/rankings`, etc.).  
   - Usar `pytest` con `coverage` para alcanzar ≥ 70 %.

3. 🧰 **Revisar los 22 code smells** detectados para mejorar mantenibilidad y legibilidad del código.

4. 🔐 **Validar manualmente los 13 security hotspots**: revisar configuraciones, variables de entorno y Dockerfiles.

5. 🔁 **Mantener el pipeline automatizado de análisis** (`gitricko/sonarless@v1.3`) activo en cada push o PR a `main`.
