import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
from functools import lru_cache
from math import radians, sin, cos, sqrt, atan2
from geopy.distance import geodesic
import city_graph
from PyQt5.QtWidgets import  QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QPushButton, QVBoxLayout, QApplication
import sys,os


def resorse_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path,relative_path)

class CityGraphBuilder:
    def __init__(self, file_path, population_threshold=50000, city_limit=50000):
        self.city_coords = {}
        self.load_data(file_path, population_threshold, city_limit)

    def load_data(self, file_path, population_threshold, city_limit):
        df = pd.read_excel(file_path)
        df_filtered = df[df['population'] > population_threshold].dropna(subset=['city_ascii', 'lat', 'lng'])
        limited_df = df_filtered.sort_values('population', ascending=False).head(city_limit)

        grouped = limited_df.groupby('city_ascii')
        for name, group in grouped:
            most_populous = group.sort_values('population', ascending=False).iloc[0]
            self.city_coords[name] = (most_populous['lat'], most_populous['lng'])

    def build_graph(self, k=40, max_distance_km=10000):
        coords_rad = np.radians(list(self.city_coords.values()))
        names = list(self.city_coords.keys())
        tree = BallTree(coords_rad, metric='haversine')
        distances, indices = tree.query(coords_rad, k=k+1)

        graph = {}
        for i, (dists, neighbors) in enumerate(zip(distances, indices)):
            city = names[i]
            graph[city] = {}
            for dist, idx in zip(dists[1:], neighbors[1:]):
                distance_km = dist * 6371
                if distance_km <= max_distance_km:
                    neighbor = names[idx]
                    graph[city][neighbor] = distance_km

        extra = self.auto_connect_distant_cities()
        for city1, city2, dist in extra:
            graph.setdefault(city1, {})[city2] = dist
            graph.setdefault(city2, {})[city1] = dist

        return graph

    def auto_connect_distant_cities(self, top_n=30, min_dist_km=3000, max_dist_km=10000):#top n це топ найпопулярніших міст
        sorted_cities = list(self.city_coords.items())[:top_n] #Посортовані міста за топ 30 з початку
        connections = []
        for i, (city1, coord1) in enumerate(sorted_cities):
            for j in range(i + 1, len(sorted_cities)):
                city2, coord2 = sorted_cities[j]
                dist = geodesic(coord1, coord2).km
                if min_dist_km < dist <= max_dist_km:
                    connections.append((city1, city2, dist))
        return connections

    def haversine(self, city1, city2):
        lat1, lon1 = self.city_coords[city1]
        lat2, lon2 = self.city_coords[city2]
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return 2 * 6371 * atan2(sqrt(a), sqrt(1 - a))

class RouteFinder:
    def __init__(self, graph):
        self.graph = graph

    @lru_cache(maxsize=10000)
    def cached_dijkstra(self, start, end):
        return city_graph.dijkstra(self.graph, start, end)

    def k_shortest_paths(self, start, end, k=3, max_ratio=1.5):
        paths = []
        potential_paths = []

        shortest_path, shortest_cost = city_graph.dijkstra(self.graph, start, end)
        if not shortest_path:
            return []

        paths.append((shortest_path, shortest_cost))
        max_length = shortest_cost * max_ratio

        for i in range(1, k):
            for j in range(len(paths[-1][0]) - 1):
                spur_node = paths[-1][0][j]
                root_path = paths[-1][0][:j+1]

                temp_graph = {node: neighbors.copy() for node, neighbors in self.graph.items()}
                for path, _ in paths:
                    if len(path) > j and path[:j+1] == root_path:
                        if j + 1 < len(path):
                            next_node = path[j+1]
                            temp_graph[spur_node].pop(next_node, None)

                spur_path, spur_cost = city_graph.dijkstra(temp_graph, spur_node, end)
                if spur_path and spur_path[0] == spur_node:
                    total_path = root_path[:-1] + spur_path
                    total_cost = sum(
                        self.graph[u][v] for u, v in zip(total_path, total_path[1:]) if v in self.graph[u]
                    )
                    if total_cost <= max_length and (total_path, total_cost) not in potential_paths:
                        potential_paths.append((total_path, total_cost))

            if not potential_paths:
                break

            potential_paths.sort(key=lambda x: x[1])
            paths.append(potential_paths.pop(0))

        return paths

class CityNavigator:
    def __init__(self, file_path,parent=None):
        self.parent = parent
        self.builder = CityGraphBuilder(file_path)

    def find_route(self, start, end):
        if start not in self.builder.city_coords or end not in self.builder.city_coords:
            return "❌ Одне з міст не знайдено."

        guess_dist = self.builder.haversine(start, end)
        graph = self.builder.build_graph(k=40, max_distance_km=guess_dist + 500)
        finder = RouteFinder(graph)
        results = finder.k_shortest_paths(start, end, k=2)

        if results:
            response = ""
            for i, (path, cost) in enumerate(results, 1):
                travel_time = cost / 900  # середня швидкість 900 км/год
                response += (
                    f"🔹 Варіант {i}:\n"
                    f" ➜ {' ➜ '.join(path)}\n"
                    f"Загальна відстань: {round(cost, 2)} км\n"
                    f"Орієнтовний час у дорозі літаком ✈️: {round(travel_time, 1)} год\n\n"
                )
            return response
        else:
            return "⚠️ Не знайдено жодного маршруту."

class RouteWindow(QDialog):
    def __init__(self, builder, parent=None):
        super().__init__(parent)
        self.builder = builder
        self.setWindowTitle("Пошук маршруту")
        self.setGeometry(800, 400, 400, 450)
        
        self.setStyleSheet("background-color: #cfc880;")

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        field_style = """
            QLineEdit {
                background-color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
        """

        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Початкове місто")
        self.start_input.setStyleSheet(field_style)
        self.end_input = QLineEdit()
        self.end_input.setPlaceholderText("Кінцеве місто")
        self.end_input.setStyleSheet(field_style)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)

        self.search_button = QPushButton("Знайти маршрут")
        self.search_button.clicked.connect(self.find_route)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #c7b37d;
                color: white;
                font-size: 16px;
                padding: 12px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #a58b5e;
            }
        """)
        self.close_btn = QPushButton("Закрити")
        self.close_btn.setStyleSheet("background-color: #a94442; color: white; font-size: 14px; padding: 8px; border-radius: 6px;")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.start_input)
        layout.addWidget(self.end_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.close_btn)
        layout.addWidget(self.result_label)

    def transliterate_city_name(self, city_name):
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g',
            'д': 'd', 'е': 'e', 'є': 'ie', 'ж': 'zh', 'з': 'z',
            'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k',
            'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
            'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
            'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ь': '', 'ю': 'iu', 'я': 'ia', '’': '', "'": ''
        }
        return ''.join(translit_map.get(c, c) for c in city_name.lower())

    def find_route(self):
        start = self.start_input.text().strip().title()
        end = self.end_input.text().strip().title()
        start = self.transliterate_city_name(start).title()
        end = self.transliterate_city_name(end).title()

        if not start or not end:
            self.result_label.setText("⚠️ Введіть обидва міста.")
            return

        try:
            result = self.builder.find_route(start, end)
            self.result_label.setText(result)

            # Візуалізація на мапі
            graph = self.builder.builder.build_graph()
            finder = RouteFinder(graph)
            paths = finder.k_shortest_paths(start, end, k=1)

            if paths:
                self.parent().show_route_on_map(paths[0][0])

        except Exception as e:
            self.result_label.setText("❌ Місто не знайдено або виникла інша помилка. Спробуйте ще раз.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    builder = CityNavigator(resorse_path("assets/worldcities.xlsx"))
    window = RouteWindow(builder)
    window.show()
    sys.exit(app.exec_())
    
