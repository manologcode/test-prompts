# API Prompts

Una aplicación web que permite gestionar y reutilizar prompts para modelos de lenguaje (LLMs), con capacidad de procesar texto desde URLs y generar respuestas utilizando diferentes modelos.

## Características

- ✨ Gestión de prompts (crear, editar, almacenar)
- 🌐 Extracción de texto desde URLs
- 📺 Soporte para transcripciones de YouTube
- 🤖 Integración con múltiples modelos de LLM
- 🎨 Interfaz moderna y responsiva con Tailwind CSS
- 🔄 Animaciones de carga y feedback visual

## Requisitos

- Docker y Docker Compose
- Acceso a un servidor LLM (configurable mediante variables de entorno)

## arrancar docker la aplicacion

primero crear el archivo de la base de datos

      touch data.db

correr la app con docker run:
```bash
docker run -d -p 5088:5088 -e LLM_URL=http://192.168.1.69:11434/api/generate -v ./data.db:/app/sql_app.db --name prompts manologcode/test-prompts
```

si lo queremos corres con docker compose:

```bash
services:
  prompts:
    image: manologcode/test-prompts
    container_name: prompts
    environment:
      - LLM_URL=http://192.168.1.69:11434/api/generate
    ports:
      - 5080:5088
    volumes:
      - ./data.db:/app/sql_app.db
```

Este ejemplo es valido se tiene corriendo **ollama** en la ip 192.168.1.69

## Uso

La aplicación estará disponible en `http://localhost:5088`


## Licencia

MIT
