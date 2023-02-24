# Table Tennis competiton calculator

This repo contains a central python script `calculate.py` that uses current round results exported in a specific format to calculate and generate a current leaderboard in a html file.

## Running the script

To run the script, ensure python3 is installed and run `python3 -m pip install -r requirements.txt`

### Generating round 1 results

If this is the first time running the script, only the `-i` or `--input_csv` file needs to be added passed in and it will generate a results csv file and a html leaderboard.

`python3 calculate.py -i round_1_results.csv`

### Generating running results

If the script has been run for a previous round, the running results csv file can be passed into the `-p` or `--previous_csv` flag to generate results with previous results. This will generate a resulting csv file and generate a html leaderboard for the current round.

`python3 calculate.py -i round_2_results.csv -p running_results.csv`
