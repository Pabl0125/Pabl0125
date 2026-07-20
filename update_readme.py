import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests

# ==========================================
# ⚙️ CONFIGURACIÓN PERSONAL
# ==========================================
USER_NAME = os.environ.get('GITHUB_USER', 'tu_usuario')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
BIRTHDAY = datetime(1998, 5, 15) # Formato: Año, Mes, Día

# Datos estáticos de tu perfil
INFO = {
    "OS": "Linux, Omarchy 3.8.3",
    "Host": "Student",
    "Role": "Estudiante y Desarrollador de Software",
    "IDE": "VS Code, IntelIJ, NeoVim",
    "Languages.Programming": "Java, C, TypeScript",
    "Languages.Computer": "HTML, CSS, JSON, SQL",
    "Languages.Real": "Español, Inglés (C1)",
    "Hobbies.CS": "Web Dev, Homelabing, AI Tech",
    "Hobbies.Other": "Cinema, Music, Sports",
    "Email.Personal": "pabloarro2005@gmail.com",
    "Email.University": "pablo.araujo0@rai.usc.es",
    "LinkedIn": "https://www.linkedin.com/in/pablo-araujo-252163423/",
    "Discord": "Pabl0125"
}
# ==========================================

def get_ascii_logo():
    logo = '''██████████████████████████████████████████████████████
██████████████████████████████████████████████████████
████                      ████                      ████
████                      ████                      ████
████    █████████████████████         ████████    ████
████    █████████████████████         ████████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████████████                              ████    ████
████████████                              ████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████    ████                              ████    ████
████    ██████████████████████████████████████    ████
████    ██████████████████████████████████████    ████
████                      ████                      ████
████                      ████                      ████
█████████████████████████████     ████████████████████
█████████████████████████████     ████████████████████'''
    return logo.split('\n')

def get_uptime(birthday):
    """Calcula el tiempo transcurrido desde la fecha de nacimiento."""
    diff = relativedelta(datetime.today(), birthday)
    return f"{diff.years} years, {diff.months} months, {diff.days} days"

def get_github_stats():
    """Obtiene estadísticas de GitHub usando la API GraphQL."""
    if not GITHUB_TOKEN:
        print("⚠️ Advertencia: No se encontró GITHUB_TOKEN. Se pondrán las estadísticas a 0.")
        return 0, 0, 0

    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    query = """
    query($login: String!) {
        user(login: $login) {
            followers { totalCount }
            repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
                totalCount
                nodes {
                    stargazers { totalCount }
                }
            }
        }
    }
    """
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': {'login': USER_NAME}}, headers=headers)
    
    if response.status_code != 200:
        print(f"⚠️ Fallo en la API de GitHub: {response.text}")
        return 0, 0, 0
        
    data = response.json()['data']['user']
    followers = data['followers']['totalCount']
    repos = data['repositories']['totalCount']
    stars = sum(node['stargazers']['totalCount'] for node in data['repositories']['nodes'])
    
    return repos, stars, followers

def format_line(label, value, total_width=61):
    """Alinea dinámicamente los puntos para mantener un diseño tabular perfecto."""
    left_part = f". {label}: "
    value_str = str(value)
    dots_count = total_width - len(left_part) - len(value_str) - 1
    dots = "." * max(1, dots_count)
    return f"{left_part}{dots} {value_str}"

def generate_svg():
    """Genera el contenido de una imagen SVG tipo terminal."""
    repos, stars, followers = get_github_stats()
    uptime = get_uptime(BIRTHDAY)
    
    lines = [
        f"{USER_NAME}@github -------------------------------------------",
        format_line("OS", INFO["OS"]),
        format_line("Uptime", uptime),
        format_line("Host", INFO["Host"]),
        format_line("Role", INFO["Role"]),
        format_line("IDE", INFO["IDE"]),
        ".",
        format_line("Languages.Programming", INFO["Languages.Programming"]),
        format_line("Languages.Computer", INFO["Languages.Computer"]),
        format_line("Languages.Real", INFO["Languages.Real"]),
        ".",
        format_line("Hobbies.CS", INFO["Hobbies.CS"]),
        format_line("Hobbies.Other", INFO["Hobbies.Other"]),
        ".",
        "- Contact ---------------------------------------------------",
        format_line("Email.Personal", INFO["Email.Personal"]),
        format_line("Email.University", INFO["Email.University"]),
        format_line("LinkedIn", INFO["LinkedIn"]),
        format_line("Discord", INFO["Discord"]),
        ".",
        "- GitHub Stats ----------------------------------------------",
        f". Repos: .... {repos:<2} | Stars: ............................. {stars:<4}",
        f". Followers: ........................................ {followers:<4}"
    ]
    
    line_height = 20
    padding = 20
    header_offset = 30
    ascii_lines = get_ascii_logo()
    
    # Calcular altura basada en las líneas de texto o logo
    height = max(len(lines), len(ascii_lines)) * line_height + padding * 2 + header_offset
    width = 1100
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" rx="10" ry="10" fill="#1e1e1e" />
    <circle cx="20" cy="20" r="6" fill="#ff5f56" />
    <circle cx="40" cy="20" r="6" fill="#ffbd2e" />
    <circle cx="60" cy="20" r="6" fill="#27c93f" />
    
    <text font-family="monospace" font-size="14" fill="#ffffff" xml:space="preserve">
'''
    # Dibujar la parte del texto (izquierda)
    for i, line in enumerate(lines):
        y = padding + header_offset + (i * line_height)
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        svg += f'        <tspan x="20" y="{y}">{line}</tspan>\n'

    # Dibujar logo ASCII (derecha)
    for i, line in enumerate(ascii_lines):
        y = padding + header_offset + (i * line_height)
        svg += f'        <tspan x="550" y="{y}" fill="#a3bb7e">{line}</tspan>\n'
        
    svg += '''    </text>
</svg>'''
    return svg

def update_files(svg_content):
    """Guarda el archivo SVG."""
    with open("terminal.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("¡terminal.svg generado con éxito!")

if __name__ == "__main__":
    svg_data = generate_svg()
    update_files(svg_data)
