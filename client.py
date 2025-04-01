import asyncio
import websockets
import json

def draw_board(mines, hits, show_mines):
    letters = "ABCDE"
    board = [["0" for _ in range(5)] for _ in range(5)]
    
    for hit in hits:
        row = int(hit[1]) - 1
        col = letters.index(hit[0])
        if hit in mines:
            board[row][col] = "-"
        else:
            board[row][col] = "+"
    
    if show_mines:
        for mine in mines:
            row = int(mine[1]) - 1
            col = letters.index(mine[0])
            board[row][col] = "*"
    
    print("  A B C D E")
    for i, row in enumerate(board, 1):
        print(f"{i} {' '.join(row)}")

async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        mines = []
        hits = []
        
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            
            if "message" in data:
                print(data["message"])
                
                if "Place your 5 mines" in data["message"]:
                    while len(mines) < 5:
                        draw_board(mines, [], True)
                        mine = input("Enter mine position (e.g., A1): ").upper()
                        if mine not in mines and len(mine) == 2 and mine[0] in "ABCDE" and mine[1] in "12345":
                            mines.append(mine)
                    await websocket.send(json.dumps({"mines": mines}))
                    draw_board(mines, [], False)
                
                elif "Your turn!" in data["message"]:
                    draw_board(mines, hits, False)
                    attack_cell = input("Enter a cell to attack (e.g., A1): ").upper()
                    if len(attack_cell) == 2 and attack_cell[0] in "ABCDE" and attack_cell[1] in "12345":
                        await websocket.send(json.dumps({"attack": attack_cell}))
                
                elif "You attacked" in data["message"]:
                    cell = data["message"].split()[2]
                    if "Hit!" in data["message"]:
                        hits.append(cell)
                    else:
                        hits.append(cell)
                    draw_board(mines, hits, False)
                
                elif "Game over!" in data["message"]:
                    break

if __name__ == "__main__":
    asyncio.run(main())
