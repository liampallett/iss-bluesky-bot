from math import sin, cos, sqrt, degrees, radians, atan2, pi, asin
from datetime import datetime, timezone, timedelta

from propagator import EARTH_RADIUS


class PathPredictor:
    def __init__(self, propagator, lat, lon, alt):
        self.propagator = propagator
        self.lat = lat
        self.lon = lon
        self.alt = alt

        self.phi = radians(self.lat)
        self.Lambda = radians(self.lon)

    def _get_gst(self, at_time):
        epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        days_since_epoch = (at_time - epoch).total_seconds() / 86400

        gst_degrees = 280.46061837 + 360.98564736629 * days_since_epoch
        gst = radians(gst_degrees) % (2 * pi)

        return gst

    def _get_observer_ecef(self):
        sphere_radius = EARTH_RADIUS * 1000 + self.alt

        x = sphere_radius * cos(self.phi) * cos(self.Lambda)
        y = sphere_radius * cos(self.phi) * sin(self.Lambda)
        z = sphere_radius * sin(self.phi)

        return x, y, z

    def _observer_ecef_to_eci(self, at_time):
        gst = self._get_gst(at_time)

        x_ecef, y_ecef, z_ecef = self._get_observer_ecef()

        X_eci = x_ecef * cos(gst) - y_ecef * sin(gst)
        Y_eci = x_ecef * sin(gst) + y_ecef * cos(gst)
        Z_eci = z_ecef

        return X_eci, Y_eci, Z_eci

    def _difference_vector(self, at_time):
        eci_sat_frame = self.propagator.get_eci_position(at_time)
        X_sat, Y_sat, Z_sat = eci_sat_frame["X"], eci_sat_frame["Y"], eci_sat_frame["Z"]
        X_obs, Y_obs, Z_obs = self._observer_ecef_to_eci(at_time)

        dX = X_sat - X_obs
        dY = Y_sat - Y_obs
        dZ = Z_sat - Z_obs

        slant_range = sqrt(dX**2 + dY**2 + dZ**2)

        return dX, dY, dZ, slant_range

    def _to_sez(self, dX, dY, dZ, at_time):
        gst = self._get_gst(at_time)

        phi = self.phi
        Lambda = self.Lambda + gst

        south_vector = [sin(phi)*cos(Lambda), sin(phi)*sin(Lambda), -cos(phi)]
        east_vector = [-sin(Lambda), cos(Lambda), 0]
        zenith_vector = [cos(phi)*cos(Lambda), cos(phi)*sin(Lambda), sin(phi)]

        s = dX*south_vector[0] + dY*south_vector[1] + dZ*south_vector[2]
        e = dX*east_vector[0] + dY*east_vector[1] + dZ*east_vector[2]
        z = dX*zenith_vector[0] + dY*zenith_vector[1] + dZ*zenith_vector[2]

        return s, e, z

    def _elevation_azimuth(self, at_time):
        dX, dY, dZ, slant_range = self._difference_vector(at_time)
        south, east, zenith = self._to_sez(dX, dY, dZ, at_time)

        elevation_radians = asin(zenith / slant_range)
        elevation_degrees = degrees(elevation_radians)

        azimuth_radians = atan2(east, -south)
        azimuth_degrees = degrees(azimuth_radians) % 360

        return elevation_degrees, azimuth_degrees

    def find_next_pass(self):
        now = datetime.now(timezone.utc)
        current_time = now
        go_to = now + timedelta(hours=24)

        max_elevation = 0
        prev_elevation = 0

        rise_time = None
        rise_azimuth = None

        set_time = None

        while current_time < go_to:
            elevation, azimuth = self._elevation_azimuth(current_time)

            max_elevation = max(max_elevation, elevation)

            if prev_elevation <= 10 < elevation:
                rise_time = current_time
                rise_azimuth = azimuth
            elif prev_elevation > 10 >= elevation:
                set_time = current_time

                pass_dict = {
                    "RISE_TIME": rise_time,
                    "RISE_AZIMUTH": rise_azimuth,
                    "MAX_ELEVATION": max_elevation,
                    "SET_TIME": set_time
                }

                return pass_dict

            current_time += timedelta(seconds=30)
            prev_elevation = elevation

        return None