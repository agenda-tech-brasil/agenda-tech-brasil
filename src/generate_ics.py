import json
import os
from datetime import datetime
from icalendar import Calendar, Event


def generate_ics():
    db_path = os.path.join("src", "db", "database.json")
    output_path = "agenda.ics"

    if not os.path.exists(db_path):
        return None

    with open(db_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    if isinstance(content, dict):
        eventos = content.get("events") or content.get("eventos") or []
    else:
        eventos = content

    cal = Calendar()
    cal.add("prodid", "-//Agenda Tech Brasil//")
    cal.add("version", "2.0")

    for item in eventos:
        if not isinstance(item, dict):
            continue

        event = Event()

        nome = item.get("name") or item.get("titulo") or "Evento Tech"
        event.add("summary", nome)

        try:
            date_str = item.get("date") or item.get("data")
            if date_str:
                event_date = datetime.strptime(date_str, "%Y-%m-%d")
                event.add("dtstart", event_date)
                event.add("dtend", event_date)
        except Exception:
            continue

        event.add("description", f"Link: {item.get('link', '')}")
        event.add("location", item.get("location", "Online"))

        cal.add_component(event)

    with open(output_path, "wb") as f:
        f.write(cal.to_ical())

    return True


if __name__ == "__main__":
    generate_ics()