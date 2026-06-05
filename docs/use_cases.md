# Use Cases

This document explains where **CurvInspect** can be useful, how to interpret its outputs, and which settings are recommended for different practical scenarios.

CurvInspect is a geometry-driven toolkit. It does not try to classify objects semantically. Instead, it analyzes **boundary geometry** and identifies candidate regions where the contour behaves unusually.

The central question CurvInspect answers is:

> Where does this boundary show unusual geometric behavior?

Depending on the application, those regions may correspond to defects, natural features, design details, or noise.

---

## 1. Educational Use in Differential Geometry

CurvInspect can be used as an applied project for a Differential Geometry or Discrete Geometry course.

It demonstrates how abstract concepts such as curvature, tangent direction, turning angle, and arc length can be translated into a computational pipeline.

### Relevant Concepts

CurvInspect connects directly to:

- planar curves,
- arc-length parametrization,
- tangent vectors,
- curvature,
- signed turning angle,
- total curvature,
- bending energy,
- polygonal approximations of smooth curves.

### Why This Is Educationally Valuable

A common challenge in learning differential geometry is understanding how smooth formulas behave in real or digital data.

CurvInspect makes this connection explicit:

```text
smooth curve
    ↓
sampled boundary
    ↓
polygonal curve
    ↓
discrete tangent
    ↓
turning angle
    ↓
discrete curvature
```

This makes it suitable for:

- course presentations,
- computational geometry assignments,
- visual demonstrations,
- applied mathematics projects,
- student GitHub portfolios.

### Recommended Command

```bash
curvinspect demo
```

This generates synthetic examples and shows how geometric irregularities affect the boundary inspection signal.

---

## 2. Boundary Defect Candidate Detection

One of the strongest practical use cases is detecting **candidate boundary defects** on objects.

Examples include:

- chipped parts,
- broken corners,
- local dents,
- notches,
- damaged edges,
- unexpected boundary deviations.

CurvInspect is especially useful when the defect is visible mainly through the shape of the object's boundary.

### Recommended Signal

For sharp notches or strong angular changes:

```bash
--inspection-signal curvature
```

For shallow local edge defects:

```bash
--inspection-signal chord
```

For mixed irregularities:

```bash
--inspection-signal combined
```

### Recommended Command

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

### Interpretation

If CurvInspect marks a region on the boundary, it should be interpreted as a **candidate irregularity**, not an automatic proof of defect.

A domain expert or a reference part may still be needed to determine whether the region is truly defective.

---

## 3. Industrial Quality Inspection Prototype

CurvInspect can be used as a prototype for boundary-based quality inspection.

It is most suitable when:

- the object has a clear silhouette,
- the boundary is important for quality,
- the camera setup is controlled,
- the object is separated from the background,
- defects appear as changes in boundary geometry.

### Possible Industrial Examples

- metal plates,
- plastic parts,
- ceramic tiles,
- cut sheets,
- molded components,
- packaging edges,
- manufactured silhouettes.

### Recommended Presets

For general industrial inspection:

```bash
curvinspect analyze image.png --preset industrial-chord
```

For cleaner and stricter results:

```bash
curvinspect analyze image.png --preset industrial-chord-strict
```

For manual override:

```bash
curvinspect analyze image.png --preset industrial-chord \
  --chord-step 35 \
  --threshold 2.2
```

### Practical Notes

Industrial use requires careful calibration:

- consistent lighting,
- clean segmentation,
- stable camera distance,
- known tolerances,
- validation on real samples,
- comparison against accepted and rejected parts.

CurvInspect is not a complete industrial inspection system by itself. It is a geometric analysis module that could become part of a larger inspection pipeline.

---

## 4. Robotics and Shape-Based Perception

Robots often need to reason about object boundaries.

CurvInspect can support geometry-based perception tasks such as:

- identifying grasp-relevant boundary features,
- locating corners or notches,
- detecting irregular object silhouettes,
- comparing object outlines,
- inspecting parts before manipulation.

### Example Scenario

A robotic arm needs to pick a flat object. Boundary irregularities may affect grasp planning. CurvInspect can highlight local regions where the boundary shape changes strongly.

### Useful Signals

For detecting grasp-relevant corners:

```bash
--inspection-signal curvature
```

For detecting subtle boundary deviations:

```bash
--inspection-signal chord
```

### Important Limitation

CurvInspect does not estimate pose, depth, or physical stability. It only analyzes 2D boundary geometry.

For robotics, it should be combined with:

- depth sensing,
- pose estimation,
- object recognition,
- motion planning,
- grasp evaluation.

---

## 5. Computer Vision Preprocessing

CurvInspect can be used as a preprocessing tool in a larger computer vision system.

Instead of feeding only raw images into a model, one can extract boundary geometry features such as:

- maximum curvature,
- mean curvature,
- total curvature,
- bending energy,
- number of anomaly regions,
- anomaly peak locations,
- chord deviation responses.

These features can be used for:

- classical machine learning,
- quality scoring,
- shape classification,
- anomaly candidate filtering,
- dataset labeling assistance.

### Example Output

The `anomaly_report.json` file contains structured information that can be used downstream.

Example fields include:

```text
contour area
contour perimeter
number of resampled points
maximum absolute curvature
mean absolute curvature
bending energy
total curvature
anomaly indices
anomaly groups
inspection signal settings
```

This makes CurvInspect useful not only as a visual tool, but also as a feature extraction module.

---

## 6. Digital Geometry and Shape Analysis

CurvInspect is useful for studying digital shapes as geometric objects.

A digital contour can be analyzed through:

- edge directions,
- turning angles,
- local curvature,
- curve smoothing,
- local chord deviation,
- total curvature,
- geometric energy.

This is relevant to:

- digital geometry,
- computational geometry,
- shape analysis,
- mathematical image processing,
- contour-based object representation.

### Example Questions

CurvInspect can help explore questions such as:

- Which parts of a digital contour bend the most?
- How does contour simplification affect curvature?
- How does resampling change the stability of curvature estimates?
- Which boundary regions are geometrically unusual?
- How do different signal scales detect different types of features?

---

## 7. Computer Graphics and Mesh-Like Boundary Analysis

Although CurvInspect currently works with 2D contours, the underlying idea is related to geometry processing.

In computer graphics, shape boundaries and curves are often analyzed using curvature-like quantities.

Potential connections include:

- curve fairing,
- silhouette analysis,
- shape smoothing,
- boundary feature detection,
- stylized contour extraction,
- vectorization quality control.

### Example Use

A designer or graphics tool could use boundary curvature to identify visually sharp features or irregularities in a vectorized shape.

### Limitation

CurvInspect is not currently a full vector graphics or mesh processing tool. It operates on image-extracted 2D contours.

---

## 8. Medical or Biological Shape Analysis

CurvInspect may be useful as a research prototype for analyzing biological shapes where the boundary is meaningful.

Possible examples:

- cell boundaries,
- leaf outlines,
- organ silhouettes,
- microscopic object contours,
- growth pattern boundaries.

However, these domains require special care.

### Why Care Is Needed

In biological shapes, boundary irregularities may be natural features rather than defects.

For example, a leaf may have many high-curvature serrations. CurvInspect may detect them as irregular regions, but that does not mean they are defects.

### Recommended Interpretation

In biological use cases, CurvInspect should be interpreted as a **shape descriptor tool**, not a defect detector.

---

## 9. Dataset Exploration and Annotation Support

CurvInspect can help during dataset exploration.

For example, when building a dataset of defective and non-defective parts, CurvInspect can:

- generate candidate regions,
- help visualize boundary irregularities,
- assist manual labeling,
- identify suspicious images,
- produce reports for comparison.

### Workflow Example

```text
collect images
    ↓
run CurvInspect
    ↓
inspect overlay_debug.png
    ↓
label candidate regions manually
    ↓
build dataset or benchmark
```

This can speed up dataset preparation without replacing human judgment.

---

## 10. Comparing Inspection Signals

CurvInspect is useful for comparing different geometric signals.

For the same image, one can run:

```bash
curvinspect analyze image.png --inspection-signal curvature
```

```bash
curvinspect analyze image.png --inspection-signal deviation
```

```bash
curvinspect analyze image.png --inspection-signal chord
```

```bash
curvinspect analyze image.png --inspection-signal combined
```

This allows users to study how different boundary features are emphasized by different geometric descriptors.

### Typical Behavior

| Signal | Best For | Possible Weakness |
|---|---|---|
| Curvature | sharp turns and notches | may miss shallow edge defects |
| Deviation | broader boundary displacement | may be too global for small defects |
| Chord | local edge defects and chips | can be sensitive to scale |
| Combined | mixed irregularities | may need careful threshold tuning |

---

## 11. Parameter Tuning Use Case

CurvInspect is designed to support experimentation.

Important parameters include:

### `threshold`

Controls detection sensitivity.

```text
lower threshold → more candidate regions
higher threshold → fewer candidate regions
```

### `chord_step`

Controls the scale of local chord comparison.

```text
small chord_step → detects small-scale irregularities
large chord_step → detects broader deviations
```

### `smoothing_window`

Controls how aggressively the signal is smoothed.

```text
smaller window → more sensitive
larger window → cleaner signal
```

### `analysis_contour`

Controls whether the raw or simplified boundary is analyzed.

```text
raw → preserves detail
simplified → cleaner but may remove subtle defects
```

This makes CurvInspect useful for teaching not only geometry, but also experimental algorithm design.

---

## 12. Suggested Workflows

### 12.1 Clean Object With Smooth Boundary

Use:

```bash
curvinspect analyze image.png --preset smooth-shape
```

Good for:

- circular objects,
- caps,
- rounded silhouettes,
- smooth manufactured parts.

### 12.2 Object With Sharp Corners

Use:

```bash
curvinspect analyze image.png --preset general-curvature
```

Good for:

- polygons,
- rectangular parts,
- objects with expected corners.

### 12.3 Object With Inward Notches

Use:

```bash
curvinspect analyze image.png --preset concave-notch
```

Good for:

- dents,
- inward cuts,
- notch-like boundary features.

### 12.4 Object With Shallow Edge Defects

Use:

```bash
curvinspect analyze image.png --preset industrial-chord
```

or the stricter version:

```bash
curvinspect analyze image.png --preset industrial-chord-strict
```

Good for:

- chipped edges,
- shallow missing material,
- local boundary damage.

---

## 13. What CurvInspect Is Not

CurvInspect is not:

- a complete industrial inspection platform,
- a trained machine-learning classifier,
- a semantic defect detector,
- a replacement for domain-specific validation,
- a universal solution for every shape.

It is a geometry-based boundary analysis toolkit.

This distinction is important because geometric irregularity does not always mean real-world defect.

---

## 14. Recommended README Example

For the main GitHub README, the recommended visual example is:

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

Recommended files to copy into `docs/assets`:

```text
docs/assets/object_04_input.png
docs/assets/object_04_overlay.png
docs/assets/object_04_overlay_debug.png
docs/assets/object_04_signal.png
```

This gives the project a concrete visual demonstration.

---

## 15. Summary

CurvInspect is useful when the boundary of an object matters.

Its strongest use cases are:

- educational demonstrations of discrete curvature,
- boundary defect candidate detection,
- industrial inspection prototypes,
- robotics shape perception,
- computer vision preprocessing,
- digital geometry experiments,
- shape analysis and dataset annotation support.

The key idea across all use cases is the same:

> Model the object boundary as a polygonal curve, compute geometric signals, and identify regions with unusual boundary behavior.

CurvInspect provides a practical and extensible way to apply differential-geometric thinking to digital and computational problems.
