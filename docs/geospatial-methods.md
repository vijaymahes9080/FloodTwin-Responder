# Geospatial Methods & Coordinate Reference Systems (CRS)

## 1. Coordinate Reference System (CRS)
All vector datasets and GeoJSON outputs in FloodTwin Responder standardize strictly on:
- **EPSG:4326** (WGS 84 Ellipsoidal Geographic Coordinates in Decimal Degrees)
- Web visualization layers are projected on-the-fly to **EPSG:3857** (WGS 84 / Pseudo-Mercator) by the Leaflet frontend renderer.

## 2. Distance Computation & Geodesy
Distance measurements between sensor nodes, critical infrastructure, and citizen reports utilize the Great-Circle Haversine formula on a spherical earth model ($R = 6371.0\text{ km}$):
$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
This yields sub-meter precision over regional disaster catchment scales (<50km) with $O(1)$ computational efficiency.

## 3. Spatial Containment (Point-in-Polygon)
Administrative ward and flood zone assignment uses:
1. **Ray-Casting Algorithm:** A horizontal semi-infinite ray is cast from test point $(x_0, y_0)$. The count of crossings through polygon boundary segments determines interior status (odd = inside, even = outside).
2. **Accelerated Shapely GEOS Integration:** When available in the runtime environment, vectorized GEOS C-libraries execute Point-in-Polygon and spatial intersection operations for maximum throughput.

## 4. Corridor Buffering & Inundation Spread
- **Waterway Buffering:** River centerlines (Cooum and Adyar rivers) feature spillway hazard zones buffered at 50m, 100m, and 150m intervals.
- **Surface Spread Delta Analysis:** Temporal flood change analysis calculates polygon symmetric differences between pre-flood SAR water masks and post-storm observations, deriving net inundation expansion percentages and acreage deltas.
