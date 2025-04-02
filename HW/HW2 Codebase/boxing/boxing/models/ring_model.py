"""
Module for simulating a boxing ring.

This module defines the RingModel class which manages boxers in a ring,
simulates fights between two boxers based on calculated fighting skills,
updates boxer statistics, and clears the ring after a fight.
"""
import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """Model representing a boxing ring where fights occur.

    This class manages the boxers currently in the ring and provides methods
    to simulate a fight, clear the ring, allow boxers to enter, retrieve boxers,
    and calculate a fighting skill for each boxer.
    """
    def __init__(self):
        """Initializes the RingModel with an empty ring.

        Attributes:
            ring (List[Boxer]): A list of Boxer instances currently in the ring.
        """
        self.ring: List[Boxer] = []
        logger.info("Initialized RingModel with an empty ring.")
        
    def fight(self) -> str:
        """Simulates a fight between the two boxers in the ring and returns the winner's name.

        This method performs the following steps:
          1. Ensures that there are exactly two boxers in the ring.
          2. Retrieves the two boxers.
          3. Calculates a fighting skill for each boxer using an arbitrary formula.
          4. Normalizes the absolute skill difference using a logistic function.
          5. Compares a random number (from get_random) to the normalized difference to determine the winner.
          6. Updates the boxers' fight statistics (win/loss) accordingly.
          7. Clears the ring after the fight.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If there are fewer than two boxers in the ring.
        """
        logger.info("Starting fight simulation.")
        if len(self.ring) < 2:
            logger.error("Fight simulation failed: not enough boxers in the ring.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.debug("Boxers retrieved: %s and %s", boxer_1.name, boxer_2.name)

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.debug("Fighting skills: %s: %f, %s: %f", boxer_1.name, skill_1, boxer_2.name, skill_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))
        logger.debug("Skill delta: %f, normalized delta: %f", delta, normalized_delta)

        random_number = get_random()
        logger.debug("Random number generated: %f", random_number)

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1
        logger.info("Fight result: Winner is %s; Loser is %s", winner.name, loser.name)

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')
        logger.info("Updated boxer stats: %s wins, %s loses", winner.name, loser.name)

        self.clear_ring()
        logger.info("Cleared the ring after the fight.")

        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring.

        If the ring is already empty, this function simply returns.
        """
        if not self.ring:
            logger.warning("clear_ring called but the ring is already empty.")
            return
        self.ring.clear()
        logger.info("Ring has been cleared.")

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to be added to the ring.

        Raises:
            TypeError: If the provided argument is not a Boxer instance.
            ValueError: If the ring is already full (contains two boxers).
        """
        if not isinstance(boxer, Boxer):
            logger.error("Invalid type: Expected 'Boxer', got '%s'.", type(boxer).__name__)
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        logger.info("Attempting to add boxer '%s' to the ring.", boxer.name)
        if len(self.ring) >= 2:
            logger.error("Cannot add boxer: ring is full.")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info("Boxer '%s' added to the ring.", boxer.name)

    def get_boxers(self) -> List[Boxer]:
        """Retrieves the list of boxers currently in the ring.

        Returns:
            List[Boxer]: The list of Boxer instances in the ring.

        Note:
            Currently, this method simply returns the internal ring list.
            Additional logic may be added later if needed.
        """
        if not self.ring:
            pass
        else:
            pass
        logger.debug("Retrieving list of boxers from the ring.")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        # Arbitrary calculations
        """Calculates the fighting skill of a given boxer.

        The fighting skill is calculated using an arbitrary formula that takes into
        account the boxer's weight, the length of their name, reach, and an age modifier.
        The age modifier is:
          - -1 if the boxer is younger than 25,
          - -2 if the boxer is older than 35,
          - 0 otherwise.

        Args:
            boxer (Boxer): The boxer whose fighting skill is to be calculated.

        Returns:
            float: The calculated fighting skill.
        """
        logger.debug("Calculating fighting skill for boxer: %s", boxer.name)
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.debug("Calculated fighting skill for %s: %f", boxer.name, skill)
        return skill
