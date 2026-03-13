import numpy as np

# Coordinates of the North Galactic Pole (NGP; Reid+09)
ra_ngp_hms = '12:51:26.2817'
dec_ngp_dms = '27:07:42.013'
ra_ngp_deg, dec_ngp_deg = 192.8595070833333, 27.128336944444445
ra_ngp_rad, dec_ngp_rad = 3.366033392377492, 0.4734788002709736

# theta_ngp is the position angle of the zero-longitude great circle
# which originanted at the NGP (Reid+09)
theta_ngp_deg = 122.932
theta_ngp_rad = np.radians(theta_ngp_deg)

# 3. Solar motion constants (Reid+14)
u_sun, du_sun = 10.7, 1.8
v_sun, dv_sun = 15.6, 6.8
w_sun, dw_sun = 8.9, 0.9

# 4. Rotation speed of the LSR (km/s)
theta_sun, d_theta_sun = 240.0, 8  # Galactic rotation (Reid+14)
r_sun, d_r_sun = 8.34, 0.16  # Solar distance to the GC (in kpc; Reid+14)


# Conversion factors
kpc_mas_per_yr_to_km_per_s = 4.74047046
