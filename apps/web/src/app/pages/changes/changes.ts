import { Component, inject } from '@angular/core';
import { MatChipsModule } from '@angular/material/chips';
import { MatTableModule } from '@angular/material/table';
import { AssuranceService } from '../../assurance.service';

@Component({
  selector: 'app-changes',
  imports: [MatChipsModule, MatTableModule],
  templateUrl: './changes.html',
  styleUrl: './changes.scss',
})
export class Changes {
  protected readonly assurance = inject(AssuranceService);
  protected readonly columns = ['component', 'api', 'type', 'severity', 'toVersion'];
}
