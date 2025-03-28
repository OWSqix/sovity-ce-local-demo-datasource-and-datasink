// src/app/services/folder-initializer.service.ts
import {Injectable} from '@angular/core';
import {DataSourceService} from './data-source.service';
import {catchError, forkJoin, of} from 'rxjs';
import {switchMap} from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class FolderInitializerService {
  constructor(private dataSourceService: DataSourceService) {}

  initializeDefaultFolders() {
    // First check if we can list directories
    return this.dataSourceService.listDirectory('').pipe(
      catchError(error => {
        console.error('Failed to list root directory:', error);
        return of({ directories: [], files: [], path: '' });
      }),
      switchMap(contents => {
        const existingDirs: string[] = contents.directories || [];
        const foldersToCreate = [];

        // Check if "My Files" needs to be created
        if (!existingDirs.includes("My Files")) {
          foldersToCreate.push(this.createDirectorySafe('My Files'));
        }

        // Check if "Received Files" needs to be created
        if (!existingDirs.includes('Received Files')) {
          foldersToCreate.push(this.createDirectorySafe('Received Files'));
        }

        if (foldersToCreate.length === 0) {
          return of({ message: 'All directories already exist' });
        }

        return forkJoin(foldersToCreate);
      })
    );
  }

  private createDirectorySafe(folderName: string) {
    return this.dataSourceService.createDirectory(folderName).pipe(
      catchError(error => {
        console.warn(`Failed to create directory '${folderName}':`, error);
        return of({ success: false, message: error.error?.detail || error.message });
      })
    );
  }
}
