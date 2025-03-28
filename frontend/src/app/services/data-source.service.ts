// src/app/services/data-source.service.ts

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { delay, Observable, throwError } from 'rxjs';
import { catchError} from 'rxjs/operators';

export interface FileInfo {
  name: string;
  size: number;
}

export interface DirectoryContents {
  path: string;
  directories: string[];
  files: FileInfo[];
}

@Injectable({ providedIn: 'root' })
export class DataSourceService {
  private apiBase = environment.dataSourceApiUrl;

  constructor(private http: HttpClient) {}

  listDirectory(path: string): Observable<DirectoryContents> {
    const params = path ? new HttpParams().set('dir', path) : undefined;
    return this.http.get<DirectoryContents>(`${this.apiBase}/files`, { params });
  }

  createDirectory(dirPath: string) {
    return this.http.post(`${this.apiBase}/files/mkdir`, { path: dirPath });
  }

  uploadFile(file: File, targetDir: string): Observable<any> {
    const formData = new FormData();
    if (targetDir) {
      formData.append('dir', targetDir);
    }
    formData.append('file', file);

    return this.http.post(`${this.apiBase}/files`, formData).pipe(
      catchError(error => {
        console.error('Error uploading file:', error);
        return throwError(() => error);
      })
    );
  }

  deleteItem(path: string) {
    const params = new HttpParams().set('path', path);
    return this.http.delete(`${this.apiBase}/files`, { params }).pipe(
      // 삭제 후 잠시 대기하여 시스템이 업데이트될 시간을 줌
      delay(100),
      catchError(error => {
        console.error('Error deleting item:', error);
        return throwError(() => error);
      })
    );
  }

  downloadFile(path: string): Observable<Blob> {
    const params = new HttpParams().set('path', path);
    return this.http.get(`${this.apiBase}/files/download`, {
      params,
      responseType: 'blob'
    });
  }
}
