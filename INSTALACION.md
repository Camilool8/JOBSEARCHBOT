# Guía de Instalación Completa - Bot de Búsqueda de Empleos v2.0

## Requisitos del Sistema

### Software Requerido

- **Python 3.8 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)
- Cuenta de Discord con permisos para crear aplicaciones

### Verificar Versión de Python

```bash
python --version
# o
python3 --version
```

Debe mostrar Python 3.8 o superior.

## Estructura del Proyecto

Tu proyecto debe tener la siguiente estructura:

```
bot-empleos-discord/
├── job_bot.py              # Bot principal (REQUERIDO)
├── config.py               # Configuración (REQUERIDO)
├── salary_utils.py         # Extracción de salarios (REQUERIDO)
├── requirements.txt        # Dependencias (REQUERIDO)
├── .env                    # Variables de entorno (REQUERIDO - crear)
├── .env.example           # Plantilla de .env
├── .gitignore             # Archivos a ignorar en Git
├── configurar_bot.py      # Script de configuración (opcional)
├── test_token.py          # Verificador de token (opcional)
├── README.md              # Documentación
├── GUIA_RAPIDA.md         # Guía rápida
├── GUIA_USO.md            # Guía de uso
└── bot_empleos.log        # Log (se crea automáticamente)
```

## Paso 1: Crear Bot en Discord

### 1.1 Acceder al Portal de Desarrolladores

1. Ve a: https://discord.com/developers/applications
2. Inicia sesión con tu cuenta de Discord
3. El bot ya está creado con estos datos:
   ```
   Application ID: 1427460555286777886
   Client ID: 1427460555286777886
   ```

### 1.2 Obtener el Token del Bot

1. En el Portal de Desarrolladores, selecciona tu aplicación
2. Ve a la sección **"Bot"** en el menú lateral
3. Haz clic en **"Reset Token"**
4. **COPIA EL TOKEN INMEDIATAMENTE** (solo se muestra una vez)
5. Guárdalo en un lugar seguro

**IMPORTANTE:** Nunca compartas este token públicamente.

### 1.3 Activar Intenciones Privilegiadas

En la misma sección "Bot":

1. Busca **"Privileged Gateway Intents"**
2. Activa **"Message Content Intent"**
3. Haz clic en **"Save Changes"**

### 1.4 Configurar Permisos

El bot necesita estos permisos:

- ✅ Enviar mensajes
- ✅ Insertar enlaces
- ✅ Leer historial de mensajes
- ✅ Usar comandos de aplicación

### 1.5 Invitar el Bot a tu Servidor

Usa esta URL (ya configurada con los permisos correctos):

```
https://discord.com/oauth2/authorize?client_id=1427460555286777886&permissions=3941734153713728&integration_type=0&scope=applications.commands+bot
```

1. Abre la URL en tu navegador
2. Selecciona tu servidor
3. Haz clic en "Autorizar"

## Paso 2: Preparar el Entorno

### 2.1 Crear Directorio del Proyecto

```bash
# Crear directorio
mkdir bot-empleos-discord
cd bot-empleos-discord
```

### 2.2 Crear Entorno Virtual (Recomendado)

**En Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**En Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Verás `(venv)` al inicio de tu línea de comandos cuando esté activado.

### 2.3 Descargar/Copiar los Archivos

Asegúrate de tener estos 4 archivos principales:

1. **job_bot.py** - El bot principal
2. **config.py** - Configuración del sistema
3. **salary_utils.py** - Utilidades de extracción de salarios
4. **requirements.txt** - Lista de dependencias

## Paso 3: Instalar Dependencias

### 3.1 Verificar requirements.txt

Debe contener:

```
discord.py>=2.3.0
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
python-dotenv>=1.0.0
```

### 3.2 Instalar Paquetes

```bash
pip install -r requirements.txt
```

Esto instalará todas las dependencias necesarias.

### 3.3 Verificar Instalación

```bash
pip list
```

Deberías ver todos los paquetes instalados.

## Paso 4: Configurar Variables de Entorno

### 4.1 Crear Archivo .env

Crea un archivo llamado `.env` en el directorio raíz del proyecto:

**En Windows:**

```bash
copy .env.example .env
# o crear manualmente con notepad
notepad .env
```

**En Linux/Mac:**

```bash
cp .env.example .env
# o crear manualmente con nano
nano .env
```

### 4.2 Editar .env

Abre el archivo `.env` y agrega tu token:

```env
# Token del Bot de Discord (REQUERIDO)
DISCORD_BOT_TOKEN=tu_token_real_aqui

# Información del Bot (solo para referencia)
# Application ID: 1427460555286777886
# Client ID: 1427460555286777886
# Channel ID: 1427462740196196352

# APIs Opcionales
# ADZUNA_API_ID=tu_api_id
# ADZUNA_API_KEY=tu_api_key
```

**Reemplaza** `tu_token_real_aqui` con el token que copiaste del Portal de Desarrolladores.

### 4.3 Verificar .env

El archivo `.env` debe estar en el mismo directorio que `job_bot.py`.

```bash
# Verificar que existe
ls .env
# o en Windows
dir .env
```

## Paso 5: Verificar Configuración

### 5.1 Usar Script de Verificación (Opcional)

Si tienes `test_token.py`:

```bash
python test_token.py
```

Este script verificará:

- ✅ Que el token sea válido
- ✅ Que las dependencias estén instaladas
- ✅ Que los archivos necesarios existan
- ✅ Que el bot pueda conectarse a Discord

### 5.2 Verificación Manual

```bash
python -c "from config import Config; Config.validar(); Config.mostrar_configuracion()"
```

Esto debe mostrar la configuración del bot sin errores.

## Paso 6: Ejecutar el Bot

### 6.1 Primera Ejecución

```bash
python job_bot.py
```

Si todo está configurado correctamente, verás:

```
======================================================================
               CONFIGURACIÓN DEL BOT DE BÚSQUEDA DE EMPLEOS
======================================================================

INFORMACIÓN DEL BOT:
  Application ID:          1427460555286777886
  Client ID:               1427460555286777886
  Channel ID:              1427462740196196352

CONFIGURACIÓN DE BÚSQUEDA:
  Trabajos por búsqueda:   10
  ...

======================================================================
Bot iniciado correctamente: TuBot#1234
ID del bot: 1427460555286777886
Servidores: 1
Sistema de búsqueda de empleos activo
Módulos cargados:
  - config.py: Configuración
  - salary_utils.py: Extracción de salarios
  - Database: Programaciones
======================================================================
```

### 6.2 Verificar en Discord

En tu servidor de Discord:

1. Verifica que el bot aparezca en línea
2. Ve al canal configurado (ID: 1427462740196196352)
3. Escribe: `/ayuda`
4. Deberías ver la lista de comandos disponibles

## Paso 7: Probar el Bot

### 7.1 Comandos Básicos de Prueba

```
/ayuda
```

Debe mostrar la ayuda completa.

```
/trabajo python developer
```

Debe buscar trabajos y mostrar navegación interactiva.

```
/trabajo-programar devops engineer
```

Debe crear una programación.

```
/trabajo-lista
```

Debe mostrar las programaciones activas.

### 7.2 Verificar Funcionalidades

- ✅ Navegación con botones (Primera, Anterior, Siguiente, Última, Cerrar)
- ✅ Información detallada de cada trabajo
- ✅ Extracción de salarios (cuando disponible)
- ✅ Ordenamiento por salario
- ✅ Enlaces funcionales

## Solución de Problemas Comunes

### Error: "DISCORD_BOT_TOKEN no encontrado"

**Causa:** El archivo `.env` no existe o el token no está configurado.

**Solución:**

1. Verifica que el archivo `.env` exista en el directorio correcto
2. Abre `.env` y verifica que la línea `DISCORD_BOT_TOKEN=...` tenga tu token
3. No debe haber espacios alrededor del `=`

### Error: "No module named 'discord'"

**Causa:** Las dependencias no están instaladas.

**Solución:**

```bash
pip install -r requirements.txt
```

### Error: "Cannot import name 'Config' from 'config'"

**Causa:** El archivo `config.py` no está en el directorio correcto.

**Solución:**

1. Verifica que `config.py` esté en el mismo directorio que `job_bot.py`
2. No debe haber espacios o caracteres especiales en el nombre

### Error: "Cannot import name 'ExtractorSalario' from 'salary_utils'"

**Causa:** El archivo `salary_utils.py` no está disponible.

**Solución:**

1. Verifica que `salary_utils.py` esté en el mismo directorio que `job_bot.py`
2. Este archivo es REQUERIDO en la versión 2.0

### El bot no responde a comandos

**Posibles causas y soluciones:**

1. **Message Content Intent no activado**

   - Ve al Portal de Desarrolladores
   - Bot → Privileged Gateway Intents → Message Content Intent

2. **Bot no invitado al servidor**

   - Usa la URL de invitación proporcionada

3. **Comandos no sincronizados**

   - Espera 2-3 minutos después de iniciar el bot
   - Los comandos pueden tardar en aparecer

4. **Bot sin permisos**
   - Verifica los permisos del rol del bot en el servidor

### Error: "Rate Limited" o "429 Too Many Requests"

**Causa:** Demasiadas peticiones a las APIs.

**Solución:**

- Espera unos minutos antes de hacer más búsquedas
- Las APIs tienen límites de tasa

## Configuración Avanzada

### Modificar Límites de Búsqueda

Edita `config.py`:

```python
MAX_TRABAJOS_POR_BUSQUEDA: int = 20  # Cambiar de 10 a 20
```

### Cambiar Intervalo de Verificación

Edita `config.py`:

```python
INTERVALO_VERIFICACION_PROGRAMACIONES: int = 2  # Verificar cada 2 horas
```

### Activar Logging Detallado

Edita `.env`:

```env
LOG_LEVEL=DEBUG
```

### Configurar API de Adzuna (Opcional)

1. Regístrate en: https://developer.adzuna.com/
2. Obtén tu App ID y API Key
3. Edita `.env`:

```env
ADZUNA_API_ID=tu_app_id
ADZUNA_API_KEY=tu_api_key
```

4. Edita `config.py`:

```python
FEATURE_ADZUNA_API: bool = True
```

## Mantenimiento

### Actualizar Dependencias

```bash
pip install --upgrade -r requirements.txt
```

### Ver Logs

```bash
# En tiempo real
tail -f bot_empleos.log

# En Windows
type bot_empleos.log

# Últimas 50 líneas
tail -n 50 bot_empleos.log
```

### Limpiar Base de Datos

Si necesitas resetear las programaciones:

```bash
rm programaciones_trabajos.db
# El bot creará una nueva al reiniciar
```

## Despliegue 24/7

Para que el bot funcione permanentemente:

### Opción 1: Servidor Local

Usa herramientas como:

- **screen** (Linux)
- **tmux** (Linux/Mac)
- **nohup** (Linux/Mac)

```bash
nohup python job_bot.py &
```

### Opción 2: Servicios en la Nube

- **Railway**: Despliegue fácil, tier gratuito
- **Heroku**: Con limitaciones en tier gratuito
- **DigitalOcean**: VPS desde $5/mes
- **AWS EC2**: Tier gratuito por 12 meses

### Opción 3: Raspberry Pi

Ideal para hospedar 24/7 en casa con bajo consumo.

## Seguridad

### Mejores Prácticas

1. **Nunca compartas tu token**
2. **Agrega .env al .gitignore**
3. **No subas el token a GitHub**
4. **Rota el token periódicamente**
5. **Usa variables de entorno en producción**

### Verificar .gitignore

Asegúrate de que `.gitignore` contenga:

```
.env
*.log
*.db
__pycache__/
venv/
```

## Siguiente Paso

Una vez instalado y funcionando:

1. Lee la **GUIA_USO.md** para aprender todos los comandos
2. Configura tus primeras búsquedas programadas
3. Invita a otros usuarios a usar el bot

## Soporte

Si encuentras problemas:

1. Verifica los logs: `bot_empleos.log`
2. Revisa esta guía nuevamente
3. Verifica que todos los archivos estén presentes
4. Prueba con el script `test_token.py`

## Checklist Final

Antes de reportar problemas, verifica:

- [ ] Python 3.8+ instalado
- [ ] Todas las dependencias instaladas (`pip list`)
- [ ] Archivos requeridos presentes (job_bot.py, config.py, salary_utils.py)
- [ ] Archivo .env creado con token válido
- [ ] Message Content Intent activado en Discord
- [ ] Bot invitado al servidor
- [ ] Bot tiene permisos necesarios
- [ ] Esperaste 2-3 minutos después de iniciar

Si todo está ✅, el bot debería funcionar perfectamente.
