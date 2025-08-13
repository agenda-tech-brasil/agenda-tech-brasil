from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import json
import os

def format_date_list(dates):
    if len(dates) > 1:
        return ', '.join(dates[:-1]) + ' e ' + dates[-1]
    return dates[0]

base_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(base_dir, 'templates')
db_path = os.path.join(base_dir, 'db', 'database.json')


with open(db_path, "r", encoding="utf-8") as f:
    json_data = json.load(f)

current_year = datetime.now().year
available_months = []
for event in json_data["eventos"]:
    if event["ano"] == current_year and not event["arquivado"]:
        available_months = [
            month["mes"]
            for month in event["meses"]
            if not month["arquivado"]
        ]
        break

env = Environment(loader=FileSystemLoader(template_path), trim_blocks=True, lstrip_blocks=True)
env.filters['format_date_list'] = format_date_list
template = env.get_template('events_improved.md.j2')

output = template.render(data=json_data, link_meses=available_months)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(output)

print("Markdown gerado com sucesso!")