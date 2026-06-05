# Algorithm

This document describes the complete algorithmic pipeline used by **CurvInspect**.

While `math_background.md` explains the geometric concepts, this file focuses on the computational workflow: how an image is transformed into a polygonal curve, how inspection signals are built, how anomaly candidates are detected, and how outputs are generated.

---

## 1. High-Level Pipeline

CurvInspect follows a geometry-first inspection pipeline:

```text
Input image
    ↓
Image loading
    ↓
Preprocessing
    ↓
Main contour extraction
    ↓
Contour selection: raw or simplified
    ↓
Uniform boundary resampling
    ↓
Inspection signal construction
    ↓
Signal smoothing
    ↓
Robust anomaly detection
    ↓
Anomaly grouping and peak selection
    ↓
Visualization and JSON reporting
```

The main design goal is to keep the pipeline modular. Each stage can be tested, adjusted, and replaced independently.

---

## 2. Input

The input is an image containing an object whose boundary should be inspected.

Typical examples include:

- synthetic geometric parts,
- industrial-looking components,
- binary or near-binary object masks,
- simple objects on clean backgrounds,
- segmented objects from a larger computer vision pipeline.

The current pipeline works best when the object is visually separable from the background.

---

## 3. Image Loading

The image is loaded using OpenCV-compatible image I/O.

CurvInspect internally works with image arrays and supports grayscale or color images depending on the processing stage.

If the image cannot be loaded, the pipeline should fail early with a clear error.

---

## 4. Preprocessing

The purpose of preprocessing is to obtain a usable binary or edge-based representation of the object boundary.

CurvInspect supports two main contour extraction methods:

```text
threshold
canny
```

### 4.1 Threshold-Based Extraction

Thresholding is useful when the object and background have clear intensity separation.

Typical use case:

```bash
curvinspect analyze image.png --method threshold
```

If the object is darker than the background, the `--invert` option may be needed:

```bash
curvinspect analyze image.png --method threshold --invert
```

Thresholding is often more stable for clean synthetic or controlled images.

### 4.2 Canny-Based Extraction

Canny edge detection can be useful when the object boundary is defined by edges rather than filled regions.

Typical use case:

```bash
curvinspect analyze image.png --method canny
```

However, Canny may also detect internal texture, noise, shadows, or irrelevant edges. For geometric boundary inspection, this can make the contour noisier.

---

## 5. Main Contour Extraction

After preprocessing, CurvInspect extracts contours and selects the main contour according to area.

Very small contours are ignored using the `min_area` parameter:

```bash
--min-area 25.0
```

This avoids selecting tiny noise components.

The output of this stage is a `ContourExtractionResult`, which contains:

- raw contour points,
- simplified contour points,
- contour area,
- contour perimeter,
- contour metadata.

---

## 6. Raw vs Simplified Contour

CurvInspect can analyze either:

```text
raw
simplified
```

### 6.1 Raw Contour

The raw contour is closer to the pixel-level boundary.

Advantages:

- preserves small defects,
- useful for shallow chips,
- better for local chord-based inspection.

Disadvantages:

- more sensitive to noise,
- may produce many raw anomalous points.

Example:

```bash
--analysis-contour raw
```

### 6.2 Simplified Contour

The simplified contour is produced using contour simplification, typically with a Douglas-Peucker-style approach.

The simplification strength is controlled by:

```bash
--epsilon-ratio
```

Advantages:

- cleaner shape representation,
- better for high-level geometric analysis,
- reduces pixel-level fluctuations.

Disadvantages:

- may remove small defects,
- can hide shallow local boundary damage.

Example:

```bash
--analysis-contour simplified --epsilon-ratio 0.005
```

### 6.3 Practical Trade-Off

The choice between raw and simplified contours is important.

```text
raw contour        → more detail, more noise
simplified contour → cleaner, less detail
```

For real defect inspection, raw contours often preserve the important local irregularities. For clean geometric explanation, simplified contours may look better.

---

## 7. Uniform Resampling

Raw contour points are usually not evenly spaced. Some boundary regions may contain many points while others contain fewer.

CurvInspect resamples the selected contour into a fixed number of points:

```bash
--num-samples 700
```

This produces a closed polygonal curve:

```text
q_0, q_1, ..., q_{m-1}
```

with approximately uniform spacing along the boundary.

Uniform resampling is important because curvature and deviation values should be comparable across different parts of the contour.

---

## 8. Inspection Signal Construction

CurvInspect supports four inspection signal families:

```text
curvature
deviation
chord
combined
```

The selected signal is controlled by:

```bash
--inspection-signal
```

---

## 9. Curvature Signal

The curvature signal is based on discrete turning angles.

For each vertex, CurvInspect computes:

```text
incoming tangent
outgoing tangent
signed turning angle
local arc-length scale
discrete curvature
```

The approximate discrete curvature is:

```math
kappa_i ≈ theta_i / Delta_s_i
```

Available curvature modes:

```text
signed
absolute
positive
negative
convex
concave
```

Example:

```bash
--inspection-signal curvature --curvature-mode absolute
```

Curvature is especially effective for:

- sharp corners,
- notches,
- strong local turns,
- concave dents when using concave mode.

---

## 10. Deviation Signal

The deviation signal compares the original curve to a smoothed reference curve.

The smoothing window is controlled by:

```bash
--deviation-window
```

The method computes how far each original point is displaced from the smoothed reference curve along local normal directions.

Available deviation modes:

```text
signed
absolute
positive
negative
```

Example:

```bash
--inspection-signal deviation --deviation-mode absolute --deviation-window 41
```

Deviation can be useful when the boundary departs from the general local trend but does not necessarily create a sharp corner.

---

## 11. Chord Deviation Signal

The chord signal is based on local chord deviation.

For each point `p_i`, CurvInspect compares it with the chord connecting two wider-neighborhood points:

```text
p_{i-k} and p_{i+k}
```

The parameter `k` is controlled by:

```bash
--chord-step
```

Example:

```bash
--inspection-signal chord --chord-step 25
```

Chord deviation is useful for:

- shallow chips,
- local edge damage,
- defects along nearly straight edges,
- irregularities that curvature alone may miss.

This signal was especially useful in practical testing because some shallow boundary defects did not produce strong curvature peaks but were captured by chord deviation.

---

## 12. Combined Signal

The combined signal merges several normalized geometric signals:

```text
curvature response
normal deviation response
chord deviation response
```

Each signal is normalized, and the final signal keeps the strongest response at each boundary point.

Conceptually:

```text
combined = max(normalized_curvature, normalized_deviation, normalized_chord)
```

Example:

```bash
--inspection-signal combined
```

Combined mode is useful when the boundary may contain several types of irregularities.

---

## 13. Signal Smoothing

After the inspection signal is computed, it can be smoothed.

Supported smoothing modes:

```text
none
median
moving_average
```

Example:

```bash
--smoothing median --smoothing-window 11
```

### 13.1 Median Smoothing

Median smoothing is useful for suppressing isolated spikes while preserving stronger local structures.

### 13.2 Moving Average

Moving average smoothing produces a smoother signal but may blur sharp responses.

### 13.3 No Smoothing

No smoothing preserves the raw signal but can be noisy.

---

## 14. Robust Anomaly Detection

CurvInspect detects unusually high responses using robust anomaly scoring.

Instead of relying only on the mean and standard deviation, robust statistics are used so that large signal spikes do not overly distort the baseline.

The detector produces:

- raw anomalous indices,
- anomaly groups,
- representative peak indices,
- anomaly scores.

The threshold is controlled by:

```bash
--threshold
```

Lower threshold:

```text
more sensitive, more detections
```

Higher threshold:

```text
stricter, fewer detections
```

---

## 15. Grouping Raw Anomaly Points

Raw anomaly points are often clustered. Instead of displaying every raw point as a final detection, CurvInspect groups nearby anomalous samples.

For each group, it selects a representative peak point.

This is why CurvInspect produces two overlay types:

```text
overlay.png
overlay_debug.png
```

### `overlay.png`

Shows representative peak points only.

### `overlay_debug.png`

Shows both raw anomalous samples and representative peak points.

This helps distinguish between two situations:

1. The signal never detected the region.
2. The signal detected the region, but grouping selected a different representative point.

---

## 16. Output Generation

Each analysis run produces:

```text
overlay.png
overlay_debug.png
curvature_signal.png
anomaly_report.json
```

### 16.1 Overlay

The overlay shows the analyzed contour and representative anomaly regions.

### 16.2 Debug Overlay

The debug overlay shows raw anomalous points and selected peak points.

This is useful for algorithm debugging and parameter tuning.

### 16.3 Signal Plot

The signal plot visualizes the processed inspection signal and selected anomaly peaks.

The file name is currently:

```text
curvature_signal.png
```

For backward compatibility, the name is kept even when the plotted signal is deviation, chord deviation, or combined.

### 16.4 JSON Report

The JSON report stores:

- input image metadata,
- contour area and perimeter,
- number of original contour points,
- number of resampled points,
- curvature statistics,
- bending energy,
- total curvature,
- anomaly indices,
- anomaly groups,
- selected peak indices,
- inspection settings,
- output file paths.

---

## 17. Presets

CurvInspect includes presets as practical starting configurations.

A preset is not a fixed mode. Users can override any parameter manually.

Example:

```bash
curvinspect analyze image.png --preset industrial-chord
```

Override example:

```bash
curvinspect analyze image.png --preset industrial-chord --chord-step 35 --threshold 2.2
```

This design allows the project to be both easy to use and flexible.

---

## 18. Recommended Preset: Industrial Chord

For shallow local edge defects, a useful configuration is:

```bash
curvinspect analyze examples/input/real/object_04.png \
  --output examples/output/real/object_04_chord_tuned_1 \
  --method threshold \
  --analysis-contour raw \
  --inspection-signal chord \
  --chord-mode absolute \
  --chord-step 25 \
  --num-samples 700 \
  --smoothing median \
  --smoothing-window 11 \
  --threshold 1.9
```

This configuration uses:

```text
raw contour        → preserves subtle boundary details
chord signal       → detects local departures from edge trend
chord_step = 25    → medium-scale local comparison
median smoothing   → reduces noise
threshold = 1.9    → balances sensitivity and cleanliness
```

---

## 19. Parameter Tuning Guide

### `num_samples`

Controls the number of boundary points after resampling.

Higher values preserve more detail but may increase sensitivity to noise.

Typical values:

```text
300 to 700
```

### `threshold`

Controls anomaly sensitivity.

```text
lower threshold → more detections
higher threshold → fewer detections
```

### `chord_step`

Controls the scale of local chord comparison.

```text
small chord_step → fine defects
large chord_step → broader defects
```

### `smoothing_window`

Controls signal smoothing.

```text
small window → more sensitive
large window → smoother and cleaner
```

### `epsilon_ratio`

Controls contour simplification.

```text
small epsilon_ratio → more detail
large epsilon_ratio → stronger simplification
```

---

## 20. Pseudocode

The main analysis pipeline can be summarized as follows:

```text
function analyze_image(image_path, output_dir, options):

    image = read_image(image_path)

    contour = extract_main_contour(
        image,
        method=options.method,
        invert=options.invert,
        min_area=options.min_area,
        epsilon_ratio=options.epsilon_ratio
    )

    if options.analysis_contour == "raw":
        points = contour.raw_points
    else:
        points = contour.simplified_points

    resampled = resample_closed_curve(
        points,
        num_samples=options.num_samples
    )

    signal = build_inspection_signal(
        resampled,
        inspection_signal=options.inspection_signal,
        curvature_mode=options.curvature_mode,
        deviation_mode=options.deviation_mode,
        chord_mode=options.chord_mode,
        deviation_window=options.deviation_window,
        chord_step=options.chord_step
    )

    processed_signal = smooth_signal(
        signal,
        method=options.smoothing,
        window_size=options.smoothing_window
    )

    anomalies = detect_anomalies(
        processed_signal,
        threshold=options.threshold
    )

    save_overlay(image, resampled, anomalies.peak_indices)
    save_debug_overlay(image, resampled, anomalies.indices, anomalies.peak_indices)
    save_signal_plot(processed_signal, anomalies.peak_indices)
    save_json_report(contour, signal, anomalies, options)

    return analysis_result
```

---

## 21. Complexity

Let:

```text
n = number of contour points
m = number of resampled points
```

Most stages are linear in the number of points.

Typical complexity:

```text
contour extraction: image-dependent
resampling: O(n + m)
curvature signal: O(m)
deviation signal: O(m × window) for simple moving average implementation
chord signal: O(m)
anomaly detection: O(m)
visualization: O(m)
```

For typical images and moderate values of `num_samples`, the pipeline is lightweight.

---

## 22. Failure Modes

CurvInspect may perform poorly when:

- the object is not clearly separated from the background,
- the selected contour is not the intended object boundary,
- the image contains shadows or internal edges,
- the contour is too noisy,
- the defect is too subtle compared to segmentation noise,
- the parameter scale does not match the size of the defect,
- the shape contains intended geometric details that look like anomalies.

These are expected limitations of a geometry-based contour inspection system.

---

## 23. Interpretation

CurvInspect should be interpreted as a candidate generator.

It answers:

> Where does the boundary show unusual geometric behavior?

It does not automatically answer:

> Is this definitely a real-world defect?

That final interpretation depends on:

- domain knowledge,
- reference shapes,
- imaging setup,
- tolerances,
- and the application context.

---

## 24. Summary

The algorithmic contribution of CurvInspect is the integration of several curve-based geometric signals into a modular inspection pipeline:

```text
discrete curvature
+ normal deviation
+ local chord deviation
+ robust anomaly grouping
```

This makes the project suitable for both educational demonstrations of discrete differential geometry and practical boundary irregularity inspection.
