import datetime
import tkinter as tk
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mpimg

MAP_PATH = os.path.join(os.path.dirname(__file__), 'images', 'Blue_Marble_2002.jpg')

class Dashboard:
    def __init__(self, propagators, parsed_data):
        self.propagators = propagators

        self.parsed_data = parsed_data

        self.root = tk.Tk()
        self.root.title("Satellite Visualiser")
        self.root.geometry("1200x600")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        map_frame = tk.Frame(self.root, bg='black')
        map_frame.grid(row=0, column=0, sticky='nsew')
        map_frame.rowconfigure(0, weight=1)
        map_frame.columnconfigure(0, weight=1)

        data_frame = tk.Frame(self.root, bg='#0d1117')
        data_frame.grid(row=0, column=1, sticky='nsew')

        self._initialise_map_frame(map_frame, self.propagators[0].get_position())
        self._initialise_data_frame(data_frame, self.propagators[0].get_position(), self.parsed_data[0])

        self.root.after(5000, self._update)

        self.root.mainloop()

    def _initialise_map_frame(self, map_frame, position):
        fig = Figure(figsize=(8, 6))
        self.ax = fig.add_subplot(111)
        self.ax.axis('off')

        img = mpimg.imread(MAP_PATH)
        self.ax.imshow(img, extent=(-180.0, 180.0, -90.0, 90.0), aspect='auto')

        lat = position['LATITUDE']
        lon = position['LONGITUDE']

        self.sat_dot, = self.ax.plot(lon, lat, 'o', color='yellow', markersize=5)

        fig.tight_layout(pad=0)

        self.canvas = FigureCanvasTkAgg(fig, master=map_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    def _initialise_data_frame(self, data_frame, location, parsed_data):
        static_labels = [
            ('OBJECT NAME', parsed_data['OBJECT_NAME']),
            ('NORAD ID', parsed_data['NORAD_CAT_ID']),
            ('INCLINATION', f"{parsed_data['INCLINATION']} deg"),
            ('EPOCH', parsed_data['EPOCH'])
        ]

        (tk.Label(data_frame, text='ISS TRACKER', fg='#ffffff', bg='#0d1117', font=('Courier', 16, 'bold'))
         .grid(row=0, column=0, columnspan=2, pady=20))

        label_latitude = tk.Label(data_frame, text=f"LATITUDE", fg='#888888', bg='#0d1117', font=('Courier', 12))
        label_latitude.grid(row=1, column=0, padx=10, pady=5)

        self.label_latitude = tk.Label(data_frame, text=f"{location['LATITUDE']:.2f} deg", fg='#00b4d8', bg='#0d1117', font=('Courier', 12))
        self.label_latitude.grid(row=1, column=1, padx=10, pady=5)

        label_longitude= tk.Label(data_frame, text=f"LONGITUDE", fg='#888888', bg='#0d1117', font=('Courier', 12))
        label_longitude.grid(row=2, column=0, padx=10, pady=5)

        self.label_longitude = tk.Label(data_frame, text=f"{location['LONGITUDE']:.2f} deg", fg='#00b4d8',bg='#0d1117', font=('Courier', 12))
        self.label_longitude.grid(row=2, column=1, padx=10, pady=5)

        label_altitude = tk.Label(data_frame, text=f"ALTITUDE", fg='#888888', bg='#0d1117', font=('Courier', 12))
        label_altitude.grid(row=3, column=0, padx=10, pady=5)

        self.label_altitude = tk.Label(data_frame, text=f"{location['ALTITUDE']/1000:.2f} km", fg='#00b4d8',bg='#0d1117', font=('Courier', 12))
        self.label_altitude.grid(row=3, column=1, padx=10, pady=5)

        for i, (key, value) in enumerate(static_labels, start=4):
            (tk.Label(data_frame, text=key, fg='#888888', bg='#0d1117',font=('Courier', 12))
             .grid(row=i, column=0, padx=10, pady=5))

            (tk.Label(data_frame, text=value, fg='#00b4d8', bg='#0d1117', font=('Courier', 12))
             .grid(row=i, column=1, padx=10, pady=5))

    def _get_orbit_track(self, at_time):
        past_pos = []
        future_pos = []

        mean_motion = self.propagators[0].mean_motion
        half_period = int((1 / mean_motion) / 2 * 24 * 60)
        for minutes in range(-half_period, 0, 2):
            t = at_time + datetime.timedelta(minutes=minutes)
            pos = self.propagators[0].get_position(at_time=t)
            past_pos.append(pos)

        for minutes in range(0, half_period, 2):
            t = at_time + datetime.timedelta(minutes=minutes)
            pos = self.propagators[0].get_position(at_time=t)
            future_pos.append(pos)

        past_pos.append(self.propagators[0].get_position(at_time=at_time))
        return past_pos, future_pos

    def _break_antimeridian(self, lons, lats):
        broken_lons, broken_lats = [lons[0]], [lats[0]]
        for i in range(1, len(lons)):
            if abs(lons[i] - lons[i-1]) > 180:
                broken_lons.append(None)
                broken_lats.append(None)
            broken_lons.append(lons[i])
            broken_lats.append(lats[i])
        return broken_lons, broken_lats

    def _update(self):
        now = datetime.datetime.now(datetime.timezone.utc)

        new_position = self.propagators[0].get_position(at_time=now)

        lat = new_position['LATITUDE']
        lon = new_position['LONGITUDE']
        alt = new_position['ALTITUDE']

        self.label_latitude.config(text=f"{lat:.2f} deg")
        self.label_longitude.config(text=f"{lon:.2f} deg")
        self.label_altitude.config(text=f"{alt/1000:.2f} km")

        self.sat_dot.remove()

        if len(self.propagators) == 1:
            past_positions, future_positions = self._get_orbit_track(at_time=now)

            lats_past = [p['LATITUDE'] for p in past_positions]
            lons_past = [p['LONGITUDE'] for p in past_positions]

            lons_past, lats_past = self._break_antimeridian(lons_past, lats_past)

            lats_future = [p['LATITUDE'] for p in future_positions]
            lons_future = [p['LONGITUDE'] for p in future_positions]

            lons_future, lats_future = self._break_antimeridian(lons_future, lats_future)
            if hasattr(self, 'past_trail'):
                self.past_trail.remove()
                self.future_trail.remove()
            self.past_trail, = self.ax.plot(lons_past, lats_past, '-', color='red', linewidth=2, alpha=1)
            self.future_trail, = self.ax.plot(lons_future, lats_future, '-', color='cyan', linewidth=2, alpha=1)
            self.sat_dot, = self.ax.plot(lon, lat, 'o', color='yellow', markersize=5)
        else:
            if hasattr(self, 'sat_dots'):
                for dot in self.sat_dots:
                    dot.remove()
                for label in self.sat_labels:
                    label.remove()
            self.sat_dots = []
            self.sat_labels = []
            for propagator in self.propagators:
                pos = propagator.get_position(at_time=now)
                dot, = self.ax.plot(pos['LONGITUDE'], pos['LATITUDE'], 'o', color='yellow', markersize=5)
                label = self.ax.text(pos['LONGITUDE'], pos['LATITUDE'], propagator.object_name, color='white',
                                     fontsize=6)
                self.sat_dots.append(dot)
                self.sat_labels.append(label)
            self.sat_dot, = self.ax.plot(lon, lat, 'o', color='yellow', markersize=1, alpha=0)

        self.ax.set_xlim(-180, 180)
        self.ax.set_ylim(-90, 90)

        self.canvas.draw_idle()
        self.canvas.flush_events()

        self.root.after(5000, self._update)