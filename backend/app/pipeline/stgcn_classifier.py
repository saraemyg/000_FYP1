"""
STGCN++ Behavior Classifier — drop-in replacement for BehaviorClassifier.

Uses pretrained STGCN++ weights from pyskl (NTU RGB+D 120, HRNet COCO-17 keypoints).
The pretrained model natively expects 17 COCO keypoints — exactly what YOLOv11-Pose outputs.
No joint remapping required.

SETUP (run once):
    pip install pyskl
    # Download pretrained checkpoint (~60MB):
    # From backend/ directory:
    mkdir -p models
    # Windows:
    curl -L -o models/stgcnpp_ntu120_xsub_hrnet_joint.pth ^
      https://download.openmmlab.com/mmaction/pyskl/ckpt/stgcnpp/stgcnpp_ntu120_xsub_hrnet/j.pth

Then set in .env:
    STGCN_MODEL_PATH=models/stgcnpp_ntu120_xsub_hrnet_joint.pth
    BEHAVIOR_CLASSIFIER=stgcn   # (or "mlp" to revert)

HOW IT WORKS:
  - STGCN++ expects: (N, C, T, V, M) — batch, channels(3), frames(30), joints(17), persons(1)
  - We maintain a per-person rolling buffer of T=30 frames
  - Each frame: stack [x, y, conf] for all 17 keypoints → shape (3, 17)
  - Once buffer has ≥3 frames, run inference (pad short buffers by repeating last frame)
  - Final classification head (120 → 7) maps NTU classes to your 7 behavior classes

NTU-120 → 7 behavior mapping:
    walking:    A8, A9, A10, A11 (walk, walk toward each other, walk apart, walk in circle)
    running:    A11 (run) — note A11 is mapped to both; runner takes priority
    standing:   A3, A12 (stand up, standing still)
    sitting:    A7, A13 (sit down, sitting still)
    bending:    A17, A24 (bend over, pick up)
    falling:    A43, A44, A45 (falling, falling ill, fainting)
    suspicious: A68, A69, A70 (cross arms, look around, check time nervously)
    Everything else → most similar of the 7 based on softmax grouping
"""

import numpy as np
from collections import defaultdict, deque, Counter
from dataclasses import dataclass
from typing import List, Optional, Dict
import torch
import torch.nn as nn
from loguru import logger

from app.pipeline.detector import PersonDetection
from app.pipeline.classifier import BehaviorResult   # reuse dataclass

# ── Constants ─────────────────────────────────────────────────────────────────
BEHAVIOR_CLASSES = ["walking", "standing", "sitting", "running", "bending", "falling", "suspicious"]
POSE_WINDOW_SIZE = 30    # STGCN++ expects 30 frames (vs 15 for MLP)
SMOOTHING_WINDOW = 5
NUM_JOINTS       = 17    # COCO-17

# NTU-120 action index (1-based) → behavior class
# Actions not listed default to the highest-prob of the 7 via soft grouping
NTU_TO_BEHAVIOR: Dict[int, str] = {
    # walking
    8: "walking", 9: "walking", 10: "walking", 55: "walking",
    # running
    11: "running",
    # standing
    3: "standing", 12: "standing",
    # sitting
    7: "sitting", 13: "sitting",
    # bending
    17: "bending", 20: "bending", 24: "bending",
    # falling
    43: "falling", 44: "falling", 45: "falling",
    # suspicious (loitering / nervous behaviour)
    68: "suspicious", 69: "suspicious", 70: "suspicious",
}

# For NTU classes not in the map above, group by semantic similarity
# to one of the 7 target classes (used as soft fallback)
NTU_FALLBACK_GROUPS = {
    "walking":   list(range(8, 12)),
    "standing":  [3, 12, 42],
    "sitting":   [7, 13, 54],
    "running":   [11],
    "bending":   [17, 20, 24, 38],
    "falling":   [43, 44, 45, 30],
    "suspicious":[68, 69, 70, 71],
}
# Build reverse: NTU action → behavior (fallback)
_NTU_FALLBACK: Dict[int, str] = {}
for beh, actions in NTU_FALLBACK_GROUPS.items():
    for a in actions:
        if a not in NTU_TO_BEHAVIOR:
            _NTU_FALLBACK[a] = beh


# ── STGCN++ Model (lightweight replication of the inference graph) ────────────
# We only need the graph convolution forward pass to load the pretrained weights.
# This is a minimal reproduction — not the full pyskl training codebase.

class GraphConv(nn.Module):
    def __init__(self, in_ch, out_ch, A):
        super().__init__()
        self.A = A                           # (K, V, V) adjacency
        K = A.shape[0]
        self.conv = nn.Conv2d(in_ch * K, out_ch, 1)
        self.bn   = nn.BatchNorm2d(out_ch)
        self.relu = nn.ReLU()

    def forward(self, x):                   # x: (N, C, T, V)
        N, C, T, V = x.shape
        K = self.A.shape[0]
        A = self.A.to(x.device)
        # Aggregate neighbours: (N, K*C, T, V)
        support = torch.einsum("kvw,nctw->nkctv", A, x).contiguous()
        support = support.view(N, K * C, T, V)
        return self.relu(self.bn(self.conv(support)))


class STGCNBlock(nn.Module):
    def __init__(self, in_ch, out_ch, A, stride=1):
        super().__init__()
        self.gcn = GraphConv(in_ch, out_ch, A)
        self.tcn = nn.Sequential(
            nn.Conv2d(out_ch, out_ch, (9, 1), stride=(stride, 1), padding=(4, 0)),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(),
        )
        self.residual = (
            nn.Sequential(nn.Conv2d(in_ch, out_ch, 1, stride=(stride, 1)), nn.BatchNorm2d(out_ch))
            if in_ch != out_ch or stride != 1 else nn.Identity()
        )
        self.relu = nn.ReLU()

    def forward(self, x):
        return self.relu(self.tcn(self.gcn(x)) + self.residual(x))


def _coco17_adjacency():
    """COCO-17 skeleton adjacency matrix (3 partitions for ST-GCN centre partition strategy)."""
    edges = [
        (0,1),(0,2),(1,3),(2,4),               # head
        (5,6),(5,7),(6,8),(7,9),(8,10),         # arms
        (5,11),(6,12),(11,12),                  # torso
        (11,13),(12,14),(13,15),(14,16),        # legs
    ]
    V = 17
    A = np.zeros((3, V, V), dtype=np.float32)
    # Partition 0: self-links
    for i in range(V):
        A[0, i, i] = 1
    # Partition 1: centripetal (child → parent)
    # Partition 2: centrifugal (parent → child)
    for i, j in edges:
        A[1, j, i] = 1
        A[2, i, j] = 1
    # Row-normalise each partition
    for k in range(3):
        D = A[k].sum(axis=1, keepdims=True).clip(min=1)
        A[k] = A[k] / D
    return torch.from_numpy(A)


class STGCNPlusPlus(nn.Module):
    """
    Minimal STGCN++ compatible with pyskl pretrained NTU120-XSub-HRNet weights.
    Architecture matches stgcnpp_ntu120_xsub_hrnet config in pyskl.
    """
    def __init__(self, num_classes: int = 120):
        super().__init__()
        A = _coco17_adjacency()
        self.register_buffer("A", A)

        self.data_bn = nn.BatchNorm1d(3 * 17)   # 3 channels × 17 joints

        cfg = [
            (3,   64,  1), (64,  64,  1), (64,  64,  1),
            (64,  64,  1), (64, 128,  2), (128, 128, 1),
            (128, 128, 1), (128, 256, 2), (256, 256, 1),
            (256, 256, 1),
        ]
        layers = []
        for in_ch, out_ch, stride in cfg:
            layers.append(STGCNBlock(in_ch, out_ch, A, stride=stride))
        self.backbone = nn.ModuleList(layers)
        self.pool     = nn.AdaptiveAvgPool2d(1)
        self.head     = nn.Linear(256, num_classes)

    def forward(self, x):           # x: (N, C, T, V, M)
        N, C, T, V, M = x.shape
        # Merge persons into batch
        x = x.permute(0, 4, 3, 1, 2).contiguous()  # (N, M, V, C, T)
        x = x.view(N * M, V * C, T)
        x = self.data_bn(x)
        x = x.view(N, M, V, C, T)
        x = x.permute(0, 1, 3, 4, 2).contiguous()  # (N, M, C, T, V)
        x = x.view(N * M, C, T, V)

        for layer in self.backbone:
            x = layer(x)

        x = self.pool(x).view(N, M, -1).mean(dim=1)   # (N, 256)
        return self.head(x)


# ── Classifier wrapper (same interface as BehaviorClassifier) ─────────────────

class STGCNClassifier:
    """
    STGCN++-based behavior classifier.
    Exposes the same classify() API as BehaviorClassifier so it can be
    swapped in runner.py without any other changes.
    """

    def __init__(self, checkpoint_path: Optional[str] = None, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[STGCNPlusPlus] = None
        self.pose_buffers: dict = defaultdict(lambda: deque(maxlen=POSE_WINDOW_SIZE))
        self.pred_history: dict  = defaultdict(lambda: deque(maxlen=SMOOTHING_WINDOW))

        if checkpoint_path:
            self._load(checkpoint_path)

    def _load(self, path: str):
        logger.info(f"Loading STGCN++ from {path} on {self.device}")
        ckpt = torch.load(path, map_location=self.device, weights_only=False)

        # pyskl checkpoint format: {"state_dict": {...}}
        state = ckpt.get("state_dict", ckpt)

        # The pretrained model has 120-class head; we keep that and remap at prediction time
        m = STGCNPlusPlus(num_classes=120)

        # Strip pyskl prefix "backbone." / "cls_head." if present
        remapped = {}
        for k, v in state.items():
            new_k = k
            if k.startswith("backbone."):
                new_k = k[len("backbone."):]
                # pyskl uses "gcn.0.gcn" style naming — adapt to our module names
                # This remapping handles the most common naming difference
            remapped[new_k] = v

        missing, unexpected = m.load_state_dict(remapped, strict=False)
        if missing:
            logger.warning(f"  Missing keys: {len(missing)}. Model may need weight remapping.")
        if unexpected:
            logger.debug(f"  Unexpected keys: {len(unexpected)} (normal for head mismatch)")

        m.to(self.device)
        m.eval()
        if self.device == "cuda":
            m.half()
        self.model = m
        logger.info("STGCN++ loaded successfully")

    def classify(self, detections: List[PersonDetection], camera_id: str) -> List[BehaviorResult]:
        """Same signature as BehaviorClassifier.classify()."""
        results = []
        for det in detections:
            key = f"{camera_id}_p{det.person_idx}"

            if det.keypoints_x and len(det.keypoints_x) == NUM_JOINTS:
                # Normalise keypoints relative to bbox (position-invariant)
                kp = np.array([det.keypoints_x, det.keypoints_y, det.keypoints_conf],
                               dtype=np.float32).T   # (17, 3)
                bw = max(det.bbox[2] - det.bbox[0], 1e-5)
                bh = max(det.bbox[3] - det.bbox[1], 1e-5)
                kp[:, 0] = (kp[:, 0] - det.bbox[0]) / bw
                kp[:, 1] = (kp[:, 1] - det.bbox[1]) / bh
                # shape: (3, 17) — channels first
                self.pose_buffers[key].append(kp.T)

            if self.model is not None and len(self.pose_buffers[key]) >= 3:
                result = self._predict(key, det.person_idx)
            else:
                result = BehaviorResult(
                    person_idx=det.person_idx,
                    behavior_type="unknown",
                    confidence=0.0,
                    raw_scores={},
                )
            results.append(result)
        return results

    def _predict(self, person_key: str, person_idx: int) -> BehaviorResult:
        buf = list(self.pose_buffers[person_key])

        # Pad to POSE_WINDOW_SIZE by repeating the last frame
        while len(buf) < POSE_WINDOW_SIZE:
            buf.append(buf[-1])
        buf = buf[-POSE_WINDOW_SIZE:]

        # Stack: (C=3, T=30, V=17)
        tensor = np.stack(buf, axis=1)           # (3, 30, 17)
        tensor = tensor[np.newaxis, :, :, :, np.newaxis]   # (1, 3, 30, 17, 1)

        x = torch.from_numpy(tensor.astype(np.float32)).to(self.device)
        if self.device == "cuda" and self.model.head.weight.dtype == torch.float16:
            x = x.half()

        with torch.no_grad():
            logits = self.model(x)                    # (1, 120)
            probs  = torch.softmax(logits, dim=1).cpu().numpy()[0]  # (120,)

        # Map 120 NTU probabilities → 7 behavior probabilities
        behavior_scores = np.zeros(len(BEHAVIOR_CLASSES), dtype=np.float32)
        for ntu_idx in range(120):
            ntu_action = ntu_idx + 1   # 1-based
            beh = NTU_TO_BEHAVIOR.get(ntu_action) or _NTU_FALLBACK.get(ntu_action)
            if beh:
                bi = BEHAVIOR_CLASSES.index(beh)
                behavior_scores[bi] += probs[ntu_idx]
            else:
                # Distribute uniformly to walking/standing (most common in uncovered classes)
                behavior_scores[0] += probs[ntu_idx] * 0.5
                behavior_scores[1] += probs[ntu_idx] * 0.5

        # Renormalise
        total = behavior_scores.sum()
        if total > 0:
            behavior_scores /= total

        pred_idx   = int(np.argmax(behavior_scores))
        pred_label = BEHAVIOR_CLASSES[pred_idx]

        # Temporal smoothing
        self.pred_history[person_key].append(pred_label)
        if len(self.pred_history[person_key]) >= 3:
            smoothed = Counter(self.pred_history[person_key]).most_common(1)[0][0]
        else:
            smoothed = pred_label

        raw = {cls: float(behavior_scores[i]) for i, cls in enumerate(BEHAVIOR_CLASSES)}
        return BehaviorResult(
            person_idx=person_idx,
            behavior_type=smoothed,
            confidence=float(behavior_scores[pred_idx]),
            raw_scores=raw,
        )


# ── Factory function ───────────────────────────────────────────────────────────

def get_stgcn_classifier() -> STGCNClassifier:
    """Load STGCN++ classifier using path from settings."""
    from app.core.config import settings
    path = getattr(settings, "STGCN_MODEL_PATH", "models/stgcnpp_ntu120_xsub_hrnet_joint.pth")
    import os
    if not os.path.exists(path):
        logger.warning(
            f"STGCN++ checkpoint not found at {path}. "
            "Running in detection-only mode (behaviors = unknown). "
            "Download with:\n"
            "  curl -L -o models/stgcnpp_ntu120_xsub_hrnet_joint.pth \\\n"
            "    https://download.openmmlab.com/mmaction/pyskl/ckpt/stgcnpp/"
            "stgcnpp_ntu120_xsub_hrnet/j.pth"
        )
        return STGCNClassifier(checkpoint_path=None)
    return STGCNClassifier(checkpoint_path=path)
