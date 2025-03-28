// src/app/components/received-files/received-files.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';

import { DataSinkService } from '../../services/data-sink.service';
import { saveAs } from 'file-saver';
import { FileInfo } from '../../services/data-source.service';

export interface ReceivedFile {
  name: string;
  size: number;
  receivedDate?: Date; // Optional as it might not be available from API
}

@Component({
  selector: 'app-received-files',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    DatePipe,
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  templateUrl: './received-files.component.html',
  styleUrls: ['./received-files.component.scss']
})
export class ReceivedFilesComponent implements OnInit {
  // Table data
  dataSource = new MatTableDataSource<ReceivedFile>([]);
  displayedColumns: string[] = ['icon', 'name', 'size', 'date', 'actions'];

  // State management
  loading = false;
  errorMsg = '';
  searchTerm = '';
  downloadInProgress = false;
  downloadFileName = '';
  selectedFile: ReceivedFile | null = null;

  constructor(private dataSinkService: DataSinkService) {}

  ngOnInit(): void {
    this.loadReceivedFiles();
  }

  /**
   * Load received files from the data sink service
   */
  loadReceivedFiles(): void {
    this.loading = true;
    this.errorMsg = '';

    this.dataSinkService.listReceivedFiles().subscribe({
      next: data => {
        const files: ReceivedFile[] = data.files.map(file => ({
          name: file.name,
          size: file.size,
          // In a real implementation, this might come from the API
          receivedDate: this.extractDateFromFileName(file.name) || new Date()
        }));

        this.dataSource.data = files;
        this.loading = false;
      },
      error: (err: any) => {
        this.errorMsg = 'Could not load received files.';
        console.error(err);
        this.loading = false;
      }
    });
  }

  /**
   * Download a file from the data sink
   */
  downloadFile(fileName: string): void {
    if (!fileName) return;

    this.downloadInProgress = true;
    this.downloadFileName = fileName;

    this.dataSinkService.downloadReceivedFile(fileName).subscribe({
      next: (blob: Blob) => {
        saveAs(blob, fileName);
        this.downloadInProgress = false;
      },
      error: (err: any) => {
        alert('Failed to download file.');
        console.error(err);
        this.downloadInProgress = false;
      }
    });
  }

  /**
   * Select a file to view details
   */
  selectFile(file: ReceivedFile): void {
    this.selectedFile = file;
  }

  /**
   * Apply search filter to the data source
   */
  applyFilter(): void {
    this.dataSource.filter = this.searchTerm.trim().toLowerCase();
  }

  /**
   * Clear search term
   */
  clearSearch(): void {
    this.searchTerm = '';
    this.dataSource.filter = '';
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

  /**
   * Get appropriate icon for file type
   */
  getFileIcon(fileName: string | null): string {
    if (!fileName) return 'insert_drive_file';

    const extension = this.getFileExtension(fileName).toLowerCase();

    switch (extension) {
      case 'pdf':
        return 'picture_as_pdf';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'bmp':
      case 'svg':
        return 'image';
      case 'doc':
      case 'docx':
      case 'txt':
      case 'rtf':
        return 'description';
      case 'xls':
      case 'xlsx':
      case 'csv':
        return 'table_chart';
      case 'ppt':
      case 'pptx':
        return 'slideshow';
      case 'zip':
      case 'rar':
      case '7z':
      case 'tar':
      case 'gz':
        return 'archive';
      case 'mp3':
      case 'wav':
      case 'ogg':
        return 'audio_file';
      case 'mp4':
      case 'avi':
      case 'mov':
      case 'wmv':
        return 'movie';
      case 'js':
      case 'html':
      case 'css':
      case 'py':
      case 'java':
      case 'json':
      case 'xml':
        return 'code';
      default:
        return 'insert_drive_file';
    }
  }

  /**
   * Get CSS class for file icon based on file type
   */
  getFileIconClass(fileName: string | null): string {
    if (!fileName) return 'icon-document';

    const extension = this.getFileExtension(fileName).toLowerCase();

    if (['pdf'].includes(extension)) {
      return 'icon-pdf';
    } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(extension)) {
      return 'icon-image';
    } else if (['doc', 'docx', 'txt', 'rtf'].includes(extension)) {
      return 'icon-document';
    } else if (['xls', 'xlsx', 'csv'].includes(extension)) {
      return 'icon-spreadsheet';
    } else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) {
      return 'icon-archive';
    } else if (['mp3', 'wav', 'ogg'].includes(extension)) {
      return 'icon-audio';
    } else if (['mp4', 'avi', 'mov', 'wmv'].includes(extension)) {
      return 'icon-video';
    } else if (['js', 'html', 'css', 'py', 'java', 'json', 'xml'].includes(extension)) {
      return 'icon-code';
    } else {
      return 'icon-document';
    }
  }

  /**
   * Get file type description
   */
  getFileType(fileName: string | null): string {
    if (!fileName) return 'Unknown';

    const extension = this.getFileExtension(fileName).toLowerCase();

    switch (extension) {
      case 'pdf':
        return 'PDF Document';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'bmp':
      case 'svg':
        return 'Image';
      case 'doc':
      case 'docx':
        return 'Word Document';
      case 'txt':
        return 'Text File';
      case 'rtf':
        return 'Rich Text Format';
      case 'xls':
      case 'xlsx':
        return 'Excel Spreadsheet';
      case 'csv':
        return 'Comma Separated Values';
      case 'ppt':
      case 'pptx':
        return 'PowerPoint Presentation';
      case 'zip':
      case 'rar':
      case '7z':
      case 'tar':
      case 'gz':
        return 'Archive';
      case 'mp3':
      case 'wav':
      case 'ogg':
        return 'Audio File';
      case 'mp4':
      case 'avi':
      case 'mov':
      case 'wmv':
        return 'Video File';
      case 'js':
        return 'JavaScript File';
      case 'html':
        return 'HTML File';
      case 'css':
        return 'CSS File';
      case 'py':
        return 'Python File';
      case 'java':
        return 'Java File';
      case 'json':
        return 'JSON File';
      case 'xml':
        return 'XML File';
      default:
        return `${extension.toUpperCase()} File`;
    }
  }

  /**
   * Get file extension
   */
  private getFileExtension(fileName: string | null): string {
    if (!fileName) return '';
    return fileName.split('.').pop() || '';
  }

  /**
   * Get received date for a file (example implementation)
   * In a real app, this would likely come from metadata from the API
   */
  getReceivedDate(file: ReceivedFile): Date {
    // Use provided date if available
    if (file.receivedDate) {
      return file.receivedDate;
    }

    // Fallback to extracted date or current date
    return this.extractDateFromFileName(file.name) || new Date();
  }

  /**
   * Try to extract date from filename (example implementation)
   * This assumes filenames might contain date patterns like 'report_2023-04-15.pdf'
   */
  private extractDateFromFileName(fileName: string): Date | null {
    // Simple regex to find date patterns like YYYY-MM-DD
    const datePattern = /(\d{4}[-/]\d{2}[-/]\d{2})/;
    const match = fileName.match(datePattern);

    if (match && match[1]) {
      const dateStr = match[1];
      const date = new Date(dateStr);

      // Check if valid date
      if (!isNaN(date.getTime())) {
        return date;
      }
    }

    return null;
  }
}
