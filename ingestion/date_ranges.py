from datetime import date, timedelta
import calendar


MONTH_NAMES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


def generate_file_names(year: int, month: int) -> list[str]:
    """Generate TSE ZIP file names for a given month."""

    first_day = date(year, month, 1)

    last_day_number = calendar.monthrange(year, month)[1]
    last_day = date(year, month, last_day_number)

    month_name = MONTH_NAMES[month - 1]

    file_names = []

    current_start = first_day

    while current_start <= last_day:

        # Find the next Thursday.
        days_until_thursday = (3 - current_start.weekday()) % 7

        current_end = current_start + timedelta(
            days=days_until_thursday
        )

        # Never allow the period to cross the month.
        if current_end > last_day:
            current_end = last_day

        file_name = (
            f"nac_{month_name}{year}_"
            f"{current_start.day:02d}_{current_end.day:02d}.zip"
        )

        file_names.append(file_name)

        # Next period starts on Friday.
        current_start = current_end + timedelta(days=1)

    return file_names


if __name__ == "__main__":
    files = generate_file_names(2026, 2)

    for file_name in files:
        print(file_name)
