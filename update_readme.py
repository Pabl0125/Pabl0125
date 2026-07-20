import os
import requests
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
from PIL import Image

# ==========================================
# ⚙️ CONFIGURACIÓN PERSONAL
# ==========================================
USER_NAME = os.environ.get('GITHUB_USER', 'tu_usuario')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
BIRTHDAY = datetime(1998, 5, 15) # Formato: Año, Mes, Día

# Datos estáticos de tu perfil
INFO = {
    "OS": "Windows 11, Android, Linux",
    "Host": "Tu Empresa / Freelance",
    "Role": "Desarrollador Full-Stack",
    "IDE": "VS Code, Neovim",
    "Languages.Programming": "Python, JavaScript, Java, C++",
    "Languages.Computer": "HTML, CSS, JSON, SQL",
    "Languages.Real": "Español, Inglés",
    "Hobbies.Software": "Open Source, Linux Ricing",
    "Hobbies.Hardware": "Teclados Custom, PC Build",
    "Email.Personal": "tu_correo@gmail.com",
    "Email.Work": "tu_correo@trabajo.com",
    "LinkedIn": "linkedin.com/in/tu_usuario",
    "Discord": "tu_usuario_discord"
}
# ==========================================

def get_ascii_art(username, width=35):
    """Descarga la foto de perfil y genera un ASCII art."""
    try:
        response = requests.get(f"https://github.com/{username}.png")
        img = Image.open(BytesIO(response.content)).convert('L')
        aspect_ratio = img.height / img.width
        # Las letras de consola son más altas que anchas
        new_height = int(width * aspect_ratio * 0.45)
        img = img.resize((width, new_height))
        pixels = img.getdata()
        chars = ["@", "%", "#", "*", "+", "=", "-", ":", ".", " "]
        new_pixels = [chars[min(9, pixel // 26)] for pixel in pixels]
        ascii_image = ["".join(new_pixels[index:index + width]) for index in range(0, len(new_pixels), width)]
        return ascii_image
    except Exception as e:
        print("No se pudo generar ASCII art:", e)
        return []

def get_uptime(birthday):
    """Calcula el tiempo transcurrido desde la fecha de nacimiento."""
    diff = relativedelta(datetime.today(), birthday)
    return f"{diff.years} years, {diff.months} months, {diff.days} days"

def get_github_stats():
    """Obtiene estadísticas de GitHub usando la API GraphQL."""
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
        raise Exception(f"Fallo en la API de GitHub: {response.text}")
        
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
        format_line("Hobbies.Software", INFO["Hobbies.Software"]),
        format_line("Hobbies.Hardware", INFO["Hobbies.Hardware"]),
        ".",
        "- Contact ---------------------------------------------------",
        format_line("Email.Personal", INFO["Email.Personal"]),
        format_line("Email.Work", INFO["Email.Work"]),
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
    
    ascii_lines = get_ascii_art(USER_NAME)
    
    # Asegurar altura suficiente para el texto y el ascii
    total_lines = max(len(lines), len(ascii_lines))
    height = total_lines * line_height + padding * 2 + header_offset
    width = 900
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" rx="10" ry="10" fill="#1e1e1e" />
    <circle cx="20" cy="20" r="6" fill="#ff5f56" />
    <circle cx="40" cy="20" r="6" fill="#ffbd2e" />
    <circle cx="60" cy="20" r="6" fill="#27c93f" />
    <text font-family="monospace" font-size="14" fill="#a9b1d6" xml:space="preserve">
'''
    # Dibujar la parte del texto (izquierda)
    for i, line in enumerate(lines):
        y = padding + header_offset + (i * line_height)
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        svg += f'        <tspan x="20" y="{y}">{line}</tspan>\n'
        
    # Dibujar la parte del ASCII art (derecha)
    for i, line in enumerate(ascii_lines):
        y = padding + header_offset + (i * line_height)
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        svg += f'        <tspan x="580" y="{y}" fill="#bb9af7">{line}</tspan>\n'
        
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
