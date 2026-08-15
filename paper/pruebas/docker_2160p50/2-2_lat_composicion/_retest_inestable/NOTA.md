# Re-test of 2.2 Docker 2160p50 (2026-07-29)
The original value (median 334 ms) was NOT a fluke: the re-test gives a median of 556 ms with
huge variance (142-3555 ms, p95 2440). This confirms that Docker's composite-switching latency
at 4K50 is high and UNSTABLE due to saturation (rescaling 4K under maximum load occasionally
stalls). Local (243 ms) and K8s (205 ms) do not show this. The "official" cell stays at 334 ms
(consistent with the Docker matrix); characterizing this properly with multiple repetitions is
left for future work.
