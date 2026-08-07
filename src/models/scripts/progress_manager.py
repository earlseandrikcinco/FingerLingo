import os
import json
from datetime import datetime, timedelta
from src.utils import config


class ProgressManager:
    def __init__(self, data_file="user_progress.json"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.filepath = os.path.join(base_dir, data_file)

        self.progress_data = self._load_data()

    def _load_data(self):
        """Loads the JSON file, or creates a blank dictionary if it doesn't exist."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_data(self):
        """Writes the current state back to the JSON file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.progress_data, f, indent=4)

    def get_card_state(self, letter):
        """Returns the current state of a specific card. Defaults to 'unseen'."""
        if letter not in self.progress_data:
            return {
                "status": "unseen",  # unseen, learning, learnt, mastered
                "interval_days": 0,
                "last_reviewed": None,
                "next_review": None
            }
        return self.progress_data[letter]

    def mark_as_learnt(self, letter):
        """
        Upgrades a card's status.
        If it's new, it becomes 'learnt'.
        If it's already 'learnt', we increase its interval. If interval > 21, it becomes 'mastered'.
        """
        card = self.get_card_state(letter)
        now = datetime.now()

        if card["status"] in ["unseen", "learning"]:
            card["status"] = "learnt"
            card["interval_days"] = 1
        elif card["status"] == "learnt":
            # Simple SRS: Double the interval on correct recall
            card["interval_days"] = max(1, card["interval_days"] * 2)

            # The 21-day threshold for "Mastered"
            if card["interval_days"] >= 21:
                card["status"] = "mastered"

        # Update timestamps
        card["last_reviewed"] = now.isoformat()
        card["next_review"] = (now + timedelta(days=card["interval_days"])).isoformat()

        self.progress_data[letter] = card
        self._save_data()

    def mark_as_learning(self, letter):
        """
        Called when a user gets a card wrong, or clicks "Practice Again / Reset".
        Drops the card back to 'learning' and resets the SRS interval.
        """
        card = self.get_card_state(letter)
        now = datetime.now()

        card["status"] = "learning"
        card["interval_days"] = 0
        card["last_reviewed"] = now.isoformat()
        card["next_review"] = now.isoformat()

        self.progress_data[letter] = card
        self._save_data()

    def get_learnt_count(self, lesson_name):
        """
        Counts how many cards in a specific lesson are 'learnt' or 'mastered'.
        This powers the '3/5' UI on the Selection Screen.
        """
        lesson_cards = config.LESSONS.get(lesson_name, [])
        count = 0

        for card_data in lesson_cards:
            letter = card_data["letter"]
            state = self.get_card_state(letter)

            # For the lesson progress bar, both 'learnt' and 'mastered' count as complete
            if state["status"] in ["learnt", "mastered"]:
                count += 1

        return count

    def get_due_cards(self):
        """
        Returns a list of all cards across all lessons that are due for review today.
        For the quiz screen.
        """
        due_cards = []
        now = datetime.now()
        for letter, data in self.progress_data.items():
            if data.get("next_review"):
                try:
                    next_review_date = datetime.fromisoformat(data["next_review"])
                    if now >= next_review_date:
                        due_cards.append(letter)
                except ValueError:
                    continue
        return due_cards

    def save(self):
        """Public method to manually trigger a save."""
        self._save_data()
