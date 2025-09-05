from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    """
    A model to store the value of a single square on the chess board.
    'location' uses standard algebraic notation (e.g., "a8", "b8", ..., "h1").
    'value' holds the HTML entity for the piece, or "&nbsp;" for an empty square.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=4)
    value = models.CharField(max_length=20)

    class Meta:
        unique_together = ("user", "location")

    def __str__(self):
        return f"{self.user.username} - {self.location}: {self.value}"

    @staticmethod
    def square_to_indices(square):
        """
        Converts a square like "e2" into (row, col) indices.
        Row 0 is the top (rank 8) and row 7 is the bottom (rank 1).
        """
        if len(square) != 2:
            raise ValueError("Square must be a 2-character string, e.g. e2.")
        file = square[0].lower()
        rank = square[1]
        col = ord(file) - ord('a')
        try:
            row = 8 - int(rank)
        except ValueError:
            raise ValueError("Rank must be a number between 1 and 8.")
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError("Square out of bounds.")
        return row, col

    # Mapping of HTML entity to (piece type, color)
    PIECE_MAPPING = {
        "&#9817;": ("pawn", "white"),
        "&#9814;": ("rook", "white"),
        "&#9816;": ("knight", "white"),
        "&#9815;": ("bishop", "white"),
        "&#9813;": ("queen", "white"),
        "&#9812;": ("king", "white"),
        "&#9823;": ("pawn", "black"),
        "&#9820;": ("rook", "black"),
        "&#9822;": ("knight", "black"),
        "&#9821;": ("bishop", "black"),
        "&#9819;": ("queen", "black"),
        "&#9818;": ("king", "black"),
    }

    @classmethod
    def get_piece_at(cls, user, square):
        """
        Returns the piece (HTML entity) at the given square for the user.
        If no record is found, returns "&nbsp;" (empty).
        """
        try:
            record = cls.objects.get(user=user, location=square)
            return record.value
        except cls.DoesNotExist:
            return "&nbsp;"

    @classmethod
    def is_path_clear(cls, user, source, destination):
        """
        Checks if the path between source and destination is clear (excluding destination).
        This is used for sliding pieces (bishop, rook, queen).
        """
        src_row, src_col = cls.square_to_indices(source)
        dst_row, dst_col = cls.square_to_indices(destination)
        delta_row = dst_row - src_row
        delta_col = dst_col - src_col

        steps = max(abs(delta_row), abs(delta_col))
        if steps <= 1:
            return True  # No intermediate squares to check

        step_row = delta_row // steps
        step_col = delta_col // steps

        # Check every square between source and destination
        for step in range(1, steps):
            r = src_row + step * step_row
            c = src_col + step * step_col
            rank = str(8 - r)
            file = chr(c + ord('a'))
            square = f"{file}{rank}"
            if cls.get_piece_at(user, square).strip() not in ("", "&nbsp;"):
                return False
        return True

    @classmethod
    def validate_move(cls, user, source, destination, piece):
        """
        Validates if a move from source to destination is legal for the given piece.
        Returns a tuple (True, "") if valid, or (False, "error message") if invalid.
        """
        try:
            src_row, src_col = cls.square_to_indices(source)
            dst_row, dst_col = cls.square_to_indices(destination)
        except ValueError as e:
            return (False, str(e))

        if piece not in cls.PIECE_MAPPING:
            return (False, "Unknown piece type.")

        piece_type, piece_color = cls.PIECE_MAPPING[piece]

        # Check if destination has a piece of the same color
        dest_piece = cls.get_piece_at(user, destination)
        if dest_piece.strip() not in ("", "&nbsp;"):
            if dest_piece in cls.PIECE_MAPPING:
                _, dest_color = cls.PIECE_MAPPING[dest_piece]
                if dest_color == piece_color:
                    return (False, "Cannot capture your own piece.")

        d_row = dst_row - src_row
        d_col = dst_col - src_col

        # Pawn move
        if piece_type == "pawn":
            # Determine forward direction and starting row
            direction = -1 if piece_color == "white" else 1
            start_row = 6 if piece_color == "white" else 1

            # Single forward move
            if d_col == 0 and d_row == direction:
                if dest_piece.strip() in ("", "&nbsp;"):
                    return (True, "")
                else:
                    return (False, "Pawn cannot move forward into an occupied square.")
            # Double forward move from starting position
            elif d_col == 0 and d_row == 2 * direction and src_row == start_row:
                intermediate_row = src_row + direction
                intermediate_square = f"{chr(src_col + ord('a'))}{8 - intermediate_row}"
                if (cls.get_piece_at(user, intermediate_square).strip() in ("", "&nbsp;") and 
                    dest_piece.strip() in ("", "&nbsp;")):
                    return (True, "")
                else:
                    return (False, "Path is not clear for pawn's double move.")
            # Diagonal capture
            elif abs(d_col) == 1 and d_row == direction:
                if dest_piece.strip() not in ("", "&nbsp;"):
                    return (True, "")
                else:
                    return (False, "Pawn diagonal move must capture an enemy piece.")
            return (False, "Illegal pawn move.")

        # Knight move: L-shape moves
        if piece_type == "knight":
            if (abs(d_row), abs(d_col)) in [(1, 2), (2, 1)]:
                return (True, "")
            return (False, "Illegal knight move.")

        # Bishop move: diagonal movement
        if piece_type == "bishop":
            if abs(d_row) == abs(d_col) and cls.is_path_clear(user, source, destination):
                return (True, "")
            return (False, "Illegal bishop move or path is blocked.")

        # Rook move: horizontal or vertical
        if piece_type == "rook":
            if (d_row == 0 or d_col == 0) and cls.is_path_clear(user, source, destination):
                return (True, "")
            return (False, "Illegal rook move or path is blocked.")

        # Queen move: combination of rook and bishop
        if piece_type == "queen":
            if ((abs(d_row) == abs(d_col)) or (d_row == 0 or d_col == 0)) and cls.is_path_clear(user, source, destination):
                return (True, "")
            return (False, "Illegal queen move or path is blocked.")

        # King move: one square any direction
        if piece_type == "king":
            if max(abs(d_row), abs(d_col)) == 1:
                return (True, "")
            return (False, "Illegal king move.")

        return (False, "Move not recognized.")

    @classmethod
    def reset_game(cls, user):
        """
        Resets the board for the given user with the standard chess initial layout.
        Layout (rank 8 at top, rank 1 at bottom):
          - Rank 8: Black back rank.
          - Rank 7: Black pawns.
          - Ranks 6-3: Empty.
          - Rank 2: White pawns.
          - Rank 1: White back rank.
        """
        initial_board = {
             "1": ["&#9820;", "&#9822;", "&#9821;", "&#9819;", "&#9818;", "&#9821;", "&#9822;", "&#9820;"],
             "2": ["&#9823;"] * 8,
             "3": ["&nbsp;"] * 8,
             "4": ["&nbsp;"] * 8,
             "5": ["&nbsp;"] * 8,
             "6": ["&nbsp;"] * 8,
             "7": ["&#9817;"] * 8,
             "8": ["&#9814;", "&#9816;", "&#9815;", "&#9813;", "&#9812;", "&#9815;", "&#9816;", "&#9814;"]
        }
        # Delete any existing board for this user
        cls.objects.filter(user=user).delete()
        files = list("abcdefgh")
        for rank, pieces in initial_board.items():
            for i, piece in enumerate(pieces):
                location = f"{files[i]}{rank}"
                cls.objects.create(user=user, location=location, value=piece)

    @classmethod
    def move_piece(cls, user, source, destination):
        """
        Moves a piece for the given user from source to destination.
        Returns a tuple (success, message).
        """
        try:
            record_src = cls.objects.get(user=user, location=source)
        except cls.DoesNotExist:
            return (False, "Source square not found.")

        piece = record_src.value
        if piece.strip() == "" or piece == "&nbsp;":
            return (False, "No piece at source.")

        # Validate the move using our new logic.
        valid, message = cls.validate_move(user, source, destination, piece)
        if not valid:
            return (False, message)

        # Remove any piece at destination (force replacement).
        cls.objects.filter(user=user, location=destination).delete()

        # Clear the source square.
        record_src.value = "&nbsp;"
        record_src.save()

        # Place the piece at the destination.
        cls.objects.create(user=user, location=destination, value=piece)
        return (True, "Move completed.")
