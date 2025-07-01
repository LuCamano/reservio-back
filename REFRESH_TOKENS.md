# Implementación de Refresh Tokens

## Funcionamiento

La implementación de refresh tokens permite mantener la seguridad mientras se proporciona una mejor experiencia de usuario, evitando que los usuarios tengan que autenticarse frecuentemente.

### Flujo de Autenticación

1. **Login inicial**: El usuario se autentica con email/password
2. **Respuesta**: El servidor devuelve un `access_token` (30 minutos) y un `refresh_token` (7 días)
3. **Uso normal**: El cliente usa el `access_token` para hacer requests protegidas
4. **Token expirado**: Cuando el `access_token` expira, el cliente usa el `refresh_token` para obtener nuevos tokens
5. **Renovación**: El servidor valida el `refresh_token` y emite nuevos tokens

### Endpoints de Autenticación

#### POST /auth/login
Autentica al usuario y devuelve tokens.

**Request:**
```json
{
    "username": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

#### POST /auth/refresh
Renueva los tokens usando un refresh token válido.

**Request:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

#### POST /auth/logout
Invalida la sesión (el cliente debe eliminar los tokens).

### Configuración de Tiempos

- **Access Token**: 30 minutos (configurable en `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Refresh Token**: 7 días (configurable en la función `create_refresh_token`)

### Implementación en Angular

#### 1. Servicio de Autenticación (auth.service.ts)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = 'http://localhost:8000';
  private currentUserSubject = new BehaviorSubject<any>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Verificar si hay tokens almacenados al inicializar
    const token = this.getAccessToken();
    if (token && !this.isTokenExpired(token)) {
      this.getCurrentUser().subscribe();
    }
  }

  login(credentials: LoginRequest): Observable<TokenResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return this.http.post<TokenResponse>(`${this.API_URL}/auth/login`, formData)
      .pipe(
        map(response => {
          this.setTokens(response.access_token, response.refresh_token);
          this.getCurrentUser().subscribe();
          return response;
        }),
        catchError(error => {
          console.error('Error en login:', error);
          return throwError(() => error);
        })
      );
  }

  refreshToken(): Observable<TokenResponse> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    const refreshRequest: RefreshRequest = { refresh_token: refreshToken };
    
    return this.http.post<TokenResponse>(`${this.API_URL}/auth/refresh`, refreshRequest)
      .pipe(
        map(response => {
          this.setTokens(response.access_token, response.refresh_token);
          return response;
        }),
        catchError(error => {
          this.logout();
          return throwError(() => error);
        })
      );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUserSubject.next(null);
  }

  getCurrentUser(): Observable<any> {
    return this.http.get(`${this.API_URL}/auth/me`)
      .pipe(
        map(user => {
          this.currentUserSubject.next(user);
          return user;
        })
      );
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000; // Convertir a millisegundos
      return Date.now() >= exp;
    } catch {
      return true;
    }
  }

  isLoggedIn(): boolean {
    const token = this.getAccessToken();
    return token != null && !this.isTokenExpired(token);
  }
}
```

#### 2. Interceptor HTTP (auth.interceptor.ts)

```typescript
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, filter, take, switchMap } from 'rxjs/operators';
import { AuthService } from './auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Agregar access token a las requests
    const accessToken = this.authService.getAccessToken();
    if (accessToken) {
      request = this.addTokenHeader(request, accessToken);
    }

    return next.handle(request).pipe(
      catchError(error => {
        if (error instanceof HttpErrorResponse && error.status === 401) {
          return this.handle401Error(request, next);
        }
        return throwError(() => error);
      })
    );
  }

  private addTokenHeader(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
      headers: request.headers.set('Authorization', `Bearer ${token}`)
    });
  }

  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      const refreshToken = this.authService.getRefreshToken();
      if (refreshToken) {
        return this.authService.refreshToken().pipe(
          switchMap((response: any) => {
            this.isRefreshing = false;
            this.refreshTokenSubject.next(response.access_token);
            return next.handle(this.addTokenHeader(request, response.access_token));
          }),
          catchError((error) => {
            this.isRefreshing = false;
            this.authService.logout();
            this.router.navigate(['/login']);
            return throwError(() => error);
          })
        );
      }
    }

    // Si ya se está refrescando, esperar a que termine
    return this.refreshTokenSubject.pipe(
      filter(token => token !== null),
      take(1),
      switchMap((token) => next.handle(this.addTokenHeader(request, token)))
    );
  }
}
```

#### 3. Guard de Autenticación (auth.guard.ts)

```typescript
import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): boolean {
    if (this.authService.isLoggedIn()) {
      return true;
    } else {
      this.router.navigate(['/login']);
      return false;
    }
  }
}
```

#### 4. Configuración en app.module.ts

```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AuthInterceptor } from './auth/auth.interceptor';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

#### 5. Componente de Login (login.component.ts)

```typescript
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../auth/auth.service';

@Component({
  selector: 'app-login',
  template: `
    <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
      <div>
        <label for="email">Email:</label>
        <input 
          type="email" 
          id="email" 
          formControlName="username"
          required>
      </div>
      <div>
        <label for="password">Password:</label>
        <input 
          type="password" 
          id="password" 
          formControlName="password"
          required>
      </div>
      <button type="submit" [disabled]="loginForm.invalid || loading">
        {{ loading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
      </button>
      <div *ngIf="error" class="error">{{ error }}</div>
    </form>
  `
})
export class LoginComponent {
  loginForm: FormGroup;
  loading = false;
  error = '';

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.formBuilder.group({
      username: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.loading = true;
      this.error = '';

      this.authService.login(this.loginForm.value).subscribe({
        next: () => {
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          this.error = 'Credenciales inválidas';
          this.loading = false;
        }
      });
    }
  }
}
```

### Ventajas de esta Implementación

1. **Seguridad**: Access tokens de corta duración reducen el riesgo de uso malicioso
2. **Experiencia de usuario**: Los usuarios no necesitan hacer login frecuentemente
3. **Flexibilidad**: Los refresh tokens pueden ser revocados individualmente
4. **Escalabilidad**: Los tokens son stateless y no requieren almacenamiento en servidor

### Consideraciones Específicas para Angular

1. **Gestión de Estado**: Usa RxJS BehaviorSubject para mantener el estado de autenticación
2. **HTTP Interceptors**: Manejo automático de tokens y renovación transparente
3. **Guards**: Protección de rutas con AuthGuard
4. **Manejo de Errores**: Operadores RxJS para manejo elegante de errores
5. **TypeScript**: Tipado fuerte para mayor seguridad y mejor DX

### Instalación de Dependencias

```bash
npm install @angular/common @angular/core @angular/router rxjs
```

### Configuración de Rutas (app-routing.module.ts)

```typescript
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './auth/auth.guard';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { 
    path: 'dashboard', 
    component: DashboardComponent, 
    canActivate: [AuthGuard] 
  },
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: '**', redirectTo: '/login' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
```

### Consideraciones de Seguridad

1. **HTTPS obligatorio**: Los tokens deben transmitirse siempre por HTTPS
2. **Almacenamiento seguro**: Considera usar httpOnly cookies en lugar de localStorage para mayor seguridad
3. **Rotación de tokens**: Cada refresh genera nuevos tokens
4. **Validación estricta**: Los tokens incluyen tipo y tiempo de expiración
5. **CORS Configuration**: Configura CORS apropiadamente en el backend para Angular
6. **Environment Variables**: Usa Angular environments para URLs de API
7. **Token Validation**: Valida tokens en el frontend antes de hacer requests
8. **Logout en múltiples tabs**: Considera usar BroadcastChannel para logout global

### Configuración de Entorno (environments/environment.ts)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

### Mejores Prácticas para Angular

1. **Usar OnDestroy**: Implementa OnDestroy para limpiar suscripciones
2. **Async Pipe**: Usa async pipe en templates para manejo automático de observables
3. **Error Handling**: Implementa un servicio global de manejo de errores
4. **Loading States**: Maneja estados de carga en la UI
5. **Token Refresh Race Conditions**: El interceptor maneja múltiples requests simultáneas correctamente
