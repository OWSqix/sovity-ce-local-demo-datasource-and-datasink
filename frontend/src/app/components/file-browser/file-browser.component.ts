// src/app/components/file-browser/file-browser.component.ts
import { Component, OnInit, ViewChild, TemplateRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';

import { DataSourceService, DirectoryContents, FileInfo } from '../../services/data-source.service';
import { saveAs } from 'file-saver';
import {ActivatedRoute} from '@angular/router';

// Interface for items in the file table
interface FileSystemItem {
  name: string;
  size: number;
  isDirectory: boolean;
}

@Component({
  selector: 'app-file-browser',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatDialogModule,
    MatTooltipModule
  ],
  templateUrl: './file-browser.component.html',
  styleUrls: ['./file-browser.component.scss']
})
export class FileBrowserComponent implements OnInit {
  currentPath = '';
  contents: DirectoryContents | null = null;
  filteredContents: DirectoryContents | null = null;
  pathSegments: string[] = [];

  // Table data source - 이름 변경됨 (dataSource → tableDataSource)
  tableDataSource = new MatTableDataSource<FileSystemItem>([]);
  displayedColumns: string[] = ['icon', 'name', 'size', 'actions'];

  // State management
  loading = false;
  uploadInProgress = false;
  uploadFileName = '';
  searchTerm = '';

  // Selection and dialogs
  selectedItem: FileSystemItem | null = null;
  itemToDelete: FileSystemItem | null = null;
  newFolderName = '';
  private readonly restrictedPaths = ['', 'data'];
  private readonly defaultFolderName = 'uploaded';

  @ViewChild('createFolderDialog') createFolderDialog!: TemplateRef<any>;
  @ViewChild('deleteDialog') deleteDialog!: TemplateRef<any>;

constructor(
  private dataSourceService: DataSourceService,
  private dialog: MatDialog,
  private route: ActivatedRoute
) {}

  ngOnInit(): void {
    // Get the initial path from route data if available
    this.route.data.subscribe(data => {
      const initialPath = data['initialPath'];
      if (initialPath) {
        this.loadDirectory(initialPath);
      } else {
        this.loadDirectory('');
      }
    });
  }

  /**
   * Load the contents of a directory
   */
  loadDirectory(path: string): void {
    if (this.restrictedPaths.includes(path)) {
      // Redirect to default folder instead
      this.loadDirectory('uploaded');
      return;
    }

    this.loading = true;
    this.selectedItem = null;
    this.currentPath = path;
    this.pathSegments = path ? path.split('/') : [];

    this.dataSourceService.listDirectory(path).subscribe({ // dataSourceService 사용
      next: (data) => {
        this.contents = data;
        this.filterContents();
        this.updateTableData();
        this.loading = false;
      },
      error: (err: any) => { // 타입 명시
        console.error('Failed to load directory', err);
        this.loading = false;
      }
    });
  }


  /**
   * Update the MatTableDataSource with current directory contents
   */
  private updateTableData(): void {
    if (!this.filteredContents) {
      this.tableDataSource.data = []; // tableDataSource 사용
      return;
    }

    // Convert directories and files to a unified format for the table
    const directories: FileSystemItem[] = this.filteredContents.directories.map(name => ({
      name,
      size: 0,
      isDirectory: true
    }));

    const files: FileSystemItem[] = this.filteredContents.files.map(file => ({
      name: file.name,
      size: file.size,
      isDirectory: false
    }));

    // Combine and set as table data source
    this.tableDataSource.data = [...directories, ...files]; // tableDataSource 사용
  }

  /**
   * Navigate to a specific directory
   */
  openDirectory(dirname: string) {
    const newPath = this.currentPath ? `${this.currentPath}/${dirname}` : dirname;
    this.loadDirectory(newPath);
  }

  /**
   * Navigate up one level in the directory structure
   */
  goUp() {
    if (!this.currentPath) return;
    const parts = this.currentPath.split('/').filter(p => p);
    parts.pop();

    const newPath = parts.join('/');
    // Check if new path would be restricted
    if (this.restrictedPaths.includes(newPath)) {
      return; // Prevent navigation to restricted path
    }

    this.loadDirectory(newPath);
  }

  /**
   * Navigate to a specific segment in the breadcrumb path
   */
  navigateToPathSegment(index: number): void {
    if (index < 0 || index >= this.pathSegments.length) return;

    const newPath = this.pathSegments.slice(0, index + 1).join('/');
    this.loadDirectory(newPath);
  }

  /**
   * Select a file to view details
   */
  selectFile(item: FileSystemItem): void {
    this.selectedItem = item;
  }

  /**
   * Download a file
   */
  downloadFile(item: FileSystemItem | null): void {
    if (!item || item.isDirectory) return;

    const filePath = this.currentPath ? `${this.currentPath}/${item.name}` : item.name;
    this.dataSourceService.downloadFile(filePath).subscribe({
      next: (blob: Blob) => {
        saveAs(blob, item.name);
      },
      error: (err: any) => {
        console.error('Failed to download file', err);
      }
    });
  }

  /**
   * Open dialog to confirm deletion of a file or directory
   */
  confirmDelete(item: FileSystemItem | null): void {
    if (!item) return;

    this.itemToDelete = item;
    const dialogRef = this.dialog.open(this.deleteDialog);

    dialogRef.afterClosed().subscribe(result => {
      if (result === true && this.itemToDelete) {
        this.deleteItem(this.itemToDelete);
      }
      this.itemToDelete = null;
    });
  }

  /**
   * Delete a file or directory
   */
  private deleteItem(item: FileSystemItem): void {
    const itemPath = this.currentPath ? `${this.currentPath}/${item.name}` : item.name;

    this.dataSourceService.deleteItem(itemPath).subscribe({ // dataSourceService 사용
      next: () => {
        // Refresh current directory
        this.loadDirectory(this.currentPath);

        // Clear selection if the deleted item was selected
        if (this.selectedItem === item) {
          this.selectedItem = null;
        }
      },
      error: (err: any) => {
        const errorMsg = item.isDirectory
          ? 'Failed to delete directory. Make sure it is empty.'
          : 'Failed to delete file.';

        alert(`${errorMsg} ${err.error?.detail || ''}`);
      }
    });
  }

  /**
   * Open dialog to create a new folder
   */
  openCreateFolderDialog(): void {
    this.newFolderName = '';
    const dialogRef = this.dialog.open(this.createFolderDialog);

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.createFolder(result);
      }
    });
  }

  /**
   * Create a new folder
   */
  private createFolder(folderName: string): void {
    if (!folderName) return;

    const newPath = this.currentPath ? `${this.currentPath}/${folderName}` : folderName;
    this.dataSourceService.createDirectory(newPath).subscribe({ // dataSourceService 사용
      next: () => {
        this.loadDirectory(this.currentPath);
      },
      error: (err: any) => {
        alert('Failed to create directory: ' + (err.error?.detail || ''));
      }
    });
  }

  /**
   * Handle file selection for upload
   */
  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (!file) return;

    this.uploadInProgress = true;
    this.uploadFileName = file.name;

    const existingFile = this.tableDataSource.data.find(
      item => !item.isDirectory && item.name === file.name
    );

    const uploadFile = () => {
      this.dataSourceService.uploadFile(file, this.currentPath).subscribe({
        next: () => {
          this.uploadInProgress = false;
          this.uploadFileName = '';
          setTimeout(() => {
            this.loadDirectory(this.currentPath);
          }, 300);
        },
        error: (err: any) => {
          this.uploadInProgress = false;
          alert('File upload failed: ' + (err.error?.detail || err.message));
        }
      });
    };

    if (existingFile) {
      if (confirm(`File '${file.name}' already exists. Replace it?`)) {
        const itemPath = this.currentPath ? `${this.currentPath}/${file.name}` : file.name;

        this.dataSourceService.deleteItem(itemPath).subscribe({
          next: () => {
            setTimeout(uploadFile, 500);
          },
          error: (err) => {
            this.uploadInProgress = false;
            alert(`Failed to replace file: ${err.error?.detail || ''}`);
          }
        });
      } else {
        this.uploadInProgress = false;
      }
    } else {
      uploadFile();
    }

    event.target.value = '';
  }

  /**
   * Apply search filter to current contents
   */
  applySearch(): void {
    this.filterContents();
    this.updateTableData();
  }

  /**
   * Clear search term
   */
  clearSearch(): void {
    this.searchTerm = '';
    this.filterContents();
    this.updateTableData();
  }

  /**
   * Filter contents based on search term
   */
  private filterContents(): void {
    if (!this.contents) {
      this.filteredContents = {
        path: '',
        directories: [],
        files: []
      };
      return;
    }

    if (!this.searchTerm) {
      this.filteredContents = {
        path: this.contents.path,
        directories: this.contents.directories || [],
        files: this.contents.files || []
      };
      return;
    }

    const term = this.searchTerm.toLowerCase();

    this.filteredContents = {
      path: this.contents.path,
      directories: (this.contents.directories || []).filter(dir =>
        dir.toLowerCase().includes(term)
      ),
      files: (this.contents.files || []).filter(file =>
        file.name.toLowerCase().includes(term)
      )
    };
  }

  /**
   * Format file size to human-readable format
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
