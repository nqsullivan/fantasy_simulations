import { Routes } from '@angular/router';
import { SimulationComponent } from './simulation/simulation.component';
import { HomeComponent } from './home/home.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'league/:league_id', component: SimulationComponent },
];
