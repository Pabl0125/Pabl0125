import os
import requests
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

def generate_layout():
    """Genera el bloque de texto completo."""
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
    return "\n".join(lines)

def update_readme(new_content):
    """Inyecta el nuevo contenido en el README.md entre las etiquetas HTML."""
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
        
    # Busca las anclas y reemplaza lo que hay en medio
    pattern = r"(<!-- START_STATS -->\n).*?(\n<!-- END_STATS -->)"
    updated_readme = re.sub(pattern, rf"\1```text\n{new_content}\n```\2", readme, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)
    print("¡README.md actualizado con éxito!")

if __name__ == "__main__":
    layout_text = generate_layout()
    update_readme(layout_text)
