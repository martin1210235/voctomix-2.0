[2026-07-25 19:29:41] ======================================================================
[2026-07-25 19:29:41] ORQUESTADOR MATRIZ — inicio (escenario Docker, 4 formatos)
[2026-07-25 19:29:41] Formatos: ['1080p25', '1080p50', '2160p25', '2160p50'] · Pruebas por celda: ['1-1_escalado', '1-2_sostenida', '2-1_lat_camara', '2-2_lat_composicion', '3-1_resiliencia']
[2026-07-25 19:29:41] Se detiene al terminar Docker (Local y Kubernetes: manual).
[2026-07-25 19:29:41] ======================================================================
[2026-07-25 19:29:41] 
########## CELDA docker · 1080p25 ##########
[2026-07-25 19:29:41]   [RUN ] 1-1_escalado (intento 1) ...
[2026-07-25 20:30:33]   [OK  ] 1-1_escalado en 3652s — 945 muestras, hasta 4 cámaras
[2026-07-25 20:30:33]   [RUN ] 1-2_sostenida (intento 1) ...
[2026-07-25 22:31:26]   [OK  ] 1-2_sostenida en 7253s — 1922 muestras
[2026-07-25 22:31:26]   [SKIP] 2-1_lat_camara ya hecho (100/100 ok)
[2026-07-25 22:31:26]   [SKIP] 2-2_lat_composicion ya hecho (100/100 ok)
[2026-07-25 22:31:26]   [SKIP] 3-1_resiliencia ya hecho (100/100 ok)
[2026-07-25 22:31:26] ########## FIN CELDA docker · 1080p25 ##########
[2026-07-25 22:31:26] 
########## CELDA docker · 1080p50 ##########
[2026-07-25 22:31:26]   [RUN ] 1-1_escalado (intento 1) ...
[2026-07-25 22:33:10]   [FAIL] 1-1_escalado intento 1 (104s): datos.csv no existe o ilegible. ERROR: voctocore no llegó a healthy

[2026-07-25 22:33:15]   [RUN ] 1-1_escalado (intento 2) ...
[2026-07-25 22:35:00]   [FAIL] 1-1_escalado intento 2 (104s): datos.csv no existe o ilegible. ERROR: voctocore no llegó a healthy

[2026-07-25 22:35:05]   [RUN ] 1-1_escalado (intento 3) ...
[2026-07-25 22:36:49]   [FAIL] 1-1_escalado intento 3 (103s): datos.csv no existe o ilegible. ERROR: voctocore no llegó a healthy

[2026-07-25 22:36:54]   [ABANDONADA] 1-1_escalado tras 3 intentos — se continúa
[2026-07-25 22:36:54]   [RUN ] 1-2_sostenida (intento 1) ...
[2026-07-25 22:38:39]   [FAIL] 1-2_sostenida intento 1 (104s): datos.csv no existe o ilegible. ERROR: voctocore no llegó a healthy

[2026-07-25 22:38:44]   [RUN ] 1-2_sostenida (intento 2) ...
[2026-07-25 22:40:29]   [FAIL] 1-2_sostenida intento 2 (105s): datos.csv no existe o ilegible. ERROR: voctocore no llegó a healthy

[2026-07-25 22:40:34]   [RUN ] 1-2_sostenida (intento 3) ...
[2026-07-25 22:42:19]   [FAIL] 1-2_sostenida intento 3 (104s): datos.csv no existe o ilegible. ERROR: voctocore no llegó a healthy

[2026-07-25 22:42:24]   [ABANDONADA] 1-2_sostenida tras 3 intentos — se continúa
[2026-07-25 22:42:24]   [RUN ] 2-1_lat_camara (intento 1) ...
[2026-07-25 22:44:05]   [FAIL] 2-1_lat_camara intento 1 (100s): datos.csv no existe o ilegible. cámaras no conectaron (latency)
[2026-07-25 22:44:10]   [RUN ] 2-1_lat_camara (intento 2) ...
[2026-07-25 22:45:51]   [FAIL] 2-1_lat_camara intento 2 (100s): datos.csv no existe o ilegible. cámaras no conectaron (latency)
[2026-07-25 22:45:56]   [RUN ] 2-1_lat_camara (intento 3) ...
[2026-07-25 22:47:37]   [FAIL] 2-1_lat_camara intento 3 (100s): datos.csv no existe o ilegible. cámaras no conectaron (latency)
[2026-07-25 22:47:42]   [ABANDONADA] 2-1_lat_camara tras 3 intentos — se continúa
[2026-07-25 22:47:42]   [RUN ] 2-2_lat_composicion (intento 1) ...
[2026-07-25 22:49:24]   [FAIL] 2-2_lat_composicion intento 1 (102s): datos.csv no existe o ilegible. cámaras no conectaron (latency)
[2026-07-25 22:49:29]   [RUN ] 2-2_lat_composicion (intento 2) ...
[2026-07-25 22:51:10]   [FAIL] 2-2_lat_composicion intento 2 (101s): datos.csv no existe o ilegible. cámaras no conectaron (latency)
[2026-07-25 22:51:15]   [RUN ] 2-2_lat_composicion (intento 3) ...
[2026-07-25 22:52:56]   [FAIL] 2-2_lat_composicion intento 3 (101s): datos.csv no existe o ilegible. cámaras no conectaron (latency)
[2026-07-25 22:53:01]   [ABANDONADA] 2-2_lat_composicion tras 3 intentos — se continúa
[2026-07-25 22:53:01]   [RUN ] 3-1_resiliencia (intento 1) ...
[2026-07-25 22:54:42]   [FAIL] 3-1_resiliencia intento 1 (100s): datos.csv no existe o ilegible. cámaras no conectaron (experiment)
[2026-07-25 22:54:48]   [RUN ] 3-1_resiliencia (intento 2) ...
[2026-07-25 22:56:30]   [FAIL] 3-1_resiliencia intento 2 (102s): datos.csv no existe o ilegible. cámaras no conectaron (experiment)
[2026-07-25 22:56:35]   [RUN ] 3-1_resiliencia (intento 3) ...
[2026-07-25 22:58:17]   [FAIL] 3-1_resiliencia intento 3 (102s): datos.csv no existe o ilegible. cámaras no conectaron (experiment)
[2026-07-25 22:58:22]   [ABANDONADA] 3-1_resiliencia tras 3 intentos — se continúa
[2026-07-25 22:58:22] ########## FIN CELDA docker · 1080p50 ##########
[2026-07-25 22:58:22] 
########## CELDA docker · 2160p25 ##########
[2026-07-25 22:58:22]   [RUN ] 1-1_escalado (intento 1) ...
[2026-07-25 23:59:12]   [OK  ] 1-1_escalado en 3650s — 1034 muestras, hasta 4 cámaras
[2026-07-25 23:59:12]   [RUN ] 1-2_sostenida (intento 1) ...
[2026-07-26 02:00:06]   [OK  ] 1-2_sostenida en 7253s — 2064 muestras
[2026-07-26 02:00:06]   [RUN ] 2-1_lat_camara (intento 1) ...

[2026-07-26 19:15:48] ============ REANUDACIÓN tras arreglos ============
[2026-07-26 19:15:48] Arreglos: (1) previews framerate = mix (fix crash 50fps), (2) sin GUI en autónomo, (3) timeouts en todo, (4) más margen conexión cámaras.
[2026-07-26 19:15:48] ======================================================================
[2026-07-26 19:15:48] ORQUESTADOR MATRIZ — inicio (escenario Docker, 4 formatos)
[2026-07-26 19:15:48] Formatos: ['1080p25', '1080p50', '2160p25', '2160p50'] · Pruebas por celda: ['1-1_escalado', '1-2_sostenida', '2-1_lat_camara', '2-2_lat_composicion', '3-1_resiliencia']
[2026-07-26 19:15:48] Se detiene al terminar Docker (Local y Kubernetes: manual).
[2026-07-26 19:15:48] ======================================================================
[2026-07-26 19:15:48] 
########## CELDA docker · 1080p25 ##########
[2026-07-26 19:15:48]   [SKIP] 1-1_escalado ya hecho (945 muestras, hasta 4 cámaras)
[2026-07-26 19:15:48]   [SKIP] 1-2_sostenida ya hecho (1922 muestras)
[2026-07-26 19:15:48]   [SKIP] 2-1_lat_camara ya hecho (100/100 ok)
[2026-07-26 19:15:48]   [SKIP] 2-2_lat_composicion ya hecho (100/100 ok)
[2026-07-26 19:15:48]   [SKIP] 3-1_resiliencia ya hecho (100/100 ok)
[2026-07-26 19:15:48] ########## FIN CELDA docker · 1080p25 ##########
[2026-07-26 19:15:48] 
########## CELDA docker · 1080p50 ##########
[2026-07-26 19:15:48]   [RUN ] 1-1_escalado (intento 1) ...
[2026-07-26 20:16:38]   [OK  ] 1-1_escalado en 3649s — 969 muestras, hasta 4 cámaras
[2026-07-26 20:16:38]   [RUN ] 1-2_sostenida (intento 1) ...
[2026-07-26 22:17:29]   [OK  ] 1-2_sostenida en 7251s — 1937 muestras
[2026-07-26 22:17:29]   [RUN ] 2-1_lat_camara (intento 1) ...
[2026-07-26 22:22:29]   [OK  ] 2-1_lat_camara en 300s — 100/100 ok
[2026-07-26 22:22:29]   [RUN ] 2-2_lat_composicion (intento 1) ...
[2026-07-26 22:27:51]   [OK  ] 2-2_lat_composicion en 321s — 100/100 ok
[2026-07-26 22:27:51]   [RUN ] 3-1_resiliencia (intento 1) ...
[2026-07-26 22:46:09]   [OK  ] 3-1_resiliencia en 1098s — 100/100 ok
[2026-07-26 22:46:09] ########## FIN CELDA docker · 1080p50 ##########
[2026-07-26 22:46:09] 
########## CELDA docker · 2160p25 ##########
[2026-07-26 22:46:09]   [SKIP] 1-1_escalado ya hecho (1034 muestras, hasta 4 cámaras)
[2026-07-26 22:46:09]   [SKIP] 1-2_sostenida ya hecho (2064 muestras)
[2026-07-26 22:46:09]   [RUN ] 2-1_lat_camara (intento 1) ...
[2026-07-26 22:51:39]   [OK  ] 2-1_lat_camara en 329s — 100/100 ok
[2026-07-26 22:51:39]   [RUN ] 2-2_lat_composicion (intento 1) ...
[2026-07-26 22:57:07]   [OK  ] 2-2_lat_composicion en 328s — 100/100 ok
[2026-07-26 22:57:07]   [RUN ] 3-1_resiliencia (intento 1) ...
[2026-07-26 23:16:23]   [OK  ] 3-1_resiliencia en 1156s — 100/100 ok
[2026-07-26 23:16:23] ########## FIN CELDA docker · 2160p25 ##########
[2026-07-26 23:16:23] 
########## CELDA docker · 2160p50 ##########
[2026-07-26 23:16:23]   SMOKE TEST 2160p50: comprobando si el sistema satura con 4 cámaras 4K50...
[2026-07-26 23:17:57]   SMOKE 2160p50: cámaras conectadas=4, arranque=OK. (Si satura, las medidas lo reflejarán como techo de rendimiento.)
[2026-07-26 23:17:57]   [RUN ] 1-1_escalado (intento 1) ...
[2026-07-27 00:18:48]   [OK  ] 1-1_escalado en 3650s — 1040 muestras, hasta 4 cámaras
[2026-07-27 00:18:48]   [RUN ] 1-2_sostenida (intento 1) ...
[2026-07-27 02:19:41]   [OK  ] 1-2_sostenida en 7253s — 2043 muestras
[2026-07-27 02:19:41]   [RUN ] 2-1_lat_camara (intento 1) ...
[2026-07-27 02:24:57]   [OK  ] 2-1_lat_camara en 315s — 100/100 ok
[2026-07-27 02:24:57]   [RUN ] 2-2_lat_composicion (intento 1) ...
[2026-07-27 02:31:08]   [OK  ] 2-2_lat_composicion en 371s — 100/100 ok
[2026-07-27 02:31:08]   [RUN ] 3-1_resiliencia (intento 1) ...
[2026-07-27 02:51:36]   [OK  ] 3-1_resiliencia en 1228s — 100/100 ok
[2026-07-27 02:51:36] ########## FIN CELDA docker · 2160p50 ##########
[2026-07-27 02:52:05] 
======================================================================
[2026-07-27 02:52:05] MATRIZ DOCKER COMPLETADA. OK=13 SKIP=7 FALLIDAS=0
[2026-07-27 02:52:05] Local y Kubernetes: pendientes (manual, contigo delante).
[2026-07-27 02:52:05] ======================================================================
[2026-07-27 02:55:22] 
======================================================================
[2026-07-27 02:55:22] ORQUESTADOR MATRIZ — escenario LOCAL (nativo)
[2026-07-27 02:55:22] ======================================================================
[2026-07-27 02:55:22]   SMOKE LOCAL: validando arranque nativo (voctocore + 1 cámara + mix)...
[2026-07-27 09:46:19] 
======================================================================
[2026-07-27 09:46:19] ORQUESTADOR MATRIZ — escenario LOCAL (nativo)
[2026-07-27 09:46:19] ======================================================================
[2026-07-27 09:46:19]   SMOKE LOCAL: validando arranque nativo (voctocore + 1 cámara + mix)...
[2026-07-27 09:46:57]   SMOKE LOCAL: OK (mix nativo produce vídeo)
[2026-07-27 09:46:57] 
########## CELDA local · 1080p25 ##########
[2026-07-27 09:46:57]   [RUN ] 1-1_escalado (intento 1) ...
[2026-07-27 10:47:24]   [OK  ] 1-1_escalado en 3627s — 716 muestras, hasta 4 cámaras
[2026-07-27 10:47:24]   [RUN ] 1-2_sostenida (intento 1) ...
[2026-07-27 12:47:53]   [OK  ] 1-2_sostenida en 7228s — 1439 muestras
[2026-07-27 12:47:53]   [RUN ] 2-1_lat_camara (intento 1) ...
[2026-07-27 12:53:30]   [OK  ] 2-1_lat_camara en 336s — 100/100 ok
[2026-07-27 12:53:30]   [RUN ] 2-2_lat_composicion (intento 1) ...
[2026-07-27 12:59:04]   [OK  ] 2-2_lat_composicion en 334s — 100/100 ok
[2026-07-27 12:59:04]   [RUN ] 3-1_resiliencia (intento 1) ...
[2026-07-27 13:19:48]   [FAIL] 3-1_resiliencia intento 1: 0/100 ok.  LISTA (se salta)

OK: 0/100  MTTR mediana=None ms  p95=None ms  min=None max=None
  → /home/sonda/Documentos/voctomix/paper/pruebas/local_1080p25/3-1_resiliencia/datos.csv , resumen.csv , datos.xlsx

[2026-07-27 13:19:50]   [RUN ] 3-1_resiliencia (intento 2) ...
[2026-07-27 13:40:33]   [FAIL] 3-1_resiliencia intento 2: 0/100 ok.  LISTA (se salta)

OK: 0/100  MTTR mediana=None ms  p95=None ms  min=None max=None
  → /home/sonda/Documentos/voctomix/paper/pruebas/local_1080p25/3-1_resiliencia/datos.csv , resumen.csv , datos.xlsx

[2026-07-27 13:40:35]   [RUN ] 3-1_resiliencia (intento 3) ...
[2026-07-27 14:01:19]   [FAIL] 3-1_resiliencia intento 3: 0/100 ok.  LISTA (se salta)

OK: 0/100  MTTR mediana=None ms  p95=None ms  min=None max=None
  → /home/sonda/Documentos/voctomix/paper/pruebas/local_1080p25/3-1_resiliencia/datos.csv , resumen.csv , datos.xlsx

[2026-07-27 14:01:21]   [ABANDONADA] 3-1_resiliencia tras 3 intentos
[2026-07-27 14:01:21] ########## FIN CELDA local · 1080p25 ##########
[2026-07-27 14:01:21] GATE: la primera celda local tuvo 1 prueba(s) abandonada(s) → posible bug sistemático. Se DETIENE Local para revisión (no se malgastan horas).
[2026-07-27 16:22:06] 
======================================================================
[2026-07-27 16:22:06] ORQUESTADOR MATRIZ — escenario LOCAL (nativo)
[2026-07-27 16:22:06] ======================================================================
[2026-07-27 16:22:06]   SMOKE LOCAL: validando arranque nativo (voctocore + 1 cámara + mix)...
[2026-07-27 16:22:44]   SMOKE LOCAL: OK (mix nativo produce vídeo)
[2026-07-27 16:22:44] 
########## CELDA local · 1080p25 ##########
[2026-07-27 16:22:44]   [SKIP] 1-1_escalado ya hecho
[2026-07-27 16:22:44]   [SKIP] 1-2_sostenida ya hecho
[2026-07-27 16:22:44]   [SKIP] 2-1_lat_camara ya hecho
[2026-07-27 16:22:44]   [SKIP] 2-2_lat_composicion ya hecho
[2026-07-27 16:22:44]   [RUN ] 3-1_resiliencia (intento 1) ...
[2026-07-27 16:42:11]   [OK  ] 3-1_resiliencia en 1166s — 100/100 ok
[2026-07-27 16:42:11] ########## FIN CELDA local · 1080p25 ##########
[2026-07-27 16:42:11] 
########## CELDA local · 1080p50 ##########
[2026-07-27 16:42:11]   [RUN ] 1-1_escalado (intento 1) ...
[2026-07-27 17:42:38]   [OK  ] 1-1_escalado en 3627s — 716 muestras, hasta 4 cámaras
[2026-07-27 17:42:38]   [RUN ] 1-2_sostenida (intento 1) ...
[2026-07-27 19:43:07]   [OK  ] 1-2_sostenida en 7228s — 1439 muestras
[2026-07-27 19:43:07]   [RUN ] 2-1_lat_camara (intento 1) ...
[2026-07-27 19:48:30]   [OK  ] 2-1_lat_camara en 323s — 100/100 ok
[2026-07-27 19:48:30]   [RUN ] 2-2_lat_composicion (intento 1) ...
[2026-07-27 19:53:54]   [OK  ] 2-2_lat_composicion en 324s — 100/100 ok
[2026-07-27 19:53:54]   [RUN ] 3-1_resiliencia (intento 1) ...
[2026-07-27 20:12:04]   [OK  ] 3-1_resiliencia en 1089s — 100/100 ok
[2026-07-27 20:12:04] ########## FIN CELDA local · 1080p50 ##########
[2026-07-27 20:12:04] 
########## CELDA local · 2160p25 ##########
[2026-07-27 20:12:04]   [RUN ] 1-1_escalado (intento 1) ...
[2026-07-27 21:12:31]   [OK  ] 1-1_escalado en 3627s — 716 muestras, hasta 4 cámaras
[2026-07-27 21:12:31]   [RUN ] 1-2_sostenida (intento 1) ...
[2026-07-27 23:13:01]   [OK  ] 1-2_sostenida en 7229s — 1439 muestras
[2026-07-27 23:13:01]   [RUN ] 2-1_lat_camara (intento 1) ...
[2026-07-27 23:18:35]   [OK  ] 2-1_lat_camara en 334s — 100/100 ok
[2026-07-27 23:18:35]   [RUN ] 2-2_lat_composicion (intento 1) ...
[2026-07-27 23:24:08]   [OK  ] 2-2_lat_composicion en 332s — 100/100 ok
[2026-07-27 23:24:08]   [RUN ] 3-1_resiliencia (intento 1) ...
[2026-07-27 23:43:14]   [OK  ] 3-1_resiliencia en 1146s — 100/100 ok
[2026-07-27 23:43:14] ########## FIN CELDA local · 2160p25 ##########
[2026-07-27 23:43:14] 
########## CELDA local · 2160p50 ##########
[2026-07-27 23:43:14]   [RUN ] 1-1_escalado (intento 1) ...
[2026-07-28 00:43:42]   [OK  ] 1-1_escalado en 3627s — 716 muestras, hasta 4 cámaras
[2026-07-28 00:43:42]   [RUN ] 1-2_sostenida (intento 1) ...
[2026-07-28 02:44:10]   [OK  ] 1-2_sostenida en 7228s — 1439 muestras
[2026-07-28 02:44:10]   [RUN ] 2-1_lat_camara (intento 1) ...
[2026-07-28 02:49:57]   [OK  ] 2-1_lat_camara en 346s — 100/100 ok
[2026-07-28 02:49:57]   [RUN ] 2-2_lat_composicion (intento 1) ...
[2026-07-28 02:55:52]   [OK  ] 2-2_lat_composicion en 355s — 100/100 ok
[2026-07-28 02:55:52]   [RUN ] 3-1_resiliencia (intento 1) ...
[2026-07-28 03:15:28]   [OK  ] 3-1_resiliencia en 1175s — 100/100 ok
[2026-07-28 03:15:28] ########## FIN CELDA local · 2160p50 ##########
[2026-07-28 03:15:30] 
======================================================================
[2026-07-28 03:15:30] MATRIZ LOCAL COMPLETADA. OK=16 SKIP=4 FALLIDAS=0
[2026-07-28 03:15:30] ======================================================================
