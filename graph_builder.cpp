#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cmath>
#include <vector>
#include <unordered_map>
#include <queue>
#include <set>
#include <algorithm>
double M_PI = 3.1415;
namespace py = pybind11;
using namespace std;

double haversine(double lat1, double lon1, double lat2, double lon2) {
    const double R = 6371.0;
    lat1 = lat1 * M_PI / 180.0;
    lon1 = lon1 * M_PI / 180.0;
    lat2 = lat2 * M_PI / 180.0;
    lon2 = lon2 * M_PI / 180.0;

    double dlat = lat2 - lat1;
    double dlon = lon2 - lon1;

    double a = sin(dlat / 2) * sin(dlat / 2) +
               cos(lat1) * cos(lat2) * sin(dlon / 2) * sin(dlon / 2);
    double c = 2 * atan2(sqrt(a), sqrt(1 - a));
    return R * c;
}

unordered_map<string, unordered_map<string, double>> build_graph_k_nearest(
    const unordered_map<string, pair<double, double>>& city_coords,
    int k) {

    unordered_map<string, unordered_map<string, double>> graph;

    for (const auto& [city, coord1] : city_coords) {
        vector<pair<double, string>> distances;
        for (const auto& [other_city, coord2] : city_coords) {
            if (city == other_city) continue;
            double dist = haversine(coord1.first, coord1.second, coord2.first, coord2.second);
            distances.emplace_back(dist, other_city);
        }
        sort(distances.begin(), distances.end());
        for (int i = 0; i < min(k, (int)distances.size()); ++i) {
            graph[city][distances[i].second] = round(distances[i].first * 100.0) / 100.0;
        }
    }

    return graph;
}

pair<vector<string>, double> dijkstra(
    const unordered_map<string, unordered_map<string, double>>& graph,
    const string& start, const string& end) {

    priority_queue<tuple<double, string, vector<string>>,
                   vector<tuple<double, string, vector<string>>>,
                   greater<>> queue;

    set<string> seen;
    queue.push({0, start, {}});

    while (!queue.empty()) {
        auto [cost, node, path] = queue.top();
        queue.pop();
        if (seen.count(node)) continue;
        seen.insert(node);
        path.push_back(node);
        if (node == end) return {path, cost};
        for (const auto& [neighbor, weight] : graph.at(node)) {
            if (!seen.count(neighbor)) {
                auto new_path = path;
                queue.push({cost + weight, neighbor, new_path});
            }
        }
    }

    return {{}, numeric_limits<double>::infinity()};
}

PYBIND11_MODULE(city_graph, m) {
    m.def("build_graph_k_nearest", &build_graph_k_nearest);
    m.def("dijkstra", &dijkstra);
}
