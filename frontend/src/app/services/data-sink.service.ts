// src/app/services/data-sink.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { DirectoryContents } from './data-source.service';
import { AuthService } from '../auth/auth.service';

@Injectable({ providedIn: 'root' })
export class DataSinkService {
  private apiBase = environment.dataSinkApiUrl;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  // This ensures our auth token is attached to all requests
  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  listReceivedFiles(): Observable<DirectoryContents> {
    return this.http.get<DirectoryContents>(`${this.apiBase}/received`, {
      headers: this.getHeaders()
    }).pipe(
      catchError(error => {
        console.error('Error fetching received files:', error);
        return throwError(() => error);
      })
    );
  }

  downloadReceivedFile(filename: string): Observable<Blob> {
    return this.http.get(`${this.apiBase}/received/download`, {
      params: { name: filename },
      responseType: 'blob',
      headers: this.getHeaders()
    }).pipe(
      catchError(error => {
        console.error('Error downloading file:', error);
        return throwError(() => error);
      })
    );
  }
}
