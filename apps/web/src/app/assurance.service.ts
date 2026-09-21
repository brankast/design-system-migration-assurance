import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { Assessment, ChangeEvent, ComponentUsage } from './models/assurance';

@Injectable({ providedIn: 'root' })
export class AssuranceService {
  private readonly http = inject(HttpClient);

  readonly assessment = signal<Assessment | null>(null);
  readonly loading = signal(false);
  readonly scanning = signal(false);
  readonly error = signal<string | null>(null);

  loadLatest(): void {
    this.loading.set(true);
    this.error.set(null);
    this.http.get<Assessment>('/api/assessments/latest').subscribe({
      next: (assessment) => {
        this.assessment.set(assessment);
        this.loading.set(false);
      },
      error: () => {
        this.error.set(
          'Could not load the latest assessment. Start the API on port 8000.',
        );
        this.loading.set(false);
      },
    });
  }

  runScan(): void {
    this.scanning.set(true);
    this.error.set(null);
    this.http.post<Assessment>('/api/scan', { fetchChangelog: true }).subscribe({
      next: (assessment) => {
        this.assessment.set(assessment);
        this.scanning.set(false);
      },
      error: () => {
        this.error.set('Scan failed. Check that the API can reach GitHub or the local changelog sample.');
        this.scanning.set(false);
      },
    });
  }

  changes(): ChangeEvent[] {
    return this.assessment()?.changeEvents ?? [];
  }

  usages(): ComponentUsage[] {
    return this.assessment()?.usages ?? [];
  }
}
