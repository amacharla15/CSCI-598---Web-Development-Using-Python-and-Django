from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import ChessForm, JoinForm, LoginForm
from .models import Board

@login_required(login_url='/login/')
def chess_view(request):
    # Initialize turn in session if not already set (white starts)
    if "turn" not in request.session:
        request.session["turn"] = "white"
    page_data = {"board": [], "chess_form": ChessForm(), "turn": request.session["turn"]}

    if request.method == 'POST':
        # If the user pressed the New Game or Reset button.
        if 'new_game' in request.POST or 'reset' in request.POST:
            print("[DEBUG] Resetting board due to new_game/reset button.")
            newGame(request)
            request.session["turn"] = "white"  # Reset turn to white
        else:
            # Process a move.
            chess_form = ChessForm(request.POST)
            if chess_form.is_valid():
                source = chess_form.cleaned_data["source"]
                destination = chess_form.cleaned_data["destination"]
                print(f"[DEBUG] Attempting move from {source} to {destination}")
                
                # Check if the piece at source matches the current turn.
                piece = Board.get_piece_at(request.user, source)
                if piece.strip() == "" or piece == "&nbsp;":
                    print("[DEBUG] No piece at source.")
                    page_data["error"] = "No piece at the source square."
                elif piece in Board.PIECE_MAPPING:
                    _, piece_color = Board.PIECE_MAPPING[piece]
                    if piece_color != request.session["turn"]:
                        print(f"[DEBUG] Illegal move: It is {request.session['turn']}'s turn, not {piece_color}'s.")
                        page_data["error"] = f"It is {request.session['turn']}'s turn."
                    else:
                        # Use the model's move_piece method.
                        success, message = Board.move_piece(request.user, source, destination)
                        print(f"[DEBUG] Move result: {success}, {message}")
                        if success:
                            # Switch turn after a successful move.
                            request.session["turn"] = "black" if request.session["turn"] == "white" else "white"
                        else:
                            page_data["error"] = message
                else:
                    print("[DEBUG] Unrecognized piece.")
                    page_data["error"] = "Unrecognized piece."
            else:
                print("[DEBUG] Form errors:", chess_form.errors)
                page_data["chess_form"] = chess_form
    else:
        # For GET requests: if the board is empty, initialize it.
        if Board.objects.filter(user=request.user).count() == 0:
            print("[DEBUG] Board is empty on GET. Initializing new game.")
            newGame(request)
            request.session["turn"] = "white"  # Ensure turn is set on new game

    # Build the board as a list-of-lists (each inner list represents one row).
    for rank in range(8, 0, -1):
        row_data = []
        for file in "abcdefgh":
            loc = f"{file}{rank}"
            try:
                record = Board.objects.get(user=request.user, location=loc)
                row_data.append(record.value)
            except Board.DoesNotExist:
                row_data.append("&nbsp;")
        page_data["board"].append(row_data)

    return render(request, 'app1/chess.html', page_data)

def newGame(request):
    """
    Reinitializes the board for the user with the standard chess starting layout.
    """
    print("[DEBUG] Initializing new game for user:", request.user)
    initial_board = {
        "8": ["&#9820;", "&#9822;", "&#9821;", "&#9819;", "&#9818;", "&#9821;", "&#9822;", "&#9820;"],
        "7": ["&#9823;"] * 8,
        "6": ["&nbsp;"] * 8,
        "5": ["&nbsp;"] * 8,
        "4": ["&nbsp;"] * 8,
        "3": ["&nbsp;"] * 8,
        "2": ["&#9817;"] * 8,
        "1": ["&#9814;", "&#9816;", "&#9815;", "&#9813;", "&#9812;", "&#9815;", "&#9816;", "&#9814;"]
    }
    # Delete any existing board for this user.
    Board.objects.filter(user=request.user).delete()
    files = list("abcdefgh")
    for rank, pieces in initial_board.items():
        for i, piece in enumerate(pieces):
            location = f"{files[i]}{rank}"
            Board(user=request.user, location=location, value=piece).save()
    print("[DEBUG] New game initialized.")

def rules(request):
    return render(request, 'app1/rules.html')

def about(request):
    return render(request, 'app1/about.html')

@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return redirect("/login/")

def history(request):
    return render(request, 'app1/history.html')

def user_login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect("/")
                else:
                    return HttpResponse("Your account is not active.")
            else:
                print(f"[DEBUG] Login failed for {username}")
                return render(request, 'app1/login.html', {"login_form": LoginForm()})
    else:
        return render(request, 'app1/login.html', {"login_form": LoginForm()})

def join(request):
    if request.method == "POST":
        join_form = JoinForm(request.POST)
        if join_form.is_valid():
            user = join_form.save()
            user.set_password(user.password)
            user.save()
            return redirect("/")
        else:
            return render(request, 'app1/join.html', {"join_form": join_form})
    else:
        return render(request, 'app1/join.html', {"join_form": JoinForm()})
