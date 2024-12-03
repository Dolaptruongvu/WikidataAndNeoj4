from flask import Flask, request, jsonify, send_file
import requests
import csv
import io
from flasgger import Swagger, swag_from
from unidecode import unidecode  # Thư viện để chuyển đổi chuỗi không dấu

app = Flask(__name__)
swagger = Swagger(app)

def search_person_by_name(name):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "language": "vi",
        "format": "json",
        "search": name
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("search"):
            return data["search"][0]["id"]
        else:
            return None
    else:
        return None

def query_person_details(q_id):
    query = f"""
    SELECT
      ?person
      ?personLabel
      ?image
      ?signature
      ?sexOrGenderLabel
      ?countryOfCitizenshipLabel
      ?nameInNativeLanguage
      ?vietnameseMiddleNameLabel
      ?familyNameLabel
      ?dateOfBirth
      ?placeOfBirthLabel
      ?spouseLabel
      ?nativeLanguageLabel
      ?languagesSpokenLabel
      ?occupationLabel
      ?educatedAtLabel
      ?memberOfPoliticalPartyLabel
      ?positionHeld
      ?positionHeldLabel
      ?startTime
      ?endTime
      ?replaces
      ?replacesLabel
      ?replacedBy
      ?replacedByLabel
    WHERE {{
      BIND(wd:{q_id} AS ?person)
      OPTIONAL {{ ?person wdt:P18 ?image . }}
      OPTIONAL {{ ?person wdt:P109 ?signature . }}
      OPTIONAL {{ ?person wdt:P21 ?sexOrGender . }}
      OPTIONAL {{ ?person wdt:P27 ?countryOfCitizenship . }}
      OPTIONAL {{ ?person wdt:P1559 ?nameInNativeLanguage . }}
      OPTIONAL {{ ?person wdt:P8500 ?vietnameseMiddleName . }}
      OPTIONAL {{ ?person wdt:P734 ?familyName . }}
      OPTIONAL {{ ?person wdt:P569 ?dateOfBirth . }}
      OPTIONAL {{ ?person wdt:P19 ?placeOfBirth . }}
      OPTIONAL {{ ?person wdt:P26 ?spouse . }}
      OPTIONAL {{ ?person wdt:P103 ?nativeLanguage . }}
      OPTIONAL {{ ?person wdt:P1412 ?languagesSpoken . }}
      OPTIONAL {{ ?person wdt:P106 ?occupation . }}
      OPTIONAL {{ ?person wdt:P69 ?educatedAt . }}
      OPTIONAL {{ ?person wdt:P102 ?memberOfPoliticalParty . }}
      OPTIONAL {{
        ?person p:P39 ?statement .
        ?statement ps:P39 ?positionHeld .
        OPTIONAL {{ ?statement pq:P580 ?startTime . }}
        OPTIONAL {{ ?statement pq:P582 ?endTime . }}
        OPTIONAL {{ ?statement pq:P1365 ?replaces . }}
        OPTIONAL {{ ?statement pq:P1366 ?replacedBy . }}
      }}
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "vi,en" .
      }}
    }}
    """
    url = "https://query.wikidata.org/sparql"
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, params={"query": query})
    if response.status_code == 200:
        return response.json()["results"]["bindings"]
    else:
        return None

def save_to_csv_in_memory(data):
    """
    Lưu dữ liệu vào file CSV trong bộ nhớ.
    """
    if not data:
        return None

    headers = {key for row in data for key in row.keys()}

    # Lưu trực tiếp vào BytesIO
    output = io.BytesIO()
    output.write(",".join(headers).encode("utf-8") + b"\n")  # Ghi tiêu đề
    
    for row in data:
        formatted_row = {key: row[key]["value"] if key in row else "" for key in headers}
        row_values = [formatted_row.get(header, "") for header in headers]
        output.write(",".join(row_values).encode("utf-8") + b"\n")
    
    output.seek(0)
    return output

@app.route("/getPoliticantDetails", methods=["POST"])
@swag_from({
    "tags": ["Politician Details"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Tên của chính trị gia cần tìm",
                        "example": "Nguyễn Xuân Phúc"
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Thành công. Trả về file CSV chứa thông tin chi tiết của chính trị gia.",
            "content": {
                "text/csv": {}
            }
        },
        "400": {
            "description": "Yêu cầu không hợp lệ.",
            "content": {
                "application/json": {
                    "example": {"error": "Missing 'name' in request data"}
                }
            }
        },
        "404": {
            "description": "Không tìm thấy chính trị gia hoặc không có dữ liệu liên quan.",
            "content": {
                "application/json": {
                    "example": {"error": "Person not found"}
                }
            }
        },
        "500": {
            "description": "Lỗi hệ thống hoặc lỗi không xác định.",
            "content": {
                "application/json": {
                    "example": {"error": "Failed to generate CSV"}
                }
            }
        }
    }
})
def generate_csv():
    try:
        data = request.json
        name = data.get("name")
        if not name:
            return jsonify({"error": "Missing 'name' in request data"}), 400
        
        q_id = search_person_by_name(name)
        if not q_id:
            return jsonify({"error": "Person not found"}), 404
        
        results = query_person_details(q_id)
        if not results:
            return jsonify({"error": "No data found for this person"}), 404
        
        csv_memory = save_to_csv_in_memory(results)
        if not csv_memory:
            return jsonify({"error": "Failed to generate CSV"}), 500
        
        # Chuyển đổi tên thành không dấu và thêm định dạng
        filename = f"{unidecode(name).replace(' ', '_')}.csv"
        
        return send_file(
            csv_memory,
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
