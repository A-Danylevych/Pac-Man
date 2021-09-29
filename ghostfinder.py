from constants import *
from road import *
from timer import Timer


class GhostFinder(object):
    def __init__(self, road_blocks, pacman, ghosts):
        self.road_blocks = road_blocks
        self.pacman = pacman
        self.ghosts = ghosts.ghosts.values()
        self.current = UCS
        self.ghosts_indexes = []
        self.paths = []
        self.targets = []
        self.graph = {}
        self.weighted_graph = {}
        self.create_graph()
        self.create_weighted_graph()
        self.timer = Timer()

    def change_algorithm(self):
        if self.current == DFS:
            self.current = BFS
        elif self.current == BFS:
            self.current = UCS
        else:
            self.current = DFS

    def update(self):
        index = 0
        for ghost in self.ghosts_indexes:
            if len(self.paths) == index:
                break
            path = self.paths[index]
            path.pop()
            path.reverse()
            ghost.goal = path
            index += 1
        self.timer.start()
        self.paths = []
        start_v = self.find_start()
        self.find_targets()
        if self.current == DFS:
            self.dfs(start_v)
        if self.current == BFS:
            self.bfs(start_v)
        if self.current == UCS:
            self.ucs(start_v)
        self.timer.stop()

    def dfs(self, start_v):
        for index in range(len(self.targets)):
            path = self.dfs_paths(start_v, self.targets[index])
            self.find_shortest(path)

    def bfs(self, start_v):
        for index in range(len(self.targets)):
            path = self.bfs_paths(start_v, self.targets[index])
            self.find_shortest(path)

    def ucs(self, start_v):
        for index in range(len(self.targets)):
            path = self.uniform_cost_search(start_v, self.targets[index])
            self.find_shortest_cost(path)

    def render(self, screen):
        lists_of_points = []
        for item in self.paths:
            lists_of_points.append(item)
        for points in lists_of_points:
            if points is None:
                break
            if not any(isinstance(x, PortalBlock) for x in points):
                points = [point.position.as_tuple() for point in points]
                pygame.draw.lines(screen, RED, False, points, 4)
            else:
                index = 0
                for point in points:
                    if isinstance(point, PortalBlock):
                        break
                    index += 1
                points = [point.position.as_tuple() for point in points]
                points_1 = points[:index+1]
                points_2 = points[index+1:]
                if len(points_1) > 1:
                    pygame.draw.lines(screen, RED, False, points_1, 4)
                if len(points_2) > 1:
                    pygame.draw.lines(screen, RED, False, points_2, 4)

    def find_start(self):
        for item in self.road_blocks:
            if item == self.pacman.road_block:
                return item

    def find_targets(self):
        self.targets = []
        for ghost in self.ghosts:
            for item in self.road_blocks:
                if item == ghost.road_block:
                    self.targets.append(item)
                    self.ghosts_indexes.append(ghost)

    def dfs_paths(self, start, goal):
        stack = [(start, [start])]
        while stack:
            (vertex, path) = stack.pop()
            for next in self.graph[vertex] - set(path):
                if next == goal:
                    yield path + [next]
                else:
                    stack.append((next, path + [next]))

    def bfs_paths(self, start, goal):
        queue = [(start, [start])]
        while queue:
            (vertex, path) = queue.pop(0)
            for next in self.graph[vertex] - set(path):
                if next == goal:
                    yield path + [next]
                else:
                    queue.append((next, path + [next]))

    def uniform_cost_search(self, start, goal):
        queue = [(0, start, [start])]
        visited = []
        while queue:
            queue = sorted(queue, key=lambda x: x[0])
            (cost, vertex, path) = queue.pop(0)
            if vertex not in visited:
                visited.append(vertex)
                for next in sorted(self.weighted_graph[vertex], key=self.weighted_graph[vertex].get):
                    if next == goal:
                        yield path + [next], cost
                    else:
                        queue.append((cost + self.weighted_graph[vertex][next], next, path + [next]))

    def create_graph(self):
        for item in self.road_blocks:
            v_list = []
            for direction in item.directions.values():
                if not isinstance(direction, NullRoad):
                    v_list.append(direction)
            self.graph[item] = set(v_list)

    def create_weighted_graph(self):
        for item in self.road_blocks:
            if not isinstance(item, NullRoad):
                self.weighted_graph[item] = {}
                for direction in item.directions.values():
                    if not isinstance(direction, NullRoad):
                        if isinstance(item, PortalBlock) and isinstance(direction, PortalBlock):
                            self.weighted_graph[item][direction] = 0
                        else:
                            self.weighted_graph[item][direction] = \
                                (item.position - direction.position).magnitude_squared()

    def find_shortest(self, paths):
        if paths is not None:
            path = min(paths, key=len, default=None)
            self.paths.append(path)

    def find_shortest_cost(self, paths):
        if paths is not None:
            path = min(paths, key=lambda x: x[1], default=None)
            if path is not None:
                self.paths.append(path[0])
