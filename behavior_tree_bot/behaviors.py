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
    attacked_planets = []
    for fleet in state.my_fleets():
        attacked_planets.append(fleet.destination_planet)
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if strongest_planet == None:
        return False
    target_planets = state.enemy_planets()
    for target in target_planets:
        if target.ID in attacked_planets:
            continue
        distance = state.distance(strongest_planet.ID, target.ID)
        if distance <= 5 and strongest_planet.num_ships / 2 > target.num_ships:
            logging.info('found a candidate')
            logging.info(strongest_planet.num_ships)
            logging.info(target.num_ships)
            return issue_order(state, strongest_planet.ID, target.ID, strongest_planet.num_ships / 2)
    return False


def attack_close_neutral_planet(state):
    attacked_planets = []
    for fleet in state.my_fleets():
        attacked_planets.append(fleet.destination_planet)
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if strongest_planet == None:
        return False
    target_planets = state.neutral_planets()
    logging.info(attacked_planets)
    logging.info(target_planets)
    for target in target_planets:
        if target.ID in attacked_planets:
            continue
        distance = state.distance(strongest_planet.ID, target.ID)
        if distance <= 5 and strongest_planet.num_ships / 2 > target.num_ships:
            logging.info('found a candidate')
            logging.info(strongest_planet.num_ships)
            logging.info(target.num_ships)
            return issue_order(state, strongest_planet.ID, target.ID, target.num_ships + 1)
    return False
