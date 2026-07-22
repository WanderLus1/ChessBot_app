#cd C:\Users\hrida\Documents\MyBot
#"C:\Users\hrida\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" play.py

#run these commands to play the model, to change color put user_color=chess.WHITE in root play.py
#if terminal gives error try command prompt

from src.model import create_model
from src.play import play
import torch
import chess

model = create_model()
model.load_state_dict(torch.load("models/bot_v1_1.pth"))
model.eval()

play(model, user_color=chess.BLACK)