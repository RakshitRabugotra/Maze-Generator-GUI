import sys

class Node():
    def __init__(self, state, parent, action, path_cost):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

class StackFrontier():
    def __init__(self):
        self.frontier = []
    
    def add(self, value:Node) -> list:
        # Adding node to the stack
        self.frontier.append(value)
        # Retuning the stack
        return self.frontier
    
    def remove(self) -> Node:
        if self.isEmpty(): raise Exception("Frontier is empty")
        # Fetching the last node
        state = self.frontier[-1]
        # Removing the state from stack
        self.frontier = self.frontier[:-1]
        # Retuning the state
        return state
    
    def containsState(self, state):
        return any(node.state == state for node in self.frontier)
    
    def isEmpty(self) -> bool:
        return len(self.frontier) == 0

    def print(self) -> None:
        print(self.frontier)

class QueueFrontier(StackFrontier):
    def remove(self) -> Node:
        if self.isEmpty(): raise Exception("Frontier is empty")
        # Fetching the first node
        state = self.frontier[0]
        # Removing the node from stack
        self.frontier = self.frontier[1:]
        # Returning the node
        return state

class Maze():
    def __init__(self, filename):
        # Read the file and set width and height of maze
        with open(filename, mode='r') as f:
            contents = f.read()
        
        # Validate Start and Goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine the height and width
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)
        
        # Solution is initialized to none
        self.solution = None
    
    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()
    
    def neighbours(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("up", (row, col + 1)),
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result
    
    def heuristic(self, node:Node) -> int:
        # This heuristic function, h(n) works on manhattan distance
        startX, startY = self.start
        goalX, goalY = self.goal
        # New goal position taking start as the orign point i.e, (0,0)
        newGoalX, newGoalY = (goalX-startX), (goalY-startY)
        print(newGoalX, newGoalY)
        # Current (X, Y) coordinates of agent
        currentX, currentY = node.state
        print(node.state)
        # Retuning the manhattan distance
        manhattanDistance = (newGoalX-currentX)+(newGoalY-currentY)
        print(manhattanDistance)
        return manhattanDistance
    
    def path_cost(self, node:Node) -> int:
        return node.path_cost
    
    def solve(self, use=None):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Intialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None, path_cost=0)
        frontier = StackFrontier() if use is None else use()
        frontier.add(start)

        # Initalize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.isEmpty():
                raise Exception("no solution")
            
            # Choose a node from the frontier, with
            # lowest possible value of g(n) + h(n)

            nodes = dict((n, self.path_cost(n) + self.heuristic(n)) for n in frontier.frontier) 
            
            temp = min(nodes.values())
            res = [key for key in nodes if nodes[key] == temp]

            if len(res) > 1:
                node = res.pop()
            else:
                node = res[0]

            # node = frontier.remove()
            
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
            
            # Mark node as explored
            self.explored.add(node.state)

            # Add neightbours to frontier
            for action, state in self.neighbours(node.state):
                if not frontier.containsState(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action, path_cost=node.path_cost+1)
                    frontier.add(child)
            
    def outputImage(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)
                
                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                
                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty Cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )
        
        img.save(filename)

# Checking if the file is passed with the code
if (len(sys.argv) != 2):
    sys.exit("Usage: python maze.py maze.txt")


m = Maze(sys.argv[1])
print("Maze:")
m.print()
print("Solving...")
m.solve(use=QueueFrontier)
print("States Explored: ", m.num_explored)
print("Solution:")
m.outputImage("maze.png")
m.print()
