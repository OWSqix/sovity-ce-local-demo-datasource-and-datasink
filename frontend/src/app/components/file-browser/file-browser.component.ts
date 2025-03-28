// src/app/components/file-browser/file-browser.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataSourceService, DirectoryContents } from '../../services/data-source.service';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-file-browser',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './file-browser.component.html'
})
export class FileBrowserComponent implements OnInit {
  currentPath = '';
  contents: DirectoryContents | null = null;
  selectedFileInfo: { name: string; size: number } | null = null;
  newFolderName = '';

  uploadInProgress = false;
  uploadFileName = '';

  constructor(private dataSource: DataSourceService) {}

  ngOnInit(): void {
    this.loadDirectory('');
  }

  loadDirectory(path: string): void {
    this.currentPath = path;
    this.dataSource.listDirectory(path).subscribe({
      next: data => {
        this.contents = data;
        this.selectedFileInfo = null;
      },
      error: err => console.error('Failed to load directory', err)
    });
  }

  openDirectory(dirname: string) {
    const newPath = this.currentPath ? `${this.currentPath}/${dirname}` : dirname;
    this.loadDirectory(newPath);
  }

  goUp() {
    if (!this.currentPath) return;
    const parts = this.currentPath.split('/').filter(p => p);
    parts.pop();
    this.loadDirectory(parts.join('/'));
  }

  selectFile(file: { name: string; size: number }) {
    this.selectedFileInfo = file;
  }

  downloadFile(file: { name: string }) {
    const filePath = this.currentPath ? `${this.currentPath}/${file.name}` : file.name;
    this.dataSource.downloadFile(filePath).subscribe(blob => {
      saveAs(blob, file.name);
    });
  }

  deleteItem(itemName: string, isDir: boolean) {
    const itemPath = this.currentPath ? `${this.currentPath}/${itemName}` : itemName;
    this.dataSource.deleteItem(itemPath).subscribe({
      next: () => this.loadDirectory(this.currentPath),
      error: err => {
        alert(`Failed to delete ${isDir ? 'directory' : 'file'}: ${err.error?.detail || ''}`);
      }
    });
  }

  createFolder() {
    if (!this.newFolderName) return;
    const newPath = this.currentPath ? `${this.currentPath}/${this.newFolderName}` : this.newFolderName;
    this.dataSource.createDirectory(newPath).subscribe({
      next: () => {
        this.newFolderName = '';
        this.loadDirectory(this.currentPath);
      },
      error: err => {
        alert('Failed to create directory: ' + (err.error?.detail || ''));
      }
    });
  }

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (!file) return;
    this.uploadInProgress = true;
    this.uploadFileName = file.name;
    this.dataSource.uploadFile(file, this.currentPath).subscribe({
      next: () => {
        this.uploadInProgress = false;
        this.uploadFileName = '';
        this.loadDirectory(this.currentPath);
      },
      error: err => {
        this.uploadInProgress = false;
        alert('File upload failed: ' + (err.error?.detail || err.message));
      }
    });
  }
}
