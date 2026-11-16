from collections import deque
from heapq import nsmallest
import unittest


class SocialGraph:

    def __init__(self):
        # Each key is a user. Its set contains users they follow.
        self._following: dict[str, set[str]] = {}

    @staticmethod
    def _validate_user_id(user_id: str) -> None:
        """Check that a user ID is a non-empty string."""
        if not isinstance(user_id, str):
            raise TypeError("User IDs must be strings.")
        if not user_id.strip():
            raise ValueError("User IDs cannot be empty.")

    def add_user(self, user_id: str) -> bool:
        """Add a user. Return True if new, or False if already present."""
        self._validate_user_id(user_id)

        if user_id in self._following:
            return False

        self._following[user_id] = set()
        return True

    def add_follow(self, follower_id: str, followed_id: str) -> bool:
        """
        Add a directed follow relationship.

        Return True if the relationship is new, or False if it already exists.
        """
        self._validate_user_id(follower_id)
        self._validate_user_id(followed_id)

        if follower_id == followed_id:
            raise ValueError("A user cannot follow themselves.")

        self.add_user(follower_id)
        self.add_user(followed_id)

        if followed_id in self._following[follower_id]:
            return False

        self._following[follower_id].add(followed_id)
        return True

    def remove_follow(self, follower_id: str, followed_id: str) -> bool:
        """Remove a relationship. Return False if it was not present."""
        self._validate_user_id(follower_id)
        self._validate_user_id(followed_id)

        following = self._following.get(follower_id)
        if following is None or followed_id not in following:
            return False

        following.remove(followed_id)
        return True

    def remove_user(self, user_id: str) -> bool:
        """Remove a user and their relationships from the graph."""
        self._validate_user_id(user_id)

        if user_id not in self._following:
            return False

        del self._following[user_id]

        # Remove this user from every other user's follow set.
        for following in self._following.values():
            following.discard(user_id)

        return True

    def is_following(self, follower_id: str, followed_id: str) -> bool:
        """Return whether one user follows another."""
        self._validate_user_id(follower_id)
        self._validate_user_id(followed_id)

        return followed_id in self._following.get(follower_id, set())

    def get_following(self, user_id: str) -> tuple[str, ...]:
        """Return a user's followed accounts in alphabetical order."""
        self._validate_user_id(user_id)

        if user_id not in self._following:
            raise KeyError(f"User {user_id!r} is not in the graph.")

        return tuple(sorted(self._following[user_id]))

    def reachable_users(self, start_user: str) -> tuple[str, ...]:
        """
        Return users reachable by following directed relationships.

        The starting user is included. Breadth-first search visits users in a
        deterministic order so the demonstration produces consistent output.
        """
        self._validate_user_id(start_user)

        if start_user not in self._following:
            raise KeyError(f"User {start_user!r} is not in the graph.")

        visited = {start_user}
        visit_queue = deque([start_user])
        traversal_order = []

        while visit_queue:
            current_user = visit_queue.popleft()
            traversal_order.append(current_user)

            for neighbor in sorted(self._following[current_user]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    visit_queue.append(neighbor)

        return tuple(traversal_order)

    def top_users_by_connections(self, limit: int) -> list[tuple[str, int]]:
        """
        Return up to `limit` users ranked by number of outgoing relationships.

        Ties are sorted alphabetically by user ID.
        """
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("The limit must be an integer.")
        if limit < 0:
            raise ValueError("The limit cannot be negative.")

        ranked_users = nsmallest(
            limit,
            self._following,
            key=lambda user_id: (
                -len(self._following[user_id]),
                user_id,
            ),
        )

        return [
            (user_id, len(self._following[user_id]))
            for user_id in ranked_users
        ]


def build_demo_graph() -> SocialGraph:
    """Create a small graph used by the demonstration and tests."""
    graph = SocialGraph()

    graph.add_follow("alice", "bob")
    graph.add_follow("alice", "carol")
    graph.add_follow("bob", "diana")
    graph.add_follow("carol", "diana")
    graph.add_follow("diana", "erin")

    return graph


class SocialGraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = build_demo_graph()

    def test_add_user_and_follow_relationship(self):
        self.assertFalse(self.graph.add_user("alice"))
        self.assertTrue(self.graph.add_user("frank"))

        self.assertFalse(self.graph.add_follow("alice", "bob"))
        self.assertTrue(self.graph.add_follow("alice", "frank"))
        self.assertTrue(self.graph.is_following("alice", "frank"))
        self.assertFalse(self.graph.is_following("frank", "alice"))

    def test_remove_follow_and_unknown_user(self):
        self.assertTrue(self.graph.remove_follow("alice", "bob"))
        self.assertFalse(self.graph.is_following("alice", "bob"))

        # Removing a relationship that is already absent is safe.
        self.assertFalse(self.graph.remove_follow("alice", "bob"))

        # Searching for a relationship from an unknown user returns False.
        self.assertFalse(self.graph.is_following("unknown", "alice"))

        # Requesting a connection list for an unknown user raises KeyError.
        with self.assertRaises(KeyError):
            self.graph.get_following("unknown")

    def test_breadth_first_traversal_is_directed_and_deterministic(self):
        self.assertEqual(
            self.graph.reachable_users("alice"),
            ("alice", "bob", "carol", "diana", "erin"),
        )

        # Relationships point toward followed users; traversal does not reverse them.
        self.assertEqual(
            self.graph.reachable_users("erin"),
            ("erin",),
        )

    def test_remove_user_removes_incoming_and_outgoing_relationships(self):
        self.assertTrue(self.graph.remove_user("diana"))
        self.assertFalse(self.graph.is_following("bob", "diana"))
        self.assertFalse(self.graph.is_following("carol", "diana"))
        self.assertFalse(self.graph.remove_user("diana"))

    def test_top_users_and_limit_edge_cases(self):
        self.assertEqual(
            self.graph.top_users_by_connections(3),
            [("alice", 2), ("bob", 1), ("carol", 1)],
        )
        self.assertEqual(len(self.graph.top_users_by_connections(10)), 5)
        self.assertEqual(self.graph.top_users_by_connections(0), [])

        with self.assertRaises(ValueError):
            self.graph.top_users_by_connections(-1)

        with self.assertRaises(TypeError):
            self.graph.top_users_by_connections(1.5)

        with self.assertRaises(TypeError):
            self.graph.top_users_by_connections(True)

    def test_invalid_user_ids_and_self_follow(self):
        with self.assertRaises(ValueError):
            self.graph.add_user("")

        with self.assertRaises(TypeError):
            self.graph.add_user(None)

        new_graph = SocialGraph()
        with self.assertRaises(ValueError):
            new_graph.add_follow("sam", "sam")

        # A rejected self-follow should not add the user as a side effect.
        self.assertEqual(new_graph._following, {})


def run_demo():
    graph = build_demo_graph()

    print("\n=== Social Network Graph PoC ===")
    print(f"Users in graph: {len(graph._following)}")
    print(f"Alice follows: {graph.get_following('alice')}")
    print(f"Does Alice follow Diana? {graph.is_following('alice', 'diana')}")
    print(f"Users reachable from Alice: {graph.reachable_users('alice')}")
    print(
        "Top 3 users by outgoing connections: "
        f"{graph.top_users_by_connections(3)}"
    )

    removed = graph.remove_follow("carol", "diana")
    print(f"Removed Carol's follow of Diana: {removed}")
    print(f"Does Carol follow Diana now? {graph.is_following('carol', 'diana')}")


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
    run_demo()