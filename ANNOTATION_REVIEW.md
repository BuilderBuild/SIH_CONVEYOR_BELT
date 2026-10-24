# Annotation and localization review queue

This review uses the original best.pt on the verified 31-image validation split, confidence .25, one-to-one box matching at IoU .5. It does not modify annotations. The owner-confirmed CVAT export remains the source of truth pending human review.

Structural audit and source matching prove that label files are valid and copied consistently; they do not prove that every box is a separate physical tear or that its extent is correct.

## Observed examples

The ground-truth/prediction comparisons for defected_5 and defected_59 were visually inspected. Multiple green ground-truth boxes overlap or nest around the same broad belt areas. Orange predictions sometimes identify a smaller region inside a much broader annotated region. Such boxes may fail IoU .5 even where the prediction is near visible damage. Some broad boxes include substantial glossy or wrinkled material, so a reviewer should check that each box tightly represents an actual tear/cut/rupture or missing material rather than a harmless surface variation.

These observations are reasons for review, not an automatic declaration that an annotation is wrong. No boxes were merged, resized, removed, or generated from predictions.

## Highest-error cases

| Validation image | GT boxes | Unmatched predictions (FP) | Unmatched GT boxes (FN) |
|---|---:|---:|---:|
| defected_8.jpeg | 8 | 8 | 8 |
| defected_5.jpeg | 8 | 4 | 8 |
| defected_70.jpeg | 9 | 5 | 6 |
| defected_73.jpeg | 9 | 3 | 8 |
| defected_50.jpeg | 10 | 4 | 6 |
| defected_59.jpeg | 11 | 2 | 8 |

An unmatched prediction is a box-level localization error under this matching rule, not proof of a separate false physical-damage alarm. Multiple unmatched annotations in one image are not necessarily multiple independently missed physical defects.

Review the actual green/orange comparisons in `outputs/reports/evaluation_20261024T024902_53c3bcf9/comparisons/` and the coordinates/confidences in that evaluation's `errors.json`. Original labels remain in `CVAT_DETECTED_YOLO/labels/train/`.

## Human review policy

1. Confirm visible physical damage first. Exclude harmless shadows, reflections, wrinkles, markings and ordinary texture.
2. Define a consistent unit: one box per clearly separable damaged region, with a stated policy for long tears and adjoining damaged material.
3. Review nested/overlapping boxes for repeated annotation of the same damage, and check extents against the actual damaged material.
4. If changes are warranted, export a new version from CVAT. Preserve existing exports and the current test set's history; do not silently replace them.
5. Acquire genuinely unseen belt images/video for a future acceptance set. The current small validation set and historical test images have already been examined.

The current continuation runs one experiment using the confirmed labels unchanged. More training cannot substitute for resolving semantic annotation ambiguity.
