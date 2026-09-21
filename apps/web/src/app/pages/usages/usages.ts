import { Component, inject } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { AssuranceService } from '../../assurance.service';

@Component({
  selector: 'app-usages',
  imports: [MatTableModule],
  templateUrl: './usages.html',
  styleUrl: './usages.scss',
})
export class Usages {
  protected readonly assurance = inject(AssuranceService);
  protected readonly columns = ['project', 'file', 'line', 'api', 'snippet'];
}
