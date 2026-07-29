# Re-test 2.2 Docker 2160p50 (2026-07-29)
El valor original (mediana 334 ms) NO era un fluke: el re-test da mediana 556 ms con
varianza enorme (142–3555 ms, p95 2440). Confirma que la latencia de composición de Docker
a 4K50 es alta e INESTABLE por saturación (reescalar 4K bajo carga máxima se atasca a veces).
Local (243 ms) y K8s (205 ms) no lo sufren. La celda "oficial" se mantiene en 334 ms
(consistencia con la matriz Docker); pendiente caracterizar con varias repeticiones.
