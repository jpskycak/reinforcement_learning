import numpy as np
import random
import pandas as pd

class State():
    def __init__(self, string_or_array):
        if type(string_or_array) == str:
            self.string = string_or_array
            self.array = np.array(list(string_or_array)).reshape(3,3)
        elif type(string_or_array) == np.ndarray:
            self.array = string_or_array
            self.string = ''.join(string_or_array.flatten())
    
    def board(self):
        return " {0} | {1} | {2} \n-----------\n {3} | {4} | {5} \n-----------\n {6} | {7} | {8} ".format(*self.array.flatten())
    
    def player(self):
        if (self.array=='x').sum() > (self.array=='o').sum():
            return 'o'
        else:
            return 'x'
    
    def winner(self):
        x = (self.array == 'x')
        o = (self.array == 'o')
    
        x_triples = x.prod(axis=0).sum() + x.prod(axis=1).sum() + np.diag(x).prod() + np.diag(x.transpose()).prod()
        o_triples = o.prod(axis=0).sum() + o.prod(axis=1).sum() + np.diag(o).prod() + np.diag(o.transpose()).prod()
        
        if x_triples > 0 and o_triples == 0:
            return 'x'
        elif o_triples > 0 and x_triples == 0:
            return 'o'
        else:
            return False
    
    def actions(self):
        if not self.winner():
            return zip(np.where(self.array == ' ')[0], np.where(self.array == ' ')[1])
        else:
            return []
    
    def is_terminal(self):
        return len(self.actions())==0
    
    def transitions(self):
        return [{'player': self.player(), 'action': action} for action in self.actions()]
    
    def result(self,transition):
        newstate = self.array.copy()
        newstate[transition['action']] = transition['player']
        return newstate
    
class Tree():
    def __init__(self):
        nodes = {0: ['         ']}
        edges = {}
        
        for i in range(1,10):
            newnodes = []
            newedges = []
            for istring, string in enumerate(nodes[i-1]):
                #start_time = time.clock()
                state = State(string)
                newedges.append([])
                for itransition, transition in enumerate(state.transitions()):
                    newstate = State(state.result(transition))
                    newstring = newstate.string
                    try:
                        newedges[istring].append(newnodes.index(newstring))
                        #if i==2:
                            #print '\n [duplicate] index ',istring,' ',string.replace(' ','.'),' --> ',' index ',str(newnodes.index(newstring)),' ',newstring.replace(' ','.')
                            #print 'the index of ',newstring,' in NEWNODES below is ',str(newnodes.index(newstring))
                            #for inewnode, newnode in enumerate(newnodes):
                            #    print inewnode, newnode
                    except:
                        newnodes.append(newstring)
                        newedges[istring].append(newnodes.index(newstring))
                        #if i==2:
                            #print '\n index ',istring,' ',string.replace(' ','.'),' --> ',' index ',str(newnodes.index(newstring)),' ',newstring.replace(' ','.')
                            #print 'the index of ',newstring,' in NEWNODES below is ',str(newnodes.index(newstring))
                            #for inewnode, newnode in enumerate(newnodes):
                            #    print inewnode, newnode
                nodes[i] = newnodes
                edges[i-1] = newedges
                #end_time = time.clock()
            
            #print '   level {0} constructed | duration: {1} | N: {2}'.format(*[i,end_time-start_time,len(newnodes)])
            
            self.nodes = nodes
            self.edges = edges
    
    def index(self, node):
        for i in range(10):
            try:
                index = {'level':i,'node_number': self.nodes[i].index(node)}
            except:
                pass
        return index
    
class Agent():
    def __init__(self, name, random_frequency, learning_rate, node = '         '):
        self.name = name
        self.random_frequency = random_frequency
        self.original_learning_rate = learning_rate
        self.current_learning_rate = learning_rate
        self.game_node = '         '
        self.tree = Tree()
        
        self.node1 = None
        self.node0 = None
        self.value0 = None
        
        values = {}
        for level, nodes in self.tree.nodes.iteritems():
            if level>0 and ((name=="x" and level%2==1) or (name=="o" and level%2==0)):
                newvalues = []
                for inode, node in enumerate(nodes):
                    if State(node).is_terminal():
                        if State(node).winner() == name:
                            newvalues.append(1.)
                        else:
                            newvalues.append(0.)
                    else:
                        newvalues.append(np.random.rand())  
                values[level] = newvalues
        self.values = values
    
    def prospects(self):
        game_index = self.tree.index(self.game_node)
        i, n = game_index['level'], game_index['node_number']
        prospective_node_numbers = self.tree.edges[i][n]
        prospective_nodes_values = {self.tree.nodes[i+1][node_num]: self.values[i+1][node_num] for node_num in prospective_node_numbers}
        return prospective_nodes_values

    def greedy_node(self):
        d = self.prospects()
        return max(d.iterkeys(), key=(lambda key: d[key]))
    
    def random_node(self):
        return random.choice(self.prospects().keys())
    
    def make_move(self):
        self.node0 = self.node1
        if np.random.rand() < self.random_frequency:
            self.node1 = self.random_node()
        else:
            self.node1 = self.greedy_node()
        self.game_node = self.node1
    
    def update_values(self):
        index0 = self.tree.index(self.node0)
        index1 = self.tree.index(self.node1)
        
        value0 = self.values[index0['level']][index0['node_number']]
        value1 = self.values[index1['level']][index1['node_number']]
        value0_updated = value0 + self.current_learning_rate*(value1 - value0)
        #print '{0}.values[{1}][{2}] = {3}'.format(*[self.name,index0['level'],index0['node_number'],self.values[index0['level']][index0['node_number']]])
        self.values[index0['level']][index0['node_number']] = value0_updated
        #print '{0}.values[{1}][{2}] = {3}'.format(*[self.name,index0['level'],index0['node_number'],self.values[index0['level']][index0['node_number']]])

        
    def reset_nodelog(self):
        self.game_node = '         '
        self.node1 = None
        self.node0 = None
        self.value0 = None
        
class Game():
    def __init__(self, agents):
        self.state = State('         ')
        self.agents = agents
        self.score = {k:0 for k,v in agents.iteritems()}
    
    def is_over(self):
        return self.state.is_terminal()
    
    def play_turn(self, training=True, output=False):
        player = self.state.player()
        if output:
            for k,v in self.agents[player].prospects().iteritems():
                print '['+str(v)[:4]+']', k.replace(' ','.')[:3],'|',k.replace(' ','.')[3:6],'|',k.replace(' ','.')[6:]
        self.agents[player].make_move()
        self.state = State(self.agents[player].game_node)
        self.agents['x'].game_node = self.state.string
        self.agents['o'].game_node = self.state.string
        
        if training and self.agents[player].node0:
            self.agents[player].update_values()
        if output:
            print self.state.board()
            print '\n'
    
    def play_game(self, training=True, output=False):
        while not self.state.is_terminal():
            self.play_turn(training, output)
        try:
            self.score[self.state.winner()] += 1
        except:
            pass
    
    def reset_state(self):
        self.state = State('         ')
        
    def reset_score(self):
        self.score = {k:0 for k,v in self.agents.iteritems()}
        
    def play_n_games(self, n, training=True):
        for _ in range(n):
            self.reset_state()
            self.agents['x'].reset_nodelog()
            self.agents['o'].reset_nodelog()
            self.play_game(training)
    
    def track_performace(self, training_batch_size, num_training_batches, estimation_batch_size):
        d = {'tot_games_trained':[],'prob_x_wins':[],'prob_o_wins':[],'prob_draw':[]}
        for batch_num in range(num_training_batches):
            self.play_n_games(estimation_batch_size, training=False)
            d['tot_games_trained'].append(training_batch_size*batch_num)
            d['prob_x_wins'].append(self.score['x']/float(estimation_batch_size))
            d['prob_o_wins'].append(self.score['o']/float(estimation_batch_size))
            d['prob_draw'].append(1.-d['prob_x_wins'][-1]-d['prob_o_wins'][-1])
            
            self.agents['x'].current_learning_rate = (1-d['prob_x_wins'][-1])*self.agents['x'].original_learning_rate
            self.agents['o'].current_learning_rate = (1-d['prob_o_wins'][-1])*self.agents['o'].original_learning_rate
            
            self.play_n_games(training_batch_size, training=True)
            self.reset_score()
        return pd.DataFrame(d)