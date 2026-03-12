"""
Calculates the orbit based on given parsed data.
"""
from math import sin, cos, sqrt, degrees, radians, atan2, pi
from datetime import datetime, timezone

GM = 3.986004418e14 # a.k.a. mu
EARTH_RADIUS = 6371.0 # Km
EARTH_ROTATION_RATE = 7.2921150e-5 # rad/s

class OrbitPropagator():
    """
    Represents a satellite orbit propagator.
    """
    def __init__(self, parsed_data):
        """
        Constructs a new OrbitPropagator object.
        :param parsed_data: Dictionary of parsed information, containing only the necessary to calculate the orbit.
        """
        self.object_name = parsed_data['OBJECT_NAME']
        self.norad_cat_id = parsed_data['NORAD_CAT_ID']
        self.epoch = parsed_data['EPOCH']
        self.mean_motion = parsed_data['MEAN_MOTION']
        self.eccentricity = parsed_data['ECCENTRICITY']
        self.inclination = parsed_data['INCLINATION']
        self.ra_of_asc_node = parsed_data['RA_OF_ASC_NODE']
        self.arg_of_pericenter = parsed_data['ARG_OF_PERICENTER']
        self.mean_anomaly = parsed_data['MEAN_ANOMALY']
        self.bstar = parsed_data['BSTAR']

    def _solve_kepler_equation(self, e, M):
        """
        Private helper method to calculate the eccentric anomaly (E) of the satellite's orbit. Uses Newton's method to
        iteratively solve for E.
        :param e: Orbit eccentricity.
        :param M: Orbit mean anomaly in degrees.
        :return: Estimate of the eccentric anomaly in radians.
        """
        M = radians(M)
        E = M # initialize the eccentric anomaly to the mean anomaly for iterative solving

        max_iterations = 50
        tolerance = 1e-10

        for i in range(max_iterations):
            E_next = E - (E - e * sin(E) - M) / (1 - e * cos(E))
            if abs(E_next - E) < tolerance:
                break
            E = E_next

        return E_next

    def _eccentric_to_true_anomaly(self, E, e):
        """
        Calculates the true anomaly given the eccentricity and eccentric anomaly.
        :param E: Eccentric anomaly in radians.
        :param e: Orbit eccentricity
        :return: True anomaly in radians.
        """
        v = 2 * atan2(sqrt(1 + e) * sin(E / 2), sqrt(1 - e) * cos(E / 2))
        return v

    def _calculate_semi_major_axis(self, n):
        """
        Calculates the semi-major axis of an orbit given the mean motion in revs/day.
        :param n: Mean motion in revs/day.
        :return: Semi-major axis in metres.
        """
        n_rad_s = n * 2 * pi / 86400

        a = (GM / (n_rad_s)**2)**(1/3)

        return a

    def _calculate_orbital_radius(self, E, e):
        """
        Calculates the radius of the orbit given the eccentricity and eccentric anomaly.
        :param E: Eccentric anomaly in radians.
        :param e: Eccentricity of the orbit.
        :return: Orbital radius in metres.
        """
        a = self._calculate_semi_major_axis(self.mean_motion)

        r = a * (1 - e * cos(E))

        return r

    def _calculate_perifocal_position(self, r, v):
        """
        Calculates the position in the perifocal frame.
        :param r: Orbital radius in metres.
        :param v: True anomaly in radians.
        :return: A tuple of co-ordinates (x, y, z)
        """
        x = r * cos(v)
        y = r * sin(v)
        z = 0

        return (x, y, z)

    def _perifocal_to_eci(self, x, y):
        """
        Calculates the position in the ECI frame given the position in the perifocal frame.
        :param x: The x co-ordinate in the perifocal frame.
        :param y: The y co-ordinate in the perifocal frame.
        :return: A tuple of co-ordinates (X, Y, Z)
        """
        raan = radians(self.ra_of_asc_node)
        arg_of_peri = radians(self.arg_of_pericenter)
        inc = radians(self.inclination)

        X = (cos(raan)*cos(arg_of_peri) - sin(raan)*sin(arg_of_peri)*cos(inc)) * x + (-cos(raan)*sin(arg_of_peri) - sin(raan)*cos(arg_of_peri)*cos(inc)) * y
        Y = (sin(raan)*cos(arg_of_peri) + cos(raan)*sin(arg_of_peri)*cos(inc)) * x + (-sin(raan)*sin(arg_of_peri) + cos(raan)*cos(arg_of_peri)*cos(inc)) * y
        Z = (sin(inc)*sin(arg_of_peri)) * x + (sin(inc)*cos(arg_of_peri)) * y

        return (X, Y, Z)

    def _eci_to_lat_lon(self, X, Y, Z, at_time=None):
        """
        Calculates the latitude and longitude of the object from a given ECI frame.
        :param X: The x co-ordinate in the ECI frame.
        :param Y: The y co-ordinate in the ECI frame.
        :param Z: The z co-ordinate in the ECI frame.
        :param at_time: Time to calculate latitude and longitude of orbiting object.
        :return: A tuple containing the latitude, longitude and the altitude of the object.
        """
        epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        days_since_epoch = (at_time - epoch).total_seconds() / 86400

        gst_degrees = 280.46061837 + 360.98564736629 * days_since_epoch
        gst = radians(gst_degrees) % (2 * pi)

        x_ecef = X * cos(gst) + Y * sin(gst)
        y_ecef = -X * sin(gst) + Y * cos(gst)
        z_ecef = Z

        lon = degrees(atan2(y_ecef, x_ecef))
        lat = degrees(atan2(z_ecef, sqrt(x_ecef**2 + y_ecef**2)))
        altitude = sqrt(x_ecef**2 + y_ecef**2 + z_ecef**2) - (EARTH_RADIUS*1000)

        return (lat, lon, altitude)

    def get_position(self, at_time=None):
        """
        Calculates the position by chaining unction calls.
        :param at_time: Default None, given time to calculate position of.
        :return: A dictionary containing the latitude, longitude and altitude of the object.
        """
        if at_time is None:
            at_time = datetime.now(timezone.utc)
        epoch = datetime.fromisoformat(self.epoch).replace(tzinfo=timezone.utc)
        days_since_epoch = (at_time - epoch).total_seconds() / 86400

        M_current = (self.mean_anomaly + (self.mean_motion * 360) * (days_since_epoch)) % 360

        eccentric_anomaly = self._solve_kepler_equation(self.eccentricity, M_current)
        true_anomaly = self._eccentric_to_true_anomaly(eccentric_anomaly, self.eccentricity)
        orbital_radius = self._calculate_orbital_radius(eccentric_anomaly, self.eccentricity)
        x, y, z = self._calculate_perifocal_position(orbital_radius, true_anomaly)
        X, Y, Z = self._perifocal_to_eci(x, y)
        latitude, longitude, altitude = self._eci_to_lat_lon(X, Y, Z, at_time)

        lat_lon_dict = {
            "LATITUDE": latitude,
            "LONGITUDE": longitude,
            "ALTITUDE": altitude
        }

        return lat_lon_dict
