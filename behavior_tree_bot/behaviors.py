import sys, logging
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        logging.info(strongest_planet.num_ships)
        logging.info(weakest_planet.num_ships)
        logging.info(state.distance(strongest_planet.ID, weakest_planet.ID))
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        logging.info(strongest_planet.num_ships)
        logging.info(weakest_planet.num_ships)
        logging.info(state.distance(strongest_planet.ID, weakest_planet.ID))
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def attack_close_enemy_planet(state):
    #attacked_planets = []
    #for fleet in state.my_fleets():
    #    attacked_planets.append(fleet.destination_planet)
#    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
#    if strongest_planet == None:
#        return False
    target_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    target_planets = iter(sorted(target_planets, key=lambda p: p.num_ships, reverse=True))

    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    if not my_planets:
        return False
    target_planets = state.enemy_planets()
    for planet in my_planets:
        for target in target_planets:
#            if target.ID in attacked_planets:
#                continue
            distance = state.distance(planet.ID, target.ID)
            if distance <= 5 and planet.num_ships / 2 > target.num_ships:
                #logging.info('found a candidate')
                #logging.info(strongest_planet.num_ships)
                #logging.info(target.num_ships)
                return issue_order(state, planet.ID, target.ID, planet.num_ships / 2)
    return False
#  for target in target_planets:
#      if target.ID in attacked_planets:
#          continue
#      distance = state.distance(strongest_planet.ID, target.ID)
#      if distance <= 5 and strongest_planet.num_ships / 2 > target.num_ships:
#           logging.info('found a candidate')
#            logging.info(strongest_planet.num_ships)
#            logging.info(target.num_ships)
#            return issue_order(state, strongest_planet.ID, target.ID, strongest_planet.num_ships / 2)


def attack_close_neutral_planet(state):
    attacked_planets = []
    for fleet in state.my_fleets():
        attacked_planets.append(fleet.destination_planet)
    #strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    #if strongest_planet is None:
    #    return False
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))
    if not my_planets:
        return False
    target_planets = state.neutral_planets()
    for source in my_planets:
        for target in target_planets:
            if target.ID in attacked_planets:
                continue
            distance = state.distance(source.ID, target.ID)
            if distance <= 5 and source.num_ships / 2 > target.num_ships:
                #logging.info('found a candidate')
                #logging.info(source.num_ships)
                #logging.info(target.num_ships)
                return issue_order(state, source.ID, target.ID, target.num_ships + 1)
    return False
#for target in target_planets:
#    if target.ID in attacked_planets:
#        continue
#    distance = state.distance(strongest_planet.ID, target.ID)
#    if distance <= 5 and strongest_planet.num_ships / 2 > target.num_ships:
#        logging.info('found a candidate')
#        logging.info(strongest_planet.num_ships)
#        logging.info(target.num_ships)
#        return issue_order(state, strongest_planet.ID, target.ID, target.num_ships + 1)


def wide_spread(state):
    """
    attacked_planets = []
    for fleet in state.my_fleets():
        attacked_planets.append(fleet.destination_planet)
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if strongest_planet is None:
        return False
    candidates = [x for x in state.neutral_planets() if x.num_ships < strongest_planet.num_ships/10]
    if not candidates:
        return False
    else:
        for candidate in candidates:
            if candidate.ID in attacked_planets:
                continue
            elif state.distance(strongest_planet.ID, candidate.ID) < 8:
                return issue_order(state, strongest_planet.ID, candidate.ID, candidate.num_ships + 1)
            else:
                return False
    """

    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    target_planets = [planet for planet in state.not_my_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    target_planets = iter(sorted(target_planets, key=lambda p: p.num_ships, reverse=True))

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            if target_planet.owner == 0:
                required_ships = target_planet.num_ships + 1
            else:
                required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships / 3 > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                target_planet = next(target_planets)

    except StopIteration:
        return False
    return False

def defend(state):
    my_planets = [planet for planet in state.my_planets()]
    if not my_planets:
        return

    def strength(p):
        return p.num_ships \
               + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    avg = sum(strength(planet) for planet in my_planets) / len(my_planets)

    weak_planets = [planet for planet in my_planets if strength(planet) < avg]
    strong_planets = [planet for planet in my_planets if strength(planet) > avg]

    if (not weak_planets) or (not strong_planets):
        return

    weak_planets = iter(sorted(weak_planets, key=strength))
    strong_planets = iter(sorted(strong_planets, key=strength, reverse=True))

 #   distances = {}
 #   closest = {}
 #   for planet in weak_planets:
 #       for strong in strong_planets:
 #           distance = state.distance(planet.ID, strong.ID)
 #           if planet.ID not in distances.keys() or distance < distances[planet.ID]:
 #               distances[planet.ID] = distance
 #               closest[planet.ID] = strong.ID

    avg_dist = 0
    count = 0
    for planet in strong_planets:
        for weak in weak_planets:
            avg_dist += state.distance(planet.ID, weak.ID)
            count += 1
    avg_dist /= count
    logging.info("dist")
    logging.info(avg_dist)
    try:
        weak_planet = next(weak_planets)
        strong_planet = next(strong_planets)
        while True:
            need = abs(int(strength(weak_planet)))
            have = abs(int(strength(strong_planet)))
            logging.info("need")
            logging.info(need)
            logging.info("have")
            logging.info(have)

            if have >= need > 0 and state.distance(strong_planet.ID, weak_planet.ID) <= avg_dist:
                logging.info("Issuing order")
                issue_order(state, strong_planet.ID, weak_planet.ID, need)
                weak_planet = next(weak_planets)
            #elif have > 0:
            #    issue_order(state, strong_planet.ID, weak_planet.ID, have)
            #    strong_planet = next(strong_planets)
            else:
                strong_planet = next(strong_planets)

    except StopIteration:
        return

    return False
