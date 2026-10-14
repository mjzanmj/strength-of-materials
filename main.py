import base64
import io
from flask import Flask, render_template_string, request
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Structural Analysis Tool</title>
    <style>
        body { font-family: sans-serif; max-width: 650px; margin: 40px auto; padding: 0 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 8px; box-sizing: border-box; }
        button { background: #0070f3; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px; }
        .warning { color: red; font-weight: bold; }
        .plot { margin-top: 20px; text-align: center; }
        img { max-width: 100%; height: auto; border-radius: 5px; }
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
        <button type="submit">Calculate & Plot</button>
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
    <div class="plot">
        <h3>Load vs. Deformation Graph</h3>
        <img src="data:image/png;base64,{{ result.plot_url }}" alt="Load vs Deformation Plot">
    </div>
    {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
  result = None
  if request.method == "POST":
    try:
      force = float(request.form["force"])
      area = float(request.form["area"])
      length = float(request.form["length"])
      modulus = float(request.form["modulus"])
      yield_strength = float(request.form["yield_strength"])

      stress = force / area
      strain = stress / modulus
      deformation = strain * length
      yielded = stress > yield_strength
      fos = yield_strength / stress if stress > 0 else float("inf")

      # Generate Matplotlib Plot
      fig, ax = plt.subplots(figsize=(6, 4))
      # Create a curve representing elastic behavior up to yield force
      max_force_plot = (
          max(force * 1.5, (yield_strength * area) * 1.2)
          if yield_strength > 0
          else force * 1.5
      )
      max_def_plot = (max_force_plot / (area * modulus)) * length

      forces = [0, max_force_plot]
      deflections = [0, max_def_plot]

      ax.plot(
          deflections,
          forces,
          color="#0070f3",
          linewidth=2,
          label="Elastic Response",
      )
      ax.scatter(
          [deformation],
          [force],
          color="red",
          zorder=5,
          label="Current State",
      )

      ax.set_xlabel("Deformation (mm)")
      ax.set_ylabel("Load / Force (N)")
      ax.set_title("Load vs. Deformation")
      ax.grid(True, linestyle="--", alpha=0.6)
      ax.legend()
      plt.tight_layout()

      # Convert plot to PNG image string
      img = io.BytesIO()
      plt.savefig(img, format="png", bbox_inches="tight")
      img.seek(0)
      plot_url = base64.b64encode(img.getvalue()).decode()
      plt.close(fig)

      result = {
          "stress": round(stress, 4),
          "strain": round(strain, 6),
          "deformation": round(deformation, 4),
          "fos": round(fos, 2) if fos != float("inf") else "N/A",
          "yielded": yielded,
          "plot_url": plot_url,
      }
    except (ValueError, ZeroDivisionError):
      result = None

  return render_template_string(HTML_TEMPLATE, result=result)


if __name__ == "__main__":
  app.run()
