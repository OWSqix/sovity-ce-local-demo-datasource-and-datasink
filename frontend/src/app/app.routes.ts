// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { FileBrowserComponent } from './components/file-browser/file-browser.component';
import { ReceivedFilesComponent } from './components/received-files/received-files.component';
import { AuthGuard } from './auth/auth.guard';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'files', component: FileBrowserComponent, canActivate: [AuthGuard] },
  { path: 'received', component: ReceivedFilesComponent, canActivate: [AuthGuard] },
  { path: '', redirectTo: 'files', pathMatch: 'full' },
  { path: '**', redirectTo: 'files' }
];
