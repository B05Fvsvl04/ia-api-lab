# API de autenticación - especificación técnica

## Descripción general
API REST de autenticación que permite registro de usuarios, inicio de sesión con JWT, consulta y actualización de perfil, y renovación de tokens.

## Stack técnico
- Python 3.12+ con FastAPI
- Base de datos: SQLite con SQLAlchemy
- Autenticación: JWT (access token + refresh token)
- Hashing de passwords: bcrypt con salt automático

## Requisitos de seguridad globales
- Todas las respuestas de error deben usar mensajes genéricos (no revelar si el usuario existe o no)
- Rate limiting: máximo 5 intentos de login por minuto por IP
- Passwords: mínimo 8 caracteres, al menos una mayúscula, una minúscula, un número y un carácter especial
- Tokens JWT firmados con clave secreta desde variable de entorno (nunca hardcodeada)
- Access token: expiración de 30 minutos
- Refresh token: expiración de 7 días, un solo uso (se invalida al usarse)
- Headers de seguridad: Content-Type application/json en todas las respuestas
- Validación de inputs en todos los endpoints: tipos, longitud máxima, caracteres permitidos

---

## Endpoints

### POST /register

**Descripción:** Registra un nuevo usuario en el sistema.

**Request:**
- Content-Type: application/json

| Campo    | Tipo   | Requerido | Validaciones                                           |
|----------|--------|-----------|--------------------------------------------------------|
| username | string | sí        | 3-30 caracteres, solo alfanuméricos y guiones bajos    |
| email    | string | sí        | formato email válido, máximo 254 caracteres            |
| password | string | sí        | 8-128 caracteres, debe cumplir política de complejidad |

**Ejemplo de request:**
```json
{
  "username": "juan_dev",
  "email": "juan@ejemplo.com",
  "password": "MiP@ssw0rd!"
}
```

**Respuestas:**

| Código | Descripción               | Body                                                  |
|--------|---------------------------|-------------------------------------------------------|
| 201    | Usuario creado            | `{"id": "uuid", "username": "string", "email": "string", "created_at": "datetime"}` |
| 400    | Validación fallida        | `{"detail": "descripción del error de validación"}`   |
| 409    | Username o email ya existe| `{"detail": "El nombre de usuario o email ya está registrado"}` |
| 429    | Rate limit excedido       | `{"detail": "Demasiadas solicitudes, intente más tarde"}` |

**Reglas de negocio:**
- El username debe ser único (case-insensitive)
- El email debe ser único
- El password se almacena hasheado con bcrypt (nunca en texto plano)
- No se devuelve el password ni el hash en ninguna respuesta

---

### POST /login

**Descripción:** Autentica un usuario y devuelve access token y refresh token.

**Request:**
- Content-Type: application/json

| Campo    | Tipo   | Requerido | Validaciones                    |
|----------|--------|-----------|---------------------------------|
| username | string | sí        | no vacío, máximo 30 caracteres  |
| password | string | sí        | no vacío, máximo 128 caracteres |

**Ejemplo de request:**
```json
{
  "username": "juan_dev",
  "password": "MiP@ssw0rd!"
}
```

**Respuestas:**

| Código | Descripción           | Body                                                                  |
|--------|-----------------------|-----------------------------------------------------------------------|
| 200    | Login exitoso         | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer", "expires_in": 1800}` |
| 401    | Credenciales inválidas| `{"detail": "Credenciales incorrectas"}`                              |
| 429    | Rate limit excedido   | `{"detail": "Demasiadas solicitudes, intente más tarde"}`             |

**Reglas de negocio:**
- El mensaje de error es el mismo para usuario inexistente y password incorrecto (prevenir enumeración de usuarios)
- Se registra cada intento de login fallido (IP, timestamp, username)
- Después de 5 intentos fallidos en 1 minuto desde la misma IP, se bloquean nuevos intentos por 15 minutos

**Estructura del access token (JWT payload):**
```json
{
  "sub": "user_id (uuid)",
  "username": "string",
  "exp": "datetime (30 min desde emisión)",
  "iat": "datetime (momento de emisión)",
  "type": "access"
}
```

**Estructura del refresh token (JWT payload):**
```json
{
  "sub": "user_id (uuid)",
  "exp": "datetime (7 días desde emisión)",
  "iat": "datetime (momento de emisión)",
  "jti": "uuid único del token",
  "type": "refresh"
}
```

---

### GET /profile

**Descripción:** Obtiene el perfil del usuario autenticado.

**Request:**
- Header: `Authorization: Bearer <access_token>`

**Respuestas:**

| Código | Descripción         | Body                                                                  |
|--------|---------------------|-----------------------------------------------------------------------|
| 200    | Perfil obtenido     | `{"id": "uuid", "username": "string", "email": "string", "created_at": "datetime", "updated_at": "datetime"}` |
| 401    | Token inválido o ausente | `{"detail": "No autenticado"}`                                   |
| 401    | Token expirado      | `{"detail": "Token expirado"}`                                        |

**Reglas de negocio:**
- Solo devuelve el perfil del usuario autenticado (el user_id viene del token, no de un parámetro)
- Nunca incluir password o hash en la respuesta

---

### PUT /profile

**Descripción:** Actualiza el perfil del usuario autenticado.

**Request:**
- Header: `Authorization: Bearer <access_token>`
- Content-Type: application/json

| Campo    | Tipo   | Requerido | Validaciones                                           |
|----------|--------|-----------|--------------------------------------------------------|
| email    | string | no        | formato email válido, máximo 254 caracteres            |
| password | string | no        | 8-128 caracteres, debe cumplir política de complejidad |

**Ejemplo de request:**
```json
{
  "email": "juan_nuevo@ejemplo.com"
}
```

**Respuestas:**

| Código | Descripción              | Body                                                                  |
|--------|--------------------------|-----------------------------------------------------------------------|
| 200    | Perfil actualizado       | `{"id": "uuid", "username": "string", "email": "string", "updated_at": "datetime"}` |
| 400    | Validación fallida       | `{"detail": "descripción del error de validación"}`                   |
| 401    | Token inválido o ausente | `{"detail": "No autenticado"}`                                        |
| 409    | Email ya registrado      | `{"detail": "El email ya está registrado"}`                           |

**Reglas de negocio:**
- Solo se pueden actualizar email y password
- El username no se puede cambiar
- Si se actualiza el password, se hashea antes de almacenar
- Solo se actualiza el perfil del usuario autenticado (user_id del token)

---

### POST /refresh

**Descripción:** Emite un nuevo par de tokens usando un refresh token válido.

**Request:**
- Content-Type: application/json

| Campo         | Tipo   | Requerido | Validaciones        |
|---------------|--------|-----------|---------------------|
| refresh_token | string | sí        | JWT válido, no vacío|

**Ejemplo de request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Respuestas:**

| Código | Descripción             | Body                                                                  |
|--------|-------------------------|-----------------------------------------------------------------------|
| 200    | Tokens renovados        | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer", "expires_in": 1800}` |
| 401    | Refresh token inválido  | `{"detail": "Token de actualización inválido"}`                                         |
| 401    | Refresh token expirado  | `{"detail": "Token de actualización expirado"}`                                         |
| 401    | Refresh token ya usado  | `{"detail": "Token de actualización ya utilizado"}`                                     |

**Reglas de negocio:**
- El refresh token es de un solo uso: al usarse se invalida y se emite uno nuevo
- Se almacena un registro de refresh tokens usados para detectar reutilización
- Si se detecta reutilización de un refresh token, se invalidan todos los tokens del usuario (posible robo de token)
- El nuevo access token tiene 30 minutos de expiración
- El nuevo refresh token tiene 7 días de expiración
