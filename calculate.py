import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from urllib.parse import urljoin

import click
import pandas as pd
from dataclass_csv import DataclassReader, DataclassWriter
from structlog import get_logger

from colours import Colours
from reader import clean_up_csv

# input_csv = "2023_Season_1_Round_1_Results.csv"
logger = get_logger()
output_csv = "output.csv"
number_of_games = 3

required_fields_starts_with = ["Player", "Game"]


@dataclass
class PlayerResult:
    """Structure of the leaderboard (i.e. results for each player)"""
    name: str
    group: str = "1"
    matches_played: int = 0
    matches_won: int = 0
    matches_lost: int = 0
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0


@dataclass
class RoundResults:
    """Structure of the csv file (i.e. imported Jira tickets)"""
    # Summary: str
    # Key: int
    # IssueType: str
    # Status: str
    # Assignee: str
    Player1: str
    Player2: str
    Created: str
    # Resolved: str
    Game1ScoreP1: int
    Game2ScoreP1: int
    Game3ScoreP1: int
    Game1ScoreP2: int
    Game2ScoreP2: int
    Game3ScoreP2: int
    Sprint: str


def get_dataclass_reader(csv) -> DataclassReader:
    """get_dataclass_reader returns a configured instance of a DataclassReader

    Args:
        csv: opened csv file as TextIOWrapper
    Returns:
        DataclassReader: configured dataclass reader
    """

    csv_reader = DataclassReader(csv, RoundResults)

    # These map functions allow us to map a column name that has spaces or special characters to ones in the Dataclass definition
    csv_reader.map("Issue Type").to("IssueType")
    csv_reader.map("Player 1").to("Player1")
    csv_reader.map("Player 2").to("Player2")
    csv_reader.map("Game 1 Score (P1)").to("Game1ScoreP1")
    csv_reader.map("Game 2 Score (P1)").to("Game2ScoreP1")
    csv_reader.map("Game 3 Score (P1)").to("Game3ScoreP1")
    csv_reader.map("Game 1 Score (P2)").to("Game1ScoreP2")
    csv_reader.map("Game 2 Score (P2)").to("Game2ScoreP2")
    csv_reader.map("Game 3 Score (P2)").to("Game3ScoreP2")

    return csv_reader


@click.command(no_args_is_help=True, context_settings={"show_default": True})
@click.option("--input_csv", "-i", type=str, help="The input round results csv file to parse.", required=True)
@click.option("--previous_csv", "-p", type=str, help="The previous calculated results csv file to add to.")
@click.option("--base_folder", "-b", type=str, help="The path to the folder to read and write from. [default: folder of input_csv]")
def calculate_results(input_csv: str, previous_csv: str, base_folder: str):
    """Calculates the table tennis results given an input file (exported Jira tickets) and or previous calculated results."""
    input_file = Path(input_csv)
    parent = input_file.parent
    os.chdir(parent)
    input_file = Path(urljoin(parent.name, input_file.name))
    print(input_file)
    cleaned_input_file = Path(
        urljoin(parent.name, "cleaned_" + input_file.name))
    # input_file.with_name("cleaned_" + input_file.name))

    if not input_file.is_file():
        logger.error("File not found. Check the input_csv file name.",
                     file_name=input_file.absolute())
        exit(0)

    clean_up_csv(input_file.name, cleaned_input_file,
                 required_fields_starts_with)

    results: Dict[str, PlayerResult] = dict()

    if previous_csv:
        previous_file = Path(previous_csv)
        previous_file = Path(urljoin(parent.name, previous_file.name))
        print(previous_file)
        with open(previous_file) as previous_csv:
            previous_csv_reader = DataclassReader(previous_csv, PlayerResult)

            for previous_data in previous_csv_reader:
                previous_data: PlayerResult = previous_data
                results[previous_data.name] = previous_data

    with open(cleaned_input_file) as results_csv:
        csv_reader = get_dataclass_reader(results_csv)
        for row in csv_reader:
            result: RoundResults = row

            player1 = result.Player1.strip(" ")
            player2 = result.Player2.strip(" ")

            player1_won = 0

            if result.Game1ScoreP1 > result.Game1ScoreP2:
                player1_won += 1
            if result.Game2ScoreP1 > result.Game2ScoreP2:
                player1_won += 1
            if result.Game3ScoreP1 > result.Game3ScoreP2:
                player1_won += 1

            if player1 not in results:
                results[player1] = PlayerResult(name=player1)

            if player2 not in results:
                results[player2] = PlayerResult(name=player2)

            results[player1].games_won += player1_won
            results[player1].games_lost += number_of_games - player1_won

            results[player2].games_won += number_of_games - player1_won
            results[player2].games_lost += player1_won

            if player1_won >= 2:
                results[player1].matches_won += 1
                results[player2].matches_lost += 1
            else:
                results[player2].matches_won += 1
                results[player1].matches_lost += 1

            # Calculating total matches and games played per player
            results[player1].matches_played = results[player1].matches_won + \
                results[player1].matches_lost
            results[player1].games_played = results[player1].games_won + \
                results[player1].games_lost

            results[player2].matches_played = results[player2].matches_won + \
                results[player2].matches_lost
            results[player2].games_played = results[player2].games_won + \
                results[player2].games_lost

    logger.info("Done with cleaned file, removing",
                file=cleaned_input_file.absolute())

    os.remove(cleaned_input_file)

    # Sort by number of matches won, then by number of games won, then alphabetically by first name
    results_sorted = sorted(
        results.items(), key=lambda x: (-x[1].matches_won, -x[1].games_won, x[0]))

    df = pd.DataFrame({'Name': [result[1].name for result in results_sorted],
                       "Matches Played": [result[1].matches_played for result in results_sorted],
                       "Matches Won": [result[1].matches_won for result in results_sorted],
                       "Matches Lost": [result[1].matches_lost for result in results_sorted],
                       "Games Played": [result[1].games_played for result in results_sorted],
                       "Games Won": [result[1].games_won for result in results_sorted],
                       "Games Lost": [result[1].games_lost for result in results_sorted]})

    # Starting indexing at 1
    df.index += 1
    print(df)

    logger.info("Results calculated successfully",
                input_csv=input_file.absolute())

    with open("test.html", "w") as html_file:
        html = df.to_html()
        html = html.replace("text-align: right;",
                            "text-align: center;")
        html = html.replace("td", 'td style="text-align: center;"')
        html_file.write(html)

    # print(results_sorted)

    output_path = Path(output_csv)
    # print(urljoin(str(parent.resolve()), output_path.name))
    if output_path.is_file():
        prompt_result: str = click.prompt(
            f"File {Colours.Bold_Red(str(output_path.resolve()))} already exists. Overwrite? (y/N)", default="N")

        if prompt_result.lower() not in ["y", "yes"]:
            logger.warning(
                "Not overwriting file as specified by user. Exiting", file=output_path.absolute())
            exit(0)

    with open(output_csv, "w") as f:
        csv_writer = DataclassWriter(f, [result[1]
                                         for result in results_sorted], PlayerResult)
        csv_writer.write()
        logger.warning("File been overwritten as specified by user",
                       file=output_path.absolute())
        logger.info("Results written to file",
                    file=output_path.absolute())


if __name__ == "__main__":
    calculate_results()
