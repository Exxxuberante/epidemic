import json
import matplotlib
matplotlib.use('Agg')  # Используем backend без GUI
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from pathlib import Path
import os

from flask import Flask, request, render_template, jsonify, send_from_directory
from calcutalor import Calculator

app = Flask(__name__)

# Настройка статических файлов
app.static_folder = 'static'
app.template_folder = 'templates'

@app.route("/")
def read_root():
    return render_template("index.html")

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

JSON_FILE_PATH = Path("function-definitions.json")

@app.route("/get-json")
def get_json():
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "JSON file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON file"}), 500

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

@app.route("/calculate/", methods=["POST"])
def calculate():
    startValues_vals = json.loads(request.form['startValues'])
    maxValues_vals = json.loads(request.form['maxValues'])
    coefs_vals = json.loads(request.form['coefs'])

    calc = Calculator(startValues_vals, maxValues_vals, coefs_vals)
    time_intervals = np.linspace(0, 1, 20)
    solution = calc.calculate(time_intervals)

    solution_display = np.clip(solution, 0, 1)


    # Разделение решения на отдельные переменные для удобства
    L1, L2, L3, L4, L5, L6, L7, L8, L9, L10, L11, L12, L13, L14, L15 = solution_display.T

    # Визуализация графика времени (разделён на два)
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))  # Два графика друг под другом

    # Определяем все линии для удобства
    lines_group1 = [
        (L1, 'Летальность'), (L2, 'Инфицированные'), (L3, 'Население региона'),
        (L4, 'Госпитализированные'), (L5, 'Изолированность'), (L6, 'Скорость распространения'),
        (L7, 'Доступность лекарства'), (L8, 'Тяжесть симптомов')
    ]

    lines_group2 = [
        (L9, 'Умершие'), (L10, 'Уровень медицины'), (L11, 'Инкубационный период'), 
        (L12, 'Период развития болезни'), (L13, 'Период реабилитации'), 
        (L14, 'Устойчивость к лекарствам'), (L15, 'Степень осложнения')
    ]   

    # ПЕРВЫЙ график (верхний) - Группа 1
    for L, label in lines_group1:
        ax1.plot(time_intervals, L, label=label)

    for L, label in lines_group1:
        for x, y in zip(time_intervals, L):
            ax1.annotate(f'{y:.2f}', xy=(x, y), xytext=(5, 5), textcoords='offset points', fontsize=8)

    ax1.set_ylabel('Значения')
    ax1.set_title('График времени - Группа 1 (Основные показатели)')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    ax1.grid(True, alpha=0.3)

    # ВТОРОЙ график (нижний) - Группа 2
    for L, label in lines_group2:
        ax2.plot(time_intervals, L, label=label)

    for L, label in lines_group2:
        for x, y in zip(time_intervals, L):
            ax2.annotate(f'{y:.2f}', xy=(x, y), xytext=(5, 5), textcoords='offset points', fontsize=8)

    ax2.set_xlabel('Время')
    ax2.set_ylabel('Значения')
    ax2.set_title('График времени - Группа 2 (Временные показатели)')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    ax2.grid(True, alpha=0.3)

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

    return jsonify({
        "image1": img_str1,
        "image2": img_str2
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)