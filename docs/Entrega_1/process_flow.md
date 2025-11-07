# Diagrama de Flujo de Procesos

El siguiente diagrama describe las **etapas del flujo de procesamiento de videos** en la plataforma **ANB Rising Stars Showcase**, desde la carga inicial del archivo hasta su publicación final para votación.  

Este flujo garantiza un procesamiento eficiente mediante **tareas asíncronas**, evitando bloqueos en la API y mejorando la experiencia del usuario.

---

## Etapas del proceso

| Etapa | Descripción |
|--------|--------------|
| **1. Carga del video** | El jugador envía un archivo de video mediante un endpoint de la API (`/api/videos/upload`). La API valida el formato y tamaño antes de continuar. |
| **2. Registro y encolado** | El backend registra el video en la base de datos con estado `uploaded` y envía una tarea al tópico `video_tasks` en Kafka para su procesamiento asíncrono. |
| **3. Procesamiento asíncrono** | El **Worker Consumer** escucha el tópico y procesa el video: recorta la duración, ajusta la resolución, agrega la marca de agua y elimina el audio. |
| **4. Almacenamiento del resultado** | Una vez finalizado el procesamiento, el worker guarda el video resultante en la carpeta `videos/processed` y actualiza su estado a `processed` en la base de datos. |
| **5. Disponibilidad pública** | La API permite que el público y los jurados visualicen los videos procesados y emitan votos. El ranking se actualiza dinámicamente según los resultados. |

---

## Diagrama de Flujo de Procesos

<img alt="process_flow" src="https://github.com/user-attachments/assets/b04e194d-2945-4ae2-8f92-474a814b750c" />
