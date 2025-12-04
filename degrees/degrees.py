# >_ uv run --with check50 check50 --local ai50/projects/2024/x/degrees
# >_ uv run --with style50 style50 degrees.py

import csv
import sys
from collections import deque

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # Actors' distance to themselves is 0.
    if source == target:
        return []

    # Doubly linked list for efficient FIFO push/pop operations.
    fifo = deque([(source, None, None)])
    # Set for efficient frontier membership lookup.
    fifo_set = set({source})

    # Map from actor id to (movie_id, parent_id).
    visited = {}

    while len(fifo) > 0:
        # Pop new connection to explore from deque.
        curr_id, connection_movie_id, parent_id = fifo.popleft()

        # Save the movie and connection that led us here.
        visited[curr_id] = (connection_movie_id, parent_id)

        # Push this person's neighbors to the deque for later exploration.
        for movie_id, star_id in neighbors_for_person(curr_id):

            # No need to push neighbors already explored in the past
            # or already present in the deque.
            if star_id in visited or star_id in fifo_set:
                continue

            # If one of the neighbors is the target, we can reconstruct
            # the path from source to this and call it a day.
            if star_id == target:
                path = [(movie_id, star_id)]
                while curr_id != source:
                    prev_movie_id, parent_id = visited[curr_id]
                    path.append((prev_movie_id, curr_id))
                    curr_id = parent_id
                return list(reversed(path))

            # Else, we add them to the deque for later exploration.
            fifo.append((star_id, movie_id, curr_id))
            fifo_set.add(star_id)

    return None


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for star_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, star_id))
    return neighbors


if __name__ == "__main__":
    main()
