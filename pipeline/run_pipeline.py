import argparse, glob, json, subprocess, sys, time
from pathlib import Path

def run(cmd, log, name):
    t = time.time()
    print(f"\n=== {name} ===\n{' '.join(map(str, cmd))}")
    subprocess.run(cmd, check=True)
    log[name] = round(time.time() - t, 1)

ap = argparse.ArgumentParser()
ap.add_argument("obj_dir", help="e.g. artifacts/obj01 (must contain 01_raw/)")
ap.add_argument("--iters", type=int, default=7000)
ap.add_argument("--max-side", type=int, default=1600)  # keeps 8 GB cards safe
ap.add_argument("--rembg-model", default="isnet-general-use")
a = ap.parse_args()

A, log = Path(a.obj_dir), {}
run([sys.executable, "pipeline/prep_images.py", A/"01_raw", A/"02_nobg",
     "--model", a.rembg_model, "--max-side", str(a.max_side)], log, "1_prep")
run(["ns-process-data", "images", "--data", A/"02_nobg",
     "--output-dir", A/"03_colmap", "--matching-method", "exhaustive"], log, "2_colmap")
run(["ns-train", "splatfacto", "--data", A/"03_colmap", "--output-dir", A/"04_train",
     "--max-num-iterations", str(a.iters),
     "--viewer.quit-on-train-completion", "True"], log, "3_train")
cfg = sorted(glob.glob(str(A/"04_train/**/config.yml"), recursive=True))[-1]
run(["ns-export", "gaussian-splat", "--load-config", cfg,
     "--output-dir", A/"05_export"], log, "4_export")

(A/"timings.json").write_text(json.dumps(log, indent=2))
print("\nDone. Next: clean splat.ply in SuperSplat, export .splat to viewer/models/")