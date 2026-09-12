# Geospatial AI & Hydrological Modeling Algorithms

This document formalizes the mathematical, remote-sensing, and hydraulic foundations powering **FloodTwin Responder**.

---

## 1. Sentinel-1 SAR Dual-Temporal Water Extraction

Synthetic Aperture Radar (SAR) sensors operate in the microwave spectrum (C-band $\approx 5.405\text{ GHz}, \lambda \approx 5.5\text{ cm}$), allowing unobstructed penetration through dense storm cloud covers, torrential monsoonal precipitation, and darkness.

### 1.1 Physical Scattering Mechanics
- **Specular Reflection**: Open, calm water behaves as a smooth specular mirror. Transmitted radar pulses reflect away from the sensor's antenna aperture, yielding very low normalized radar cross-section (NRCS) backscatter ($\sigma^0 \in [-24\text{ dB}, -17\text{ dB}]$ in VV / VH polarizations).
- **Diffuse Backscatter**: Rough, dry soil, urban structures, and vegetative canopies generate volume or double-bounce diffuse scattering, returning higher energy ($\sigma^0 \in [-13\text{ dB}, -6\text{ dB}]$).

### 1.2 Lee Adaptive Speckle Reduction Filter
To suppress multiplicative speckle noise without blurring sharp flood inundation boundaries, we compute the local variance $\text{Var}(x)$ over a $(2k+1) \times (2k+1)$ sliding kernel:

$$W = \max\left(0, \frac{\text{Var}(x) - \sigma_{\text{noise}}^2}{\text{Var}(x)}\right)$$
$$\hat{x} = \mu_x + W \cdot (x - \mu_x)$$

Where:
- $\sigma_{\text{noise}}^2 \approx 1.5\text{ dB}^2$ for 4-look Sentinel-1 GRD products in logarithmic decibel representation.
- In homogeneous areas ($\text{Var}(x) \approx \sigma_{\text{noise}}^2$), $W \to 0$, producing maximum spatial smoothing.
- Near water-land interfaces ($\text{Var}(x) \gg \sigma_{\text{noise}}^2$), $W \to 1$, strictly preserving sharp shoreline edges.

### 1.3 Otsu Optimal Bimodal Thresholding
The automated threshold $T^*$ separating water from non-water maximizes between-class variance:

$$\sigma_B^2(T) = \omega_0(T) \omega_1(T) \left[\mu_0(T) - \mu_1(T)\right]^2$$
$$T^* = \arg\max_T \sigma_B^2(T)$$

---

## 2. Digital Elevation Model (DEM) Hydrology & Flow Dynamics

### 2.1 D8 Flow Direction Algorithm
For any digital elevation cell $(r, c)$, flow drains to the steepest descent neighbor $k \in \{1, \dots, 8\}$:

$$S_k = \frac{z(r, c) - z(r_k, c_k)}{d_k}$$

Where $d_k = \Delta x$ for cardinal neighbors and $d_k = \sqrt{2} \Delta x$ for diagonal neighbors. The direction code corresponding to $\max_k(S_k)$ is encoded.

### 2.2 Topographic Wetness Index (TWI)
Developed by Beven and Kirkby (1979), TWI characterizes the physical tendency of terrain to accumulate runoff and saturate:

$$\text{TWI} = \ln\left(\frac{\alpha}{\tan \beta}\right)$$

Where:
- $\alpha = \frac{\text{FlowAccumulation} \cdot \Delta x}{b}$ is specific contributing catchment area per unit contour width ($b = 10\text{ m}$).
- $\beta = \arctan(\max S_k)$ is local slope angle in radians (clamped to $\beta \ge 0.001\text{ rad}$).
- Cells with $\text{TWI} \ge 8.5$ in urban basins indicate chronic waterlogging sinks requiring de-watering pumps.

---

## 3. Urban Drainage Hydraulic Capacity (Manning's Equation)

Open canal and culvert discharge capacity under gravity flow is governed by:

$$Q = \frac{1}{n} A R_h^{2/3} S_0^{1/2}$$

Where:
- $Q$: Maximum flow rate $(\text{m}^3/\text{s})$
- $n$: Manning's roughness coefficient (0.013 for smooth concrete, 0.025 for earthen canals)
- $A = W \cdot D_{\text{eff}}$: Cross-sectional flow area $(\text{m}^2)$
- $R_h = \frac{A}{W + 2 D_{\text{eff}}}$: Hydraulic radius $(\text{m})$
- $S_0 = \frac{z_{\text{upstream}} - z_{\text{downstream}}}{L}$: Longitudinal bed slope

### 3.1 River Tailwater Backflow Condition
When downstream river flood levels rise such that $h_{\text{outfall}} > h_{\text{junction}}$, the hydraulic head gradient reverses ($S_0 < 0$), causing dangerous backflow into residential streets regardless of local rainfall intensity.
