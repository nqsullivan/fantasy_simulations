import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SimulationService } from '../services/simulation.service';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-simulation',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    FormsModule,
    MatTableModule,
    MatTooltipModule,
    MatIconModule,
  ],
  templateUrl: './simulation.component.html',
  styleUrls: ['./simulation.component.css'],
})
export class SimulationComponent implements OnInit {
  leagueId: string = '';
  matchups: any[] = [];
  numSimulations: number = 1000;
  simulationResults: any[] | null = null;
  displayedColumns: string[] = [
    'week',
    'team1',
    'team2',
    'team1_score',
    'team2_score',
  ];
  displayedMatchups: any[] = [];
  currentWeek: number = 1;
  aggregateResults: any[] = [];
  aggregateColumns: string[] = [
    'teamName',
    'averageWins',
    'averageLosses',
    'playoffPercentage',
    'averageSeed',
    'totalPoints',
  ];

  constructor(
    private route: ActivatedRoute,
    private simulationService: SimulationService
  ) {}

  ngOnInit(): void {
    console.log('Simulation component initialized');
    this.leagueId = this.route.snapshot.paramMap.get('league_id') || '';

    if (
      this.simulationService.leagueData &&
      this.simulationService.rosters.length &&
      this.simulationService.matchups.length
    ) {
      this.matchups = this.simulationService.matchups;
      this.currentWeek = this.simulationService.leagueData?.settings?.leg;
      this.updateDisplayedMatchups();
      console.log('Using stored league data from service.');
      console.log('Stored roster data:', this.simulationService.rosters);
      console.log('Stored matchup data:', this.simulationService.matchups);
      console.log('Stored league data:', this.simulationService.leagueData);

      this.runSimulation();
    } else {
      this.simulationService.fetchFullLeagueData(this.leagueId).subscribe({
        next: (fullLeagueData: any) => {
          console.log('League data fetched successfully:', fullLeagueData);
          this.matchups = fullLeagueData.matchups;
          this.currentWeek = this.simulationService.leagueData?.settings?.leg;
          this.updateDisplayedMatchups();

          console.log('Stored roster data:', this.simulationService.rosters);
          console.log('Stored matchup data:', this.simulationService.matchups);
          console.log('Stored league data:', this.simulationService.leagueData);

          this.runSimulation();
        },
        error: (error) => {
          console.error('Error fetching league data:', error);
        },
      });
    }
  }

  updateDisplayedMatchups(): void {
    this.displayedMatchups = this.matchups.reduce(
      (acc: any[], matchup: any) => {
        if (
          matchup.week >= this.currentWeek - 1 && // Include the current week/latest matchup
          matchup.week <
            this.simulationService.leagueData?.settings?.playoff_week_start - 1
        ) {
          acc.push(matchup);
        }
        return acc;
      },
      []
    );
  }

  runSimulation(): void {
    // Combine the previous matchups with the displayed matchups
    this.displayedMatchups = this.matchups.reduce(
      (acc: any[], matchup: any) => {
        if (matchup.week < this.currentWeek) {
          acc.push(matchup);
        }
        return acc;
      },
      this.displayedMatchups
    );

    console.log('Running simulation with matchups:', this.displayedMatchups);
    this.simulationResults = this.simulationService.runSimulations(
      this.leagueId,
      this.numSimulations,
      this.displayedMatchups
    );
    console.log('Simulation results:', this.simulationResults);
    this.calculateAggregateResults();

    this.updateDisplayedMatchups();
  }

  calculateAggregateResults(): void {
    const teamAggregate: Record<
      string,
      {
        wins: number;
        losses: number;
        points: number;
        playoffCount: number;
        averageSeed: number | null;
      }
    > = {};

    this.simulationResults?.forEach((simulation) => {
      simulation.teamRecords.forEach((teamRecord: any) => {
        if (!teamAggregate[teamRecord.teamId]) {
          teamAggregate[teamRecord.teamId] = {
            wins: 0,
            losses: 0,
            points: 0,
            playoffCount: 0,
            averageSeed: null,
          };
        }
        teamAggregate[teamRecord.teamId].wins += teamRecord.wins;
        teamAggregate[teamRecord.teamId].losses += teamRecord.losses;
        teamAggregate[teamRecord.teamId].points += teamRecord.points;
        if (simulation.playoffTeams.includes(teamRecord.teamId)) {
          teamAggregate[teamRecord.teamId].playoffCount += 1;
          const teamIndex = simulation.playoffTeams.indexOf(teamRecord.teamId);
          teamAggregate[teamRecord.teamId].averageSeed += teamIndex + 1;
        }
      });
    });

    this.aggregateResults = Object.keys(teamAggregate).map((teamId) => {
      const record = teamAggregate[teamId];
      return {
        teamId,
        teamName: this.getNameFromRosterId(teamId),
        averageWins: (record.wins / this.numSimulations).toFixed(2),
        averageLosses: (record.losses / this.numSimulations).toFixed(2),
        playoffPercentage:
          ((record.playoffCount / this.numSimulations) * 100).toFixed(2) + '%',
        totalPoints: (record.points / this.numSimulations).toFixed(2),
        averageSeed: record.averageSeed ? (record.averageSeed / record.playoffCount).toFixed(2) : null,
      };
    });

    console.log('Aggregate results:', this.aggregateResults);
  }

  getNameFromRosterId(rosterId: string): string {
    const rosterIdInt = parseInt(rosterId, 10);
    return this.simulationService.getNameFromRosterId(rosterIdInt);
  }
}
