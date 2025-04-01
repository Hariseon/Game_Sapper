import asyncio
import websockets
import json

clients = {}

def check_win(opponent_mines, hits):
    return all(mine in hits for mine in opponent_mines)

async def handle_client(websocket):
    if len(clients) >= 2:
        await websocket.send(json.dumps({"message": "Server is full. Try again later."}))
        await websocket.close()
        return

    player_id = len(clients) + 1
    clients[player_id] = {"websocket": websocket, "mines": [], "hits": []}
    opponent_id = 2 if player_id == 1 else 1

    if len(clients) < 2:
        await websocket.send(json.dumps({"message": "Waiting for another player..."}))
        while len(clients) < 2:
            await asyncio.sleep(1)
    
    await websocket.send(json.dumps({"message": "Place your 5 mines on a 5x5 grid (e.g., A1, B2)"}))
    async for message in websocket:
        data = json.loads(message)
        opponent = clients.get(opponent_id)
        
        if "mines" in data:
            clients[player_id]["mines"] = data["mines"]
            if opponent and opponent["mines"]:
                for pid in clients:
                    await clients[pid]["websocket"].send(json.dumps({"message": "Both players have placed their mines. The game begins!"}))
                await clients[1]["websocket"].send(json.dumps({"message": "Your turn! Enter a cell to attack (e.g., A1)"}))
        
        elif "attack" in data:
            attacked_cell = data["attack"]
            hit = attacked_cell in opponent["mines"]
            clients[player_id]["hits"].append(attacked_cell)
            
            await opponent["websocket"].send(json.dumps({"message": f"Your opponent attacked {attacked_cell}. {'Hit!' if hit else 'Miss.'}"}))
            await websocket.send(json.dumps({"message": f"You attacked {attacked_cell} - {'Hit!' if hit else 'Miss.'}"}))
            
            if check_win(opponent["mines"], clients[player_id]["hits"]):
                await websocket.send(json.dumps({"message": "Game over! You lose!"}))
                await opponent["websocket"].send(json.dumps({"message": "Game over! You win!"}))
                await websocket.close()
                await opponent["websocket"].close()
                clients.clear()
                break
            else:
                await opponent["websocket"].send(json.dumps({"message": "Your turn! Enter a cell to attack (e.g., A1)"}))

async def main():
    server = await websockets.serve(handle_client, "localhost", 8765, ping_interval=60, ping_timeout=120)
    print("Server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())