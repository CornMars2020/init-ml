import torch
from torch import nn
from torch.nn import functional as F
from torch import optim
import numpy as np
import pandas as pd
from time import time

from dataset import Dataset
from model import VerifyCode


def get_sec(e, s) -> float:
    return int((e - s) * 1000) / 1000.0


def get_ms(e, s) -> int:
    return int((e - s) * 1000)


def get_percent(p) -> float:
    return int(p * 100 * 100) / 100.0


def train(epochs, logic, optimizer, train_dl):
    stime = time()

    for epoch in range(epochs):
        print(f"== Epoch {epoch}")

        i = 0
        sstime = time()
        for xb, yb in train_dl:
            i += 1

            xb = torch.flatten(xb, start_dim=0, end_dim=1)
            yb = torch.flatten(yb, start_dim=0, end_dim=1)
            # print(type(xb), type(yb), xb.shape, yb.shape)

            xb = torch.swapdims(xb, 1, 3)

            y_pred = logic(xb)
            # print(type(y_pred), y_pred.shape)

            loss = F.cross_entropy(y_pred, yb)
            loss.backward()

            optimizer.step()
            optimizer.zero_grad()

            if i % 100 == 0:
                cctime = get_ms(time(), sstime)
                print(f"i={i} loss: {loss} cost {cctime}ms")
                sstime = time()

    ctime = get_sec(time(), stime)
    print(f"\nloss: {loss}\ncost: {ctime}s\n")


def test(logic, test_ds):
    x, y = test_ds[:]
    x = torch.flatten(x, start_dim=0, end_dim=1)
    y = torch.flatten(y, start_dim=0, end_dim=1)
    x = torch.swapdims(x, 1, 3)

    y_pred = logic(x)
    # print(torch.argmax(y_pred[0:10], 1))
    # print(y[0:10])
    # print(torch.argmax(y[0:10]))

    accuracy = torch.argmax(y_pred, 1) == y
    accuracy = np.mean(accuracy.cpu().numpy())
    return accuracy


# 读取数据集
DATESET_PATH = "../dataset/verification_code/"
epochs = 5
batch_size = 32
learning_rate = 0.001


loader = Dataset(DATESET_PATH)
# loader.rewrite_ds()

# train_ds, test_ds = loader.read_ds()
# print(train_ds, test_ds)
# print(type(train_ds), type(test_ds))

# x_train, y_train = train_ds[:]
# x_test, y_test = test_ds[:]

# print(type(x_train), x_train.shape)
# print(type(y_train), y_train.shape)
# print(y_train[0])

_, test_ds = loader.read_ds()
train_dl, _ = loader.read_dl(batch_size)
print(train_dl, test_ds)
print(type(train_dl), type(test_ds))

# print(test_ds[0][0].shape, test_ds[0][1].shape)
img = test_ds[0][0].cpu()
code = test_ds[0][1].cpu()
img = np.swapaxes(img, 1, 3)
print(img[0], code[0])


in_channels = 3
out_channels = 26 * 2 + 10

logic = VerifyCode(in_channels, out_channels).get_model()
optimizer = optim.SGD(logic.parameters(), lr=learning_rate)

# train(epochs, logic, optimizer, train_dl)
# accuracy = get_percent(test(logic, test_ds))
# print(f"accuracy: {accuracy}%")