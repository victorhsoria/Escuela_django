# Programa Vida y Ministerio — Django local

Aplicación local para Windows 11. Conserva la gestión de estudiantes, semanas,
asignaciones, ayudantes, reportes, formularios S-89 e importación de la guía PDF,
pero guarda la información en una base SQLite administrada por Django.

## Instalación en Windows 11

1. Instalar Python 3.12 o superior desde python.org y marcar **Add Python to PATH**.
2. Descomprimir esta carpeta en una ubicación permanente.
3. Ejecutar `INSTALAR.bat` una sola vez.
4. Abrir **Programa Vida y Ministerio** desde el Escritorio.
5. Ingresar inicialmente con usuario `admin` y contraseña `admin`.
6. Cambiar la contraseña desde Configuración.

El instalador importa automáticamente `data/respaldo_inicial.json` únicamente si
la base está vacía. No necesita internet después de completar la instalación.

## Copias de seguridad

La opción **Exportar respaldo** descarga un JSON completo. Además, se recomienda
copiar periódicamente `db.sqlite3` mientras la aplicación está cerrada.

## Desarrollo

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py initialize_vym
python manage.py runserver
```
