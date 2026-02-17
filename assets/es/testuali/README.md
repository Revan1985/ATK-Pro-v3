# ATK-Pro – Reconstrucción de Baldosas Antiguas
**Nota:** Este proyecto es desarrollado, mantenido y soportado enteramente por una sola persona. Toda retroalimentación, informe o contribución es bienvenida, pero no hay un equipo o estructura corporativa detrás del desarrollo.
## Descripción
ATK-Pro es una herramienta avanzada para la reconstrucción, archivo y consulta de imágenes y documentos genealógicos digitalizados del portal Antenati. El proyecto soporta la gestión multilingüe y la distribución como aplicación independiente para Windows.
## Funcionalidades principales
- Reconstrucción automática de imágenes a partir de teselas IIIF
- Soporte multilingüe (20 idiomas)
- Interfaz gráfica moderna (Qt)
- Compilar EXE independiente e instalador multilingüe
## Instalación
1. Descarga el instalador ATK-Pro-Setup-v2.0.exe o el ejecutable independiente ATK-Pro.exe de la sección de lanzamientos.
1. Sigue las instrucciones en pantalla para completar la instalación.
1. Inicie ATK-Pro desde el menú Inicio o desde la carpeta de instalación.
## Estructura del proyecto
- `src/` – Código fuente principal (GUI, lógica, módulos)
- `assets/` – Activos multilingües (guías, plantillas, recursos)
- `locales/` – Archivos de traducción .ini para cada idioma
- `docs_generali/` – Glosarios, documentación general, hoja de ruta
- `scripts/` – Scripts de mantenimiento, traducción, validación
- `tests/` – Pruebas automáticas y de cobertura
- `dist/` – Compilación/instalador de salida
## Documentación
- La documentación histórica y de profundización está ahora archivada en `docs_generales/archivo/`.
- El presente README y el archivo `CHANGELOG.md` resumen el estado y las etapas principales del proyecto.
## Historia y desarrollo
El proyecto nace como evolución de herramientas para la genealogía digital, con atención a la transparencia, el archivo histórico y el soporte internacional. Cada hito se rastrea y documenta en el repositorio.
## Créditos
Desarrollo y mantenimiento: Daniele Pigoli
Contribuciones: ver changelog y notas de lanzamiento
## Registro de cambios
Consulta el archivo `docs_generali/CHANGELOG.md` para conocer las principales novedades y hitos del proyecto.
Para detalles históricos y notas completas, véase la carpeta `docs_generali/archivio/`.

-----
## Estado actual
- Todos los módulos activos han sido probados con cobertura directa y defensiva
- Anotación con bloque `# === Cobertura de prueba ===` en módulos validados
- El módulo main.py, a pesar de tener una cobertura parcial (64%), ha sido validado lógicamente al ser orquestador
### Próximos pasos
- Preparar la v2.1 con evolución incremental y documentación actualizada

✍️ Curado por Daniele Pigoli – con la intención de unir rigor técnico y memoria histórica.
