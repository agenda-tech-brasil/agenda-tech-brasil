from datetime import datetime
import json
import os

from jinja2 import Environment, FileSystemLoader

from tools.agenda._paths import database_path, readme_path


def format_date_list(dates):
    if len(dates) > 1:
        return ", ".join(dates[:-1]) + " e " + dates[-1]
    return dates[0]


def get_available_months(json_data, current_year):
    for event in json_data.get("eventos", []):
        if event.get("ano") == current_year and not event.get("arquivado", False):
            return [
                month["mes"]
                for month in event.get("meses", [])
                if not month.get("arquivado", False)
            ]
    return []


def render_markdown(json_data, template_path, current_year):
    available_months = get_available_months(json_data, current_year)

    env = Environment(
        loader=FileSystemLoader(template_path),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["format_date_list"] = format_date_list
    template = env.get_template("events.md.j2")

    return template.render(data=json_data, link_meses=available_months)


def generate_readme(db_path, template_path, output_path, now=None):
    with open(db_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    current_year = (now or datetime.now()).year
    output = render_markdown(json_data, template_path, current_year)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates")
    db_path = str(database_path())
    output_path = str(readme_path())

    generate_readme(db_path, template_path, output_path)
    print("Markdown gerado com sucesso!")


if __name__ == "__main__":
    main()
