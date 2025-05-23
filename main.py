import PyPDF2
import csv
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
    l=[]

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
                # Find normal range: number - number pattern
                for k in range(i + 1, min(i + 15, len(tokens) - 2)):
                    if (is_number(tokens[k]) and tokens[k + 1] == "-" and is_number(tokens[k + 2])):
                        normal_min = float(tokens[k])
                        normal_max = float(tokens[k + 2])
                        break
                # Find patient value (next number after the label)
                for j in range(i + 1, min(i + 10, len(tokens))):
                    if is_number(tokens[j]):
                        patient_val = float(tokens[j])

                # Only append if we have at least patient_val and a normal range
                if patient_val is not None and normal_min is not None and normal_max is not None:
                    extracted_data.append([label,normal_min,normal_max,patient_val])
                i += 1
            else:
                i += 1

    return extracted_data


# Call the function
cbc_output = extract_text_pypdf2("report2.pdf")

# Save to CSV
with open("report_data.csv", "w", newline="") as fw:
    writer = csv.writer(fw)
    writer.writerow(["Label", "Normal Min", "Normal Max","Patient Value"])
    for row in cbc_output:
        writer.writerow(row)