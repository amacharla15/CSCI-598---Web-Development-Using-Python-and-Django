CSCI 598: SSR/MPA Single-Player Chess Game
Overview

This project is a full-stack Django web application implementing a single-player chess game with server-side rendering and per-user game state persistence.
It replaces the JavaScript-based client-side logic from Assignment 2 with a backend-driven approach, using Django for form handling, state management, and rendering, and Bootstrap for styling.

Features

Multi-Page Application (MPA) with:

Home (Chessboard & Move Controls)

Chess History

Chess Rules

About Page (with personal image)

User Authentication:

Join (sign-up)

Login

Logout

Per-User Chessboard State stored in the database and preserved across sessions.

Server-side Move Handling via HTTP POST form submissions with validation.

Bootstrap Navigation Bar and shared template components.

Responsive Layout using Bootstrap grid system.

Requirements Implemented

Pages & Navigation

"" → Home (Chessboard)

/history → Chess History

/rules → Chess Rules

/about → About

Django MVC Structure

urls.py for routing.

views.py for request handling.

Templates for each page using a shared base template.

Backend Game State

Model for storing per-user game state.

Preserves board state on navigation and re-login.

Form Handling

Move submission through POST requests.

Server-side form validation and error reporting.

Static & Media

CSS and JavaScript in static/.

About page image stored in static folder.

Deployment

Dockerized and deployed to Google Cloud Platform (GCP) on a single VM instance.

Technology Stack

Backend: Django (Python)

Frontend: Bootstrap (HTML/CSS), Django Templates

Database: SQLite / PostgreSQL (depending on deployment)

Deployment: Docker, Google Cloud Platform (GCP) VM
