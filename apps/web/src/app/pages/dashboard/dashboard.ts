import { Component, computed, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AssuranceService } from '../../assurance.service';

@Component({
  selector: 'app-dashboard',
  imports: [MatButtonModule, MatCardModule, MatProgressSpinnerModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  protected readonly assurance = inject(AssuranceService);

  protected readonly affectedCount = computed(() => {
    const assessment = this.assurance.assessment();
    if (!assessment) {
      return 0;
    }
    return assessment.impacts.filter((impact) => impact.action !== 'none').length;
  });
}
