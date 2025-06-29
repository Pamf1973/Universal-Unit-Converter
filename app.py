# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # Used for handling Cross-Origin Resource Sharing
import datetime
import json
import re

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

# Define unit categories and their properties
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
        "emojis": "🧪",
        "defaultFrom": "Liters",
        "defaultTo": "Gallons",
    },
}

# This list will hold the conversion history (in-memory for this example)
CONVERSION_HISTORY = []

# --- Helper Functions (Ensuring correct order for Python execution) ---

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
        # Handle cases where direct number is provided for feet/inches
        if from_unit == 'Feet':
            return num * 12 # Convert feet to inches
        elif from_unit == 'Inches':
            return num # Already in inches
        return num # For other units like Meters/Centimeters (will be handled by convert_length)
    except ValueError:
        return float('nan')

def format_height_output(total_value_in_meters, to_unit):
    if to_unit in ['Feet', 'Inches']:
        total_inches = convert_length(total_value_in_meters, 'Meters', 'Inches')
        
        feet = int(total_inches // 12)
        remaining_inches = total_inches % 12
        
        # Round remaining_inches to the nearest whole number
        rounded_remaining_inches = int(round(remaining_inches))
        
        # Handle carry-over if inches round up to 12
        if rounded_remaining_inches >= 12: # If it rounds to 12, it means a full foot
            feet += 1
            rounded_remaining_inches = 0 # Reset inches to 0
        
        # Ensure inches don't display as 0'0" if the input was 0
        if feet == 0 and rounded_remaining_inches == 0 and total_inches > 0:
             # If total_inches was very small, but not exactly zero, show it as a small inch value
             if total_inches < 1 and to_unit == 'Inches':
                 return f"{round(total_inches, 2)}\""
             return f"0'0\"" # For a very small value that rounds to 0 feet 0 inches
        
        if to_unit == 'Feet':
            return f"{feet}'{rounded_remaining_inches}\""
        elif to_unit == 'Inches':
            # This path is for when 'Inches' is the *target* unit, and we want total inches, possibly with decimals
            return f"{round(total_inches, 2)}\""
    # For metric height units, keep 2 decimal places as per previous requirement
    return f"{total_value_in_meters:.2f}"


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
        match = re.search(r"unit '([^']+)'", prompt_text)
        unit_name = match.group(1) if match else "unknown unit"
        return f"AI: The unit '{unit_name}' is a fundamental measurement used globally."
    elif "fun fact" in prompt_text.lower():
        return "AI Fun Fact: Did you know that the metric system was first introduced in France during the late 18th century?"
    else:
        return "AI: I'm designed to help with unit explanations and fun facts!"

def perform_conversion_and_record(input_value, selected_unit_type, from_unit, to_unit, language="English"):
    """
    Performs a unit conversion, records it in the global history, and returns the result.

    This function orchestrates the entire conversion process:
    1. Parses the input value, handling special formats like 'Height' (feet/inches).
    2. Validates inputs (e.g., checks if units are selected, if value is a number).
    3. Calls the appropriate specific conversion helper function (e.g., convert_length).
    4. Formats the converted result for display based on new decimal rules.
    5. Creates a structured dictionary representing the conversion event.
    6. Adds the new conversion record to the global CONVERSION_HISTORY.
    7. Returns a dictionary containing the formatted result string, the updated
       history, and the raw converted value.

    Args:
        input_value (str): The value entered by the user (e.g., "10", "6'3\"").
        selected_unit_type (str): The category of units (e.g., "Length", "Height").
        from_unit (str): The unit to convert from (e.g., "Meters", "Feet").
        to_unit (str): The unit to convert to (e.g., "Feet", "Meters").
        language (str): The selected language for messages (e.g., "English").

    Returns:
        dict: A dictionary containing:
            - "result_string" (str): The formatted conversion result for display.
            - "history" (list): The updated list of conversion history records.
            - "raw_converted_value" (float/int): The numerical converted value.
            - "error" (str, optional): An error message if the conversion failed.
    """
    # Get translations for the current language
    t = TRANSLATIONS.get(language, TRANSLATIONS["English"])

    # 1. Input Parsing and Validation
    num_value = None
    if selected_unit_type == 'Height' and (from_unit in ['Feet', 'Inches']):
        # If height is selected and from unit is Feet or Inches, parse complex string
        num_value = parse_height_input(input_value, from_unit)
        if isinstance(num_value, float) and (num_value != num_value): # Check for NaN
            return {"error": t["invalidHeightFormat"]}
        # Convert parsed inches value to the base unit (Meters) for `convert_length`
        if from_unit == 'Feet' or from_unit == 'Inches':
            # This step converts inches (or feet converted to inches) to meters for internal consistency
            num_value = convert_length(num_value, 'Inches', 'Meters')
    else:
        # For other unit types or simple numerical height input, attempt float conversion
        try:
            num_value = float(input_value)
        except ValueError:
            return {"error": t["enterNumber"]}

    # Basic unit selection validation
    if num_value is None or \
       from_unit not in UNIT_CATEGORIES.get(selected_unit_type, {}).get("units", []) or \
       to_unit not in UNIT_CATEGORIES.get(selected_unit_type, {}).get("units", []):
        return {"error": t["selectUnits"]}

    # 2. Perform Conversion based on unit type
    converted_value = None
    if selected_unit_type == 'Length':
        converted_value = convert_length(num_value, from_unit, to_unit)
    elif selected_unit_type == 'Height':
        # `num_value` is already in meters if original was feet/inches,
        # otherwise it's direct float input in meters/centimeters
        converted_value = convert_length(num_value, 'Meters', to_unit) # Always convert from meters for height
    elif selected_unit_type == 'Weight':
        converted_value = convert_weight(num_value, from_unit, to_unit)
    elif selected_unit_type == 'Temperature':
        converted_value = convert_temperature(num_value, from_unit, to_unit)
    elif selected_unit_type == 'Volume':
        converted_value = convert_volume(num_value, from_unit, to_unit)
    else:
        return {"error": t["unknownType"]}

    # Check for errors returned by conversion helper functions
    if isinstance(converted_value, str) and "Error" in converted_value:
        return {"error": converted_value}

    # 3. Format the Result for display
    formatted_result = None
    if selected_unit_type == 'Height':
        # If it's height, check the target unit for formatting
        if to_unit in ['Feet', 'Inches']:
            # Feet/Inches output uses special format, not fixed decimals
            formatted_result = format_height_output(converted_value, to_unit)
        else:
            # Metric height units (Meters, Centimeters) should have 2 decimal places
            formatted_result = f"{converted_value:.2f}"
    else:
        # All other unit types (Length, Weight, Temperature, Volume) get 4 decimal places
        formatted_result = f"{converted_value:.4f}"

    # Construct the full result string for display in the UI
    final_result_string = f"{input_value} {t['units'][from_unit]} = {formatted_result} {t['units'][to_unit]}"

    # 4. Record Conversion in History (as a dictionary)
    new_conversion_record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Current timestamp
        "unit_type": selected_unit_type,
        "input_value": input_value,
        "from_unit": from_unit,
        "to_unit": to_unit,
        "converted_result": formatted_result, # Store the formatted string result
        "result_string": final_result_string, # Store the full display string
    }
    CONVERSION_HISTORY.insert(0, new_conversion_record) # Add to the beginning for most recent first

    # 5. Return the result and updated history
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
    # app.run(debug=True, host='0.0.0.0', port=5000) # This line should be commented out or removed for Render deployment
    pass # Added 'pass' to satisfy the 'if' statement's indentation requirement
