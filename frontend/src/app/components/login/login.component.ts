// src/app/components/login/login.component.ts
import { Component, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../auth/auth.service';
import { FormsModule, NgForm } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatCard, MatCardContent, MatCardHeader, MatCardTitle } from '@angular/material/card';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatButton } from '@angular/material/button';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCard,
    MatCardContent,
    MatCardHeader,
    MatCardTitle,
    MatFormField,
    MatLabel,
    MatError,
    MatInput,
    MatButton
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  @ViewChild('authForm') authForm!: NgForm;

  isLoginMode = true;
  username = '';
  password = '';
  confirmPassword = '';
  errorMsg = '';

  constructor(private auth: AuthService, private router: Router) {}

  toggleMode(): void {
    this.isLoginMode = !this.isLoginMode;
    this.errorMsg = '';
    this.authForm?.resetForm({
      username: this.username,
      password: '',
      confirmPassword: ''
    });
  }

  onSubmit(): void {
    if (!this.authForm.valid) {
      return;
    }

    this.errorMsg = '';

    if (this.isLoginMode) {
      this.handleLogin();
    } else {
      this.handleRegister();
    }
  }

  private handleLogin(): void {
    this.auth.login(this.username, this.password).subscribe({
      next: (res) => {
        this.auth.saveToken(res.token);
        void this.router.navigate(['/files']);
      },
      error: (err) => {
        this.errorMsg = 'Login failed: ' + (err.error?.detail || 'Invalid credentials');
      }
    });
  }

  private handleRegister(): void {
    if (this.password !== this.confirmPassword) {
      this.errorMsg = 'Passwords do not match';
      return;
    }

    this.auth.register(this.username, this.password).subscribe({
      next: () => {
        // Switch to login mode or auto-login
        if (this.auth.shouldAutoLoginAfterRegister) {
          this.handleLogin();
        } else {
          this.isLoginMode = true;
          this.password = '';
          this.confirmPassword = '';
          this.errorMsg = 'Registration successful! Please log in.';
        }
      },
      error: (err) => {
        this.errorMsg = 'Registration failed: ' + (err.error?.detail || 'Please try again');
      }
    });
  }
}
