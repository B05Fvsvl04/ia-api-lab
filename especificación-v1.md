# API de autenticación

## Descripción
API para manejar el login y registro de usuarios.

## Endpoints

### POST /register
Registra un nuevo usuario.
- Recibe: username, password, email
- Devuelve: usuario creado

### POST /login
Inicia sesión.
- Recibe: username y password
- Devuelve: token de acceso

### GET /profile
Obtiene el perfil del usuario.
- Devuelve: datos del usuario

### PUT /profile
Actualiza el perfil.
- Recibe: campos a actualizar
- Devuelve: perfil actualizado

### POST /refresh
Renueva el token.
- Recibe: token actual
- Devuelve: nuevo token

## Notas
- Usar JWT para los tokens
- La base de datos puede ser SQLite
- Los passwords deben guardarse de forma segura