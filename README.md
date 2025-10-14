# Sistema de Búsqueda de Empleos Remotos para Discord

Bot automatizado de Discord para búsqueda de trabajos remotos en LinkedIn y otras plataformas de empleo, con actualizaciones programadas diarias.

## Características Principales

- **Búsqueda Instantánea**: Comando `/trabajo` para obtener los 10 mejores trabajos remotos al instante
- **Información Detallada**: Cada trabajo muestra empresa, ubicación, salario, tipo de trabajo, nivel de experiencia y más
- **Extracción Automática de Salarios**: Sistema avanzado con expresiones regulares que detecta salarios en múltiples formatos
- **Ordenamiento Inteligente**: Los trabajos se ordenan automáticamente por salario (los mejor pagados primero)
- **Navegación Interactiva**: Sistema de paginación con botones para explorar trabajos uno por uno
- **Actualizaciones Automáticas**: Comando `/trabajo-programar` para recibir publicaciones diarias programadas
- **Múltiples Fuentes**: Integración con LinkedIn y APIs alternativas de empleos
- **Gestión de Programaciones**: Visualiza y administra todas las búsquedas programadas activas

## Comandos Disponibles

| Comando                               | Descripción                                        | Ejemplo                                     |
| ------------------------------------- | -------------------------------------------------- | ------------------------------------------- |
| `/trabajo <keyword> <pais>`           | Buscar trabajos remotos con navegación interactiva | `/trabajo python developer usa`             |
| `/trabajo-programar <keyword> <pais>` | Programar actualizaciones diarias                  | `/trabajo-programar react developer canada` |
| `/trabajo-lista`                      | Ver todas las programaciones activas               | `/trabajo-lista`                            |
| `/trabajo-cancelar <keyword> <pais>`  | Cancelar una programación                          | `/trabajo-cancelar python usa`              |
| `/ayuda`                              | Mostrar información de comandos                    | `/ayuda`                                    |

### Características Especiales de Búsqueda

**Sistema de Paginación Interactiva:**

- Navega entre trabajos usando botones
- Primera página / Anterior / Siguiente / Última página
- Cierra la vista cuando termines
- Cada trabajo se muestra en detalle completo

**Extracción Automática de Salarios:**
El bot detecta salarios en múltiples formatos:

- Rangos con símbolos: `$50,000 - $80,000`
- Formato abreviado: `50k-80k` o `$50k-$80k`
- Salarios por hora: `$25-$35/hr` (se convierte a anual)
- Múltiples monedas: `# Sistema de Búsqueda de Empleos Remotos para Discord

Bot automatizado de Discord para búsqueda de trabajos remotos en LinkedIn y otras plataformas de empleo, con actualizaciones programadas diarias.

## Características Principales

- **Búsqueda Instantánea**: Comando `/trabajo` para obtener los 10 mejores trabajos remotos al instante
- **Información Detallada**: Cada trabajo muestra empresa, ubicación, salario, tipo de trabajo, nivel de experiencia y más
- **Extracción Automática de Salarios**: Sistema avanzado con expresiones regulares que detecta salarios en múltiples formatos
- **Ordenamiento Inteligente**: Los trabajos se ordenan automáticamente por salario (los mejor pagados primero)
- **Navegación Interactiva**: Sistema de paginación con botones para explorar trabajos uno por uno
- **Actualizaciones Automáticas**: Comando `/trabajo-programar` para recibir publicaciones diarias programadas
- **Múltiples Fuentes**: Integración con LinkedIn y APIs alternativas de empleos
- **Gestión de Programaciones**: Visualiza y administra todas las búsquedas programadas activas

, `€`, `£`

- Contexto explícito: `Salary: 50,000-80,000`

**Ordenamiento por Salario:**

- Los trabajos se ordenan automáticamente por salario promedio
- Los mejor pagados aparecen primero
- Trabajos sin salario disponible van al final

## Instalación Rápida

```bash
# 1. Clonar o descargar archivos requeridos
# Necesitas: job_bot.py, config.py, salary_utils.py, requirements.txt

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear archivo .env con tu token
echo "DISCORD_BOT_TOKEN=tu_token_aqui" > .env

# 4. Ejecutar el bot
python job_bot.py
```

**Nota:** Los archivos `config.py` y `salary_utils.py` son **REQUERIDOS**. El bot no funcionará sin ellos.

## Guía de Instalación Completa

Para instrucciones paso a paso detalladas, consulta **[INSTALACION.md](INSTALACION.md)**

La guía completa incluye:

- Configuración del bot en Discord
- Activación de permisos necesarios
- Configuración de APIs opcionales
- Solución de problemas comunes
- Configuración para despliegue 24/7

## Dependencias y Requisitos

### Requisitos del Sistema

- **Python:** 3.8 o superior
- **Espacio en disco:** ~50 MB
- **RAM:** Mínimo 256 MB
- **Conexión a Internet:** Requerida

### Dependencias de Python

```
discord.py>=2.3.0        # Framework para bots de Discord
aiohttp>=3.9.0           # Cliente HTTP asíncrono
beautifulsoup4>=4.12.0   # Parser HTML para scraping
lxml>=4.9.0              # Parser XML/HTML rápido
python-dotenv>=1.0.0     # Carga de variables de entorno
```

### Archivos Requeridos

| Archivo            | Descripción              | Obligatorio |
| ------------------ | ------------------------ | ----------- |
| `job_bot.py`       | Bot principal            | Sí          |
| `config.py`        | Sistema de configuración | Sí          |
| `salary_utils.py`  | Extracción de salarios   | Sí          |
| `requirements.txt` | Lista de dependencias    | Sí          |
| `.env`             | Variables de entorno     | Sí (crear)  |
| `README.md`        | Documentación            | No          |

**IMPORTANTE:** El bot NO funcionará sin `config.py` y `salary_utils.py`. Estos módulos son parte integral de la arquitectura v2.0.

## Características Técnicas

### Sistema de Logging

- **Archivo de log:** `bot_empleos.log`
- **Niveles:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotación:** Configurable
- **Formato:** Timestamp, nivel, módulo, mensaje

```bash
# Ver logs en tiempo real
tail -f bot_empleos.log

# Últimas 100 líneas
tail -n 100 bot_empleos.log
```

### Base de Datos

- **Tipo:** SQLite3
- **Archivo:** `programaciones_trabajos.db`
- **Gestión:** Clase `DatabaseManager` con métodos seguros
- **Operaciones:** CRUD completo para programaciones

### Manejo de Errores

- Try-catch en todas las operaciones críticas
- Logging detallado de excepciones
- Mensajes de error claros al usuario
- Validación de configuración al inicio

### Fuentes de Datos

#### LinkedIn (Scraping)

- **Estado:** Funcional con limitaciones
- **Nota:** LinkedIn bloquea scraping activamente
- **Recomendación:** Usar como respaldo, no como fuente principal

#### RemoteOK API

- **Estado:** Activo
- **Autenticación:** No requerida
- **Límites:** Sin límites documentados
- **Datos:** Trabajos remotos globales

#### Adzuna API (Opcional)

- **Estado:** Configurable
- **Autenticación:** App ID + API Key
- **Límites:** 250 requests/mes (tier gratuito)
- **Configuración:** Ver `config.py`

### Performance

- **Búsquedas asíncronas:** Múltiples fuentes en paralelo
- **Timeout configurable:** 20 segundos por defecto
- **Caché:** No implementado (futuro)
- **Rate limiting:** Respeta límites de APIs

### Seguridad

- Tokens en variables de entorno
- Validación de configuración
- Sanitización de entradas
- Logging sin información sensible
- .gitignore configurado

## Solución de Problemas Detallada

### Error: "Cannot import name 'Config'"

**Causa:** `config.py` no está disponible o tiene errores de sintaxis.

**Solución:**

```bash
# Verificar que el archivo existe
ls config.py

# Probar importación
python -c "from config import Config"
```

### Error: "Cannot import name 'ExtractorSalario'"

**Causa:** `salary_utils.py` no está disponible.

**Solución:**

```bash
# Verificar que el archivo existe
ls salary_utils.py

# Probar importación
python -c "from salary_utils import ExtractorSalario"
```

### Error: "Validation Error" al iniciar

**Causa:** Configuración inválida en `config.py`.

**Solución:**

```bash
# Verificar configuración
python -c "from config import Config; Config.validar()"
```

### El bot no encuentra salarios

**Causa:** Los trabajos no incluyen información salarial o los patrones no coinciden.

**Solución:**

1. Revisa los patrones en `salary_utils.py`
2. Activa DEBUG logging para ver qué se está extrayendo
3. Considera agregar patrones personalizados

### Base de datos bloqueada

**Causa:** Otra instancia del bot está corriendo.

**Solución:**

```bash
# Linux/Mac
ps aux | grep job_bot.py
kill -9 [PID]

# Windows
tasklist | findstr python
taskkill /PID [PID] /F
```

### Comandos no aparecen en Discord

**Causa:** Los comandos no se han sincronizado.

**Solución:**

1. Espera 2-3 minutos después de iniciar el bot
2. Reinicia Discord (Ctrl+R)
3. Verifica que el bot tenga permisos de "applications.commands"

### Rate Limiting / 429 Errors

**Causa:** Demasiadas peticiones a las APIs.

**Solución:**

1. Espera unos minutos antes de hacer más búsquedas
2. Aumenta `INTERVALO_VERIFICACION_PROGRAMACIONES`
3. Reduce `MAX_TRABAJOS_POR_BUSQUEDA`

### Logs no se generan

**Causa:** Permisos de escritura insuficientes.

**Solución:**

```bash
# Verificar permisos del directorio
ls -la

# Dar permisos de escritura
chmod +w .

# Crear archivo manualmente
touch bot_empleos.log
chmod 644 bot_empleos.log
```

## Opciones de Despliegue

Para operación 24/7, hospeda el bot en:

**Servicios en la Nube:**

- **Railway**: Nivel gratuito disponible, fácil despliegue
- **Heroku**: Nivel gratuito (con limitaciones)
- **DigitalOcean**: VPS desde $5/mes
- **AWS EC2**: Nivel gratuito por 12 meses
- **Google Cloud Platform**: Créditos gratuitos para nuevos usuarios

**Servidores Locales:**

- Raspberry Pi con conexión estable
- Servidor personal con uptime garantizado

### Ejemplo de Despliegue en Railway

1. Crea una cuenta en [Railway](https://railway.app)
2. Conecta tu repositorio de GitHub
3. Agrega las variables de entorno en la configuración
4. Railway detectará automáticamente el proyecto Python y lo desplegará

## Estructura del Proyecto

```
bot-empleos-discord/
│
├── job_bot.py                    # Código principal del bot
├── config.py                     # Gestión de configuración
├── salary_utils.py               # Extracción de salarios
├── requirements.txt              # Dependencias de Python
├── .env                         # Variables de entorno (no subir a GitHub)
├── .env.example                 # Plantilla de variables de entorno
├── programaciones_trabajos.db   # Base de datos SQLite (generada automáticamente)
└── README.md                    # Este archivo
```

## Configuración Avanzada

### Modificar Límites de Búsqueda

Edita `config.py`:

```python
class Config:
    MAX_TRABAJOS_POR_BUSQUEDA: int = 20  # Cambiar de 10 a 20
    MAX_TRABAJOS_POR_FUENTE: int = 30    # Máximo por API
    TIMEOUT_REQUEST_HTTP: int = 30        # Aumentar timeout
```

### Activar/Desactivar Fuentes

```python
class Config:
    FEATURE_LINKEDIN_SCRAPING: bool = False  # Desactivar LinkedIn
    FEATURE_REMOTEOK_API: bool = True        # Mantener RemoteOK
    FEATURE_ADZUNA_API: bool = True          # Activar Adzuna (si configurado)
```

### Personalizar Colores

```python
class Config:
    COLOR_PRINCIPAL: int = 0x5865F2      # Discord Blurple
    COLOR_EXITO: int = 0x57F287          # Discord Green
    COLOR_ADVERTENCIA: int = 0xFEE75C    # Discord Yellow
    COLOR_ERROR: int = 0xED4245          # Discord Red
```

### Configurar Intervalo de Programaciones

```python
class Config:
    INTERVALO_VERIFICACION_PROGRAMACIONES: int = 2  # Verificar cada 2 horas
    INTERVALO_ACTUALIZACION_PROGRAMADA: int = 12    # Actualizar cada 12 horas
```

### Activar Logging Detallado

En `.env`:

```env
LOG_LEVEL=DEBUG
```

O en `config.py`:

```python
LOG_LEVEL: str = 'DEBUG'
```

### Configurar API de Adzuna

1. Regístrate en: https://developer.adzuna.com/
2. Obtén tu App ID y API Key
3. Edita `.env`:

```env
ADZUNA_API_ID=tu_app_id_aqui
ADZUNA_API_KEY=tu_api_key_aqui
```

4. Activa en `config.py`:

```python
FEATURE_ADZUNA_API: bool = True
```

### Personalizar Patrones de Extracción de Salarios

Edita `salary_utils.py` para agregar nuevos patrones:

```python
class ExtractorSalario:
    PATRONES_SALARIO = {
        'tu_patron_personalizado': [
            r'nuevo_patron_regex_aqui',
        ],
        # ... patrones existentes
    }
```

## Seguridad

**Prácticas recomendadas:**

- Nunca compartas tu token de Discord públicamente
- Mantén el archivo `.env` en tu `.gitignore`
- Usa variables de entorno para información sensible
- Actualiza regularmente las dependencias para parches de seguridad
- Revisa los permisos del bot periódicamente

## Soporte y Contribuciones

Este proyecto es de código abierto. Las contribuciones son bienvenidas.

**Para reportar problemas:**

1. Describe el problema detalladamente
2. Incluye mensajes de error (sin tokens sensibles)
3. Especifica tu versión de Python y sistema operativo

## Licencia

Este proyecto se distribuye bajo la Licencia MIT. Puedes usar y modificar el código libremente para tus necesidades.
