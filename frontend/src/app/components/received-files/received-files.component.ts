// src/app/components/received-files/received-files.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataSinkService } from '../../services/data-sink.service';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-received-files',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './received-files.component.html'
})
export class ReceivedFilesComponent implements OnInit {
  receivedFiles: { name: string; size: number }[] = [];
  errorMsg = '';

  constructor(private dataSink: DataSinkService) {}

  ngOnInit(): void {
    this.loadReceivedFiles();
  }

  loadReceivedFiles(): void {
    this.dataSink.listReceivedFiles().subscribe({
      next: data => {
        this.receivedFiles = data.files;
      },
      error: err => {
        this.errorMsg = 'Could not load received files.';
        console.error(err);
      }
    });
  }

  downloadFile(fileName: string): void {
    this.dataSink.downloadReceivedFile(fileName).subscribe({
      next: blob => saveAs(blob, fileName),
      error: err => {
        alert('Failed to download file.');
        console.error(err);
      }
    });
  }
}
