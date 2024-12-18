import sys

sys.path.insert(0, "")
from collections import Counter
from pathlib import Path

from yfpy.query import YahooFantasySportsQuery

from helpers import (
    all_seasons_rank,
    create_league_dict,
)

query = YahooFantasySportsQuery(
    league_id="",
    game_code="nfl",
    game_id=449,
    # save_token_data_to_env_file=True,
    env_file_location=Path("."),
)

league_dict = create_league_dict(query=query)

ranks = all_seasons_rank(league_dict=league_dict, nweeks=15)
ranks_pairs = [
    f"{player}-{rank}"
    for season in ranks
    for player, rank in season.items()
]

rank_counts = Counter(ranks_pairs)

rank_counts_by_player = {player: {} for player in league_dict}
for player, count in rank_counts.items():
    player, rank = player.split("-")
    rank_counts_by_player[player][rank] = count


rank_counts_by_player_sortable = [
    (int(rank), count)
    for rank, count in rank_counts_by_player["Paul"].items()
]
rank_counts_by_player_sorted = sorted(
    rank_counts_by_player_sortable,
    key=lambda x: x[0]
)
for rank, count in rank_counts_by_player_sorted:
    print(f"Rank: {rank} - n: {count:,} - {count / len(ranks) * 100:.2f}%")
