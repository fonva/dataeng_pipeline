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


def find_txt_files() -> list[Path]:
    """Find all TXT files in the raw data directory."""

    txt_files = sorted(RAW_DIR.glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError(
            f"No TXT files found in {RAW_DIR}"
        )

    return txt_files


def parse_line(line: str, line_number: int) -> dict:
    """Parse one fixed-width line into a dictionary."""

    line = line.rstrip("\r\n")

    if len(line) != EXPECTED_LINE_LENGTH:
        raise ValueError(
            f"Invalid line length at line {line_number}: "
            f"expected {EXPECTED_LINE_LENGTH}, "
            f"got {len(line)}"
        )

    record = {}

    position = 0

    for field_name, width in zip(FIELD_NAMES, FIELD_WIDTHS):

        record[field_name] = line[
            position:position + width
        ]

        position += width

    return record


def parse_file(input_file: Path) -> pd.DataFrame:
    """Parse a fixed-width TXT file into a DataFrame."""

    records = []

    with open(
        input_file,
        "r",
        encoding="latin-1"
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1
        ):

            if not line.strip():
                continue

            record = parse_line(
                line,
                line_number
            )

            records.append(record)

    return pd.DataFrame(records)


def validate_dataframe(df: pd.DataFrame) -> None:
    """Validate the parsed DataFrame."""

    if len(df.columns) != len(FIELD_NAMES):
        raise ValueError(
            f"Invalid number of columns: "
            f"expected {len(FIELD_NAMES)}, "
            f"got {len(df.columns)}"
        )

    if list(df.columns) != FIELD_NAMES:
        raise ValueError(
            "Column names do not match "
            "the expected schema."
        )

    valid_nationality = {
        "0", "1", "2", "3", "4", "5"
    }

    invalid_nationality = (
        set(df["nacionalidad"].unique())
        - valid_nationality
    )

    if invalid_nationality:
        raise ValueError(
            f"Invalid nationality values: "
            f"{invalid_nationality}"
        )

    valid_death_indicator = {"0", "1"}

    invalid_death = (
        set(df["marca_defuncion"].unique())
        - valid_death_indicator
    )

    if invalid_death:
        raise ValueError(
            f"Invalid death indicator values: "
            f"{invalid_death}"
        )

    valid_movement_types = {"1", "2", "3"}

    invalid_movement = (
        set(df["tipo_movimiento"].unique())
        - valid_movement_types
    )

    if invalid_movement:
        raise ValueError(
            f"Invalid movement type values: "
            f"{invalid_movement}"
        )

    date_columns = [
        "fecha_suceso",
        "fecha_marginal",
        "fecha_naturalizacion",
        "fecha_aplicacion",
    ]

    for column in date_columns:

        # 00000000 represents a missing/non-applicable date.
        valid_dates = df[column].replace("00000000", pd.NA).dropna()

        pd.to_datetime(
            valid_dates,
            format="%Y%m%d",
            errors="raise"
            )

    duplicates = (
        df["cita_nacimiento"]
        .duplicated()
        .sum()
    )

    if duplicates > 0:
        print(
            f"Warning: {duplicates} duplicated "
            f"cita_nacimiento values found."
        )

    print("Data validation passed.")


def main() -> None:
    """Parse and validate all TXT files."""

    txt_files = find_txt_files()

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for input_file in txt_files:

        print()
        print(f"Processing: {input_file.name}")

        df = parse_file(input_file)

        print(f"Records parsed: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        validate_dataframe(df)

        output_file = (
            PROCESSED_DIR
            / f"{input_file.stem}.parquet"
        )

        df.to_parquet(
            output_file,
            index=False
        )

        print(
            f"Output file: {output_file.name}"
        )


if __name__ == "__main__":
    main()
