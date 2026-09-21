import { Routes } from '@angular/router';
import { Dashboard } from './pages/dashboard/dashboard';
import { Changes } from './pages/changes/changes';
import { Usages } from './pages/usages/usages';
import { Consumer } from './pages/consumer/consumer';

export const routes: Routes = [
  { path: '', component: Dashboard },
  { path: 'changes', component: Changes },
  { path: 'usages', component: Usages },
  { path: 'consumer', component: Consumer },
];
