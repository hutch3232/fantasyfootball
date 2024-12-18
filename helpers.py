from collections import Counter
from itertools import cycle, permutations


def create_league_dict(query, nweeks=None):
    teams = query.get_league_teams()
    if nweeks is None:
        nweeks = query.get_league_metadata().current_week - 1
    league_dict = {
        team.managers[0].nickname: {
            "team_id": team.team_id,
            "team_key": team.team_key
        }
        for team in teams
    }
    for team in league_dict:
        league_dict[team]["points_by_week"] = get_points_by_week(
            nickname=team,
            nweeks=nweeks,
            league_dict=league_dict,
            query=query
        )
        league_dict[team]["total_points"] = sum(
            league_dict[team]["points_by_week"].values()
        )
    return league_dict


def get_points_by_week(nickname, nweeks, query, league_dict):
    return {
        w: query.get_team_stats_by_week(
            team_id=league_dict[nickname]["team_id"],
            chosen_week=w
        )["team_points"].total
        for w in range(1, nweeks + 1)
    }


def find_winner(player1, player2, week, league_dict):
    player1_score = league_dict[player1]["points_by_week"][week]
    player2_score = league_dict[player2]["points_by_week"][week]
    if player1_score > player2_score:
        return player1
    else:
        return player2


def generate_base_schedule(players):
    num_players = len(players)

    # Generate unique matchups for the first y-1 weeks using round-robin
    matchups = []
    for _ in range(num_players - 1):  # y - 1 weeks
        week = []
        for j in range(num_players // 2):  # Pair players
            p1 = players[j]
            p2 = players[-(j + 1)]
            week.append((min(p1, p2), max(p1, p2)))
        matchups.append(week)

        # Rotate players (except the first player) for next week
        players = [players[0]] + players[-1:] + players[1:-1]

    return matchups


def generate_all_season_permutations(players, nweeks):
    base_schedule = generate_base_schedule(players)

    # If weeks exceed base schedule, repeat using cycle
    if nweeks > len(base_schedule):
        all_seasons = []
        base_permutations = list(permutations(base_schedule))

        for base_perm in base_permutations:
            # Extend the permutation to full season length using cycle
            season = list(base_perm)
            remaining_weeks = nweeks - len(base_perm)

            # Add remaining weeks by cycling through the permutation
            season_cycle = cycle(base_perm)
            for _ in range(remaining_weeks):
                season.append(next(season_cycle))

            all_seasons.append(season)

    else:
        # If weeks are less than or equal to base schedule, generate permutations
        base_permutations = list(permutations(base_schedule[:nweeks]))
        all_seasons = [list(perm) for perm in base_permutations]

    return all_seasons


def season_record(season, league_dict):
    winners = [
        find_winner(
            player1=player1,
            player2=player2,
            week=week,
            league_dict=league_dict
        )
        for week, matchup in enumerate(season, start=1)
        for player1, player2 in matchup
    ]

    return Counter(winners)


def season_rank(season, league_dict):
    record = season_record(season, league_dict)
    result = [
        (player, record[player], league_dict[player]["total_points"])
        for player in record
    ]
    result = sorted(result, key=lambda x: (-x[1], -x[2]))
    return {player[0]: rank for rank, player in enumerate(result, start=1)}


def all_seasons_rank(league_dict, nweeks):
    seasons = generate_all_season_permutations(
        players=list(league_dict.keys()),
        nweeks=nweeks,
    )
    rank = [season_rank(season, league_dict) for season in seasons]
    return rank
