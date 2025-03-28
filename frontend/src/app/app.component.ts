// src/app/app.component.ts
import { Component } from '@angular/core';
import { AuthService } from './auth/auth.service';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    NgIf,
    RouterLink,
    RouterOutlet
  ],
  template: `
    <nav *ngIf="auth.isLoggedIn()">
      <a routerLink="/files">My Files</a> |
      <a routerLink="/received">Received Files</a> |
      <a href="#" (click)="logout($event)">Logout</a>
    </nav>
    <router-outlet></router-outlet>
  `
})
export class AppComponent {
  constructor(public auth: AuthService, private router: Router) {}

  logout(event: Event) {
    event.preventDefault();
    this.auth.logout();
    void this.router.navigate(['/login']);
  }
}
