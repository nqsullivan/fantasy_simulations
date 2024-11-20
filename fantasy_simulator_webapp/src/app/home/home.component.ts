import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { SimulationService } from '../services/simulation.service';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-home',
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    RouterModule,
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {

  leagueId: string = '';

  constructor( private simulationService: SimulationService, private router: Router ) {}

  validateLeagueId(): void {
    if (!this.leagueId) {
      alert('Please enter a valid League ID.');
      return;
    }

    console.log('Validating league ID:', this.leagueId);

    this.simulationService.validateLeague(this.leagueId).subscribe({
      next: (response: boolean) => {
        if (response) {
          this.router.navigate([`/league/${this.leagueId}`]);
        } else {
          alert('Invalid League ID. Please try again.');
        }
      },
      error: (error: any) => {
        console.error('Error validating league:', error);
        alert('Error validating league ID. Please try again later.');
      },
    });
  }
}
