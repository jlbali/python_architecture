To Add:

- More tests for FakeBatchRepository (Ok)

- Add funcionality for updating and deleting, with its associated tests for both types of repos.
Tocando el objeto y haciendo commit ya se modifica en la base de datos (Ok)


- Do the same Repository handler for the OrderLine (Ok)

- Seguir con las cosas de la capa de servicio (chapter 4) y la ruta Flask.
    - Services Layer (Ok)
    - Dockerization (Docker and docker-compose) (ok)
    - Makefile (ok)
    - endpints (flask_app y tests asociados en test_api.py) (ok)
    - Arreglar el problema con los tests que fallan de API (ok)
    - Agregar un CRUD básico de Batches junto con sus tests en todos los niveles (faltan services y api).

- Faltan los tests para la API de get_batch (ok) y get_batches.

Problema: no se está limpiando la base de datos. Se está llenando de info.
Ver la forma de resetear la base de datos para probar el get_batches.
Se tiene un arreglo parcial para ese test, quizás no del todo satisfactorio...

- Para chapter 5, será necesario refactorizar código y reubicarlo en carpetas src y tests.







