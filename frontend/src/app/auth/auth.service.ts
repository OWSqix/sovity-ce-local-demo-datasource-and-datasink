// src/app/auth/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

// Define interfaces for type safety
export interface AuthResponseData {
  token: string;
  token_type: string;
  expires_in?: number;
}

export interface User {
  username: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private tokenKey = 'authToken';
  private authUrl = `${environment.dataSourceApiUrl}/auth`;

  // Flag to determine if auto-login should occur after registration
  public shouldAutoLoginAfterRegister = true;

  // Observable for checking auth state in components
  private userSubject = new BehaviorSubject<User | null>(null);
  user$ = this.userSubject.asObservable();

  constructor(private http: HttpClient) {
    // Check for existing token on service initialization
    this.checkStoredToken();
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  saveToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
    // When saving token, update user state
    this.updateUserState(token);
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    this.userSubject.next(null);
  }

  login(username: string, password: string): Observable<AuthResponseData> {
    return this.http.post<AuthResponseData>(`${this.authUrl}/login`, {
      username,
      password
    }).pipe(
      catchError(this.handleError),
      tap(resData => {
        if (resData.token) {
          this.saveToken(resData.token);
        }
      })
    );
  }

  register(username: string, password: string): Observable<any> {
    return this.http.post(`${this.authUrl}/register`, {
      username,
      password
    }).pipe(
      catchError(this.handleError)
    );
  }

  isTokenExpired(token: string): boolean {
    // A simple implementation to check token expiration
    try {
      // This is a simplified version - in a real app, use a library like jwt-decode
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));

      const payload = JSON.parse(jsonPayload);
      const expiry = payload.exp;

      return expiry ? (Date.now() >= expiry * 1000) : false;
    } catch (e) {
      // If we can't decode the token, assume it's expired
      console.error('Error checking token expiration:', e);
      return true;
    }
  }

  private updateUserState(token: string | null): void {
    if (!token) {
      this.userSubject.next(null);
      return;
    }

    // In a real app, you might decode the JWT to get user info
    // For simplicity, we'll just set a username object
    // In production, use a library like jwt-decode to properly decode token
    try {
      // This is a simplistic approach - in a real app, decode the JWT
      this.userSubject.next({ username: 'user' });
    } catch (error) {
      console.error('Invalid token format', error);
      this.logout();
    }
  }

  private checkStoredToken(): void {
    const token = this.getToken();
    if (token) {
      // In a real app, check token expiration here
      this.updateUserState(token);
    }
  }

  private handleError(errorRes: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An unknown error occurred';

    if (!errorRes.error || !errorRes.error.detail) {
      return throwError(() => new Error(errorMessage));
    }

    // Use the error detail from the API response
    errorMessage = errorRes.error.detail;
    return throwError(() => new Error(errorMessage));
  }
}
