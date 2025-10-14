"""
Configuración del Bot de Búsqueda de Empleos Remotos
Este módulo maneja todas las configuraciones y validaciones del sistema
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Cargar variables de entorno desde archivo .env
load_dotenv()


class Config:
    """Clase de configuración centralizada para el bot"""
    
    # ==================== CONFIGURACIÓN DE DISCORD ====================
    
    # Token del Bot de Discord (Requerido)
    DISCORD_TOKEN: str = os.getenv('DISCORD_BOT_TOKEN', '')
    
    # Información del Bot (solo para referencia)
    APPLICATION_ID: str = '1427460555286777886'
    CLIENT_ID: str = '1427460555286777886'
    CHANNEL_ID: str = '1427462740196196352'
    
    # ==================== CONFIGURACIÓN DE APIs EXTERNAS ====================
    
    # API de Adzuna (Opcional)
    ADZUNA_APP_ID: str = os.getenv('ADZUNA_API_ID', '')
    ADZUNA_API_KEY: str = os.getenv('ADZUNA_API_KEY', '')
    
    # API de Indeed (Opcional - para futuras implementaciones)
    INDEED_PUBLISHER_ID: str = os.getenv('INDEED_PUBLISHER_ID', '')
    
    # ==================== CONFIGURACIÓN DEL BOT ====================
    
    # Límites de búsqueda
    MAX_TRABAJOS_POR_BUSQUEDA: int = 10
    MIN_TRABAJOS_POR_BUSQUEDA: int = 1
    MAX_TRABAJOS_POR_FUENTE: int = 20  # Máximo a obtener de cada fuente
    
    # Intervalos de tiempo (en horas)
    INTERVALO_VERIFICACION_PROGRAMACIONES: int = 1  # Verificar programaciones cada hora
    INTERVALO_ACTUALIZACION_PROGRAMADA: int = 24    # Ejecutar búsquedas programadas cada 24h
    
    # Timeouts (en segundos)
    TIMEOUT_VISTA_PAGINACION: int = 300  # 5 minutos
    TIMEOUT_REQUEST_HTTP: int = 20       # 20 segundos
    
    # ==================== BASE DE DATOS ====================
    
    # Nombre del archivo de base de datos SQLite
    NOMBRE_DB: str = 'programaciones_trabajos.db'
    
    # ==================== COLORES PARA EMBEDS ====================
    
    # Colores en formato hexadecimal (sin el 0x prefix para facilitar uso)
    COLOR_PRINCIPAL: int = 0x0A66C2      # Azul profesional (LinkedIn)
    COLOR_EXITO: int = 0x00FF00          # Verde brillante
    COLOR_EXITO_OSCURO: int = 0x00AA00   # Verde oscuro (para actualizaciones diarias)
    COLOR_ADVERTENCIA: int = 0xFFA500    # Naranja
    COLOR_ERROR: int = 0xFF0000          # Rojo
    COLOR_INFO: int = 0x808080           # Gris
    
    # ==================== CONFIGURACIÓN DE LOGGING ====================
    
    # Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Archivo de log
    LOG_FILE: str = 'bot_empleos.log'
    
    # Formato de log
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ==================== CONFIGURACIÓN DE SCRAPING ====================
    
    # User agents para requests
    USER_AGENT_LINKEDIN: str = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    USER_AGENT_API: str = 'Mozilla/5.0 (compatible; DiscordBot/2.0; +https://discord.com)'
    
    # Headers base para requests
    HEADERS_BASE: dict = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # ==================== URLs DE APIs ====================
    
    # RemoteOK
    URL_REMOTEOK_API: str = 'https://remoteok.com/api'
    
    # LinkedIn (base URL para scraping)
    URL_LINKEDIN_JOBS: str = 'https://www.linkedin.com/jobs/search/'
    
    # Adzuna (template URL)
    URL_ADZUNA_API: str = 'https://api.adzuna.com/v1/api/jobs/{country}/search/1'
    
    # ==================== CONFIGURACIÓN DE EXTRACCIÓN DE SALARIOS ====================
    
    # Monedas soportadas
    MONEDAS_SOPORTADAS: list = ['$', '€', '£']
    
    # Multiplicador para calcular salario anual desde salario por hora
    # Asume 40 horas/semana * 52 semanas/año = 2080 horas/año
    HORAS_TRABAJO_ANUAL: int = 2080
    
    # ==================== MENSAJES DEL SISTEMA ====================
    
    # Mensajes de error
    MSG_ERROR_GENERICO: str = "Ocurrió un error inesperado. Por favor, intenta nuevamente."
    MSG_ERROR_SIN_RESULTADOS: str = "No se encontraron trabajos que coincidan con los criterios."
    MSG_ERROR_TIMEOUT: str = "La búsqueda tomó demasiado tiempo. Intenta nuevamente."
    
    # Mensajes de éxito
    MSG_PROGRAMACION_CREADA: str = "Programación creada exitosamente."
    MSG_PROGRAMACION_CANCELADA: str = "Programación cancelada exitosamente."
    
    # ==================== FEATURES FLAGS ====================
    
    # Activar/desactivar features
    FEATURE_LINKEDIN_SCRAPING: bool = True
    FEATURE_REMOTEOK_API: bool = True
    FEATURE_ADZUNA_API: bool = False  # Activar cuando se configure
    FEATURE_PROGRAMACIONES: bool = True
    FEATURE_EXTRACCION_SALARIOS: bool = True
    
    # ==================== MÉTODOS DE VALIDACIÓN ====================
    
    @classmethod
    def validar(cls) -> bool:
        """
        Valida que toda la configuración requerida esté presente.
        
        Returns:
            bool: True si la configuración es válida
            
        Raises:
            ValueError: Si falta configuración requerida
        """
        errores = []
        
        # Validar token de Discord (REQUERIDO)
        if not cls.DISCORD_TOKEN:
            errores.append(
                "DISCORD_BOT_TOKEN no encontrado en las variables de entorno.\n"
                "Crea un archivo .env con: DISCORD_BOT_TOKEN=tu_token_aqui"
            )
        elif len(cls.DISCORD_TOKEN) < 50:
            errores.append(
                "DISCORD_BOT_TOKEN parece inválido (muy corto).\n"
                "Los tokens de Discord suelen tener 70+ caracteres."
            )
        
        # Validar límites
        if cls.MAX_TRABAJOS_POR_BUSQUEDA < cls.MIN_TRABAJOS_POR_BUSQUEDA:
            errores.append(
                f"MAX_TRABAJOS_POR_BUSQUEDA ({cls.MAX_TRABAJOS_POR_BUSQUEDA}) "
                f"debe ser mayor que MIN_TRABAJOS_POR_BUSQUEDA ({cls.MIN_TRABAJOS_POR_BUSQUEDA})"
            )
        
        if cls.MAX_TRABAJOS_POR_BUSQUEDA > 50:
            errores.append(
                f"MAX_TRABAJOS_POR_BUSQUEDA ({cls.MAX_TRABAJOS_POR_BUSQUEDA}) "
                "es demasiado alto. Máximo recomendado: 50"
            )
        
        # Validar intervalos
        if cls.INTERVALO_VERIFICACION_PROGRAMACIONES < 1:
            errores.append(
                "INTERVALO_VERIFICACION_PROGRAMACIONES debe ser al menos 1 hora"
            )
        
        # Validar base de datos
        if not cls.NOMBRE_DB or not cls.NOMBRE_DB.endswith('.db'):
            errores.append(
                "NOMBRE_DB debe ser un nombre de archivo válido terminado en .db"
            )
        
        # Advertencias sobre APIs opcionales
        advertencias = []
        if not cls.ADZUNA_APP_ID or not cls.ADZUNA_API_KEY:
            advertencias.append(
                "ADZUNA API no configurada (opcional). "
                "Para usarla, agrega ADZUNA_API_ID y ADZUNA_API_KEY al .env"
            )
        
        # Si hay errores, lanzar excepción
        if errores:
            mensaje_error = "\n\n".join([f"• {error}" for error in errores])
            raise ValueError(f"\nERRORES DE CONFIGURACIÓN:\n\n{mensaje_error}\n")
        
        # Mostrar advertencias si las hay
        if advertencias:
            print("\nADVERTENCIAS DE CONFIGURACIÓN:")
            for advertencia in advertencias:
                print(f"  ⚠ {advertencia}")
            print()
        
        return True
    
    @classmethod
    def mostrar_configuracion(cls) -> None:
        """Muestra la configuración actual del bot (sin información sensible)"""
        print("\n" + "="*70)
        print(" " * 15 + "CONFIGURACIÓN DEL BOT DE BÚSQUEDA DE EMPLEOS")
        print("="*70)
        
        print("\nINFORMACIÓN DEL BOT:")
        print(f"  Application ID:          {cls.APPLICATION_ID}")
        print(f"  Client ID:               {cls.CLIENT_ID}")
        print(f"  Channel ID:              {cls.CHANNEL_ID}")
        
        print("\nCONFIGURACIÓN DE BÚSQUEDA:")
        print(f"  Trabajos por búsqueda:   {cls.MAX_TRABAJOS_POR_BUSQUEDA}")
        print(f"  Trabajos por fuente:     {cls.MAX_TRABAJOS_POR_FUENTE}")
        print(f"  Timeout de requests:     {cls.TIMEOUT_REQUEST_HTTP}s")
        print(f"  Timeout de vista:        {cls.TIMEOUT_VISTA_PAGINACION}s")
        
        print("\nPROGRAMACIONES:")
        print(f"  Verificar cada:          {cls.INTERVALO_VERIFICACION_PROGRAMACIONES} hora(s)")
        print(f"  Ejecutar cada:           {cls.INTERVALO_ACTUALIZACION_PROGRAMADA} hora(s)")
        print(f"  Base de datos:           {cls.NOMBRE_DB}")
        
        print("\nFUENTES DE DATOS:")
        print(f"  LinkedIn Scraping:       {'✓ Activo' if cls.FEATURE_LINKEDIN_SCRAPING else '✗ Desactivado'}")
        print(f"  RemoteOK API:            {'✓ Activo' if cls.FEATURE_REMOTEOK_API else '✗ Desactivado'}")
        print(f"  Adzuna API:              {'✓ Configurado' if cls.ADZUNA_API_KEY else '✗ No configurado'}")
        
        print("\nFUNCIONALIDADES:")
        print(f"  Extracción de salarios:  {'✓ Activo' if cls.FEATURE_EXTRACCION_SALARIOS else '✗ Desactivado'}")
        print(f"  Programaciones:          {'✓ Activo' if cls.FEATURE_PROGRAMACIONES else '✗ Desactivado'}")
        
        print("\nSEGURIDAD:")
        print(f"  Token configurado:       {'✓ Sí' if cls.DISCORD_TOKEN else '✗ No'}")
        print(f"  Nivel de log:            {cls.LOG_LEVEL}")
        print(f"  Archivo de log:          {cls.LOG_FILE}")
        
        print("\nMONEDAS SOPORTADAS:")
        print(f"  {', '.join(cls.MONEDAS_SOPORTADAS)}")
        
        print("="*70 + "\n")
    
    @classmethod
    def obtener_headers_linkedin(cls) -> dict:
        """Retorna headers configurados para LinkedIn"""
        headers = cls.HEADERS_BASE.copy()
        headers['User-Agent'] = cls.USER_AGENT_LINKEDIN
        return headers
    
    @classmethod
    def obtener_headers_api(cls) -> dict:
        """Retorna headers configurados para APIs"""
        headers = cls.HEADERS_BASE.copy()
        headers['User-Agent'] = cls.USER_AGENT_API
        headers['Accept'] = 'application/json'
        return headers
    
    @classmethod
    def es_api_configurada(cls, api: str) -> bool:
        """
        Verifica si una API específica está configurada.
        
        Args:
            api: Nombre de la API ('adzuna', 'indeed', etc.)
            
        Returns:
            bool: True si la API está configurada
        """
        api_lower = api.lower()
        
        if api_lower == 'adzuna':
            return bool(cls.ADZUNA_APP_ID and cls.ADZUNA_API_KEY)
        elif api_lower == 'indeed':
            return bool(cls.INDEED_PUBLISHER_ID)
        
        return False
    
    @classmethod
    def obtener_url_adzuna(cls, country: str = 'us') -> Optional[str]:
        """
        Construye la URL de la API de Adzuna para un país.
        
        Args:
            country: Código de país (us, uk, ca, etc.)
            
        Returns:
            str: URL completa de la API o None si no está configurada
        """
        if not cls.es_api_configurada('adzuna'):
            return None
        
        return cls.URL_ADZUNA_API.format(country=country)
    
    @classmethod
    def obtener_configuracion_dict(cls) -> dict:
        """
        Retorna la configuración como diccionario (sin información sensible).
        
        Returns:
            dict: Configuración del bot
        """
        return {
            'application_id': cls.APPLICATION_ID,
            'max_trabajos': cls.MAX_TRABAJOS_POR_BUSQUEDA,
            'intervalo_verificacion': cls.INTERVALO_VERIFICACION_PROGRAMACIONES,
            'base_datos': cls.NOMBRE_DB,
            'features': {
                'linkedin': cls.FEATURE_LINKEDIN_SCRAPING,
                'remoteok': cls.FEATURE_REMOTEOK_API,
                'adzuna': cls.es_api_configurada('adzuna'),
                'programaciones': cls.FEATURE_PROGRAMACIONES,
                'salarios': cls.FEATURE_EXTRACCION_SALARIOS
            },
            'monedas': cls.MONEDAS_SOPORTADAS,
            'colores': {
                'principal': hex(cls.COLOR_PRINCIPAL),
                'exito': hex(cls.COLOR_EXITO),
                'advertencia': hex(cls.COLOR_ADVERTENCIA),
                'error': hex(cls.COLOR_ERROR)
            }
        }


# Validar configuración al importar el módulo
try:
    Config.validar()
except ValueError as e:
    print(f"\n{e}")
    print("\nEl bot no puede iniciarse sin una configuración válida.")
    print("Por favor, corrige los errores y vuelve a intentar.\n")
    exit(1)