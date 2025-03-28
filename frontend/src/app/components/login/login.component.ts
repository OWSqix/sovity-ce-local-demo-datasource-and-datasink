// src/app/components/login/login.component.ts
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../auth/auth.service';
import { FormsModule } from '@angular/forms';
import { MatCard, MatCardContent, MatCardHeader, MatCardTitle } from '@angular/material/card';
import { MatFormField } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatButton } from '@angular/material/button';
import { MatLabel } from '@angular/material/form-field';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    FormsModule,
    MatCardContent,
    MatCard,
    MatCardHeader,
    MatCardTitle,
    MatFormField,
    MatFormField,
    MatFormField,
    MatInput,
    MatButton,
    MatLabel
  ],
  templateUrl: './login.component.html',

})
export class LoginComponent {
  username = '';
  password = '';
  errorMsg = '';

  constructor(private auth: AuthService, private router: Router) {}

  onLogin(): void {
    this.errorMsg = '';
    this.auth.login(this.username, this.password).subscribe({
      next: (res) => {
        this.auth.saveToken(res.token);
        this.router.navigate(['/files']);
      },
      error: (err) => {
        this.errorMsg = 'Login failed: ' + (err.error?.detail || 'Invalid credentials');
      }
    });
  }

  onRegister(): void {
    this.errorMsg = '';
    this.auth.register(this.username, this.password).subscribe({
      next: () => {
        // 회원가입 후 자동 로그인
        this.onLogin();
      },
      error: (err) => {
        this.errorMsg = 'Registration failed: ' + (err.error?.detail || '');
      }
    });
  }
}
