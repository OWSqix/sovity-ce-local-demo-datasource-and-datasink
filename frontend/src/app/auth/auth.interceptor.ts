
// src/app/auth/auth.interceptor.ts
import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from './auth.service';
import { Router } from '@angular/router';
import {environment} from '../../environments/environment';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private auth: AuthService, private router: Router) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.auth.getToken();
    const isDataSourceApi = req.url.startsWith(environment.dataSourceApiUrl);
    const isDataSinkApi = req.url.startsWith(environment.dataSinkApiUrl);

    if (!token) {
      return next.handle(req);
    }

    if (isDataSourceApi || isDataSinkApi) {
      const token = this.auth.getToken();
      if (token) {
        const cloned = req.clone({
          setHeaders: {
            Authorization: `Bearer ${token}`
          }
        });

        return next.handle(cloned).pipe(
          catchError((error: HttpErrorResponse) => {
            // Only redirect to login on authentication errors for non-login requests
            if (error.status === 401 && !req.url.includes('/auth/login')) {
              console.warn('Authentication error, redirecting to login');
              this.auth.logout();
              this.router.navigate(['/login']);
            }
            return throwError(() => error);
          })
        );
      }
    }

    // Add the token to the request
    const authReq = this.addTokenToRequest(req, token);

    // Handle the request and catch any authentication errors
    return next.handle(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        // Handle 401 Unauthorized errors
        if (error instanceof HttpErrorResponse && error.status === 401) {
          // Instead of immediate logout, check if token exists but might be invalid
          // In a real implementation, you would refresh the token here
          // For now, we'll use this as a safety check to prevent false logouts
          if (token && this.auth.isTokenExpired(token)) {
            this.auth.logout();
            void this.router.navigate(['/login']);
          }
        }
        return throwError(() => error);
      })
    );
  }

  private addTokenToRequest(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }
}
