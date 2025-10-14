"""
Bot de Búsqueda de Empleos Remotos para Discord
Versión: 2.2 (Corregida)
"""

import discord
from discord import app_commands
from discord.ext import tasks
from discord.ui import Button, View
import aiohttp
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime, timedelta
import sqlite3
from typing import List, Dict, Optional
import urllib.parse
import logging

# Importar módulos requeridos
from config import Config
from salary_utils import (
    ExtractorSalario,
    ExtractorExperiencia,
    formatear_salario,
    ordenar_por_salario
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_empleos.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Inicializar extractores
extractor_salario = ExtractorSalario()
extractor_experiencia = ExtractorExperiencia()


class DatabaseManager:
    """Gestor de base de datos para programaciones"""
    
    def __init__(self, db_name: str = None):
        self.db_name = db_name or Config.NOMBRE_DB
        self.inicializar()
    
    def inicializar(self):
        """Inicializa la base de datos"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS programaciones
                         (guild_id INTEGER,
                          channel_id INTEGER,
                          keyword TEXT,
                          country TEXT,
                          ultima_ejecucion TIMESTAMP,
                          activo INTEGER,
                          PRIMARY KEY (guild_id, channel_id, keyword, country))''')
            conn.commit()
            conn.close()
            logger.info(f"Base de datos inicializada: {self.db_name}")
        except Exception as e:
            logger.error(f"Error al inicializar base de datos: {e}")
            raise
    
    def agregar_programacion(self, guild_id: int, channel_id: int, keyword: str, country: str) -> bool:
        """Agrega una nueva programación"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            c.execute('''SELECT * FROM programaciones
                         WHERE guild_id=? AND channel_id=? AND keyword=? AND country=?''',
                      (guild_id, channel_id, keyword, country))
            
            if c.fetchone():
                conn.close()
                return False
            
            c.execute('''INSERT INTO programaciones
                         (guild_id, channel_id, keyword, country, ultima_ejecucion, activo)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (guild_id, channel_id, keyword, country, datetime.now(), 1))
            conn.commit()
            conn.close()
            logger.info(f"Programación agregada: {keyword} en {country or 'global'}")
            return True
        except Exception as e:
            logger.error(f"Error al agregar programación: {e}")
            return False
    
    def eliminar_programacion(self, guild_id: int, channel_id: int, keyword: str, country: str) -> bool:
        """Elimina una programación"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''DELETE FROM programaciones
                         WHERE guild_id=? AND channel_id=? AND keyword=? AND country=?''',
                      (guild_id, channel_id, keyword, country))
            filas_afectadas = c.rowcount
            conn.commit()
            conn.close()
            
            if filas_afectadas > 0:
                logger.info(f"Programación eliminada: {keyword}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error al eliminar programación: {e}")
            return False
    
    def obtener_programaciones(self, guild_id: int, channel_id: int) -> List:
        """Obtiene programaciones activas de un canal"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''SELECT keyword, country, ultima_ejecucion FROM programaciones
                         WHERE guild_id=? AND channel_id=? AND activo=1''',
                      (guild_id, channel_id))
            programaciones = c.fetchall()
            conn.close()
            return programaciones
        except Exception as e:
            logger.error(f"Error al obtener programaciones: {e}")
            return []
    
    def obtener_todas_programaciones_activas(self) -> List:
        """Obtiene todas las programaciones activas"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('SELECT * FROM programaciones WHERE activo=1')
            programaciones = c.fetchall()
            conn.close()
            return programaciones
        except Exception as e:
            logger.error(f"Error al obtener todas las programaciones: {e}")
            return []
    
    def actualizar_ultima_ejecucion(self, guild_id: int, channel_id: int, keyword: str, country: str):
        """Actualiza timestamp de última ejecución"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''UPDATE programaciones SET ultima_ejecucion=?
                        WHERE guild_id=? AND channel_id=? AND keyword=? AND country=?''',
                      (datetime.now(), guild_id, channel_id, keyword, country))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error al actualizar última ejecución: {e}")


class JobScraper:
    """Clase para búsqueda de trabajos"""

    @staticmethod
    async def _fetch_url(session, url, headers):
        """Función auxiliar para obtener el contenido de una URL."""
        try:
            async with session.get(url, headers=headers, timeout=20) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"URL {url} retornó status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error obteniendo {url}: {e}")
            return None

    @staticmethod
    async def buscar_linkedin(keyword: str, country: str = "", limite: int = None) -> List[Dict]:
        """Busca trabajos en LinkedIn"""
        if limite is None:
            limite = Config.MAX_TRABAJOS_POR_BUSQUEDA
        
        trabajos = []
        consulta = urllib.parse.quote(keyword)
        ubicacion = urllib.parse.quote(country) if country else ""
        
        url = f"https://www.linkedin.com/jobs/search/?keywords={consulta}&location={ubicacion}&f_WT=2"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        async with aiohttp.ClientSession() as session:
            html = await JobScraper._fetch_url(session, url, headers)
            if not html:
                return trabajos

            soup = BeautifulSoup(html, 'html.parser')
            job_cards = soup.find_all('div', class_='base-card', limit=limite * 2)
            
            tasks = []
            for card in job_cards:
                link_elem = card.find('a', class_='base-card__full-link')
                if link_elem:
                    job_url = link_elem.get('href', '').split('?')[0]
                    tasks.append(JobScraper._parsear_linkedin_card(session, card, job_url, headers))

            parsed_results = await asyncio.gather(*tasks)
            
            for trabajo in parsed_results:
                if trabajo:
                    trabajos.append(trabajo)
                    if len(trabajos) >= limite:
                        break
            
            logger.info(f"LinkedIn: {len(trabajos)} trabajos encontrados para '{keyword}'")

        return trabajos

    @staticmethod
    async def _parsear_linkedin_card(session, card, job_url, headers) -> Optional[Dict]:
        """Parsea una tarjeta de LinkedIn y obtiene la descripción completa."""
        title_elem = card.find('h3', class_='base-search-card__title')
        company_elem = card.find('h4', class_='base-search-card__subtitle')
        location_elem = card.find('span', class_='job-search-card__location')
        date_elem = card.find('time')

        if not (title_elem and company_elem and job_url):
            return None

        titulo = title_elem.text.strip()
        
        # Obtener la descripción completa de la página del trabajo
        descripcion_html = await JobScraper._fetch_url(session, job_url, headers)
        descripcion_texto = ""
        nivel_experiencia = "No especificado"
        tipo_trabajo = "No especificado"

        if descripcion_html:
            desc_soup = BeautifulSoup(descripcion_html, 'html.parser')
            
            # 1. Intenta obtener datos estructurados (más fiable)
            criteria_list = desc_soup.find('ul', class_='description__job-criteria-list')
            if criteria_list:
                criteria_items = criteria_list.find_all('li', class_='description__job-criteria-item')
                for item in criteria_items:
                    subheader = item.find('h3', class_='description__job-criteria-subheader')
                    text_value = item.find('span', class_='description__job-criteria-text')
                    if subheader and text_value:
                        header_text = subheader.text.strip().lower()
                        if 'nivel de antigüedad' in header_text:
                            nivel_experiencia = text_value.text.strip()
                        elif 'tipo de empleo' in header_text:
                            tipo_trabajo = text_value.text.strip()

            # 2. Obtiene el bloque de texto de la descripción principal
            desc_container = desc_soup.find('div', class_='show-more-less-html__markup')
            if desc_container:
                descripcion_texto = desc_container.get_text(separator='\n').strip()

        # Extraer salario de la descripción (si existe)
        salario_info = extractor_salario.extraer_salario(descripcion_texto)
        if not salario_info: # Si no se encuentra en la descripción, intentar en el título
             salario_info = extractor_salario.extraer_salario(titulo)

        # Si el nivel de experiencia no se encontró en los datos estructurados, usar el método de análisis de texto
        if nivel_experiencia == "No especificado":
            nivel_experiencia = extractor_experiencia.extraer_nivel(
                titulo=titulo,
                descripcion=descripcion_texto,
                tags=[]
            )

        return {
            'titulo': titulo,
            'empresa': company_elem.text.strip(),
            'ubicacion': location_elem.text.strip() if location_elem else 'Remoto',
            'url': job_url,
            'fecha': date_elem.get('datetime', 'Reciente') if date_elem else 'Reciente',
            'descripcion': descripcion_texto[:500] if descripcion_texto else 'No disponible.',
            'tipo_trabajo': tipo_trabajo,
            'nivel_experiencia': nivel_experiencia,
            'salario': salario_info,
            'fuente': 'LinkedIn',
            'tags': []
        }
    
    @staticmethod
    async def buscar_remoteok(keyword: str, country: str = "", limite: int = None) -> List[Dict]:
        """Busca trabajos en RemoteOK"""
        if limite is None:
            limite = Config.MAX_TRABAJOS_POR_BUSQUEDA
        
        trabajos = []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://remoteok.com/api"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; DiscordBot/2.0)',
                    'Accept': 'application/json'
                }
                
                async with session.get(url, headers=headers, timeout=20) as response:
                    if response.status == 200:
                        data = await response.json()
                        keyword_lower = keyword.lower()
                        country_lower = country.lower() if country else ""
                        
                        for job in data[1:]:
                            try:
                                if JobScraper._filtrar_remoteok_job(job, keyword_lower, country_lower):
                                    trabajo = JobScraper._parsear_remoteok_job(job)
                                    if trabajo:
                                        trabajos.append(trabajo)
                                        if len(trabajos) >= limite:
                                            break
                            except Exception as e:
                                logger.debug(f"Error al parsear trabajo: {e}")
                                continue
                        
                        logger.info(f"RemoteOK: {len(trabajos)} trabajos encontrados")
        except Exception as e:
            logger.error(f"Error al buscar en RemoteOK: {e}")
        
        return trabajos
    
    @staticmethod
    def _filtrar_remoteok_job(job: Dict, keyword: str, country: str) -> bool:
        """Filtra trabajos de RemoteOK"""
        position = job.get('position', '').lower()
        location = job.get('location', '').lower()
        description = job.get('description', '').lower()
        
        if keyword not in position and keyword not in description:
            return False
        
        if country and country not in location:
            return False
        
        return True
    
    @staticmethod
    def _parsear_remoteok_job(job: Dict) -> Optional[Dict]:
        """Parsea un trabajo de RemoteOK"""
        titulo = job.get('position', 'N/A')
        description = job.get('description', '')
        tags = job.get('tags', [])
        
        if not isinstance(tags, list):
            tags = []
        
        # Extraer salario - prioridad: campos dedicados > título > descripción > tags
        salario_info = None
        
        if job.get('salary_min') and job.get('salary_max'):
            salario_info = {
                'minimo': int(job.get('salary_min', 0)),
                'maximo': int(job.get('salary_max', 0)),
                'promedio': (int(job.get('salary_min', 0)) + int(job.get('salary_max', 0))) // 2,
                'moneda': '$',
                'texto': f"${job.get('salary_min', 0)} - ${job.get('salary_max', 0)}",
                'tipo': 'rango'
            }
        
        if not salario_info:
            salario_info = extractor_salario.extraer_salario(titulo)
        
        if not salario_info and description:
            salario_info = extractor_salario.extraer_salario(description)
        
        if not salario_info and tags:
            texto_tags = ' '.join(str(tag) for tag in tags)
            salario_info = extractor_salario.extraer_salario(texto_tags)
        
        # Determinar tipo de trabajo
        tipo_trabajo = 'Full-time'
        if tags:
            tags_lower = [str(t).lower() for t in tags]
            if 'contract' in tags_lower or 'contractor' in tags_lower:
                tipo_trabajo = 'Contrato'
            elif 'part-time' in tags_lower or 'part time' in tags_lower:
                tipo_trabajo = 'Medio tiempo'
            elif 'freelance' in tags_lower:
                tipo_trabajo = 'Freelance'
            elif 'internship' in tags_lower or 'intern' in tags_lower:
                tipo_trabajo = 'Pasantía'
        
        # Extraer nivel de experiencia
        nivel_experiencia = extractor_experiencia.extraer_nivel(
            titulo=titulo,
            descripcion=description[:1000],
            tags=tags
        )
        
        return {
            'titulo': titulo,
            'empresa': job.get('company', 'N/A'),
            'ubicacion': job.get('location', 'Remoto'),
            'url': job.get('url', 'N/A'),
            'fecha': job.get('date', 'Reciente'),
            'descripcion': description[:500] if description else 'No disponible',
            'tipo_trabajo': tipo_trabajo,
            'nivel_experiencia': nivel_experiencia,
            'salario': salario_info,
            'fuente': 'RemoteOK',
            'tags': tags[:10] if isinstance(tags, list) else []
        }
    
    @staticmethod
    async def buscar_trabajos(keyword: str, country: str = "") -> List[Dict]:
        """Busca trabajos en todas las fuentes"""
        logger.info(f"Iniciando búsqueda: '{keyword}' en '{country or 'global'}'")
        
        trabajos = await JobScraper.buscar_linkedin(keyword, country)
        
        if len(trabajos) < Config.MAX_TRABAJOS_POR_BUSQUEDA:
            trabajos_remoteok = await JobScraper.buscar_remoteok(keyword, country)
            trabajos.extend(trabajos_remoteok)
        
        if not trabajos and country:
            logger.info(f"Sin resultados con país, intentando búsqueda global")
            trabajos = await JobScraper.buscar_remoteok(keyword, "")
        
        trabajos = ordenar_por_salario(trabajos, descendente=True)
        trabajos = trabajos[:Config.MAX_TRABAJOS_POR_BUSQUEDA]
        
        logger.info(f"Búsqueda completada: {len(trabajos)} trabajos encontrados")
        return trabajos


class PaginadorTrabajos(View):
    """Vista de paginación interactiva"""
    
    def __init__(self, trabajos: List[Dict], keyword: str, country: str, timeout=300):
        super().__init__(timeout=timeout)
        self.trabajos = trabajos
        self.keyword = keyword
        self.country = country
        self.pagina_actual = 0
        self.total_paginas = len(trabajos)
        self.actualizar_botones()
    
    def actualizar_botones(self):
        """Actualiza estado de botones"""
        self.boton_anterior.disabled = self.pagina_actual == 0
        self.boton_siguiente.disabled = self.pagina_actual >= self.total_paginas - 1
        self.boton_primera.disabled = self.pagina_actual == 0
        self.boton_ultima.disabled = self.pagina_actual >= self.total_paginas - 1
    
    def crear_embed(self) -> discord.Embed:
        """Crea embed para página actual"""
        if not self.trabajos:
            embed = discord.Embed(
                title="Sin Resultados",
                description="No se encontraron trabajos que coincidan con los criterios.",
                color=Config.COLOR_ERROR
            )
            return embed
        
        trabajo = self.trabajos[self.pagina_actual]
        titulo = f"Trabajo Remoto: {trabajo['titulo']}"
        descripcion = trabajo['descripcion']
        
        if len(descripcion) > 500:
            descripcion = descripcion[:497] + "..."
        
        embed = discord.Embed(
            title=titulo,
            description=descripcion if descripcion else "Sin descripción disponible.",
            color=Config.COLOR_PRINCIPAL,
            url=trabajo['url']
        )
        
        embed.add_field(name="Empresa", value=trabajo['empresa'], inline=True)
        embed.add_field(name="Ubicación", value=trabajo['ubicacion'], inline=True)
        embed.add_field(name="Tipo de Trabajo", value=trabajo.get('tipo_trabajo', 'No especificado'), inline=True)
        
        salario_texto = formatear_salario(trabajo.get('salario'))
        embed.add_field(name="Salario Anual", value=f"**{salario_texto}**", inline=True)
        
        embed.add_field(name="Nivel de Experiencia", value=trabajo.get('nivel_experiencia', 'No especificado'), inline=True)
        embed.add_field(name="Fecha de Publicación", value=trabajo['fecha'], inline=True)
        
        if trabajo.get('tags') and len(trabajo['tags']) > 0:
            tags_texto = ", ".join(trabajo['tags'][:8])
            embed.add_field(name="Tecnologías / Habilidades", value=tags_texto, inline=False)
        
        embed.add_field(
            name="Aplicar",
            value=f"[Ver Oferta Completa en {trabajo.get('fuente', 'la plataforma')}]({trabajo['url']})",
            inline=False
        )
        
        footer_texto = f"Página {self.pagina_actual + 1} de {self.total_paginas} | Búsqueda: {self.keyword}"
        if self.country:
            footer_texto += f" en {self.country}"
        embed.set_footer(text=footer_texto)
        embed.timestamp = datetime.now()
        
        return embed
    
    @discord.ui.button(label="Primera", style=discord.ButtonStyle.secondary)
    async def boton_primera(self, interaction: discord.Interaction, button: Button):
        self.pagina_actual = 0
        self.actualizar_botones()
        await interaction.response.edit_message(embed=self.crear_embed(), view=self)
    
    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary)
    async def boton_anterior(self, interaction: discord.Interaction, button: Button):
        self.pagina_actual = max(0, self.pagina_actual - 1)
        self.actualizar_botones()
        await interaction.response.edit_message(embed=self.crear_embed(), view=self)
    
    @discord.ui.button(label="Siguiente", style=discord.ButtonStyle.primary)
    async def boton_siguiente(self, interaction: discord.Interaction, button: Button):
        self.pagina_actual = min(self.total_paginas - 1, self.pagina_actual + 1)
        self.actualizar_botones()
        await interaction.response.edit_message(embed=self.crear_embed(), view=self)
    
    @discord.ui.button(label="Última", style=discord.ButtonStyle.secondary)
    async def boton_ultima(self, interaction: discord.Interaction, button: Button):
        self.pagina_actual = self.total_paginas - 1
        self.actualizar_botones()
        await interaction.response.edit_message(embed=self.crear_embed(), view=self)
    
    @discord.ui.button(label="Cerrar", style=discord.ButtonStyle.danger)
    async def boton_cerrar(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="Búsqueda cerrada.", embed=None, view=None)
        self.stop()
    
    async def on_timeout(self):
        """Desactiva botones al expirar"""
        for item in self.children:
            item.disabled = True


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()


# Comandos del Bot

@tree.command(name="trabajo", description="Buscar trabajos remotos con información detallada")
@app_commands.describe(
    keyword="Título del trabajo o palabra clave a buscar",
    pais="País o ubicación (opcional)"
)
async def buscar_trabajos_cmd(interaction: discord.Interaction, keyword: str, pais: str = ""):
    """Comando principal para buscar trabajos"""
    await interaction.response.defer(thinking=True)
    
    try:
        logger.info(f"Comando /trabajo: usuario={interaction.user}, keyword={keyword}, pais={pais}")
        
        trabajos = await JobScraper.buscar_trabajos(keyword, pais)
        
        if not trabajos:
            embed = discord.Embed(
                title="Sin Resultados",
                description=f"No se encontraron trabajos remotos para **{keyword}**" +
                           (f" en **{pais}**" if pais else ""),
                color=Config.COLOR_ERROR
            )
            await interaction.followup.send(embed=embed)
            return
        
        vista = PaginadorTrabajos(trabajos, keyword, pais)
        await interaction.followup.send(embed=vista.crear_embed(), view=vista)
        logger.info(f"Búsqueda exitosa: {len(trabajos)} trabajos enviados")
        
    except Exception as e:
        logger.error(f"Error en comando /trabajo: {e}", exc_info=True)
        error_embed = discord.Embed(
            title="Error en la Búsqueda",
            description="Ocurrió un error inesperado al buscar trabajos.",
            color=Config.COLOR_ERROR
        )
        await interaction.followup.send(embed=error_embed)


@tree.command(name="trabajo-programar", description="Programar actualizaciones diarias")
@app_commands.describe(
    keyword="Título del trabajo o palabra clave",
    pais="País o ubicación (opcional)"
)
async def programar_trabajos_cmd(interaction: discord.Interaction, keyword: str, pais: str = ""):
    """Comando para programar búsquedas automáticas"""
    await interaction.response.defer(thinking=True)
    
    try:
        exito = db_manager.agregar_programacion(
            interaction.guild_id,
            interaction.channel_id,
            keyword,
            pais
        )
        
        if not exito:
            embed = discord.Embed(
                title="Programación Existente",
                description=f"Ya existe una programación para **'{keyword}'** en este canal.",
                color=Config.COLOR_ADVERTENCIA
            )
        else:
            embed = discord.Embed(
                title="Programación Creada",
                description=(
                    f"Se ha programado la búsqueda diaria de trabajos.\n\n"
                    f"**Palabra clave:** {keyword}\n"
                    f"**Ubicación:** {pais or 'Cualquier ubicación'}\n"
                    f"**Frecuencia:** Cada 24 horas\n"
                    f"**Canal:** {interaction.channel.mention}"
                ),
                color=Config.COLOR_EXITO
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error en /trabajo-programar: {e}", exc_info=True)
        await interaction.followup.send("Error al crear programación.")


@tree.command(name="trabajo-lista", description="Ver programaciones activas")
async def ver_programaciones_cmd(interaction: discord.Interaction):
    """Comando para ver programaciones activas"""
    try:
        programaciones = db_manager.obtener_programaciones(
            interaction.guild_id,
            interaction.channel_id
        )
        
        if not programaciones:
            embed = discord.Embed(
                title="Programaciones Activas",
                description="No hay programaciones activas en este canal.",
                color=Config.COLOR_ADVERTENCIA
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title="Programaciones Activas",
            description=f"Total de programaciones: {len(programaciones)}",
            color=Config.COLOR_PRINCIPAL
        )
        
        for keyword, country, ultima_ejecucion in programaciones:
            ubicacion = country if country else "Cualquier ubicación"
            valor = f"**Ubicación:** {ubicacion}\n**Última ejecución:** {ultima_ejecucion}"
            embed.add_field(name=f"▸ {keyword}", value=valor, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        logger.error(f"Error en /trabajo-lista: {e}", exc_info=True)


@tree.command(name="trabajo-cancelar", description="Cancelar una programación")
@app_commands.describe(
    keyword="Palabra clave de la programación",
    pais="País (opcional)"
)
async def cancelar_programacion_cmd(interaction: discord.Interaction, keyword: str, pais: str = ""):
    """Comando para cancelar programaciones"""
    try:
        exito = db_manager.eliminar_programacion(
            interaction.guild_id,
            interaction.channel_id,
            keyword,
            pais
        )
        
        if exito:
            embed = discord.Embed(
                title="Programación Cancelada",
                description=f"Se canceló la programación para **'{keyword}'**.",
                color=Config.COLOR_EXITO
            )
        else:
            embed = discord.Embed(
                title="Programación No Encontrada",
                description=f"No se encontró programación para **'{keyword}'**.",
                color=Config.COLOR_ADVERTENCIA
            )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        logger.error(f"Error en /trabajo-cancelar: {e}", exc_info=True)


@tree.command(name="ayuda", description="Información sobre comandos")
async def ayuda_cmd(interaction: discord.Interaction):
    """Comando de ayuda"""
    embed = discord.Embed(
        title="Sistema de Búsqueda de Empleos Remotos",
        description="Bot automatizado para búsqueda de trabajos con información detallada.",
        color=Config.COLOR_PRINCIPAL
    )
    
    embed.add_field(
        name="/trabajo <keyword> <pais>",
        value="Busca trabajos remotos con navegación interactiva.",
        inline=False
    )
    
    embed.add_field(
        name="/trabajo-programar <keyword> <pais>",
        value="Programa actualizaciones diarias automáticas.",
        inline=False
    )
    
    embed.add_field(
        name="/trabajo-lista",
        value="Muestra todas las programaciones activas.",
        inline=False
    )
    
    embed.add_field(
        name="/trabajo-cancelar <keyword> <pais>",
        value="Cancela una programación existente.",
        inline=False
    )
    
    embed.add_field(
        name="Características",
        value=(
            "• Información detallada de cada trabajo\n"
            "• Extracción automática de salarios\n"
            "• Detección de nivel de experiencia\n"
            "• Ordenamiento por salario\n"
            "• Navegación interactiva con botones"
        ),
        inline=False
    )
    
    embed.set_footer(text="Sistema de Búsqueda de Empleos v2.2")
    await interaction.response.send_message(embed=embed)


# Tarea en segundo plano

@tasks.loop(hours=1)
async def verificar_trabajos_programados():
    """Verificar y publicar búsquedas programadas"""
    logger.info("Verificando programaciones...")
    
    try:
        programaciones = db_manager.obtener_todas_programaciones_activas()
        
        for programacion in programaciones:
            guild_id, channel_id, keyword, country, ultima_ejecucion, activo = programacion
            
            try:
                ultima_ejecucion_dt = datetime.fromisoformat(ultima_ejecucion)
                if datetime.now() - ultima_ejecucion_dt >= timedelta(hours=24):
                    channel = client.get_channel(channel_id)
                    if channel:
                        trabajos = await JobScraper.buscar_trabajos(keyword, country)
                        
                        if trabajos:
                            vista = PaginadorTrabajos(trabajos, keyword, country)
                            embed = vista.crear_embed()
                            embed.title = f"Actualización Diaria | {embed.title}"
                            await channel.send(embed=embed, view=vista)
                        
                        db_manager.actualizar_ultima_ejecucion(
                            guild_id, channel_id, keyword, country
                        )
            except Exception as e:
                logger.error(f"Error al procesar programación: {e}")
                continue
        
    except Exception as e:
        logger.error(f"Error en verificación: {e}")


# Eventos

@client.event
async def on_ready():
    """Evento cuando el bot está listo"""
    try:
        await tree.sync()
        verificar_trabajos_programados.start()
        
        Config.mostrar_configuracion()
        logger.info("="*60)
        logger.info(f"Bot iniciado: {client.user}")
        logger.info(f"ID: {client.user.id}")
        logger.info(f"Servidores: {len(client.guilds)}")
        logger.info("Sistema activo")
        logger.info("="*60)
    except Exception as e:
        logger.error(f"Error en on_ready: {e}", exc_info=True)


# Ejecutar bot

def main():
    """Función principal"""
    try:
        Config.validar()
        logger.info("Iniciando bot...")
        client.run(Config.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()