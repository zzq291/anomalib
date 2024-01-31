"""Test SPRO metric."""

# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import torch

from anomalib.metrics.spro import SPRO


def test_spro() -> None:
    """Checks if SPRO metric computes the score utilizing the given saturation configs."""
    saturation_config = {
        255: {
            "saturation_threshold": 10,
            "relative_saturation": False,
        },
        254: {
            "saturation_threshold": 0.5,
            "relative_saturation": True,
        },
    }

    masks = torch.Tensor(
        [
            [
                [0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1],
            ],
            [
                [1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0],
            ],
        ],
    )

    masks[0] *= 255
    masks[1] *= 254
    # merge the multi-mask and add batch dim
    merged_masks = (masks[0] + masks[1]).unsqueeze(0)

    preds = (torch.arange(8) / 10) + 0.05
    # metrics receive squeezed predictions (N, H, W)
    preds = preds.unsqueeze(1).repeat(1, 5).view(1, 8, 5)

    thresholds = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    targets = [1.0, 1.0, 1.0, 0.75, 0.0, 0.0]
    targets_wo_saturation = [1.0, 0.625, 0.5, 0.375, 0.0, 0.0]
    for threshold, target, target_wo_saturation in zip(thresholds, targets, targets_wo_saturation, strict=True):
        # test using saturation_cofig
        spro = SPRO(threshold=threshold, saturation_config=saturation_config)
        spro.update(preds, None, merged_masks)
        assert spro.compute() == target

        # test without saturation_config
        spro_wo_saturaton = SPRO(threshold=threshold)
        spro_wo_saturaton.update(preds, None, merged_masks)
        assert spro_wo_saturaton.compute() == target_wo_saturation
