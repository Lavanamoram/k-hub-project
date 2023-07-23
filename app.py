import plotly.graph_objects as go
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['data_db']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Save the data to MongoDB
        data = {col: request.form[col] for col in request.form}
        db.form_data.insert_one(data)

        return redirect(url_for('form'))

    return render_template('form.html')

@app.route('/excel', methods=['GET', 'POST'])
def excel_upload():
    if request.method == 'POST':
        # Read the uploaded Excel file and save the data to MongoDB
        file = request.files['file']
        if file.filename.endswith('.xlsx'):
            data_df = pd.read_excel(file)
            data = data_df.to_dict(orient='records')
            try:
                # Use ordered=False to ignore duplicates and insert non-duplicate records
                db.excel_data.insert_many(data, ordered=False)
            except Exception as e:
                # Handle any errors if needed
                print(f"Error: {e}")

            return redirect(url_for('pie_chart'))

    return render_template('excel_upload.html')


# ... (previously defined routes and imports)

# ... (previously defined routes and imports)

@app.route('/piechart')
def pie_chart():
    # Fetch data from MongoDB for pie charts
    data = list(db.form_data.find({}, {'_id': 0}))

    # Create a list to store pie chart HTML
    pie_charts = []

    # Create a pie chart for each column (excluding 'Name')
    columns_for_pie_chart = [column for column in data[0] if column != 'Name']

    for column in columns_for_pie_chart:
        column_values = [item[column] for item in data if item.get(column)]
        column_counts = {value for value in column_values if value}
        labels = list(column_counts)

        values = [len([value for value in column_values if value == label]) for label in labels]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        pie_chart_html = fig.to_html(full_html=False)
        pie_charts.append(pie_chart_html)

    return render_template('pie_chart.html', pie_charts=pie_charts)

# ... (other routes and app.run as before)


@app.route('/scatterplot')
def scatter_plot():
    # Fetch data from MongoDB for scatter plot
    data = list(db.form_data.find({}, {'_id': 0}))

    # Create a scatter plot for each pair of columns
    scatter_plots = []
    for i in range(len(data[0])):
        for j in range(i + 1, len(data[0])):
            x_data = [item[list(data[0])[i]] for item in data]
            y_data = [item[list(data[0])[j]] for item in data]

            fig = go.Figure(data=go.Scatter(x=x_data, y=y_data, mode='markers'))
            scatter_plot_html = fig.to_html(full_html=False)
            scatter_plots.append(scatter_plot_html)

    return render_template('scatter_plot.html', scatter_plots=scatter_plots)


if __name__ == '__main__':
    app.run(debug=True)