import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, forkJoin } from 'rxjs';
import { catchError, map, switchMap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class SimulationService {
  private CACHE = true;

  leagueData: any = null;
  rosters: any[] = [];
  matchups: any[] = [];
  private cacheExpirationTime: number = 5 * 60 * 1000; // 5 minutes in milliseconds
  private cacheKey: string = 'fantasyLeagueCache';

  constructor(private http: HttpClient) {
    this.loadCache();
  }

  private isCacheValid(cacheTimestamp: number): boolean {
    return Date.now() - cacheTimestamp < this.cacheExpirationTime && this.CACHE;
  }

  private loadCache(): void {
    const cachedData = localStorage.getItem(this.cacheKey);
    if (cachedData) {
      const parsedData = JSON.parse(cachedData);
      if (this.isCacheValid(parsedData.timestamp)) {
        this.leagueData = parsedData.leagueData;
        this.rosters = parsedData.rosters;
        this.matchups = parsedData.matchups;
      } else {
        localStorage.removeItem(this.cacheKey);
      }
    }
  }

  private saveCache(): void {
    const cacheData = {
      leagueData: this.leagueData,
      rosters: this.rosters,
      matchups: this.matchups,
      timestamp: Date.now(),
    };
    localStorage.setItem(this.cacheKey, JSON.stringify(cacheData));
  }

  validateLeague(leagueId: string): Observable<boolean> {
    const url = `https://api.sleeper.app/v1/league/${leagueId}`;
    return this.http.get<any>(url).pipe(
      map((response) => response !== null),
      catchError(() => of(false)) // If an error occurs, return false
    );
  }

  fetchLeagueData(leagueId: string): Observable<any> {
    if (this.leagueData) {
      return of(this.leagueData);
    }

    const url = `https://api.sleeper.app/v1/league/${leagueId}`;
    return this.http.get<any>(url).pipe(
      map((data) => {
        this.leagueData = data;
        this.saveCache();
        return data;
      })
    );
  }

  fetchMatchupData(leagueId: string, totalWeeks: number): Observable<any[]> {
    if (this.matchups.length > 0) {
      return of(this.matchups);
    }

    const requests: Observable<any>[] = [];
    for (let week = 1; week <= totalWeeks; week++) {
      const url = `https://api.sleeper.app/v1/league/${leagueId}/matchups/${week}`;
      requests.push(this.http.get<any>(url));
    }
    return forkJoin(requests).pipe(
      map((data) => {
        this.matchups = data;
        this.saveCache();
        return data;
      })
    ); // Fetch all matchups concurrently and combine their responses
  }

  getRosterData(leagueId: string): Observable<any> {
    if (this.rosters.length > 0) {
      return of(this.rosters);
    }

    const url = `https://api.sleeper.app/v1/league/${leagueId}/rosters`;
    return this.http.get<any[]>(url).pipe(
      switchMap((rosters: any[]) => {
        const ownerRequests = rosters.map((roster: any) =>
          this.http
            .get<any>(`https://api.sleeper.app/v1/user/${roster.owner_id}`)
            .pipe(catchError(() => of({ display_name: 'Unknown' })))
        );

        return forkJoin(ownerRequests).pipe(
          map((owners: any[]) => {
            owners.forEach((owner: any, index: number) => {
              rosters[index].owner_name = owner?.display_name || 'Unknown';
            });

            this.rosters = rosters.map((roster: any) => {
              return {
                roster_id: roster.roster_id,
                owner_id: roster.owner_id,
                owner_name: roster.owner_name,
                settings: roster.settings,
              };
            });
            this.saveCache();
            return this.rosters;
          })
        );
      }),
      catchError(() => of([]))
    );
  }

  getOwnerName(ownerId: string): string {
    // This is a synchronous placeholder, but ideally you would fetch this info through an HTTP request and cache it.
    return `Owner-${ownerId}`;
  }

  runSimulations(
    leagueId: string,
    numSimulations: number,
    new_matchups: any[]
  ): any[] {
    // Get a map of team id to Average Points so far during the season
    const teamPointsMap: Record<string, number> = this.matchups.reduce(
      (acc: Record<string, number>, matchup: any) => {
        if (!acc[matchup.team1]) {
          acc[matchup.team1] = 0;
        }
        if (!acc[matchup.team2]) {
          acc[matchup.team2] = 0;
        }
        acc[matchup.team1] += matchup.team1_score;
        acc[matchup.team2] += matchup.team2_score;
        return acc;
      },
      {}
    );

    // Use the PF random +- 20 to simulate the score
    const simulateMatchup = (team1: number, team2: number, week: number) => {
      const team1Points = teamPointsMap[team1] / week + Math.random() * 40 - 20;
      const team2Points = teamPointsMap[team2] / week + Math.random() * 40 - 20;
      return [team1Points, team2Points];
    };

    // Simulate the matchups
    let allSimulationResults = [];
    for (let i = 0; i < numSimulations; i++) {
      const simulationResults = new_matchups.map((matchup: any) => {
        // Check if the matchup has been played already
        if (matchup.team1_score && matchup.team2_score) {
          return {
            week: matchup.week,
            team1: matchup.team1,
            team2: matchup.team2,
            team1_score: matchup.team1_score,
            team2_score: matchup.team2_score,
          };
        }

        const [team1Points, team2Points] = simulateMatchup(
          matchup.team1,
          matchup.team2,
          matchup.week
        );

        return {
          week: matchup.week,
          team1: matchup.team1,
          team2: matchup.team2,
          team1_score: Math.round(team1Points * 100) / 100,
          team2_score: Math.round(team2Points * 100) / 100,
        };
      });

      // Aggregate team wins, points for, and losses
      const teamRecords: Record<
        string,
        { wins: number; losses: number; points: number }
      > = {};
      simulationResults.forEach((matchup) => {
        const { team1, team2, team1_score, team2_score } = matchup;
        if (!teamRecords[team1])
          teamRecords[team1] = { wins: 0, losses: 0, points: 0 };
        if (!teamRecords[team2])
          teamRecords[team2] = { wins: 0, losses: 0, points: 0 };

        if (team1_score > team2_score) {
          teamRecords[team1].wins += 1;
          teamRecords[team2].losses += 1;
        } else if (team2_score > team1_score) {
          teamRecords[team2].wins += 1;
          teamRecords[team1].losses += 1;
        }

        teamRecords[team1].points += team1_score;
        teamRecords[team2].points += team2_score;
      });

      // Determine playoff teams based on wins and points as tiebreaker
      const playoffTeams = Object.keys(teamRecords)
        .map((teamId) => ({
          teamId,
          wins: teamRecords[teamId].wins,
          losses: teamRecords[teamId].losses,
          points: teamRecords[teamId].points,
        }))
        .sort((a, b) => {
          if (b.wins === a.wins) {
            return b.points - a.points; // Tie breaker based on points for
          }
          return b.wins - a.wins;
        })
        .slice(0, this.leagueData.settings.playoff_teams)
        .map((team) => team.teamId);

      allSimulationResults.push({
        simulation: i + 1,
        playoffTeams,
        teamRecords: Object.keys(teamRecords).map((teamId) => ({
          teamId,
          wins: teamRecords[teamId].wins,
          losses: teamRecords[teamId].losses,
          points: teamRecords[teamId].points,
        })),
      });
    }

    return allSimulationResults;
  }

  fetchFullLeagueData(leagueId: string): Observable<any> {
    if (
      this.leagueData &&
      this.rosters.length > 0 &&
      this.matchups.length > 0
    ) {
      return of({
        league_id: leagueId,
        league_name: this.leagueData.name,
        playoff_info: {
          num_teams: this.leagueData.settings?.num_playoff_teams || 0,
          num_playoff_weeks: this.leagueData.settings?.num_playoff_weeks || 0,
          playoff_weeks: [14, 15, 16],
        },
        teams: this.rosters,
        matchups: this.matchups,
      });
    }

    return forkJoin({
      leagueData: this.fetchLeagueData(leagueId),
      rosters: this.getRosterData(leagueId),
      matchups: this.fetchMatchupData(leagueId, 17), // Assuming 17 weeks as default
    }).pipe(
      map(({ leagueData, rosters, matchups }) => {
        const teams = rosters.map((roster: any) => {
          const avgPoints =
            roster.settings?.fpts &&
            roster.settings?.wins + roster.settings?.losses > 0
              ? (roster.settings.fpts + roster.settings.fpts_decimal / 100) /
                (roster.settings.wins + roster.settings.losses)
              : 0;
          const totalPoints = roster.settings?.fpts
            ? roster.settings.fpts + roster.settings.fpts_decimal / 100
            : 0;

          return {
            roster_id: roster.roster_id,
            owner_name: roster.owner_name,
            team_owner: roster.owner_id,
            avg_points: Math.round(avgPoints * 100) / 100,
            total_points: Math.round(totalPoints * 100) / 100,
            wins: roster.settings?.wins || 0,
            losses: roster.settings?.losses || 0,
          };
        });

        const matchupList = matchups
          .flatMap((weekMatchups: any[], week: number) =>
            weekMatchups.reduce((acc: any, matchup: any) => {
              const existingMatchup = acc.find(
                (m: any) => m.matchup_id === matchup.matchup_id
              );
              if (existingMatchup) {
                existingMatchup.team2 = matchup.roster_id;
                existingMatchup.team2_name = this.getNameFromRosterId(
                  matchup.roster_id
                );
                existingMatchup.team2_score = matchup.points;
              } else {
                acc.push({
                  week,
                  matchup_id: matchup.matchup_id,
                  team1: matchup.roster_id,
                  team1_name: this.getNameFromRosterId(matchup.roster_id),
                  team1_score: matchup.points,
                });
              }
              return acc;
            }, [])
          )
          .map((matchup: any) => {
            const winner =
              matchup.team1_score > matchup.team2_score
                ? matchup.team1
                : matchup.team2;
            return {
              ...matchup,
              winner,
            };
          });

        this.matchups = matchupList;
        this.leagueData = leagueData;
        this.rosters = teams;
        this.saveCache();

        return {
          league_id: leagueId,
          league_name: leagueData.name,
          teams,
          matchups: matchupList,
        };
      })
    );
  }
  getNameFromRosterId(roster_id: any) {
    return this.rosters.find((roster) => roster.roster_id === roster_id)
      ?.owner_name;
  }
}
