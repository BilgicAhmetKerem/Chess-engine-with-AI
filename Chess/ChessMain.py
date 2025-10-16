"""
Will be used in order to display the current state and user input
"""
import pygame as p

from Chess import ChessEngine, SmartMoveFinder
WIDTH = HEIGHT = 400  #if its getting bigger, the resolution would be better
DIMENSION = 8 # dimension fo the board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
Matching images with the piece identifiers
"""

def loadimages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bQ', 'bR', 'bN', 'bB', 'bp', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

"""
This part will be handling the graphics and user input
"""

def main():
    print("'r' to reset the game\n'b' to remove the last move you made")

    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    loadimages()   # not to forget, the images must be loaded only for one time
    running = True
    sqSelected = () #no square selected yet, but keep tract of last klick
    playerOne = True #is true, when human plays the whites, if AI
                     # takes the whites, then it will be false
    playerTwo = False#The same like playerOne but for black
    playerClicks = [] #keep track of player clicks
    animate = False #if we should animate the move or not
    gameOver = False #finishes the game


    """
    Mouse inputs
    """
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():   #exit usage
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() #(x,y) location of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): # if it clicked twice it will be unselected
                        sqSelected = () #deselect
                        playerClicks = [] #clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation() ,playerClicks)
                        for i in range(len(validMoves)):
                            if  move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                        if not moveMade:
                            playerClicks = [sqSelected]
                        else:
                            #letting know that it is a check
                            gs.kinginCheck()
                            if gs.whiteKinginCheck:
                                print("Check by Black! \n")
                            elif gs.blackKinginCheck:
                                print("Check by White! \n")

                        sqSelected = () #reset the inputs
                        playerClicks = []
            elif e.type == p.KEYDOWN:
                if e.key == p.K_b: #undo when b is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r: #press r to reset the game to default settings
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        #AI move finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMoveMinMax(gs, validMoves)
            if AIMove == None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            #animating the last move
            if animate:
                if len(gs.moveLog) > 0:
                    animationofamove(gs.moveLog[-1], screen, gs.board, clock)

            validMoves = gs.getValidMoves()
            gs.kinginCheck()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, "Black wins by checkmate!")
            else:
                drawEndGameText(screen, "White wins by checkmate")
        elif gs.staleMate:
            gameOver = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

"""
Showing the possible moves and the square that is selected
"""
def highlightingSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('yellow'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('orange'))
            for moves in validMoves:
                if moves.startRow == r and moves.startCol == c:
                    screen.blit(s, (SQ_SIZE * moves.endCol, SQ_SIZE * moves.endRow))

    #If it is a check than draw the square of the king that got checked with red
    if gs.inCheck():
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(150)
        s.fill(p.Color('red'))
        if gs.whiteToMove:
            screen.blit(s, (SQ_SIZE * gs.whiteKingLocation[1], SQ_SIZE * gs.whiteKingLocation[0]))
        else:
            screen.blit(s, (SQ_SIZE * gs.blackKingLocation[1], SQ_SIZE * gs.blackKingLocation[0]))




"""
#Responsible for the graphs
"""




def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # draw the squares on the board
    highlightingSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # just draw the pieces on the top of the board


"""
responsible for drawing the board
"""

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
"""
responsible for drawing the pieces
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Animation of the moving piece
"""

def animationofamove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    #the count of frames in order to move one square
    framesPerSquare = 5
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame/frameCount, move.startCol + dC * frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece from the ending square
        color = colors[(move.startRow + move.startCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw the captured one on the rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #drawing the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


"""
Draws the syntax on the board
"""

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - textObject.get_width() / 2,
        HEIGHT / 2 - textObject.get_height() / 2,
    )
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == '__main__':
    main()
