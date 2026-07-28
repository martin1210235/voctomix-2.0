#!/usr/bin/env python3
"""Genera los manifiestos de las 4 cámaras para K8s (k3s) según formato y perfil.

Reproduce EXACTAMENTE los comandos ffmpeg validados en experiments/comprehensive/
local_scenario.sh (bt709 + marcadores de esquina en 'experiment', color sólido en
'latency'), pero como Deployments de Kubernetes con hostNetwork (localhost:1000N ->
voctocore) e imagen local importada en containerd.

El vídeo maestro BBB se monta desde el host vía hostPath (el pod no lo contiene).

Uso:
  python3 gen_camera_manifests.py <1080p25|1080p50|2160p25|2160p50> <experiment|latency> [salida.yaml]
"""
import sys

FORMATS = {
    "1080p25": (1920, 1080, 25),
    "1080p50": (1920, 1080, 50),
    "2160p25": (3840, 2160, 25),
    "2160p50": (3840, 2160, 50),
}
# N: (offset_s, color_name, hex, port)
CAMS = {
    1: (0,   "red",    "0xFF0000", 10000),
    2: (150, "lime",   "0x00FF00", 10001),
    3: (300, "blue",   "0x0000FF", 10002),
    4: (450, "yellow", "0xFFFF00", 10003),
}
AUDIORATE = 48000
NAMESPACE = "voctomix-exp"
IMAGE = "voctomix-voctocore:latest"
HOST_VIDEOS = "/home/sonda/Documentos/voctomix/videos"
MASTER = "/videos/bbb_sunflower_2160p_60fps_normal.mp4"


def ffmpeg_experiment(w, h, f, offset, color, port):
    return (
        f'ffmpeg -y -nostdin -re -stream_loop -1 -ss {offset} -i "{MASTER}" -ac 2 '
        f'-filter_complex "[0:v] format=yuv420p,scale={w}:{h}:out_range=tv,fps={f},'
        f'drawbox=x=0:y=0:w=iw:h=ih:color={color}:t=40,'
        f'drawbox=x=0:y=0:w=300:h=300:color={color}:t=fill,'
        f'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; '
        f'[0:a] aresample={AUDIORATE} [a]" '
        f'-map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 '
        f'-colorspace bt709 -color_range tv -pix_fmt yuv420p '
        f'-c:v rawvideo -c:a pcm_s16le -f matroska tcp://localhost:{port}'
    )


def ffmpeg_latency(w, h, f, hexc, port):
    return (
        f'ffmpeg -y -nostdin -f lavfi -i "color=c={hexc}:s={w}x{h}:r={f}" '
        f'-f lavfi -i "anullsrc=r={AUDIORATE}:cl=stereo" '
        f'-filter_complex "[0:v] format=yuv420p,'
        f'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709 [v]; '
        f'[1:a] aresample={AUDIORATE} [a]" '
        f'-map "[v]" -map "[a]" -color_primaries bt709 -color_trc bt709 '
        f'-colorspace bt709 -color_range tv -pix_fmt yuv420p '
        f'-c:v rawvideo -c:a pcm_s16le -f matroska tcp://localhost:{port}'
    )


def deployment(n, cmd, profile):
    needs_video = profile == "experiment"
    vol = ""
    mnt = ""
    if needs_video:
        vol = (
            "      volumes:\n"
            "        - name: videos\n"
            "          hostPath:\n"
            f"            path: {HOST_VIDEOS}\n"
            "            type: Directory\n"
        )
        mnt = (
            "          volumeMounts:\n"
            "            - name: videos\n"
            "              mountPath: /videos\n"
            "              readOnly: true\n"
        )
    return f"""---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cam{n}
  namespace: {NAMESPACE}
  labels:
    app: cam{n}
    role: camera
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cam{n}
  template:
    metadata:
      labels:
        app: cam{n}
        role: camera
    spec:
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
      restartPolicy: Always
      terminationGracePeriodSeconds: 2
      containers:
        - name: cam{n}
          image: {IMAGE}
          imagePullPolicy: Never
          command:
            - bash
            - -c
            - |
              while true; do
                {cmd} 2>/dev/null
                sleep 1
              done
{mnt}          resources:
            requests:
              cpu: "250m"
              memory: "128Mi"
{vol}"""


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in FORMATS or sys.argv[2] not in ("experiment", "latency"):
        print(__doc__)
        sys.exit(1)
    fmt, profile = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else f"cameras.{profile}.{fmt}.yaml"
    w, h, f = FORMATS[fmt]
    blocks = []
    for n, (offset, color, hexc, port) in CAMS.items():
        if profile == "experiment":
            cmd = ffmpeg_experiment(w, h, f, offset, color, port)
        else:
            cmd = ffmpeg_latency(w, h, f, hexc, port)
        blocks.append(deployment(n, cmd, profile))
    with open(out, "w", encoding="utf-8") as fp:
        fp.write("".join(blocks))
    print(f"Generado {out}  ({fmt}, {profile}, {w}x{h}@{f})")


if __name__ == "__main__":
    main()
