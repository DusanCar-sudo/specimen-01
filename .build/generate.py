#!/usr/bin/env python3
"""Seed-locked image generation against the local stable-diffusion.cpp server."""
import base64
import json
import pathlib
import sys
import time
import urllib.request

API = "http://127.0.0.1:8190/sdapi/v1/txt2img"
OUT = pathlib.Path("/home/dusan/preview-demo/.build/raw")
OUT.mkdir(parents=True, exist_ok=True)

NEG = "blurry, low quality, watermark, text, logo, deformed, extra limbs, cartoon, illustration, oversaturated"

PROMPTS = {
    "hero": "full body photograph of a tall bipedal humanoid robot, matte black and brushed aluminum, thin amber indicator lights, dark industrial test chamber, dramatic side light, photorealistic, sharp focus, 35mm, wide shot",
    "joint": "macro photograph of a robotic leg actuator and machined rotary joint, brushed aluminum, black carbon fiber, copper cables, dark studio, hard rim light, photorealistic, high detail",
    "gantry": "industrial robotic arms in a dark factory, repeating gantry structure, haze, dramatic overhead light, wide angle, photorealistic, monochrome",
    "blueprint": "engineering blueprint of a humanoid robot skeleton, orthographic side view, thin white lines on black, dimension lines, technical drawing, precise, no shading",
    "hand": "close-up of an articulated robotic hand, brushed metal fingers, dark background, rim light, photorealistic, sharp focus, engineered joints",
    "lab": "empty robotics test laboratory, painted grid floor, steel gantry frame, amber safety markings on concrete, dark, wide shot, cinematic, photorealistic",
    "servo": "extreme close-up of a servo motor and planetary gear assembly, machined steel, dark background, hard directional light, industrial, photorealistic, shallow depth of field",
    "silhouette": "silhouette of a humanoid robot standing still in a dark room, thin rim light along the edges, volumetric haze, cinematic, photorealistic, wide frame",
    "hero2": "centered full body humanoid robot standing in an empty black studio, matte black armor with exposed brushed aluminum frame, single hard rim light outlining the silhouette, symmetric, product photography, photorealistic, sharp",
    "arm": "single white industrial robotic arm reaching across a dark empty room, clean engineered segments, cable routing, hard side light, photorealistic, minimal composition",
    "mocap": "dancer wearing a black motion capture suit covered in small reflective markers, dark stage, thin white tracking lines connecting markers, photorealistic, wide shot, technical",
}

SEEDS = [101, 211, 307]


def gen(name: str, prompt: str, seed: int) -> dict:
    body = json.dumps(
        {
            "prompt": prompt,
            "negative_prompt": NEG,
            "width": 768,
            "height": 512,
            "steps": 1,
            "cfg_scale": 1,
            "seed": seed,
            "sampler_name": "euler",
        }
    ).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as res:
        payload = json.load(res)
    dt = time.time() - t0
    img = base64.b64decode(payload["images"][0])
    path = OUT / f"{name}-{seed}.png"
    path.write_bytes(img)
    return {"name": name, "seed": seed, "path": str(path), "seconds": round(dt, 2)}


def main() -> None:
    only = set(sys.argv[1:])
    manifest = []
    for name, prompt in PROMPTS.items():
        if only and name not in only:
            continue
        for seed in SEEDS:
            rec = gen(name, prompt, seed)
            rec["prompt"] = prompt
            manifest.append(rec)
            print(json.dumps(rec), flush=True)
    with open(OUT / "manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=2)


if __name__ == "__main__":
    main()
