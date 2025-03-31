"""
Module for managing boxer records and fight statistics in the Boxing application.

This module defines the Boxer data class and provides functions to:
  - Create, retrieve, and delete boxer records in the database.
  - Retrieve a leaderboard of boxers based on fight statistics.
  - Determine the weight class for a boxer.
  - Update a boxer's fight statistics based on match results.

All database operations are handled using SQLite, and logging is integrated 
to track application events and errors.
"""

from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    """Data class representing a boxer.

    Attributes:
        id (int): Unique identifier of the boxer.
        name (str): The name of the boxer.
        weight (int): The weight of the boxer in pounds.
        height (int): The height of the boxer in centimeters.
        reach (float): The reach of the boxer in inches.
        age (int): The age of the boxer.
        weight_class (str, optional): The weight class of the boxer, auto-assigned.
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
         """Automatically assigns the weight class based on the boxer's weight."""
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
     """Creates a new boxer record in the database.

    Validates the input parameters, checks for duplicates, and inserts
    the new boxer into the 'boxers' table.

    Args:
        name (str): The boxer's name.
        weight (int): The boxer's weight. Must be at least 125.
        height (int): The boxer's height. Must be greater than 0.
        reach (float): The boxer's reach in inches. Must be greater than 0.
        age (int): The boxer's age. Must be between 18 and 40.

    Raises:
        ValueError: If any validation fails (e.g., invalid weight, height, reach, or age)
                    or if a boxer with the same name already exists.
        sqlite3.Error: If there is an error during database operations.
    """
    if weight < 125:
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()

    except sqlite3.IntegrityError:
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Deletes a boxer record from the database by its ID.

    Args:
        boxer_id (int): The unique identifier of the boxer to delete.

    Raises:
        ValueError: If no boxer with the given ID is found.
        sqlite3.Error: If there is an error during the deletion process.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

    except sqlite3.Error as e:
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
   """Retrieves the leaderboard of boxers sorted by wins or win percentage.

    The function returns records only for boxers with at least one fight.
    It calculates the win percentage and orders the results accordingly.

    Args:
        sort_by (str, optional): The field to sort by. Must be either "wins" or "win_pct".
                                 Defaults to "wins".

    Returns:
        List[dict[str, Any]]: A list of dictionaries where each dictionary represents a boxer
                              with keys: id, name, weight, height, reach, age, weight_class, fights, wins, win_pct.

    Raises:
        ValueError: If the provided sort_by parameter is invalid.
        sqlite3.Error: If there is an error during the database query.
    """
    
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        return leaderboard

    except sqlite3.Error as e:
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer record by its ID.

    Args:
        boxer_id (int): The unique identifier of the boxer.

    Returns:
        Boxer: A Boxer instance populated with the boxer's details.

    Raises:
        ValueError: If no boxer with the given ID is found.
        sqlite3.Error: If there is an error during the database query.
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer record by its name.

    Args:
        boxer_name (str): The name of the boxer.

    Returns:
        Boxer: A Boxer instance populated with the boxer's details.

    Raises:
        ValueError: If no boxer with the given name is found.
        sqlite3.Error: If there is an error during the database query.
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        raise e


def get_weight_class(weight: int) -> str:
    """Determines the weight class for a boxer based on weight.

    Args:
        weight (int): The weight of the boxer.

    Returns:
        str: The weight class, e.g., 'HEAVYWEIGHT', 'MIDDLEWEIGHT', 'LIGHTWEIGHT', or 'FEATHERWEIGHT'.

    Raises:
        ValueError: If the weight is below 125.
    """
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Updates the fight statistics of a boxer.

    Increments the number of fights, and if the result is 'win', also increments the number of wins.

    Args:
        boxer_id (int): The unique identifier of the boxer.
        result (str): The result of the fight; must be either 'win' or 'loss'.

    Raises:
        ValueError: If the result is not 'win' or 'loss', or if no boxer with the given ID is found.
        sqlite3.Error: If there is an error during the database update.
    """
    if result not in {'win', 'loss'}:
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()

    except sqlite3.Error as e:
        raise e
