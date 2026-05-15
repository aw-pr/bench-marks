# Task Brief — EXAMPLE-001

> **THIS IS AN EXAMPLE. It is illustrative only and does not represent real benchmark data.**

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | EXAMPLE-001 |
| Date | 2026-05-15 |
| Source repo | standalone |
| Source issue / PR | n/a |
| Tools to run | claude, codex, cursor, gemini |

---

## Spec

Implement a single deterministic Gray-Scott reaction-diffusion step function in Python.

Gray-Scott models two chemical species U and V on a 2-D grid. At each time step, the concentrations are updated according to:

```
dU/dt = Du * laplacian(U) - U*V^2 + F*(1 - U)
dV/dt = Dv * laplacian(V) + U*V^2 - (F + k)*V
```

Where:
- `Du`, `Dv` are diffusion rates
- `F` is the feed rate
- `k` is the kill rate
- The Laplacian is computed using a 2-D discrete convolution with a 5-point stencil and periodic boundary conditions

**Required signature:**

```python
def gray_scott_step(
    U: np.ndarray,   # shape (H, W), dtype float64
    V: np.ndarray,   # shape (H, W), dtype float64
    Du: float,
    Dv: float,
    F: float,
    k: float,
    dt: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (U_new, V_new) after one Euler step."""
```

Use NumPy only — no SciPy, no external dependencies.

---

## Constraints

- NumPy only. No SciPy `convolve2d` or `laplace`.
- Periodic boundary conditions (wrap-around at edges).
- Must be deterministic: same inputs always produce same outputs.
- No in-place mutation of the input arrays.
- The function must be importable and runnable without a display environment.

---

## Definition of done

- [ ] Function signature matches exactly.
- [ ] Laplacian uses a 5-point stencil with periodic boundaries via `np.roll`.
- [ ] Running 1000 steps from a standard initial condition (centre blob of V) produces a `V.max()` value in the range [0.3, 0.7] for parameters `Du=0.16, Dv=0.08, F=0.035, k=0.060`.
- [ ] No mutation of input arrays (verified by checking U and V are unchanged after call).
- [ ] Passes a basic type-check: return value is a tuple of two float64 arrays with the same shape as inputs.

---

## Context paste

No additional context required. The spec above is self-contained.

---

## Notes for the scorer

Boundary condition handling is a common failure point. Watch for tools that use zero-padding instead of wrap-around, or that use `scipy.ndimage.laplace` despite the constraint. The determinism check is straightforward; the range check on `V.max()` after 1000 steps is the real correctness signal.
