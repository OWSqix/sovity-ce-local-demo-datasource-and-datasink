// src/app/services/data-sink.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';
import { DirectoryContents } from './data-source.service';

@Injectable({ providedIn: 'root' })
export class DataSinkService {
  private apiBase = environment.dataSinkApiUrl;

  constructor(private http: HttpClient) {}

  listReceivedFiles(): Observable<DirectoryContents> {
    return this.http.get<DirectoryContents>(`${this.apiBase}/received`);
  }

  downloadReceivedFile(filename: string): Observable<Blob> {
    return this.http.get(`${this.apiBase}/received/download`, {
      params: { name: filename },
      responseType: 'blob'
    });
  }
}
