#!/usr/bin/env python
from ants import *
from random import choice
import datetime
import random
import itertools
# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
LOGGING = False

class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.hills = []
        self.turn = 0

        self.to_explore = {}
        for row in range(ants.rows):
            for col in range(ants.cols):
                if ants.passable((row, col)) and row%10==0 and col%10 == 0:
                    self.to_explore[(random.random(), (row, col))] = 0

        """
        self.unseen = []
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))
        """

    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):

        self.turn += 1

        my_ants = ants.my_ants()
        not_used_ants = list(my_ants)
        enemy_ants = ants.enemy_ants()

        def unoccupied(loc):
            return ants.unoccupied(loc) or loc in orders.values()

        # track all moves, prevent collisions
        orders = {}
        def do_move_direction(loc, direction):
            new_loc = ants.destination(loc, direction)
            if (ants.unoccupied(new_loc) and new_loc not in orders) and loc not in orders.values():
                ants.issue_order((loc, direction))
                orders[new_loc] = loc
                if loc in not_used_ants:
                    not_used_ants.remove(loc)
                return True
            else:
                return False

        targets = {}
        def do_move_location(loc, dest):
            directions = ants.direction(loc, dest)
            random.shuffle(directions)
            for direction in directions:
                if do_move_direction(loc, direction):
                    targets[dest] = loc
                    return True
            return False

        def defensive_move():
            
            def adjacent_positions(pos):
                row, col = pos
                return [
                    (r, c) for (r, c) in [
                        ((row-1) % ants.rows, col),
                        ((row+1) % ants.rows, col),
                        (row, (col+1) % ants.cols),
                        (row, (col-1) % ants.cols),
                        (row, col)
                    ] if ants.passable((r, c))
                ]

            def make_defense_move(close_friends, enemy):
                try:
                    #print 'pensou o movimento {} {}'.format(close_friends, enemy)
                    ants_and_distances = []
                    for ant in close_friends:
                        if ants.time_remaining() < 40:
                            if LOGGING:
                                print 'timeout soon @ defense_moves'
                            return
                        ants_and_distances.append((ants.distance(ant, enemy), ant))
                    ants_and_distances.sort()
                    min_dist = ants_and_distances[0][0]

                    possible_moves = [adjacent_positions(ant) for ant in close_friends]
                    combinations = list(itertools.product(*possible_moves))
                    valid_combinations = [comb for comb in combinations if len(comb) == len(set(comb))]

                    for comb in valid_combinations[:30]:

                        new_min_dist = 999
                        for pos in comb:
                            if ants.time_remaining() < 40:
                                if LOGGING:
                                    print 'timeout soon @ defense_moves'
                                return
                            dist = ants.distance(pos, enemy)
                            new_min_dist = min(new_min_dist, dist)
                        #print comb
                        #print new_min_dist, min_dist
                        if new_min_dist > min_dist:
                            #print '-------------------- DEFENSIVE MOVE'
                            for index, ant in enumerate(close_friends):
                                if ants.time_remaining() < 40:
                                    if LOGGING:
                                        print 'timeout soon @ defense_moves'
                                    return
                                if ant not in orders.values():
                                    #print 'defendeu'
                                    do_move_location(ant, comb[index])
                            return
                except Exception as e:
                    print 'exception at make_defense_move'


            if LOGGING:
                start = datetime.datetime.now()
        
            not_used_so_far = not_used_ants[:]

            try:
                endangered_ants = []
                for my_ant_loc in not_used_so_far:
                    closer_enemy = None
                    closer_distance = 999
                    for enemy_loc, owner in enemy_ants:
                        if ants.time_remaining() < 40:
                            if LOGGING:
                                print 'timeout soon @ defense_moves'
                            return
                        if ants.euclidian_distance(my_ant_loc, enemy_loc) < 6:
                            distance = ants.distance(my_ant_loc, enemy_loc)
                            if distance < 6 and distance < closer_distance:
                                closer_enemy = enemy_loc
                                closer_distance = distance
                    if closer_enemy:
                        endangered_ants.append((closer_distance, closer_enemy, my_ant_loc))
                endangered_ants.sort()
                for dist, enemy, my_ant_loc in endangered_ants:
                    if ants.time_remaining() < 40:
                        if LOGGING:
                            print 'timeout soon @ defense_moves'
                        return

                    if my_ant_loc not in not_used_ants:
                        continue
                    
                    close_friends = []
                    for ant_friend in not_used_ants[:]:
                        if ants.time_remaining() < 40:
                            if LOGGING:
                                print 'timeout soon @ defense_moves'
                            return
                        if ants.distance_lt(my_ant_loc, ant_friend, 3):
                            close_friends.append(ant_friend)

                    make_defense_move(close_friends, enemy_loc)
            except:
                raise Exception("wat the fuck")

            if LOGGING:
                print "{} @ defensive_move".format(datetime.datetime.now() - start)

        def attack_move():
            def make_attack_move(attacking_ants, enemy):
                distances = [
                    (ants.distance(attacking_ant, enemy), attacking_ant) for attacking_ant in attacking_ants
                ]
                distances.sort()
                min_dist = distances[0][0]
                for dist, ant in distances:
                    if ants.time_remaining() < 40:
                        if LOGGING:
                            print 'timeout soon @ attack_moves'
                        return
                    #if dist > min_dist and ant not in orders.values():
                    do_move_location(ant, enemy)
                    #else:
                    #    if ant not in orders.values():
                    #        orders[ant] = ant

            if LOGGING:
                start = datetime.datetime.now()

            not_used_so_far = not_used_ants[:]

            for my_ant_loc in not_used_so_far:
                if ants.time_remaining() < 40:
                    if LOGGING:
                        print 'timeout soon @ attack_moves'
                    return
                if my_ant_loc not in not_used_ants:
                    continue
                ant_friends = []
                close_enemies = []
                for ant_loc, owner in enemy_ants:
                    if ants.distance_lt(my_ant_loc, ant_loc, 5):
                        close_enemies.append(ant_loc)

                for enemy in close_enemies:
                    for ant_loc in not_used_so_far:
                        if my_ant_loc == ant_loc:
                            continue

                        if ants.time_remaining() < 40:
                            if LOGGING:
                                print 'timeout soon @ attack_moves'
                            return

                        if ants.distance_lt(enemy, ant_loc, 5):
                            ant_friends.append(ant_loc)

                    if len(ant_friends) >= len(close_enemies):
                        attacking_ants = ant_friends + [my_ant_loc]
                        make_attack_move(attacking_ants, enemy)
                        break

            if LOGGING:
                print datetime.datetime.now() - start


        def food_move():
            if LOGGING:
                start = datetime.datetime.now()
            # find close food
            ant_dist = []
            for food_loc in ants.food():
                if ants.time_remaining() < 40:
                    if LOGGING:
                        print 'timeout soon @ food_moves'
                    return
                for ant_loc in not_used_ants[:]:
                    dist = ants.distance(ant_loc, food_loc)
                    ant_dist.append((dist, ant_loc, food_loc))
            ant_dist.sort()
            for dist, ant_loc, food_loc in ant_dist:
                if ants.time_remaining() < 40:
                    if LOGGING:
                        print 'timeout soon @ food_moves'
                    return
                if food_loc not in targets and ant_loc not in targets.values():
                    do_move_location(ant_loc, food_loc)
                # check if we still have time left to calculate more orders
                if ants.time_remaining() < 10:
                    break
            if LOGGING:
                print datetime.datetime.now() - start


        def haze_hills():

            if LOGGING:
                start = datetime.datetime.now()
            # attack hills
            for hill_loc, hill_owner in ants.enemy_hills():
                if hill_loc not in self.hills:
                    self.hills.append(hill_loc)
            ant_dist = []
            for hill_loc in self.hills:
                if hill_loc not in my_ants:
                    for ant_loc in not_used_ants[:]:
                        if ants.time_remaining() < 40:
                            if LOGGING:
                                print 'timeout soon @ haze_hills'
                            return
                        if ant_loc not in orders.values():
                            dist = ants.distance(ant_loc, hill_loc)
                            ant_dist.append((dist, ant_loc, hill_loc))
            ant_dist.sort()
            if LOGGING:
                print "{} @ preparing_distances_haze_hills".format(datetime.datetime.now() - start)
            if LOGGING:
                start = datetime.datetime.now()
            n_hills = len(self.hills)
            n_ants = len(ant_dist)
            if n_ants > 10:
                n_ants = int(0.7*n_ants)
            if n_ants >= 30:
                n_ants = int(n_ants/2) if n_hills <= 1 else int(0.8*n_ants)
            if n_ants >= 50:
                n_ants = int(0.35*n_ants) if n_hills <= 1 else int(0.7*n_ants)

            for dist, ant_loc, hill_loc in ant_dist[:n_ants]:
                if ants.time_remaining() < 40:
                    if LOGGING:
                        print 'timeout soon @ haze_hills'
                    return
                do_move_location(ant_loc, hill_loc)
            if LOGGING:
                print "{} @ ants_attacking_haze_hills".format(datetime.datetime.now() - start)

            


        def setup_exploration_map():
            if LOGGING:
                start = datetime.datetime.now()
            if ants.time_remaining() < 40:
                if LOGGING:
                    print 'timeout soon @ setup_exploration_map'
                return
            # explore exotic areas
            for _r, loc in self.to_explore.keys()[:]:
                if not ants.passable(loc):
                    del self.to_explore[(_r, loc)]
            for _r, loc in self.to_explore.keys():
                if ants.visible(loc):
                    self.to_explore[(_r, loc)] = 0
                else:
                    if self.to_explore[(_r, loc)] > 30:
                        self.to_explore[(_r, loc)] = -10
                    else:   
                        self.to_explore[(_r, loc)] += 1
            if LOGGING:
                print "{} @ setup_exploration_map".format(datetime.datetime.now() - start)

        def explore_map():
            
            if LOGGING:
                start = datetime.datetime.now()

            locs_and_counters = [(counter, loc) for loc, counter in self.to_explore.items()]
            locs_and_counters.sort(reverse=True)
            """
            i = 0
            used_locs_and_counters = locs_and_counters[:3*len(not_used_ants[:])]
            size = len(used_locs_and_counters)
            while i*4 < size/2 - 1:
                used_locs_and_counters[i*4], used_locs_and_counters[size-4*i - 1] = used_locs_and_counters[size-4*i -1], used_locs_and_counters[i*4]
                i += 1
            #"""
            if LOGGING:
                print "{} @ sorting_exploration_map".format(datetime.datetime.now() - start)
            if LOGGING:
                start = datetime.datetime.now()
            
            for counter, exotic_loc in locs_and_counters[:3*len(not_used_ants[:])]:
                if ants.time_remaining() < 40:
                    if LOGGING:
                        print 'timeout soon @ explore_map'
                    break

                ant_dist = []
                for ant_loc in not_used_ants[:]:
                    if ants.time_remaining() < 40:
                        if LOGGING:
                            print 'timeout soon @ explore_map'
                        break
                    dist = ants.distance(ant_loc, exotic_loc[1])
                    ant_dist.append((dist, ant_loc, exotic_loc[1]))

                ant_dist.sort()
                if ant_dist:
                    dist, ant_loc, exotic_loc = ant_dist[0]
                    if exotic_loc not in targets and ant_loc not in targets.values():
                        do_move_location(ant_loc, exotic_loc)
            #print len(ant_dist), len(not_used_ants)
            if LOGGING:
                print "{} @ ant_explore_map".format(datetime.datetime.now() - start)
            

        # prevent stepping on own hill
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None

        # prevent going out of an enemy hill
        for index, hill_loc in enumerate(self.hills):
            if hill_loc in my_ants:
                orders[index] = hill_loc

        #attack if with many ants
        if len(not_used_ants) > 30:
            attack_move()

        if self.turn > 0.7*ants.turns:
            attack_move()
        
        #run away from losing battles
        defensive_move()

        #collect food
        food_move()

        #attack if few ants
        attack_move()

        #attack hils
        haze_hills()

        #explore
        setup_exploration_map()
        explore_map()

        if ants.time_remaining() > 200 and len(not_used_ants) > 10 :
            explore_map()
        
        if ants.time_remaining() > 100 and len(not_used_ants) > 10:
            explore_map()
        

        if LOGGING:
            start = datetime.datetime.now()
        
        # unblock own hill
        for hill_loc in ants.my_hills():
            if ants.time_remaining() < 10:
                if LOGGING:
                    print 'timeout soon @ unblock own hill'
                break
            if hill_loc in ants.my_ants() and hill_loc not in orders.values():
                for direction in ('s','e','w','n'):
                    if do_move_direction(hill_loc, direction):
                        break

        if LOGGING:
            print datetime.datetime.now() - start
            print "{} unused ants".format(len(not_used_ants))

            
if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
