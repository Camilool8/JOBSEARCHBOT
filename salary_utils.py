"""
Utilidades para extracción de salarios y nivel de experiencia
Versión: 2.1
"""

import re
from typing import Optional, Dict, List


class ExtractorSalario:
    """Extrae información de salario desde texto usando regex"""
    
    PATRONES_SALARIO = {
        'rango_simbolo_completo': [
            r'\$\s*(\d{1,3}(?:[,\.]\d{3})+)\s*(?:-|to|a)\s*\$?\s*(\d{1,3}(?:[,\.]\d{3})+)',
            r'€\s*(\d{1,3}(?:[,\.]\d{3})+)\s*(?:-|to|a)\s*€?\s*(\d{1,3}(?:[,\.]\d{3})+)',
            r'£\s*(\d{1,3}(?:[,\.]\d{3})+)\s*(?:-|to|a)\s*£?\s*(\d{1,3}(?:[,\.]\d{3})+)',
        ],
        'rango_k': [
            r'\$\s*(\d{1,3})k\s*(?:-|to|a)\s*\$?\s*(\d{1,3})k',
            r'(\d{2,3})k\s*(?:-|to|a)\s*(\d{2,3})k',
            r'€\s*(\d{1,3})k\s*(?:-|to|a)\s*€?\s*(\d{1,3})k',
            r'£\s*(\d{1,3})k\s*(?:-|to|a)\s*£?\s*(\d{1,3})k',
        ],
        'salario_unico': [
            r'\$\s*(\d{1,3}(?:[,\.]\d{3})+|\d+k?)\s*(?:/|per|por)?\s*(?:year|yr|annum|annually|annual|año)',
            r'€\s*(\d{1,3}(?:[,\.]\d{3})+|\d+k?)\s*(?:/|per|por)?\s*(?:año|year|yr)',
            r'£\s*(\d{1,3}(?:[,\.]\d{3})+|\d+k?)\s*(?:/|per)?\s*(?:annum|year|annually)',
        ],
        'rango_contexto': [
            r'(?:salary|sueldo|compensation|compensación|salario|pay|wage)[\s:]+\$?\s*(\d{1,3})[,\.]?(\d{3})\s*(?:-|to|a)\s*\$?\s*(\d{1,3})[,\.]?(\d{3})',
            r'(?:salary|sueldo|pay)\s*(?:range|rango)?[\s:]+\$?\s*(\d{1,3})k?\s*(?:-|to|a)\s*\$?\s*(\d{1,3})k?',
            r'(?:up\s*to|upto|hasta)\s*\$?\s*(\d{1,3})k?',
        ],
        'por_hora': [
            r'\$\s*(\d{1,3})\s*(?:-|to|a)\s*\$?\s*(\d{1,3})\s*(?:/|per)?\s*(?:hr|hour|hora)',
            r'€\s*(\d{1,3})\s*(?:-|to|a)\s*€?\s*(\d{1,3})\s*/?\s*h',
            r'\$\s*(\d{1,3})\s*(?:/|per)\s*(?:hr|hour)',
        ]
    }
    
    @staticmethod
    def limpiar_numero(texto: str) -> int:
        """Limpia y convierte texto numérico a entero"""
        texto_limpio = texto.replace(',', '').replace('.', '')
        if texto.lower().endswith('k'):
            return int(texto_limpio[:-1]) * 1000
        try:
            return int(texto_limpio)
        except ValueError:
            return 0
    
    @staticmethod
    def detectar_moneda(texto: str) -> str:
        """Detecta símbolo de moneda"""
        if '€' in texto:
            return '€'
        elif '£' in texto:
            return '£'
        elif '$' in texto or 'USD' in texto.upper():
            return '$'
        return '$'
    
    @classmethod
    def extraer_salario(cls, texto: str) -> Optional[Dict]:
        """Extrae información de salario del texto"""
        if not texto:
            return None
        
        for tipo, patrones in cls.PATRONES_SALARIO.items():
            for patron in patrones:
                matches = list(re.finditer(patron, texto, re.IGNORECASE))
                if matches:
                    for match in matches:
                        try:
                            resultado = cls._procesar_match(match, tipo, texto)
                            if resultado:
                                return resultado
                        except (ValueError, IndexError):
                            continue
        return None
    
    @classmethod
    def _procesar_match(cls, match, tipo: str, texto_original: str) -> Optional[Dict]:
        """Procesa un match de regex y retorna información estructurada"""
        grupos = match.groups()
        moneda = cls.detectar_moneda(match.group(0))
        
        if tipo == 'por_hora':
            if len(grupos) >= 2:
                min_hora = int(grupos[0])
                max_hora = int(grupos[1])
            else:
                min_hora = max_hora = int(grupos[0])
            
            min_anual = min_hora * 40 * 52
            max_anual = max_hora * 40 * 52
            
            return {
                'minimo': min_anual,
                'maximo': max_anual,
                'promedio': (min_anual + max_anual) // 2,
                'moneda': moneda,
                'texto': match.group(0),
                'tipo': 'por_hora',
                'tarifa_hora_min': min_hora,
                'tarifa_hora_max': max_hora
            }
        
        elif tipo in ['rango_simbolo_completo', 'rango_k']:
            min_sal = cls.limpiar_numero(grupos[0])
            max_sal = cls.limpiar_numero(grupos[1]) if len(grupos) > 1 else min_sal
            
            if 'k' in match.group(0).lower() and min_sal < 1000:
                min_sal *= 1000
                max_sal *= 1000
            
            return {
                'minimo': min_sal,
                'maximo': max_sal,
                'promedio': (min_sal + max_sal) // 2,
                'moneda': moneda,
                'texto': match.group(0),
                'tipo': 'rango'
            }
        
        elif tipo == 'salario_unico':
            salario = cls.limpiar_numero(grupos[0])
            if 'k' in grupos[0].lower() and salario < 1000:
                salario *= 1000
            
            return {
                'minimo': salario,
                'maximo': salario,
                'promedio': salario,
                'moneda': moneda,
                'texto': match.group(0),
                'tipo': 'unico'
            }
        
        elif tipo == 'rango_contexto':
            if len(grupos) == 4:
                min_sal = int(grupos[0] + grupos[1])
                max_sal = int(grupos[2] + grupos[3])
            elif len(grupos) == 2:
                min_sal = cls.limpiar_numero(grupos[0])
                max_sal = cls.limpiar_numero(grupos[1])
            else:
                salario = cls.limpiar_numero(grupos[0])
                if 'k' in match.group(0).lower() and salario < 1000:
                    salario *= 1000
                return {
                    'minimo': 0,
                    'maximo': salario,
                    'promedio': salario // 2,
                    'moneda': moneda,
                    'texto': match.group(0),
                    'tipo': 'maximo'
                }
            
            if 'k' in match.group(0).lower() and min_sal < 1000:
                min_sal *= 1000
                max_sal *= 1000
            
            return {
                'minimo': min_sal,
                'maximo': max_sal,
                'promedio': (min_sal + max_sal) // 2,
                'moneda': moneda,
                'texto': match.group(0),
                'tipo': 'rango'
            }
        
        return None


class ExtractorExperiencia:
    """Extrae nivel de experiencia desde texto"""
    
    NIVELES = {
        'Junior': [
            r'junior', r'entry[\s-]?level', r'associate', r'trainee',
            r'graduate', r'jr\.?', r'0[\s-]?2\s*(?:years|yrs)',
            r'less than 2', r'menos de 2'
        ],
        'Mid-level': [
            r'mid[\s-]?level', r'intermediate', r'experienced',
            r'2[\s-]?5\s*(?:years|yrs)', r'3[\s+]?years',
            r'several years', r'algunos años'
        ],
        'Senior': [
            r'senior', r'sr\.?', r'lead', r'principal',
            r'5\+?\s*(?:years|yrs)', r'6\+?\s*(?:years|yrs)',
            r'7\+?\s*(?:years|yrs)', r'8\+?\s*(?:years|yrs)',
            r'expert', r'advanced', r'staff'
        ],
        'Expert': [
            r'architect', r'distinguished', r'fellow',
            r'10\+?\s*(?:years|yrs)', r'15\+?\s*(?:years|yrs)',
            r'expert', r'guru', r'veteran'
        ],
        'Manager': [
            r'manager', r'head\s+of', r'director',
            r'vp\s+of', r'chief', r'team\s+lead',
            r'engineering\s+manager', r'tech\s+lead'
        ]
    }
    
    @classmethod
    def extraer_nivel(cls, titulo: str = "", descripcion: str = "", tags: List[str] = None) -> str:
        """Extrae nivel de experiencia del título, descripción y tags"""
        if tags is None:
            tags = []
        
        texto_completo = f"{titulo} {descripcion} {' '.join(str(t) for t in tags)}".lower()
        
        for nivel, patrones in cls.NIVELES.items():
            for patron in patrones:
                if re.search(patron, texto_completo, re.IGNORECASE):
                    return nivel
        
        titulo_lower = titulo.lower()
        if any(word in titulo_lower for word in ['junior', 'jr', 'entry']):
            return 'Junior'
        elif any(word in titulo_lower for word in ['senior', 'sr', 'lead']):
            return 'Senior'
        elif any(word in titulo_lower for word in ['manager', 'director', 'head']):
            return 'Manager'
        
        return 'No especificado'


def formatear_salario(info_salario: Optional[Dict]) -> str:
    """Formatea información de salario para mostrar"""
    if not info_salario:
        return "No disponible"
    
    moneda = info_salario['moneda']
    minimo = f"{info_salario['minimo']:,}".replace(',', '.')
    maximo = f"{info_salario['maximo']:,}".replace(',', '.')
    
    if info_salario.get('tipo') == 'por_hora':
        hora_min = info_salario.get('tarifa_hora_min', 0)
        hora_max = info_salario.get('tarifa_hora_max', 0)
        return f"{moneda}{hora_min}-{hora_max}/hora ({moneda}{minimo}-{moneda}{maximo}/año)"
    
    if info_salario.get('tipo') == 'maximo':
        return f"Hasta {moneda}{maximo}/año"
    
    if info_salario['minimo'] == info_salario['maximo']:
        return f"{moneda}{minimo}/año"
    
    if info_salario['minimo'] == 0:
        return f"Hasta {moneda}{maximo}/año"
    
    return f"{moneda}{minimo} - {moneda}{maximo}/año"


def formatear_salario_corto(info_salario: Optional[Dict]) -> str:
    """Formatea salario de forma abreviada"""
    if not info_salario:
        return "N/A"
    
    moneda = info_salario['moneda']
    promedio = info_salario['promedio']
    
    if promedio >= 1000:
        return f"{moneda}{promedio / 1000:.0f}K"
    
    return f"{moneda}{promedio:,}".replace(',', '.')


def ordenar_por_salario(trabajos: List[Dict], descendente: bool = True) -> List[Dict]:
    """Ordena trabajos por salario promedio"""
    def obtener_salario(trabajo):
        if trabajo.get('salario') and trabajo['salario'].get('promedio'):
            return trabajo['salario']['promedio']
        return -1 if descendente else float('inf')
    
    return sorted(trabajos, key=obtener_salario, reverse=descendente)