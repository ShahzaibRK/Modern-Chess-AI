# Shahzaib Khan
# srk161265@gmail.com

import tkinter as tk
from tkinter import messagebox
import re
import math

# --- Move and Piece definitions ---
class Move:
    def __init__(self, start, end, piece):
        self.start = start
        self.end = end
        self.piece = piece
        self.captured = None

class Piece:
    def __init__(self, color):
        self.color = color
    def get_valid_moves(self, board, r, c):
        raise NotImplementedError

class Pawn(Piece):
    def get_valid_moves(self, board, r, c):
        moves, dir_ = [], (1 if self.color == 'white' else -1)
        start = 1 if self.color == 'white' else 6
        # forward moves
        if board.is_empty(r + dir_, c):
            moves.append((r + dir_, c))
            if r == start and board.is_empty(r + 2*dir_, c):
                moves.append((r + 2*dir_, c))
        # captures
        for dc in (-1, 1):
            nr, nc = r + dir_, c + dc
            if board.in_bounds(nr, nc):
                t = board.get_piece(nr, nc)
                if t and t.color != self.color:
                    moves.append((nr, nc))
        return moves

class Knight(Piece):
    def get_valid_moves(self, board, r, c):
        moves = []
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            nr, nc = r+dr, c+dc
            if board.in_bounds(nr, nc):
                t = board.get_piece(nr, nc)
                if not t or t.color != self.color:
                    moves.append((nr, nc))
        return moves

class Bishop(Piece):
    def get_valid_moves(self, board, r, c):
        return board._sliding(r, c, self.color, [(1,1),(1,-1),(-1,1),(-1,-1)])

class Rook(Piece):
    def get_valid_moves(self, board, r, c):
        return board._sliding(r, c, self.color, [(1,0),(-1,0),(0,1),(0,-1)])

class Queen(Piece):
    def get_valid_moves(self, board, r, c):
        return board._sliding(r, c, self.color, [
            (1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)
        ])

class King(Piece):
    def get_valid_moves(self, board, r, c):
        moves = []
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==0 and dc==0: continue
                nr, nc = r+dr, c+dc
                if board.in_bounds(nr, nc):
                    t = board.get_piece(nr, nc)
                    if not t or t.color != self.color:
                        moves.append((nr, nc))
        return moves

# --- Board logic with move/unmove ---
class Board:
    def __init__(self):
        self.grid = [[None]*8 for _ in range(8)]
        self._init_pieces()

    def _init_pieces(self):
        layout = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for c, cls in enumerate(layout):
            self.grid[0][c] = cls('white')
            self.grid[7][c] = cls('black')
        for c in range(8):
            self.grid[1][c] = Pawn('white')
            self.grid[6][c] = Pawn('black')

    def in_bounds(self, r, c): return 0 <= r < 8 and 0 <= c < 8
    def is_empty(self, r, c): return self.in_bounds(r, c) and not self.grid[r][c]
    def get_piece(self, r, c): return self.grid[r][c] if self.in_bounds(r, c) else None

    def _sliding(self, r, c, color, dirs):
        moves = []
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            while self.in_bounds(nr, nc):
                t = self.get_piece(nr, nc)
                if not t:
                    moves.append((nr, nc))
                else:
                    if t.color != color:
                        moves.append((nr, nc))
                    break
                nr += dr; nc += dc
        return moves

    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                p = self.get_piece(r, c)
                if isinstance(p, King) and p.color==color:
                    return (r, c)
        return None

    def in_check(self, color):
        king = self.find_king(color)
        if not king: return False
        kr, kc = king
        for r in range(8):
            for c in range(8):
                p = self.get_piece(r, c)
                if p and p.color!=color and (kr, kc) in p.get_valid_moves(self, r, c):
                    return True
        return False

    def move(self, m):
        sr, sc = m.start; er, ec = m.end
        p = self.grid[sr][sc]
        m.captured = self.grid[er][ec]
        # promotion
        if isinstance(p, Pawn) and (er == 0 or er == 7):
            p = Queen(p.color)
        self.grid[er][ec] = p
        self.grid[sr][sc] = None

    def unmove(self, m):
        sr, sc = m.start; er, ec = m.end
        p = self.grid[er][ec]
        self.grid[sr][sc] = p
        self.grid[er][ec] = m.captured

    def all_valid_moves(self, color):
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.get_piece(r, c)
                if p and p.color==color:
                    for nr, nc in p.get_valid_moves(self, r, c):
                        moves.append(Move((r,c),(nr,nc),p))
        legal = []
        for m in moves:
            self.move(m); ok = not self.in_check(color); self.unmove(m)
            if ok: legal.append(m)
        return legal

    def is_checkmate(self, color): return self.in_check(color) and not self.all_valid_moves(color)
    def is_stalemate(self, color): return not self.in_check(color) and not self.all_valid_moves(color)

    def evaluate(self, ai_color):
        vals = {Pawn:100, Knight:320, Bishop:330, Rook:500, Queen:900, King:20000}
        mobility_w = 10
        score = 0
        for r in range(8):
            for c in range(8):
                p = self.get_piece(r,c)
                if p:
                    v = vals[type(p)]
                    score += v if p.color==ai_color else -v
        score += mobility_w*(len(self.all_valid_moves(ai_color)) - len(self.all_valid_moves('white' if ai_color=='black' else 'black')))
        return score

# --- AI with Minimax + Alpha–Beta ---
class AIPlayer:
    def __init__(self, color, depth=1):
        self.color = color; self.depth = depth
    def get_move(self, board):
        best_val, best_move = -math.inf, None
        for m in board.all_valid_moves(self.color):
            board.move(m)
            val = self.minimax(board, self.depth-1, -math.inf, math.inf, False)
            board.unmove(m)
            if val>best_val: best_val, best_move = val, m
        return best_move

    def minimax(self, board, depth, alpha, beta, max_player):
        if depth==0 or board.is_checkmate(self.color) or board.is_checkmate(self.opponent()):
            return board.evaluate(self.color)
        if max_player:
            max_eval=-math.inf
            for m in board.all_valid_moves(self.color):
                board.move(m)
                eval_ = self.minimax(board, depth-1, alpha, beta, False)
                board.unmove(m)
                max_eval = max(max_eval, eval_)
                alpha = max(alpha, eval_)
                if beta<=alpha: break
            return max_eval
        else:
            min_eval=math.inf; opp=self.opponent()
            for m in board.all_valid_moves(opp):
                board.move(m)
                eval_ = self.minimax(board, depth-1, alpha, beta, True)
                board.unmove(m)
                min_eval = min(min_eval, eval_)
                beta = min(beta, eval_)
                if beta<=alpha: break
            return min_eval

    def opponent(self): return 'white' if self.color=='black' else 'black'

# --- GUI with modern colors & sharp pieces ---
class ChessGame:
    def __init__(self):
        self.board=Board(); self.ai=AIPlayer('black', depth=1)
        self.root=tk.Tk(); self.root.title('Modern Chess AI')
        self.cell=80; self.selected=None; self.highlighted=[]
        self.canvas=tk.Canvas(self.root, width=8*self.cell+40, height=8*self.cell+40, bg='#282c34')
        self.canvas.pack(); self.canvas.bind('<Button-1>', self.on_click)
        frm=tk.Frame(self.root); frm.pack(pady=5)
        self.status=tk.Label(frm,text='Your move (white)'); self.status.grid(row=0,column=0,columnspan=2)
        self.entry=tk.Entry(frm); self.entry.grid(row=1,column=0)
        self.entry.bind('<Return>',self.on_move)
        tk.Button(frm,text='Move',command=self.on_move).grid(row=1,column=1)
        self.draw(); self.root.mainloop()

    def draw(self):
        self.canvas.delete('all'); off=20; cols=['#98c379','#e06c75']
        for r in range(8):
            for c in range(8):
                x0,y0=off+c*self.cell,off+(7-r)*self.cell
                self.canvas.create_rectangle(x0,y0,x0+self.cell,y0+self.cell, fill=cols[(r+c)%2], outline='')
                if (r,c) in self.highlighted:
                    self.canvas.create_rectangle(x0,y0,x0+self.cell,y0+self.cell, outline='yellow', width=4)
                p=self.board.get_piece(r,c)
                if p:
                    glyph=self.unicode(p)
                    self.canvas.create_text(x0+self.cell/2,y0+self.cell/2, text=glyph, font=('Helvetica',int(self.cell*0.8),'bold'), fill='black')
        for i in range(8):
            x=off+i*self.cell+self.cell/2
            self.canvas.create_text(x,off+8*self.cell+10, text=chr(ord('a')+i), font=('Arial',12), fill='white')
            self.canvas.create_text(x,off-10, text=chr(ord('a')+i), font=('Arial',12), fill='white')
            y=off+(7-i)*self.cell+self.cell/2
            self.canvas.create_text(off-10,y, text=str(i+1), font=('Arial',12), fill='white')
            self.canvas.create_text(off+8*self.cell+10,y, text=str(i+1), font=('Arial',12), fill='white')

    def unicode(self,p):
        W={Pawn:'♙',Knight:'♘',Bishop:'♗',Rook:'♖',Queen:'♕',King:'♔'}
        B={Pawn:'♟',Knight:'♞',Bishop:'♝',Rook:'♜',Queen:'♛',King:'♚'}
        return W[type(p)] if p.color=='white' else B[type(p)]

    def parse_move(self,text):
        m=re.fullmatch(r"([a-h][1-8])([a-h][1-8])",text)
        if not m: return None
        s,e=m.group(1),m.group(2)
        return (int(s[1])-1,ord(s[0])-ord('a')),(int(e[1])-1,ord(e[0])-ord('a'))

    def on_move(self,event=None):
        txt=self.entry.get().strip(); self.entry.delete(0,'end')
        parsed=self.parse_move(txt)
        if not parsed:
            messagebox.showerror('Invalid Input','Enter move as e.g. e2e4'); return
        s,e=parsed
        move=next((m for m in self.board.all_valid_moves('white') if m.start==s and m.end==e),None)
        if not move:
            messagebox.showerror('Illegal Move',f'Move {txt} not valid'); return
        self.make_player_move(move)

    def on_click(self,event):
        off=20; x,y=event.x-off,event.y-off
        if x<0 or y<0: return
        c,rp=x//self.cell,y//self.cell; r=7-rp
        if not self.board.in_bounds(r,c): return
        if self.selected is None:
            p=self.board.get_piece(r,c)
            if p and p.color=='white':
                self.selected=(r,c)
                self.highlighted=[m.end for m in self.board.all_valid_moves('white') if m.start==self.selected]
                self.status.config(text=f"Selected {chr(ord('a')+c)}{r+1}"); self.draw()
        else:
            if (r,c) in self.highlighted:
                move=next(m for m in self.board.all_valid_moves('white') if m.start==self.selected and m.end==(r,c))
                self.make_player_move(move)
            else:
                self.selected=None; self.highlighted=[]
                self.status.config(text='Your move (white)'); self.draw()

    def make_player_move(self,move):
        self.board.move(move)
        self.selected=None; self.highlighted=[]
        if self.board.is_checkmate('black'):
            self.draw(); messagebox.showinfo('Game Over','You win!'); return
        if self.board.is_stalemate('black'):
            self.draw(); messagebox.showinfo('Game Over','Draw!'); return
        self.draw(); self.status.config(text='AI is thinking...'); self.root.config(cursor='watch'); self.root.update()
        ai_move=self.ai.get_move(self.board)
        self.root.config(cursor='')
        if ai_move:
            self.board.move(ai_move)
            if self.board.is_checkmate('white'):
                self.draw(); messagebox.showinfo('Game Over','AI wins!'); return
            if self.board.is_stalemate('white'):
                self.draw(); messagebox.showinfo('Game Over','Draw!'); return
        self.draw(); self.status.config(text='Your move (white)')

if __name__=='__main__':
    ChessGame()
