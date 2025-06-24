# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # Used for handling Cross-Origin Resource Sharing
import datetime
import json
import re

# Import the core logic functions directly from your unit_converter_logic.py
# For a single file, you can copy-paste them or include them directly.
# For simplicity in this single file example, I'll include the core logic here.

# --- Translation Data (Copied from unit-converter-python-logic Canvas) ---
TRANSLATIONS = {
    "English": {
        "title": "🌍 Universal Unit Converter",
        "purpose": "Convert everyday measurements like length, weight, temperature, and volume with ease. A mini project for my AI Native journey 🚀.",
        "selectType": "Select Type:",
        "inputValue": "Value to Convert:",
        "fromUnit": "From Unit:",
        "toUnit": "To Unit:",
        "convertButton": "Convert",
        "explainUnitButton": "Explain Unit ✨",
        "funFactButton": "Fun Fact ✨",
        "loadingAI": "AI is thinking...",
        "enterNumber": "Please enter a valid number.",
        "selectUnits": "Please select both 'from' and 'to' units.",
        "unknownType": "Error: Unknown unit type",
        "invalidHeightFormat": "Invalid height format. Use 'X'Y\"' (e.g., 6'3\") or a number (e.g., 75 for inches).",
        "resultPrefix": "✨ ",
        "resultSuffix": " ✨",
        "conversionHistoryTitle": "Conversion History",
        "unitTypes": {
            "Length": "Length", "Height": "Height", "Weight": "Weight",
            "Temperature": "Temperature", "Volume": "Volume",
        },
        "units": {
            "Meters": "Meters", "Feet": "Feet", "Kilometers": "Kilometers", "Miles": "Miles",
            "Inches": "Inches", "Centimeters": "Centimeters", "Yards": "Yards",
            "Pounds": "Pounds", "Kilograms": "Kilograms", "Ounces": "Ounces", "Grams": "Grams", "Stones": "Stones",
            "Celsius": "Celsius", "Fahrenheit": "Fahrenheit",
            "Liters": "Liters", "Gallons": "Gallons", "Milliliters": "Milliliters",
            "Fluid Ounces": "Fluid Ounces", "Cups": "Cups",
        },
    },
    "French": {
        "title": "🌍 Convertisseur d'Unités Universel",
        "purpose": "Convertissez facilement les mesures courantes comme la longueur, le poids, la température et le volume. Un mini-projet pour mon parcours IA Native 🚀.",
        "selectType": "Sélectionner le type:",
        "inputValue": "Valeur à convertir:",
        "fromUnit": "De l'unité:",
        "toUnit": "Vers l'unité:",
        "convertButton": "Convertir",
        "explainUnitButton": "Expliquer l'unité ✨",
        "funFactButton": "Fait Amusant ✨",
        "loadingAI": "L'IA réfléchit...",
        "enterNumber": "Veuillez entrer un nombre valide.",
        "selectUnits": "Veuillez sélectionner les unités 'de' et 'vers'.",
        "unknownType": "Erreur: Type d'unité inconnu",
        "invalidHeightFormat": "Format de hauteur invalide. Utilisez 'X'Y\"' (ex: 6'3\") ou un nombre (ex: 75 pour pouces).",
        "resultPrefix": "✨ ",
        "resultSuffix": " ✨",
        "conversionHistoryTitle": "Historique des Conversions",
        "unitTypes": {
            "Length": "Longueur", "Height": "Hauteur", "Weight": "Poids",
            "Temperature": "Température", "Volume": "Volume",
        },
        "units": {
            "Meters": "Mètres", "Feet": "Pieds", "Kilometers": "Kilomètres", "Miles": "Milles",
            "Inches": "Pouces", "Centimeters": "Centimètres", "Yards": "Verges",
            "Pounds": "Livres", "Kilograms": "Kilogrammes", "Ounces": "Onces", "Grams": "Grammes", "Stones": "Stones",
            "Celsius": "Celsius", "Fahrenheit": "Fahrenheit",
            "Liters": "Litres", "Gallons": "Gallons", "Milliliters": "Millilitres",
            "Fluid Ounces": "Onces liquides", "Cups": "Tasses",
        },
    },
}

# Define unit categories and their properties (Copied from unit-converter-python-logic Canvas)
UNIT_CATEGORIES = {
    "Length": {
        "units": ["Meters", "Feet", "Kilometers", "Miles", "Inches", "Centimeters", "Yards"],
        "defaultFrom": "Meters",
        "defaultTo": "Feet",
    },
    "Height": {
        "units": ["Meters", "Feet", "Inches", "Centimeters"],
        "defaultFrom": "Feet",
        "defaultTo": "Meters",
    },
    "Weight": {
        "units": ["Pounds", "Kilograms", "Ounces", "Grams", "Stones"],
        "defaultFrom": "Pounds",
        "defaultTo": "Kilograms",
    },
    "Temperature": {
        "units": ["Celsius", "Fahrenheit"],
        "defaultFrom": "Celsius",
        "defaultTo": "Fahrenheit",
    },
    "Volume": {
        "units": ["Liters", "Gallons", "Milliliters", "Fluid Ounces", "Cups"],
        "defaultFrom": "Liters",
        "defaultTo": "Gallons",
    },
}

# This list will hold the conversion history (in-memory for this example)
# In a real deployed app, this would be backed by a database.
CONVERSION_HISTORY = []

# --- Helper Functions (Copied from unit-converter-python-logic Canvas) ---

def parse_height_input(input_string, from_unit):
    input_string = input_string.strip()
    feet_inches_match = re.match(r"^(\d+)'(\d*)\"?$", input_string)
    if feet_inches_match:
        feet = int(feet_inches_match.group(1) or '0')
        inches = int(feet_inches_match.group(2) or '0')
        return (feet * 12) + inches
    pure_inches_match = re.match(r"^(\d+)\"?$", input_string)
    if pure_inches_match:
        return int(pure_inches_match.group(1))
    try:
        num = float(input_string)
        if from_unit == 'Feet':
            return num * 12
        elif from_unit == 'Inches':
            return num
        return num
    except ValueError:
        return float('nan')

def format_height_output(total_value_in_meters, to_unit):
    if to_unit in ['Feet', 'Inches']:
        total_inches = convert_length(total_value_in_meters, 'Meters', 'Inches')
        feet = int(total_inches // 12)
        remaining_inches = total_inches % 12
        rounded_remaining_inches = round(remaining_inches, 2)
        if to_unit == 'Feet':
            if rounded_remaining_inches >= 11.99:
                return f"{feet + 1}'0\""
            return f"{feet}'{rounded_remaining_inches}\""
        elif to_unit == 'Inches':
            return f"{round(total_inches, 2)}\""
    return f"{total_value_in_meters:.4f}"

def convert_length(value, from_unit, to_unit):
    to_meters_factors = {
        "Meters": lambda v: v, "Feet": lambda v: v * 0.3048, "Kilometers": lambda v: v * 1000,
        "Miles": lambda v: v * 1609.34, "Inches": lambda v: v * 0.0254, "Centimeters": lambda v: v * 0.01,
        "Yards": lambda v: v * 0.9144,
    }
    from_meters_factors = {
        "Meters": lambda v: v, "Feet": lambda v: v / 0.3048, "Kilometers": lambda v: v / 1000,
        "Miles": lambda v: v / 1609.34, "Inches": lambda v: v / 0.0254, "Centimeters": lambda v: v / 0.01,
        "Yards": lambda v: v / 0.9144,
    }
    if from_unit not in to_meters_factors or to_unit not in from_meters_factors:
        return "Error: Invalid unit for length conversion."
    value_in_meters = to_meters_factors[from_unit](value)
    return from_meters_factors[to_unit](value_in_meters)

def convert_weight(value, from_unit, to_unit):
    to_kilograms_factors = {
        "Pounds": lambda v: v * 0.453592, "Kilograms": lambda v: v, "Ounces": lambda v: v * 0.0283495,
        "Grams": lambda v: v * 0.001, "Stones": lambda v: v * 6.35029,
    }
    from_kilograms_factors = {
        "Pounds": lambda v: v / 0.453592, "Kilograms": lambda v: v, "Ounces": lambda v: v / 0.0283495,
        "Grams": lambda v: v / 0.001, "Stones": lambda v: v / 6.35029,
    }
    if from_unit not in to_kilograms_factors or to_unit not in from_kilograms_factors:
        return "Error: Invalid unit for weight conversion."
    value_in_kilograms = to_kilograms_factors[from_unit](value)
    return from_kilograms_factors[to_unit](value_in_kilograms)

def convert_temperature(value, from_unit, to_unit):
    if from_unit == "Celsius" and to_unit == "Fahrenheit":
        return (value * 9 / 5) + 32
    elif from_unit == "Fahrenheit" and to_unit == "Celsius":
        return (value - 32) * 5 / 9
    elif from_unit == to_unit:
        return value
    else:
        return "Error: Invalid temperature conversion."

def convert_volume(value, from_unit, to_unit):
    to_liters_factors = {
        "Liters": lambda v: v, "Gallons": lambda v: v * 3.78541, "Milliliters": lambda v: v * 0.001,
        "Fluid Ounces": lambda v: v * 0.0295735, "Cups": lambda v: v * 0.236588,
    }
    from_liters_factors = {
        "Liters": lambda v: v, "Gallons": lambda v: v / 3.78541, "Milliliters": lambda v: v / 0.001,
        "Fluid Ounces": lambda v: v / 0.0295735, "Cups": lambda v: v / 0.236588,
    }
    if from_unit not in to_liters_factors or to_unit not in from_liters_factors:
        return "Error: Invalid unit for volume conversion."
    value_in_liters = to_liters_factors[from_unit](value)
    return from_liters_factors[to_unit](value_in_liters)

def get_llm_response(prompt_text, language="English"):
    # This is a placeholder. In a real Python application, you would
    # use a library like 'requests' to make an HTTP POST request to the Gemini API.
    # The API key would be loaded from environment variables, not hardcoded.
    if "explanation" in prompt_text.lower():
        # Extract the unit from the prompt
        match = re.search(r"unit '([^']+)'", prompt_text)
        unit_name = match.group(1) if match else "unknown unit"
        return f"AI: The unit '{unit_name}' is a fundamental measurement used globally."
    elif "fun fact" in prompt_text.lower():
        return "AI Fun Fact: Did you know that the metric system was first introduced in France during the late 18th century?"
    else:
        return "AI: I'm designed to help with unit explanations and fun facts!"

def perform_conversion_and_record(input_value, selected_unit_type, from_unit, to_unit, language="English"):
    t = TRANSLATIONS.get(language, TRANSLATIONS["English"])
    num_value = None
    if selected_unit_type == 'Height' and (from_unit in ['Feet', 'Inches']):
        num_value = parse_height_input(input_value, from_unit)
        if isinstance(num_value, float) and (num_value != num_value):
            return {"error": t["invalidHeightFormat"]}
        if from_unit == 'Feet' or from_unit == 'Inches':
            num_value = convert_length(num_value, 'Inches', 'Meters')
    else:
        try:
            num_value = float(input_value)
        except ValueError:
            return {"error": t["enterNumber"]}

    if num_value is None or from_unit not in UNIT_CATEGORIES[selected_unit_type]["units"] or \
       to_unit not in UNIT_CATEGORIES[selected_unit_type]["units"]:
        return {"error": t["selectUnits"]}

    converted_value = None
    if selected_unit_type == 'Length' or selected_unit_type == 'Height':
        converted_value = convert_length(num_value, 'Meters' if selected_unit_type == 'Height' and (from_unit == 'Feet' or from_unit == 'Inches') else from_unit, to_unit)
    elif selected_unit_type == 'Weight':
        converted_value = convert_weight(num_value, from_unit, to_unit)
    elif selected_unit_type == 'Temperature':
        converted_value = convert_temperature(num_value, from_unit, to_unit)
    elif selected_unit_type == 'Volume':
        converted_value = convert_volume(num_value, from_unit, to_unit)
    else:
        return {"error": t["unknownType"]}

    if isinstance(converted_value, str) and "Error" in converted_value:
        return {"error": converted_value}

    formatted_result = None
    if selected_unit_type == 'Height' and (to_unit in ['Feet', 'Inches']):
        formatted_result = format_height_output(converted_value, to_unit)
    else:
        formatted_result = f"{converted_value:.4f}"

    final_result_string = f"{input_value} {t['units'][from_unit]} = {formatted_result} {t['units'][to_unit]}"

    new_conversion_record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unit_type": selected_unit_type,
        "input_value": input_value,
        "from_unit": from_unit,
        "to_unit": to_unit,
        "converted_result": formatted_result,
        "result_string": final_result_string,
    }
    CONVERSION_HISTORY.insert(0, new_conversion_record)

    return {
        "result_string": final_result_string,
        "history": CONVERSION_HISTORY,
        "raw_converted_value": converted_value
    }


app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing your React app to make requests

@app.route('/convert', methods=['POST'])
def convert_unit():
    data = request.get_json()
    input_value = data.get('inputValue')
    selected_unit_type = data.get('selectedUnitType')
    from_unit = data.get('fromUnit')
    to_unit = data.get('toUnit')
    language = data.get('language', 'English')

    # Call the core conversion logic
    response = perform_conversion_and_record(input_value, selected_unit_type, from_unit, to_unit, language)
    return jsonify(response)

@app.route('/explain-unit', methods=['POST'])
def explain_unit():
    data = request.get_json()
    unit = data.get('unit')
    language = data.get('language', 'English')
    
    prompt = f"Provide a brief, concise explanation of the unit '{unit}' in {language} language. Focus on its definition and common usage."
    llm_response = get_llm_response(prompt, language)
    return jsonify({"explanation": llm_response})

@app.route('/fun-fact', methods=['POST'])
def fun_fact():
    data = request.get_json()
    from_unit = data.get('fromUnit')
    to_unit = data.get('toUnit')
    language = data.get('language', 'English')

    prompt = f"Provide a short, interesting fun fact or historical trivia related to the conversion between {from_unit} and {to_unit}, or about these units in general, in {language} language."
    llm_response = get_llm_response(prompt, language)
    return jsonify({"funFact": llm_response})

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify({"history": CONVERSION_HISTORY})

if __name__ == '__main__':
    # This runs the Flask development server
    # For production deployment on Render, Gunicorn or similar WSGI server is used.
    app.run(debug=True, host='0.0.0.0', port=5000)
