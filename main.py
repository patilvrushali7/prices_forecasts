from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import pickle
import os
from datetime import datetime

app = Flask(__name__)

# Load Historical Data at Startup
def load_historical_data():
    file_path = "histtorical_data.pkl"
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading historical data: {str(e)}")
    else:
        print(f"File {file_path} not found.")
    return {}

# Load Forecast Data at Startup (CSV-like format)
def load_forecasts():
    file_path = "path_to_pkl_only_folder/all_forecasts.pkl"
    if os.path.exists(file_path):
        try:
            return joblib.load(file_path)
        except Exception as e:
            print(f"Error loading forecasts: {str(e)}")
    else:
        print(f"File {file_path} not found.")
    return {}

# Data loaded at startup
historical_data = load_historical_data()
all_forecasts = load_forecasts()

# Function to convert date to desired format (YYYY-MM-DD)
def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT").strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error parsing date: {str(e)}")
        return date_str

@app.route('/product_info', methods=['GET'])
def product_info():
    try:
        # Retrieve product_name from query parameters
        product_name = request.args.get("product_name")

        if not product_name:
            return render_template("product_info.html", product_name=None)

        # Fetch Historical Data for the product
        historical_info = None
        for item_number, item_data in historical_data.items():
            if item_data.get("item_name", "").strip().lower() == product_name.strip().lower():
                historical_info = item_data
                break

        if not historical_info:
            return render_template("product_info.html", product_name=product_name, historical_info=None)

        # Format Historical Data
        historical_info_formatted = [
            {
                "year_month": year_month,
                "max_discount": data["max_discount"],
                "max_discount_date": data["max_discount_date"],
                "min_discount": data["min_discount"],
                "min_discount_date": data["min_discount_date"],
                "max_sales_price": data["max_sales_price"],
                "min_sales_price": data["min_sales_price"],
                "max_sales_price_date": data["max_sales_price_date"],
                "min_sales_price_date": data["min_sales_price_date"]
            }
            for year_month, data in historical_info.get("discounts", {}).items()
        ]

        # Fetch Forecast Data for the product
        forecast_df = None
        for item_number, forecast in all_forecasts.items():
            for _, row in forecast.iterrows():
                if row["Item Name"].strip().lower() == product_name.strip().lower():
                    forecast_df = forecast
                    break

        forecast_data = None
        if forecast_df is not None:
            forecast_data = [
                {
                    "date": format_date(row["Date"]),
                    "forecasted_discount_percentage": float(row["Forecasted Discount Percentage"]),
                    "forecasted_sales_price": float(row["Forecasted Sales Price"])
                }
                for _, row in forecast_df.iterrows()
            ]

        # Render the template with data
        return render_template(
            "product_info.html",
            product_name=product_name,
            historical_info=historical_info_formatted,
            forecast_data=forecast_data
        )

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return render_template("product_info.html", product_name=None, error=str(e))

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

