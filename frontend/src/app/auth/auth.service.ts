// src/app/auth/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
// import { environment } from 'src/environments/environment'; // 필요 시

@Injectable({ providedIn: 'root' })
export class AuthService {
  private tokenKey = 'authToken';
  // private authUrl = `${environment.dataSourceApiUrl}/auth`; // 필요 시
  private authUrl = 'http://localhost:8000/auth'; // 예시

  constructor(private http: HttpClient) {}

  isLoggedIn(): boolean {
    return !!this.getToken();
  }
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }
  saveToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }
  logout(): void {
    localStorage.removeItem(this.tokenKey);
  }

  // 실제 API에 맞춰 수정
  login(username: string, password: string): Observable<{ token: string }> {
    return this.http.post<{ token: string }>(`${this.authUrl}/login`, { username, password });
  }
  register(username: string, password: string): Observable<any> {
    return this.http.post(`${this.authUrl}/register`, { username, password });
  }
}
