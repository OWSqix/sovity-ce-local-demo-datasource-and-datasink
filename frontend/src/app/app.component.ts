// src/app/app.component.ts
import { Component, OnInit } from '@angular/core';
import { AuthService } from './auth/auth.service';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { FolderInitializerService } from './services/folder-initializer.service';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterLinkActive,
    RouterOutlet,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <mat-toolbar color="primary" *ngIf="auth.isLoggedIn()">
      <span>Data Space Connector</span>
      <span class="spacer"></span>

      <nav class="nav-links">
        <a mat-button routerLink="/files" routerLinkActive="active-link">
          <mat-icon>folder</mat-icon>
          My Files
        </a>

        <a mat-button routerLink="/received" routerLinkActive="active-link">
          <mat-icon>download</mat-icon>
          Received Files
        </a>

        <button mat-button (click)="logoutUser($event)">
          <mat-icon>exit_to_app</mat-icon>
          Logout
        </button>
      </nav>
    </mat-toolbar>

    <div class="app-container">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [`
    .spacer { flex: 1 1 auto; }

    .nav-links {
      display: flex;

      a, button {
        margin-left: 8px;
      }

      .active-link {
        background-color: rgba(255, 255, 255, 0.15);
      }
    }

    .app-container {
      padding: 16px;
      max-width: 1600px;
      margin: 0 auto;
    }
  `]
})
export class AppComponent implements OnInit {
  constructor(
    public auth: AuthService,
    private router: Router,
    private folderInitializer: FolderInitializerService,
    private snackBar: MatSnackBar
  ) {}

  logoutUser(event: Event): void {
    // Prevent event bubbling that might trigger navigation
    event.preventDefault();
    event.stopPropagation();

    // Perform logout and navigate to login page
    this.auth.logout();
    void this.router.navigate(['/login']);
  }

  ngOnInit() {
    // Initialize default folders when user is logged in
    if (this.auth.isLoggedIn()) {
      this.initializeDefaultFolders();
    }

    this.auth.user$.subscribe(user => {
      if (user) {
        this.folderInitializer.initializeDefaultFolders().subscribe({
          next: results => console.log('Default folders initialized'),
          error: err => console.error('Failed to initialize folders:', err)
        });
      }
    });
  }

  private initializeDefaultFolders(): void {
    this.folderInitializer.initializeDefaultFolders().subscribe({
      next: (result) => {
        console.log('Default folders initialized');
      },
      error: (err) => {
        console.error('Error initializing folders:', err);
        this.snackBar.open('Failed to initialize folders. Some features may not work properly.', 'Close', {
          duration: 5000
        });
      }
    });
  }
}
