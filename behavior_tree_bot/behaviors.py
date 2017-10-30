import sys, logging
import math
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    """
    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
    """
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    enemy_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(enemy_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return

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
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def attack_close_enemy_planet(state):
    target_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    target_planets = sorted(target_planets, key=lambda p: p.num_ships, reverse=True)
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)
    if not my_planets:
        return False
    for source in my_planets:
        for target in target_planets:
            distance = state.distance(source.ID, target.ID)
            required_ships = target.num_ships + distance * target.growth_rate + 1
            if distance <= 5 and source.num_ships / 1.25 > required_ships:
                issue_order(state, source.ID, target.ID, required_ships)
    return False


def attack_close_neutral_planet(state):
    target_planets = [planet for planet in state.neutral_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)
    if not my_planets:
        return False
    for source in my_planets:
        for target in target_planets:
            distance = state.distance(source.ID, target.ID)
            if distance <= 5 and source.num_ships / 1.25 > target.num_ships:
                issue_order(state, source.ID, target.ID, target.num_ships + 1)
    return False


def wide_spread(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    target_planets = [planet for planet in state.not_my_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    target_planets = iter(sorted(target_planets, key=lambda p: p.num_ships))

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            if target_planet.owner == 0:
                required_ships = target_planet.num_ships + 1
            else:
                required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships * 1.25 > required_ships:
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

    reinforce = []
    weak_planets = [planet for planet in my_planets if strength(planet) < avg]
    incoming = [fleet.destination_planet for fleet in state.enemy_fleets()]
    for planet in weak_planets:
        for fleet in incoming:
            if fleet == planet.ID:
                reinforce.append(planet)

    strong_planets = [planet for planet in my_planets if strength(planet) > avg]

    if (not reinforce) or (not strong_planets):
        return

    reinforce = sorted(reinforce, key=strength)
    strong_planets = sorted(strong_planets, key=strength, reverse=True)

    avg_dist = 0
    for planet in strong_planets:
        for weak in reinforce:
            avg_dist += state.distance(planet.ID, weak.ID)
    avg_dist /= int(len(strong_planets)*len(reinforce))
    avg_dist = math.ceil(int(avg_dist))

    inbound = {}
    for strong_planet in strong_planets:
        for weak_planet in reinforce:
            incoming = 0
            if weak_planet.ID in inbound.keys():
                incoming += inbound[weak_planet.ID]
            need = abs(int(strength(weak_planet) + incoming))
            have = abs(int(strength(strong_planet)))

            if have >= need > 0 and state.distance(strong_planet.ID, weak_planet.ID) <= avg_dist:
                issue_order(state, strong_planet.ID, weak_planet.ID, need)
                if weak_planet.ID not in inbound.keys():
                    inbound[weak_planet.ID] = need
                else:
                    inbound[weak_planet.ID] += need
    return False
