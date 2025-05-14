import json

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from pathlib import Path
import os

from calcutalor import Calculator

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")




@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


JSON_FILE_PATH = Path("function-definitions.json")
@app.get("/get-json", response_class=JSONResponse)
async def get_json():
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "JSON file not found"}
        )
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500,
            content={"error": "Error decoding JSON file"}
        )


@app.post("/calculate/")
async def calculate(startValues=Form(...), maxValues=Form(...), coefs=Form(...)):
    startValues_vals = json.loads(startValues)
    maxValues_vals = json.loads(maxValues)
    coefs_vals = json.loads(coefs)

    calc = Calculator(startValues_vals, maxValues_vals, coefs_vals)
    time_intervals = np.linspace(0, 1, 20)
    solution = calc.calculate(time_intervals)

    # Разделение решения на отдельные переменные для удобства
    L1, L2, L3, L4, L5, L6, L7, L8, L9, L10, L11, L12, L13, L14, L15 = solution.T

    # Визуализация графика времени
    fig1, ax1 = plt.subplots(figsize=(16, 8))  # Увеличиваем график

    # Определяем все линии для удобства
    lines = [
        (L1, 'Летальность'), (L2, 'Инфицированные'), (L3, 'Население региона'),
        (L4, 'Госпитализированные'), (L5, 'Изолированность'), (L6, 'Скорость распространения'),
        (L7, 'Доступность лекарства'), (L8, 'Тяжесть симптомов'), (L9, 'Умершие'),
        (L10, 'Уровень медицины'), (L11, 'Инкубационный период'), (L12, 'Период развития болезни'),
        (L13, 'Период реабилитации'), (L14, 'Устойчивость к лекарствам'), (L15, 'Степень осложнения')
    ]

    # Строим линии графика
    for L, label in lines:
        ax1.plot(time_intervals, L, label=label)

    # Отображаем значения на графике
    for L, label in lines:
        for x, y in zip(time_intervals, L):
            ax1.annotate(f'{y:.2f}', xy=(x, y), xytext=(5, 5), textcoords='offset points', fontsize=8)

    ax1.set_xlabel('Время')
    ax1.set_ylabel('Значения')
    ax1.set_title('График времени')

    # Устанавливаем легенду вне графика
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    plt.tight_layout()

    # Сохранение первого графика в буфер
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)
    img_str1 = base64.b64encode(buf1.getvalue()).decode("utf-8")

    # Названия категорий
    categories = [
        'Летальность', 'Инфицированные', 'Население региона', 'Госпитализированные', 'Изолированность',
        'Скорость распространения', 'Доступность лекарства', 'Тяжесть симптомов', 'Умершие', 'Уровень медицины',
        'Инкубационный период', 'Период развития болезни', 'Период реабилитации', 'Устойчивость к лекарствам',
        'Степень осложнения'
    ]

    # Углы для категорий
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    # Допустим, maxValues — это список из максимальных значений для каждой категории
    maxValues = calc.maxValues
    maxValues += maxValues[:1]

    # Строим графики для каждого времени
    fig2, axes = plt.subplots(2, 3, figsize=(18, 12), subplot_kw=dict(polar=True))

    for i, ax in enumerate(axes.flat):
        idx = int(i * (len(solution)-1) / 5)

        values = solution[idx].tolist()

        values += values[:1]

        ax.fill(angles, values, color='blue', alpha=0.25)
        ax.plot(angles, values, color='blue', linewidth=2)

        ax.plot(angles, maxValues, color='red', linewidth=2, linestyle='--', label='Max Values')

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=8)

        time_idx = int(i * (len(time_intervals)-1) / 5)
        ax.set_title(f't = {round(time_intervals[time_idx], 2)}', size=16, y=1.1)

    plt.legend(loc='upper right')

    plt.tight_layout()

    # Сохранение второго графика в буфер
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)
    img_str2 = base64.b64encode(buf2.getvalue()).decode("utf-8")

    # Закрытие фигур после сохранения
    plt.close(fig1)
    plt.close(fig2)

    return {
        "image1": img_str1,
        "image2": img_str2
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)