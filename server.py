import socket
import threading
import json
import time

HOST = '127.0.0.1'  
PORT = 5555  

clients = {}  
scores = {}  


with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def handle_client(conn, addr):
    try:
        conn.sendall("Digite seu nome: ".encode())
        name = conn.recv(1024).decode().strip()
        clients[conn] = name
        scores[name] = 0

        print(f"[+] {name} entrou no jogo ({addr})")
    except Exception as e:
        print(f"Erro ao conectar cliente: {e}")
        conn.close()

def broadcast(message):
    for conn in list(clients.keys()):
        try:
            conn.sendall(message.encode())
        except:
            conn.close()
            del clients[conn]

def quiz():
    
    for question in questions:
        pergunta_completa = f"\nPergunta: {question['pergunta']}\n" + "\n".join([f"{i+1}) {alt}" for i, alt in enumerate(question["alternativas"])]) + "\n"
        broadcast(pergunta_completa)

        start_time = time.time()
        responses = {}

        while time.time() - start_time < 20:  
            for conn in list(clients.keys()):
                conn.settimeout(1)  
                try:
                    answer = conn.recv(1024).decode().strip()
                    if answer and clients[conn] not in responses:  
                        responses[clients[conn]] = answer
                except socket.timeout:
                    continue  
                except:
                    conn.close()
                    del clients[conn]

        correct_answer = str(question["correta"])
        for player, answer in responses.items():
            if answer == correct_answer:
                scores[player] += 1

        broadcast(f"\nResposta correta: {correct_answer}")
        broadcast("\nRanking Parcial: " + str(scores))

    broadcast("\n=== FIM DO JOGO ===\nRanking Final: " + str(scores))
    
    broadcast("\n[!] O servidor será encerrado. Obrigado por jogar!")

    for conn in list(clients.keys()):
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("[*] Servidor esperando jogadores...")

    while len(clients) < 1:  
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

    broadcast("\n[+] O jogo começará em 5 segundos...")
    time.sleep(5)
    quiz()

start_server()
