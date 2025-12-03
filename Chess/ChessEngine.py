class GameState():
    def __init__(self):
        # * Board is 8x8 and 2d
        # * b stands for black and white stands for white
        # * second character stands for the type of the piece

        self.board = [  #libraries could have been more efficient but this one also works
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR" ], # and more concrete
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp" ],
            ["--", "--", "--", "--", "--", "--", "--", "--" ],
            ["--", "--", "--", "--", "--", "--", "--", "--" ],
            ["--", "--", "--", "--", "--", "--", "--", "--" ],
            ["--", "--", "--", "--", "--", "--", "--", "--" ],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR" ]
        ]

        self.moveFunctions = {'p' : self.getPawnMoves,  'R' : self.getRookMoves,  'N': self.getKnightMoves,
                              'B': self.getBishopMoves,   'Q': self.getQueenMoves,   'K': self.getKingMoves }
        #This enables us to call all pieces and their possible move functions withoud overwriting them

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        #self.promotionChoice = 'Q'
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightLog = [
            CastleRights(
                self.currentCastlingRights.wks,
                self.currentCastlingRights.bks,
                self.currentCastlingRights.wqs,
                self.currentCastlingRights.bqs,
            )
        ]
        self.whiteKinginCheck = False
        self.blackKinginCheck = False


    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove #swapping the players
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # to the right: king side castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                    move.endCol + 1
                    ]
                self.board[move.endRow][move.endCol + 1] = "--"  # remove the old rook
            elif move.endCol - move.startCol == -2:  # to the left: queen side castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                    move.endCol - 2
                    ]
                self.board[move.endRow][move.endCol - 2] = "--"  # remove the old rook
            # update the enpassantPossibleLog
        self.enpassantPossibleLog.append(self.enpassantPossible)
        self.updateCastlRights(move)
        self.castleRightLog.append(
            CastleRights(
                self.currentCastlingRights.wks,
                self.currentCastlingRights.bks,
                self.currentCastlingRights.wqs,
                self.currentCastlingRights.bqs,
            )
        )


    def undoMove(self):
        if(len(self.moveLog) != 0):
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            self.castleRightLog.pop()

            newRights = self.castleRightLog[-1]
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # to the right: king side castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                        move.endCol - 1
                        ]
                    self.board[move.endRow][move.endCol - 1] = "--"
                elif (
                        move.endCol - move.startCol == -2):  # to the left: queen side castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][
                        move.endCol + 1
                        ]
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.checkmate = False
            self.stalemate = False

    def updateCastlRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                if move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                if move.startCol == 7:
                    self.currentCastlingRights.bks = False
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove

        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    All moves with the "check" control
    """
    def kinginCheck(self):
        if self.whiteToMove and (self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])):
            self.whiteKinginCheck = True
            self.blackKinginCheck = False
        elif not self.whiteToMove and (self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])):
            self.whiteKinginCheck = False
            self.blackKinginCheck = True
        else:
            self.whiteKinginCheck = False
            self.blackKinginCheck = False

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(
            self.currentCastlingRights.wks,
            self.currentCastlingRights.bks,
            self.currentCastlingRights.wqs,
            self.currentCastlingRights.bqs,
        )
        moves = self.getAllPossibleMoves()
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        if self.whiteToMove:
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves
            )
        else:
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves
            )
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves


    """
    All moves without "check" control
    """
    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    pieceIndicator = self.board[r][c][1]
                    self.moveFunctions[pieceIndicator](r, c, moves)
                    #calls every pieces possible move functions
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn move
            if self.board[r - 1][c] == "--":  # the square in front of a pawn is empty
                moves.append(Move((r, c), (r - 1, c), self.board))
                # check if it possible to advance to squares in the first move
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # don't go outside the board from the left :)
                if (
                    self.board[r - 1][c - 1][0] == "b"
                ):  # there's an enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True)
                    )
            if c + 1 <= 7:  # don't go outside the board from the right :)
                if (
                    self.board[r - 1][c + 1][0] == "b"
                ):  # there's an enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True)
                    )

        else:  # black pawn move
            if self.board[r + 1][c] == "--":  # the square in front of a pawn is empty
                # startSquare, endSquare, board
                moves.append(Move((r, c), (r + 1, c), self.board))
                # check if it possible to advance to squares in the first move
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # don't go outside the board from the left :)
                if (
                    self.board[r + 1][c - 1][0] == "w"
                ):  # there's an enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True)
                    )
            if c + 1 <= 7:  # don't go outside the board from the right :)
                if (
                    self.board[r + 1][c + 1][0] == "w"
                ):  # there's an enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True)
                    )


    """ all moves for a knight located at row:r and column:c
    then this move to the list """

    def getKnightMoves(self, r, c, moves):
        knightMoves = (
            (-1, -2),
            (-1, 2),
            (-2, -1),
            (-2, 1),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if (
                    0 <= endRow < 8 and 0 <= endCol < 8):
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    """ all moves for a rock located at row:r and column:c
    then this move to the list """

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if (
                    0 <= endRow < 8 and 0 <= endCol < 8):
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    """ all moves for a queen located at row:r and column:c
    then this move to the list """

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    """ all moves for a king located at row:r and column:c
    then this move to the list """

    def getKingMoves(self, r, c, moves):
        kingMoves = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks
        ):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs
        ):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(
                    r, c + 2
            ):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if (self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--"):
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    #classify columns with "a", "b", "c", "d", "e", "f", "g", "h"
    #classify rows with 1 2 3 4 5 6 7 8
    #aus String zu Integer
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}


    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"

        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True

        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != "--"

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #giving a unique ID for every possible move on the board
        #print(self.moveID)

    """
    Override the equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __str__(self):
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare