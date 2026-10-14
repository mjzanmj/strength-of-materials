from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Structural Analysis Tool</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 8px; box-sizing: border-box; }
        button { background: #0070f3; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px; }
        .warning { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h2>Structural Analysis Tool</h2>
    <form method="POST">
        <div class="form-group">
            <label>Axial Force (N):</label>
            <input type="number" step="any" name="force" required>
        </div>
        <div class="form-group">
            <label>Cross-Sectional Area (mm²):</label>
            <input type="number" step="any" name="area" required>
        </div>
        <div class="form-group">
            <label>Original Length (mm):</label>
            <input type="number" step="any" name="length" required>
        </div>
        <div class="form-group">
            <label>Young's Modulus E (MPa):</label>
            <input type="number" step="any" name="modulus" required>
        </div>
        <div class="form-group">
            <label>Yield Strength (MPa):</label>
            <input type="number" step="any" name="yield_strength" required>
        </div>
        <button type="submit">Calculate</button>
    </form>

    {% if result %}
    <div class="result">
        <h3>Results:</h3>
        <p><strong>Stress:</strong> {{ result.stress }} MPa</p>
        <p><strong>Strain:</strong> {{ result.strain }}</p>
        <p><strong>Deformation:</strong> {{ result.deformation }} mm</p>
        <p><strong>Factor of Safety:</strong> {{ result.fos }}</p>
        {% if result.yielded %}
            <p class="warning">⚠️ WARNING: Stress exceeds Yield Strength!</p>
        {% else %}
            <p style="color: green;">✓ Structure is within elastic limits.</p>
        {% endif %}
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    if request.method == 'POST':
        try:
            force = float(request.form['force'])
            area = float(request.form['area'])
            length = float(request.form['length'])
            modulus = float(request.form['modulus'])
            yield_strength = float(request.form['yield_strength'])

            stress = force / area
            strain = stress / modulus
            deformation = strain * length
            yielded = stress > yield_strength
            fos = yield_strength / stress if stress > 0 else float('inf')

            result = {
                'stress': round(stress, 4),
                'strain': round(strain, 6),
                'deformation': round(deformation, 4),
                'fos': round(fos, 2) if fos != float('inf') else 'N/A',
                'yielded': yielded
            }
        except (ValueError, ZeroDivisionError):
            result = None

    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run()
