# Mathematical Background

This document explains the geometric ideas behind **CurvInspect**.

CurvInspect is based on a simple but powerful idea:

> A digital object boundary can be modeled as a closed polygonal curve, and geometric irregularities can be studied through discrete curvature and related curve-based signals.

The goal of this document is not only to describe the formulas used in the code, but also to explain why these formulas are meaningful from the point of view of differential geometry and discrete geometry.

---

## 1. From Smooth Curves to Digital Boundaries

In classical differential geometry, a planar curve is often represented by a smooth parametrization

$$
\gamma : I \to \mathbb{R}^2.
$$

If the curve is parametrized by arc length $s$, then the unit tangent vector is

$$
T(s) = \frac{d\gamma}{ds}.
$$

The curvature of the smooth curve is defined by

$$
\kappa(s) = \left\|\frac{dT}{ds}\right\|.
$$

This definition measures how quickly the tangent direction changes as we move along the curve.

However, in a digital image, the boundary of an object is not given as a smooth curve. It is given as a finite sequence of contour points extracted from pixels. Therefore, CurvInspect replaces the smooth curve with a **polygonal curve**.

---

## 2. Polygonal Curve Model

A closed object boundary is modeled as a sequence of points

$$
p_0, p_1, \ldots, p_{n-1} \in \mathbb{R}^2,
$$

with the convention that

$$
p_n = p_0.
$$

This forms a closed polygonal curve.

The edge vectors are

$$
e_i = p_{i+1} - p_i,
$$

where indices are interpreted cyclically for a closed curve.

The edge lengths are

$$
\ell_i = \|e_i\|.
$$

A unit tangent along edge $i$ is then

$$
T_i = \frac{e_i}{\|e_i\|}.
$$

This is the discrete analogue of the tangent vector of a smooth curve.

---

## 3. Signed Turning Angle

At each vertex $p_i$, the curve changes direction from the previous edge to the next edge.

Let $T_{i-1}$ be the incoming unit tangent and $T_i$ be the outgoing unit tangent.

The signed turning angle is computed using

$$
\theta_i =
\mathrm{atan2}
\left(
\mathrm{det}(T_{i-1}, T_i),
T_{i-1} \cdot T_i
\right).
$$

Here,

$$
\mathrm{det}(T_{i-1}, T_i)
=
T_{i-1}^{(x)}T_i^{(y)}
-
T_{i-1}^{(y)}T_i^{(x)}.
$$

The dot product measures alignment, while the determinant measures oriented area and therefore direction of rotation.

Using `atan2` is important because it gives a signed angle in a numerically stable way.

A positive angle indicates one orientation of turning, and a negative angle indicates the opposite orientation. For closed contours, this sign can be used to distinguish convex and concave behavior after normalizing by the dominant orientation of the curve.

---

## 4. Local Arc-Length Scale

For a smooth curve, curvature is the rate of change of the tangent vector with respect to arc length.

For a polygonal curve, the local arc-length scale around vertex $p_i$ is approximated by averaging the lengths of the adjacent edges:

$$
\Delta s_i =
\frac{\|e_{i-1}\| + \|e_i\|}{2}.
$$

This gives a local length scale around the vertex.

---

## 5. Discrete Curvature

The discrete curvature at vertex $p_i$ is approximated by

$$
\kappa_i \approx \frac{\theta_i}{\Delta s_i}.
$$

This formula is the discrete analogue of

$$
\kappa = \frac{d\theta}{ds},
$$

where $\theta$ is the tangent angle.

In CurvInspect, both signed and absolute forms of curvature are useful.

Signed curvature:

$$
\kappa_i = \frac{\theta_i}{\Delta s_i}.
$$

Absolute curvature:

$$
|\kappa_i|.
$$

The absolute value is useful when the goal is to detect regions with strong bending regardless of direction.

---

## 6. Total Signed Turning

For a simple closed polygonal curve, the sum of signed turning angles is theoretically close to

$$
\sum_i \theta_i = \pm 2\pi.
$$

The sign depends on the orientation of the curve.

This is a discrete version of the classical turning tangent theorem, which states that the tangent direction of a simple closed curve rotates once around the origin.

CurvInspect uses this idea to reason about the dominant turning orientation of a closed contour.

---

## 7. Total Curvature

The total curvature of a polygonal curve is defined as

$$
K_{\mathrm{total}} =
\sum_i |\theta_i|.
$$

Unlike total signed turning, total curvature measures the total amount of bending without cancellation between positive and negative turns.

For a convex closed curve, total curvature is close to

$$
2\pi.
$$

For a more complex boundary with dents, notches, or oscillations, total curvature can be larger.

---

## 8. Discrete Bending Energy

A useful curvature-based shape descriptor is bending energy.

For a smooth curve, bending energy is often written as

$$
E = \int \kappa(s)^2 \, ds.
$$

CurvInspect approximates this in the discrete setting as

$$
E \approx
\sum_i \kappa_i^2 \Delta s_i.
$$

This value increases when the boundary contains strong or frequent bending.

Bending energy is not used alone as the final detector, but it is useful as a global geometric summary of the contour.

---

## 9. Convex and Concave Curvature

For a closed curve, most vertices of a simple convex boundary share the same turning sign.

CurvInspect computes the dominant orientation of the closed contour using the total signed turning. After orientation normalization:

- positive curvature tends to represent convex turning,
- negative curvature tends to represent concave turning.

This allows the project to form specialized signals such as:

```text
convex
concave
```

A concave curvature signal is useful for detecting inward notches or dents, but it is not sufficient for every type of boundary defect. For example, a missing corner may still be geometrically convex along its new boundary.

---

## 10. Why Resampling Is Necessary

Raw image contours often have irregular point spacing. Some parts of the boundary may contain many pixel points, while others contain fewer.

If curvature is computed directly on such uneven data, the result can be unstable.

CurvInspect therefore resamples the contour approximately uniformly by arc length.

The goal is to obtain a sequence

$$
q_0, q_1, \ldots, q_{m-1}
$$

such that consecutive points are more evenly spaced along the boundary.

This makes curvature and deviation signals more comparable across the whole contour.

---

## 11. Raw vs Simplified Contours

CurvInspect supports two analysis contour types.

### Raw contour

The raw contour preserves small details.

Advantages:

- better for small chips,
- better for shallow defects,
- preserves fine local geometry.

Disadvantages:

- more sensitive to segmentation noise,
- may require smoothing or stricter thresholds.

### Simplified contour

The simplified contour removes small-scale boundary fluctuations.

Advantages:

- cleaner and more stable,
- useful for high-level shape analysis,
- reduces pixel-level noise.

Disadvantages:

- may remove subtle defects.

This creates an important trade-off:

> Raw contours preserve local detail, while simplified contours produce cleaner but less sensitive geometry.

---

## 12. Smoothed Normal Deviation

Discrete curvature detects rapid changes in tangent direction. However, not every important boundary irregularity produces a strong curvature peak.

CurvInspect therefore includes a smoothed normal deviation signal.

First, the original curve is smoothed to produce a reference curve:

$$
\widetilde{p}_i.
$$

Then, local tangents and normals are estimated on the smoothed curve.

Let $N_i$ be a unit normal vector at the smoothed reference point $\widetilde{p}_i$.

The displacement between the original and smoothed curve is

$$
d_i = p_i - \widetilde{p}_i.
$$

The signed normal deviation is

$$
\delta_i = d_i \cdot N_i.
$$

The absolute normal deviation is

$$
|\delta_i|.
$$

This signal measures how far the original boundary locally departs from a smoother version of itself.

---

## 13. Local Chord Deviation

Some defects are shallow and occur on nearly straight edges. These may not produce a very strong curvature peak.

To address this, CurvInspect includes local chord deviation.

For each point $p_i$, choose a scale parameter $k$. The method considers the chord connecting $p_{i-k}$ and $p_{i+k}$.

The point $p_i$ is compared to this chord.

Let

$$
a_i = p_{i-k},
\qquad
b_i = p_{i+k}.
$$

Define the chord direction

$$
u_i =
\frac{b_i - a_i}{\|b_i - a_i\|}.
$$

The signed perpendicular distance from $p_i$ to the chord is computed by a two-dimensional cross-product expression:

$$
c_i =
\mathrm{det}(u_i, p_i - a_i).
$$

The absolute chord deviation is

$$
|c_i|.
$$

This signal is scale-dependent. The parameter $k$, called `chord_step` in the CLI, controls the neighborhood size.

Small values of $k$ detect finer irregularities. Larger values of $k$ detect broader deviations.

---

## 14. Relation Between Chord Deviation and Curvature

For a smooth curve, the sagitta of a short arc is related to curvature.

If a curve segment has chord length $L$ and approximately constant curvature $\kappa$, then the sagitta is approximately

$$
h \approx \frac{\kappa L^2}{8}.
$$

This means local chord deviation is not unrelated to curvature. It can be understood as a scale-dependent geometric descriptor of how far the curve departs from a local straight chord.

This is why chord deviation remains consistent with the geometric theme of the project.

---

## 15. Detection Signal and Robust Scores

After building an inspection signal, CurvInspect detects unusually strong responses.

A robust anomaly score is computed from the signal using robust statistics rather than only mean and standard deviation.

Conceptually, the score measures how far a signal value is from a typical signal level.

A common robust form is based on the median and median absolute deviation:

$$
z_i =
\frac{x_i - \mathrm{median}(x)}
{\mathrm{MAD}(x) + \varepsilon}.
$$

Large values of this score indicate unusually strong boundary responses.

CurvInspect then groups nearby anomalous samples and selects representative peak points.

This is why the project exports both:

- `overlay.png`, showing representative peak regions,
- `overlay_debug.png`, showing raw anomalous points and grouped peak points.

---

## 16. Interpretation of Results

A detected region should be interpreted as a **geometric irregularity candidate**.

It may correspond to:

- a true defect,
- a designed corner,
- a natural shape feature,
- segmentation noise,
- or an artifact of image acquisition.

CurvInspect does not claim to determine semantic defects by itself. Instead, it provides a geometry-based analysis layer.

In industrial use, this should be combined with:

- controlled imaging,
- domain-specific thresholds,
- reference shapes,
- and validation data.

---

## 17. Why This Belongs to Differential Geometry

Although CurvInspect works with images and code, the central ideas come directly from the geometry of curves:

| Smooth Geometry | Discrete CurvInspect Version |
|---|---|
| Smooth curve $\gamma(s)$ | Polygonal contour $p_i$ |
| Tangent vector $T(s)$ | Edge unit tangent $T_i$ |
| Curvature $\kappa = \|dT/ds\|$ | Turning angle divided by local arc length |
| Arc length $ds$ | Edge-length-based local scale $\Delta s_i$ |
| Total curvature | Sum of absolute turning angles |
| Bending energy | Sum of $\kappa_i^2 \Delta s_i$ |
| Normal direction | Estimated normal of a smoothed discrete curve |
| Local curve deviation | Normal and chord-based deviation signals |

Therefore, the project is not merely an image-processing script. It is an applied implementation of differential-geometric ideas in the discrete digital setting.

---

## 18. Summary

CurvInspect uses the following geometric chain:

```text
image boundary
    ↓
closed polygonal curve
    ↓
discrete tangent and turning angle
    ↓
discrete curvature
    ↓
optional deviation and chord-based signals
    ↓
robust anomaly candidate detection
```

The most important mathematical idea is the translation of smooth curvature into a discrete polygonal setting.

The practical contribution is showing how this idea can be used for real digital boundary inspection.
