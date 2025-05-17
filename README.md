Modern Chess AI

A Python-based chess engine with a sleek Tkinter GUI featuring a red and green themed board and modern Unicode glyphs. It uses Minimax with Alpha–Beta pruning, piece–square tables, and move/unmove optimizations for fast, responsive play.

Features

Adjustable AI Depth: Configure AI search depth for varying difficulty and performance.

Fast Move Generation: In-place move/unmove reduces overhead compared to deep copies.

Modern UI: Red/green color scheme, Helvetica glyphs, and status updates.

Algebraic Notation Input: Enter moves like e2e4 via text box or click-to-move.

Check/Checkmate Detection: Automatic detection and end‑game dialogs.

Prerequisites

Python 3.7 or higher

Tkinter (usually included with standard Python)

Installation

Clone this repository:

git clone https://github.com/ShahzaibRK/Modern-Chess-AI
cd ModernChessAI

(Optional) Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # Unix/macOS
venv\\Scripts\\activate  # Windows

Install any dependencies (if you have extra modules):

pip install -r requirements.txt

Usage

Ensure SK_chess.py is executable or run via Python:

python SK_chess.py

The GUI window will open:

Click on a white piece to select, then click an empty or enemy square to move.

Or type an algebraic move (e.g. e2e4) in the input box and press Move or Enter.

Watch the AI’s response. Adjust difficulty by editing the depth parameter in the AIPlayer initialization (lower = faster, weaker; higher = slower, stronger).
