#!/usr/bin/env python
from ants import *
from random import choice

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
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

        self.to_explore = {}
        for row in range(ants.rows):
            for col in range(ants.cols):
                if ants.passable((row, col)):
                    self.to_explore[(row, col)] = 0

        self.unseen = []
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.unseen.append((row, col))

    
    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):

        my_ants = ants.my_ants()
        enemy_ants = ants.enemy_ants()

        # track all moves, prevent collisions
        orders = {}
        def do_move_direction(loc, direction):
            new_loc = ants.destination(loc, direction)
            if (ants.unoccupied(new_loc) and new_loc not in orders) and loc not in orders.values():
                ants.issue_order((loc, direction))
                orders[new_loc] = loc
                return True
            else:
                return False

        targets = {}
        def do_move_location(loc, dest):
            directions = ants.direction(loc, dest)
            for direction in directions:
                if do_move_direction(loc, direction):
                    targets[dest] = loc
                    return True
            return False

        def defensive_move():
            for my_ant_loc in my_ants:
                pos_counters = {"n": 0, "e": 0, "s": 0, "w": 0, "enemies": 0, "friends": 0}
                for ant_loc in my_ants:
                    if my_ant_loc == ant_loc:
                        continue
                    if ants.distance_lt(my_ant_loc, ant_loc, 3):
                        pos_counters["friends"] += 1
                        #for direction in ants.direction(my_ant_loc, ant_loc):
                        #    pos_counters[direction] += 2
                for ant_loc, owner in enemy_ants:
                    if ants.distance_lt(my_ant_loc, ant_loc, 8):
                        pos_counters["enemies"] += 1
                        for direction in ants.direction(my_ant_loc, ant_loc):
                            pos_counters[direction] += 1

                if pos_counters["enemies"] > pos_counters["friends"]:
                    min_direction = "n"
                    if pos_counters["e"] < pos_counters[min_direction]:
                        min_direction = "e"
                    if pos_counters["s"] < pos_counters[min_direction]:
                        min_direction = "s"
                    if pos_counters["w"] < pos_counters[min_direction]:
                        min_direction = "w"
                    #directions_counters = [(counter, direction) for direction, counter in pos_counters.items()]

                    
                    if my_ant_loc not in orders.values():
                        do_move_direction(my_ant_loc, min_direction)

        def attack_move():
            for my_ant_loc in my_ants:
                pos_counters = {"n": 0, "e": 0, "s": 0, "w": 0, "friends": 0, "enemies": 0}
                for ant_loc in my_ants:
                    if my_ant_loc == ant_loc:
                        continue
                    if ants.distance_lt(my_ant_loc, ant_loc, 3):
                        pos_counters["friends"] += 1
                        #for direction in ants.direction(my_ant_loc, ant_loc):
                        #    pos_counters[direction] += 1
                for ant_loc, owner in enemy_ants:
                    if ants.distance_lt(my_ant_loc, ant_loc, 6):
                        pos_counters["enemies"] += 1
                        for direction in ants.direction(my_ant_loc, ant_loc):
                            pos_counters[direction] += 1

                if pos_counters["friends"] >= pos_counters["enemies"] and pos_counters["enemies"] > 0:
                    max_direction = "n"
                    if pos_counters["e"] > pos_counters[max_direction]:
                        max_direction = "e"
                    if pos_counters["s"] > pos_counters[max_direction]:
                        max_direction = "s"
                    if pos_counters["w"] > pos_counters[max_direction]:
                        max_direction = "w"
                    #directions_counters = [(counter, direction) for direction, counter in pos_counters.items()]

                    if my_ant_loc not in orders.values():
                        print "atacou"
                        print max_direction
                        do_move_direction(my_ant_loc, max_direction)



        # prevent stepping on own hill
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None

        #run away from losing battles
        defensive_move()

        # find close food
        ant_dist = []
        for food_loc in ants.food():
            for ant_loc in my_ants:
                dist = ants.distance(ant_loc, food_loc)
                ant_dist.append((dist, ant_loc, food_loc))
        ant_dist.sort()
        for dist, ant_loc, food_loc in ant_dist:
            if food_loc not in targets and ant_loc not in targets.values():
                do_move_location(ant_loc, food_loc)
            # check if we still have time left to calculate more orders
            if ants.time_remaining() < 10:
                break

        # attack hills
        for hill_loc, hill_owner in ants.enemy_hills():
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)
        ant_dist = []
        for hill_loc in self.hills:
            for ant_loc in my_ants:
                if ant_loc not in orders.values():
                    dist = ants.distance(ant_loc, hill_loc)
                    ant_dist.append((dist, ant_loc, hill_loc))
        ant_dist.sort()
        for dist, ant_loc, hill_loc in ant_dist:
            do_move_location(ant_loc, hill_loc)


        attack_move()

        
        # explore exotic areas
        for loc in self.to_explore.keys():
            if ants.visible(loc):
                self.to_explore[loc] = 0
            else:
                self.to_explore[loc] += 1
        locs_and_counters = [(counter, loc) for loc, counter in self.to_explore.items()]
        locs_and_counters.sort(reverse=True)
        for counter, exotic_loc in locs_and_counters:
            for ant_loc in my_ants:
                if ant_loc not in orders.values():
                    if do_move_location(ant_loc, exotic_loc):
                        break

        """
        # explore unseen areas
        for loc in self.unseen[:]:
            if ants.visible(loc):
                self.unseen.remove(loc)
        for ant_loc in ants.my_ants():
            if ant_loc not in orders.values():
                unseen_dist = []
                #for unseen_loc in self.unseen:
                    #dist = ants.distance(ant_loc, unseen_loc)
                    #unseen_dist.append((dist, unseen_loc))
                for i in range(2):
                    unseen_loc = choice(self.unseen)
                    dist = ants.distance(ant_loc, unseen_loc)
                    unseen_dist.append((dist, unseen_loc))
                unseen_dist.sort()
                for dist, unseen_loc in unseen_dist:
                    if do_move_location(ant_loc, unseen_loc):
                        break
        """
        
        # unblock own hill
        for hill_loc in ants.my_hills():
            if hill_loc in ants.my_ants() and hill_loc not in orders.values():
                for direction in ('s','e','w','n'):
                    if do_move_direction(hill_loc, direction):
                        break


            
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
