# Plays Settlers of Catan
# Michael Barnett
# Aug 2015

from random import randint

# initialized with hard-to-calculate values
edge_dict = {
             1: [2, 4],
             2: [1, 5],
             3: [4, 8],
             4: [1, 3, 9],
             5: [2, 6, 10],
             6: [5, 11],
             7: [8, 13],
             8: [3, 7, 14],
             9: [4, 10, 15],
             10: [5, 9, 16],
             11: [6, 12, 17],
             12: [6, 18],
             43: [37, 44],
             44: [38, 43, 49],
             45: [39, 46, 50],
             46: [40, 45, 51],
             47: [41, 48, 52],
             48: [42, 47],
             49: [44, 50],
             50: [45, 49, 53],
             51: [46, 52, 54],
             52: [49, 51],
             53: [50, 54],
             54: [51, 53]
             }

node_edges = []

# also initialized with hard to get edges
tile_edges = [
              {1, 2}, {1, 3},
              {2, 4}, {2, 5}, {2, 7},
              {3, 5}, {3, 6}, {3, 8},
              {4, 7}, {4, 9},
              {5, 7}, {5, 8}, {5, 10},
              {6, 8}, {6, 11},
              {7, 9}, {7, 10}, {7, 12},
              {8, 10}, {8, 11}, {8, 13},
              {9, 12}, {9, 14},
              {10, 12}, {10, 13}, {10, 15},
              {11, 13}, {11, 16},
              {12, 14}, {12, 15}, {12, 17},
              {13, 15}, {13, 16}, {13, 18},
              {14, 17},
              {15, 17}, {15, 18}, {15, 19},
              {16, 18},
              {17, 19},
              {18, 19}
              ]

open_nodes = list(range(1,55))

players = []
tiles = []
ports = []
deck = None
weights = {}



class Tile(object): 
    def __init__(self, tid):
        self.tid = tid
        self.nodes = find_hex_nodes(tid)
        self.prod = None
        self.freq = None
        self.resource = None
        self.has_robber = False
        
    def get_freq(self):
        if self.resource != "desert":
            self.freq = 6 - abs(self.prod-7)
        
class Port(object):
    def __init__(self, nodes, pid):
        self.pid = pid
        self.nodes = nodes
        self.trade = None
        
class Player(object):
    def __init__(self, ai, pid):
        self.pid = pid
        self.ai = ai
        self.hand = []
        self.development_cards = []
        self.vp = 0
        self.settlements = []
        self.cities = []
        self.roads = []
        self.playable_nodes = []
        
        self.desires = {"sheep": 0.01, 
                        "wheat": 0.01, 
                        "wood": 0.01, 
                        "clay": 0.01, 
                        "rocks": 0.01
                        }
        
    def build_settlement(self, node):
        global open_nodes
        
        self.settlements.append(node)
        self.vp += 1
        open_nodes.remove(node)
        
        for edge in node_edges:
            if node in edge:
                #print edge
                for n in edge:
                    #print n
                    # tries to remove both ends of edge
                    if n in open_nodes:
                        #print "removing..."
                        open_nodes.remove(n)
        
        for tile in tiles:
            if tile.resource == "desert":
                continue
            if node in tile.nodes:
                self.desires[tile.resource] += tile.freq
    
    def build_city(self, node):
        self.settlements.remove(node)
        self.cities.append(node)
        self.vp += 1
        
        for tile in tiles:
            if node in tile.nodes:
                self.desires[tile.resource] += tile.freq
    
    def build_road(self, edge):
        global node_edges
        
        self.roads.append(edge)
        for node in edge:
            if node not in playable_nodes:
                playable_nodes.append(node)
        node_edges.remove(edge)
                
    def find_best_node(self, poss):
        best_so_far = (0, None)
        for i in poss:
            score = 0
            for tile in tiles:
                if i in tile.nodes and tile.resource != "desert":
                    score += tile.freq * (1.0/(weights[tile.resource]) + 
                                          1.0/(self.desires[tile.resource]))
                                              
            if score > best_so_far[0]:
                best_so_far = (score, i)
        
        return best_so_far[1]
    
    def take_turn(self):
        return

class Deck(object):
    def __init__(self):
        self.contents = []
        for i in range(14):
            self.contents.append("knight")
        for i in range(5):
            self.contents.append("vp")
        for i in range(2):
            self.contents.append("year of plenty")
            self.contents.append("monopoly")
            self.contents.append("road building")
        
        self.contents = shuffle(self.contents)
        
    def draw(self):
        card = self.contents[0]
        self.contents.pop(0)
        return card


# ------------------ MISCELLANEOUS FUNCTIONS -------------------------

def shuffle(lst):
    shuffled = []
    for i in range(len(lst)):
        r = randint(0, len(lst)-1)
        shuffled.append(lst[r])
        lst.pop(r)
    return shuffled

def roll():
    return randint(1, 6) + randint(1, 6)

# returns the non- n element of a two element set
def get_other_elem(n, a_set):
    for elem in a_set:
        if elem != n:
            return elem

# returns True if nodes a and b are adjacent        
def adjacent(a, b):
    for edge in node_edges:
        if a in edge and b in edge:
            return True, edge
    return False,

# returns the final node in a path    
def last_node(path, start):
    if len(path) == 1:
        return get_other_elem(start, path[0])
    
    odd_edges = []
    last_edge = list(path[-1])
    for old in list(path[-2]):
        for new in list(path[-1]):
            if old != new:
                odd_edges.append(new)
    
    odd_edges.remove(last_edge[0])
    if last_edge[0] in odd_edges:
        return last_edge[0]
    else:
        return last_edge[1]

# finds shortest path between start and end
def get_path(start, end):
    paths = []
    best_path = []

    # find first edges
    for edge in node_edges:
        if start in edge and end in edge:
            return [edge]
        elif start in edge:
            paths.append([edge])

    # given these edges, continue until you get to the end
    d = 2
    while True:
        #print "looking for paths of length", d
        new_paths = []
        for path in paths:
            #print path
            for edge in node_edges:
                if last_node(path, start) in edge and end in edge:
                    path += [edge]
                    return path
                
                elif last_node(path, start) in edge and edge not in path:
                    new_paths.append(path + [edge])
                    
        paths = new_paths
        if d == 8:
            return None
        d += 1     
        

# ------------------ PRE-GAME SETUP -------------------------

def find_hex_nodes(hid):
    top_lefts = [1, 3, 5, 7, 9, 11, 14, 16, 19, 21, 23,
                 26, 28, 31, 33, 35, 38, 40, 45]
    start = top_lefts[hid-1]
    
    if start == 1:
        return [start, start+1, start+3, start+4, start+8, start+9]
    elif start in [3, 5]:
        return [start, start+1, start+5, start+6, start+11, start+12]
    elif start in [38, 40]:
        return [start, start+1, start+6, start+7, start+11, start+12]
    elif start == 45:
        return [start, start+1, start+5, start+6, start+8, start+9]
    else:
        return [start, start+1, start+6, start+7, start+12, start+13]


def build_board():
    global edge_dict
    global tiles
    global tile_edges
    global node_edges
    global deck
    
    # sets up edge_dict
    for i in range(55):
        if i in edge_dict:
            continue
        
        if i in [14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40]:
            # then edges leave in this formation: >-
            edge_dict[i] = [i-6, i+1, i+6]  
            
        elif i % 6 == 0 and i % 12 == 6:
            # then on right edge
            edge_dict[i] = [i-6, i+6]
            
        elif i % 6 == 1 and i % 12 == 1:
            # then on left edge
            edge_dict[i] = [i-6, i+6]        
        
        else:
            # then edges leave in this formation: -<
            edge_dict[i] = [i-6, i-1, i+6]

    # creates node_edges
    for i in edge_dict:
        for j in edge_dict[i]:
            if {i, j} not in node_edges:
                node_edges.append({i, j})


    # creates tiles
    for i in range(1,20):
        tiles.append(Tile(i))
      
    # creates ports    
    portholes = [[3, 4], [5, 6],
                 [7, 13], [12, 18],
                 [25, 31], [30, 36],
                 [44, 49], [47, 52],
                 [53, 54]]     
    for i in range(len(portholes)):
        ports.append(Port(portholes[i], i+1))
        
    # creates deck
    deck = Deck()


def no_adj_reds():  
    
    red_tiles = []
    for n in [6, 8]:
        for tile in tiles:
            if tile.prod == n:
                red_tiles.append(tile)
                
    red_combos = [{red_tiles[0].tid, red_tiles[1].tid},
                  {red_tiles[0].tid, red_tiles[2].tid},
                  {red_tiles[0].tid, red_tiles[3].tid},
                  {red_tiles[1].tid, red_tiles[2].tid},
                  {red_tiles[1].tid, red_tiles[3].tid},
                  {red_tiles[2].tid, red_tiles[3].tid}]
    
    for elem in red_combos:
        if elem in tile_edges:
            return False
    return True


def setup_game():
    # determine resource
    resources = []
    for r in ["sheep", "wheat", "wood"]:
        for i in range(4):
            resources.append(r)
    for r in ["rocks", "clay"]:
        for i in range(3):
            resources.append(r)
    resources.append("desert")
    
    resources = shuffle(resources)
    
    for i in range(len(tiles)):
        tiles[i].resource = resources[i]
        
    # determine production
    prods = []
    for f in range(3, 12):
        for i in range(2):
            if f != 7:
                prods.append(f)
    prods.append(2)
    prods.append(12)  
        
    while True:      
        prods = shuffle(prods)      
        
        found_desert = False
        for i in range(len(tiles)):            
            if tiles[i].resource == "desert":
                found_desert = True
                tiles[i].has_robber = True
                continue
            if found_desert:
                tiles[i].prod = prods[i-1]
            else:
                tiles[i].prod = prods[i]      
        if no_adj_reds():
            break
    for tile in tiles:
        tile.get_freq()
    
    # build ports
    trades = []
    for i in range(4):
        trades.append("misc")
    for r in ["sheep", "wheat", "wood", "clay", "rocks"]:
        trades.append(r)
    
    trades = shuffle(trades)
    
    for i in range(len(ports)):
        ports[i].trade = trades[i]
    
    
    print_board()
    
        

def analyze_resource(res):
    score = 0
    for tile in tiles:
        if tile.resource == res:
            score += tile.prod
    
    return score
    
def balance(scores):
    balance = 0
    for i in range(3):
        balance += abs(scores[i]-28)
    for i in range(3, 5):
        balance += abs(scores[i]-21)
        
    return balance

def print_board():
    global weights
    print
    print "Here is the map:"
    for tile in tiles:
        print tile.tid, tile.resource, tile.prod

    print
    print "Here are the ports:"   
    for port in ports:
        print port.pid, port.trade
    
    print
    print "Here is my analysis of the resources:"
    scores = []
    for res in ["sheep", "wheat", "wood", "clay", "rocks"]:
        score = analyze_resource(res)
        scores.append(score)
        print res, score
        weights[res] = score
        
    print    
    print "This island has a skew score of:", balance(scores)
    print

# -------------- OPENING TURNS ---------------

def opening_phase():
    global players
    
    order = []
    for player in players:
        order.append((roll(), player))
    order.sort()
    players = []
    for elem in order:
        players.append(elem[1])
    
    for player in players:
        if player.ai:
            node = player.find_best_node(open_nodes)
            player.build_settlement(node)

            temp_open_nodes = []
            next_best = player.find_best_node(open_nodes)
            for elem in open_nodes:
                if elem != next_best:
                    temp_open_nodes.append(elem)
                    
            path = None
            while path == None:
                third_best = player.find_best_node(temp_open_nodes)
                temp_open_nodes.remove(third_best)
                #print node, third_best
                path = get_path(node, third_best)
                                                     
            print "PLAYER", player.pid, "plays settlement on node", node,
            print "and a road to node", get_other_elem(node, path[0]) 
            
    for player in reversed(players):
        if player.ai:
            node = player.find_best_node(open_nodes)
            player.build_settlement(node)
            
            temp_open_nodes = []
            for elem in open_nodes:
                temp_open_nodes.append(elem)
            
            path = None
            while path == None:
                next_best = player.find_best_node(temp_open_nodes)
                temp_open_nodes.remove(next_best)
                path = get_path(node, next_best)
                
            print "PLAYER", player.pid, "plays settlement on node", node,
            print "and a road to node", get_other_elem(node, path[0]) 



def main():
    print "Initializing board..."
    build_board()
    print "Adding players..."
    for i in range(4):
        players.append(Player(True, i))
    print "Setting up game..."
    setup_game()
    
    #print get_path(6, 50)
    
    opening_phase()
    
    game_over = False
    winner = None
    while not game_over:
        for player in players:
            player.take_turn()
            if player.vp > 10:
                game_over = True
                winner = player
                break
            
    print "PLAYER", winner.pid, "WINS THE GAME!"
    
    
    

if __name__ == '__main__':
    main()