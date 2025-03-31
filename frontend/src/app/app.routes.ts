import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { FileBrowserComponent } from './components/file-browser/file-browser.component';
import { ReceivedFilesComponent } from './components/received-files/received-files.component';
import { AuthGuard } from './auth/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: 'files',
    component: FileBrowserComponent,
    canActivate: [AuthGuard],
    data: { initialPath: 'uploaded' }  // Pass initial directory path
  },
  {
    path: 'received',
    component: ReceivedFilesComponent,
    canActivate: [AuthGuard],
    data: { initialPath: 'received' }  // Pass initial directory path
  },
  { path: '', redirectTo: 'files', pathMatch: 'full' },
  { path: '**', redirectTo: 'files' }
];
