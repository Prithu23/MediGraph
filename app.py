from flask import Flask, render_template, request
import tempfile
import os
import PyPDF2

app = Flask(__name__)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def extract_text_pypdf2(filepath):
    cbc = ["Hemoglobin", "RBC", "Hematocrit", "MCV", "MCH", "MCHC", "RDW",
           "WBC", "Neutrophils", "Lymphocytes", "Eosinophils", "Monocytes",
           "Basophils", "Platelet", "MPV", "ESR"]

    extracted_data = []

    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        full_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        tokens = full_text.split()

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in cbc:
                label = token
                normal_min = None
                normal_max = None
                patient_val = None

                for k in range(i + 1, min(i + 15, len(tokens) - 2)):
                    if (is_number(tokens[k]) and tokens[k + 1] == "-" and is_number(tokens[k + 2])):
                        normal_min = float(tokens[k])
                        normal_max = float(tokens[k + 2])
                        break

                for j in range(i + 1, min(i + 10, len(tokens))):
                    if is_number(tokens[j]):
                        patient_val = float(tokens[j])
                        break

                if patient_val is not None and normal_min is not None and normal_max is not None:
                    extracted_data.append([label, normal_min, normal_max,patient_val])
                i += 1
            else:
                i += 1

    return extracted_data

def classify_value(value,normal_min, normal_max):
    center = (normal_min + normal_max) / 2
    if normal_min <= value <= normal_max:
        return "Normal"
    percent_diff = 10+(value / center) * 100
    if percent_diff < 50:
        return "Very Low"
    elif percent_diff < 100:
        return "Low"
    elif percent_diff <= 150:
        return "High"
    else:
        return "Very High"

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        patient_name = request.form.get("patient_name")
        file = request.files.get("file")

        if not file or not patient_name:
            return "Missing file or patient name", 400

        # Save to a temp file
        filepath = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(filepath)

        # Extract and classify
        cbc_data = extract_text_pypdf2(filepath)

        labels = []
        classifications = []

        for label,normal_min,normal_max,patient_val  in cbc_data:
            labels.append(label)
            classifications.append(classify_value(normal_min,normal_max,patient_val))

        return render_template(
            "chartjs_classification_plot.html",
            patient_name=patient_name,
            labels=labels,
            classifications=classifications
        )

    # Render upload form on GET
    return render_template("chartjs_upload_form.html")

if __name__ == "__main__":
    app.run(debug=True)