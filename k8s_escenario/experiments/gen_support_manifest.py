#!/usr/bin/env python3
"""Genera el manifiesto del pod de SOPORTE para K8s (stream-blanker, audio, break,
intro), replicando exactamente las fuentes de local_scenario.sh base_up, con
hostNetwork y el vídeo montado por hostPath. Parametrizado por formato.

Uso:
  python3 gen_support_manifest.py <1080p25|1080p50|2160p25|2160p50> [salida.yaml]
"""
import sys

FORMATS = {
    "1080p25": (1920, 1080, 25),
    "1080p50": (1920, 1080, 50),
    "2160p25": (3840, 2160, 25),
    "2160p50": (3840, 2160, 50),
}
AUDIORATE = 48000
NAMESPACE = "voctomix-exp"
IMAGE = "voctomix-voctocore:latest"
HOST_VIDEOS = "/home/sonda/Documentos/voctomix/videos"


def script(w, h, f):
    ar = AUDIORATE
    sb = ("ffmpeg -hide_banner -nostdin -nostats -loglevel error -stream_loop -1 -re "
          "-i /videos/{vid} -pix_fmt yuv420p -s {w}x{h} -r {f} -c:v rawvideo -an "
          "-metadata comment=vocto_{tag} -f matroska tcp://localhost:{port}")
    audio = ("ffmpeg -hide_banner -nostdin -nostats -loglevel error -re -stream_loop -1 "
             "-i /videos/musica_pausa.mp3 -c:a pcm_s16le -ar {ar} -ac 2 -vn "
             "-metadata comment=vocto_audio -f matroska tcp://localhost:18000")
    vid = ("ffmpeg -y -nostdin -loglevel error -stream_loop -1 -i /videos/{vid} "
           "-f lavfi -i anullsrc=r={ar}:cl=stereo -filter_complex "
           "\"[0:v] format=yuv420p,scale={w}:{h}:out_range=tv,fps={f},"
           "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; "
           "[1:a] aresample={ar} [a]\" -map \"[v]\" -map \"[a]\" "
           "-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv "
           "-pix_fmt yuv420p -c:v rawvideo -c:a pcm_s16le "
           "-metadata comment=vocto_{tag} -f matroska tcp://localhost:{port}")
    lines = [
        "set -u",
        "while true; do",
        "  " + sb.format(vid="SLIDES_video_starting_soon.mp4", w=w, h=h, f=f, tag="sb1", port=17000) + " 2>/dev/null &",
        "  " + sb.format(vid="stream_offline.mp4", w=w, h=h, f=f, tag="sb2", port=17001) + " 2>/dev/null &",
        "  " + audio.format(ar=ar) + " 2>/dev/null &",
        "  " + vid.format(vid="video_cuenta_regresiva_10s.mp4", ar=ar, w=w, h=h, f=f, tag="break", port=10004) + " 2>/dev/null &",
        "  " + vid.format(vid="intro.mp4", ar=ar, w=w, h=h, f=f, tag="intro", port=10005) + " 2>/dev/null &",
        "  wait",
        "  sleep 1",
        "done",
    ]
    return "\n".join("              " + ln for ln in lines)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in FORMATS:
        print(__doc__)
        sys.exit(1)
    fmt = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else f"support.{fmt}.yaml"
    w, h, f = FORMATS[fmt]
    body = script(w, h, f)
    manifest = f"""---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: support
  namespace: {NAMESPACE}
  labels:
    app: support
    role: support
spec:
  replicas: 1
  selector:
    matchLabels:
      app: support
  template:
    metadata:
      labels:
        app: support
        role: support
    spec:
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
      containers:
        - name: support
          image: {IMAGE}
          imagePullPolicy: Never
          command:
            - bash
            - -c
            - |
{body}
          volumeMounts:
            - name: videos
              mountPath: /videos
              readOnly: true
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
      volumes:
        - name: videos
          hostPath:
            path: {HOST_VIDEOS}
            type: Directory
"""
    with open(out, "w", encoding="utf-8") as fp:
        fp.write(manifest)
    print(f"Generado {out}  (soporte {fmt}, {w}x{h}@{f})")


if __name__ == "__main__":
    main()
