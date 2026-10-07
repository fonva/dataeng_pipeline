from pathlib import Path
import pandas as pd


FIELD_WIDTHS = [
    12,  # Cita de Nacimiento
     9,  # Cédula Progenitor 1
     9,  # Cédula Progenitor 2
     3,  # Código Hospital
     4,  # Hora Suceso
     8,  # Fecha Suceso
     1,  # Relleno 1
     2,  # Relleno 2
     1,  # Nacionalidad
     1,  # Marca Defunción
     3,  # País Progenitor 1
     3,  # País Progenitor 2
     1,  # Indicador Advertencia
    26,  # Primer Apellido
    26,  # Segundo Apellido
    50,  # Nombre
    29,  # Nombre Progenitor 1
    29,  # Nombre Progenitor 2
    29,  # Lugar Nacimiento
     1,  # Tipo Movimiento
     8,  # Fecha Marginal
     6,  # Hora Marginal
     8,  # Fecha Naturalización
     1,  # Indicador extensión
     3,  # Provincia/Cantón procedencia
     8,  # Fecha Aplicación
]


FIELD_NAMES = [
    "cita_nacimiento",
    "cedula_progenitor_1",
    "cedula_progenitor_2",
    "codigo_hospital",
    "hora_suceso",
    "fecha_suceso",
    "relleno_1",
    "relleno_2",
    "nacionalidad",
    "marca_defuncion",
    "pais_progenitor_1",
    "pais_progenitor_2",
    "indicador_advertencia",
    "primer_apellido",
    "segundo_apellido",
    "nombre",
    "nombre_progenitor_1",
    "nombre_progenitor_2",
    "lugar_nacimiento",
    "tipo_movimiento",
    "fecha_marginal",
    "hora_marginal",
    "fecha_naturalizacion",
    "indicador_extension",
    "provincia_canton_procedencia",
    "fecha_aplicacion",
]


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
EXPECTED_LINE_LENGTH = sum(FIELD_WIDTHS)


def find_txt_file() -> Path:
    """Find the TXT file in the raw data directory."""

    txt_files = list(RAW_DIR.glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError(
            f"No TXT files found in {RAW_DIR}"
        )

    if len(txt_files) > 1:
        raise RuntimeError(
            f"More than one TXT file found in {RAW_DIR}: {txt_files}"
        )

    return txt_files[0]


def parse_line(line: str, line_number: int) -> dict:
    """Parse one fixed-width line into a dictionary."""

    line = line.rstrip("\r\n")

    if len(line) != EXPECTED_LINE_LENGTH:
        raise ValueError(
            f"Invalid line length at line {line_number}: "
            f"expected {EXPECTED_LINE_LENGTH}, got {len(line)}"
        )

    record = {}
    position = 0

    for field_name, width in zip(FIELD_NAMES, FIELD_WIDTHS):
        record[field_name] = line[position:position + width]
        position += width

    return record


def parse_file(input_file: Path) -> pd.DataFrame:
    """Parse a fixed-width file into a pandas DataFrame."""

    records = []

    with open(input_file, "r", encoding="latin-1") as file:
        for line_number, line in enumerate(file, start=1):

            if not line.strip():
                continue

            record = parse_line(line, line_number)
            records.append(record)

    return pd.DataFrame(records)


def validate_dataframe(df: pd.DataFrame) -> None:
    """Validate the parsed DataFrame."""

    # Validate number of columns
    if len(df.columns) != len(FIELD_NAMES):
        raise ValueError(
            f"Invalid number of columns: "
            f"expected {len(FIELD_NAMES)}, got {len(df.columns)}"
        )

    # Validate column names
    if list(df.columns) != FIELD_NAMES:
        raise ValueError(
            "Column names do not match the expected schema."
        )

    # Validate nationality values
    valid_nationality = {"0", "1", "2", "3", "4", "5"}

    invalid_nationality = set(
        df["nacionalidad"].dropna().unique()
    ) - valid_nationality

    if invalid_nationality:
        raise ValueError(
            f"Invalid nationality values found: "
            f"{invalid_nationality}"
        )

    # Validate death indicator
    valid_death_indicator = {"0", "1"}

    invalid_death = set(
        df["marca_defuncion"].dropna().unique()
    ) - valid_death_indicator

    if invalid_death:
        raise ValueError(
            f"Invalid death indicator values found: "
            f"{invalid_death}"
        )

    # Validate movement type
    valid_movement_types = {"1", "2", "3"}

    invalid_movement = set(
        df["tipo_movimiento"].dropna().unique()
    ) - valid_movement_types

    if invalid_movement:
        raise ValueError(
            f"Invalid movement type values found: "
            f"{invalid_movement}"
        )

    # Validate date fields
    date_columns = [
        "fecha_suceso",
        "fecha_marginal",
        "fecha_naturalizacion",
        "fecha_aplicacion",
    ]

    for column in date_columns:
        pd.to_datetime(
            df[column],
            format="%Y%m%d",
            errors="raise"
        )

    # Validate duplicate birth appointment IDs
    duplicates = df["cita_nacimiento"].duplicated().sum()

    if duplicates > 0:
        print(
            f"Warning: {duplicates} duplicated "
            f"cita_nacimiento values found."
        )

    print("Data validation passed.")


def main() -> None:
    """Find, parse, validate, and save the TXT file."""

    input_file = find_txt_file()

    print(f"Input file: {input_file}")

    df = parse_file(input_file)

    print(f"Records parsed: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    validate_dataframe(df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / "nacimientos.parquet"

    df.to_parquet(output_file, index=False)

    print(f"Output file: {output_file}")


if __name__ == "__main__":
    main()
