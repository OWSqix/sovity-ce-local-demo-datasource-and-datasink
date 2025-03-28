// src/app/auth/auth.guard.ts
import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): boolean {
    const token = this.auth.getToken();

    // First check if token exists
    if (!token) {
      void this.router.navigate(['/login']);
      return false;
    }

    // Then check if it's valid (not expired)
    if (this.auth.isTokenExpired(token)) {
      this.auth.logout();
      void this.router.navigate(['/login']);
      return false;
    }

    // Token exists and is valid
    return true;
  }
}
