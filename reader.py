import csv
from typing import List

from structlog import get_logger


logger = get_logger()


def clean_up_csv(input_file: str, output_file: str, required_columns_starts_with: List[str]):
    """clean_up_csv removes all rows in the csv that don't have all required fields populated.

    required_column_starts_with contains a list of strings that are the required columns. This 
    code will check if any columns that start with (i.e. prefix matching) any of the strings in
    required_columns_starts_with and discard any rows that have empty values in any of the 
    required columns.

    Args:
        input_file: the name of the input csv file to clean up
        output_file: the name of the output csv file to write the cleaned up csv to
        required_columns_starts_with: the list of names of required columns to prefix match
    """
    with open(input_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        with open(output_file, 'w') as csv_output:
            csv_writer = csv.writer(csv_output, delimiter=',')

            required_fields_columns = []
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    # Gets indexes of all columns that start with the required fields
                    required_fields_columns = [
                        idx for idx, header in enumerate(row) if header.startswith(
                            tuple(required_columns_starts_with))]

                    csv_writer.writerow(row)
                    line_count += 1
                else:
                    filtered_row = list(row[i]
                                        for i in required_fields_columns)
                    if any(value != "" for value in filtered_row):
                        csv_writer.writerow(row)

            logger.info(
                "Input results csv cleaned up and written to a file", input_file=input_file, output_file=output_file)
