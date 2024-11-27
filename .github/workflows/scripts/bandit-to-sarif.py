import json
import sys
from datetime import datetime

def convert_to_sarif(bandit_json_file, sarif_file):
    with open(bandit_json_file, 'r') as f:
        bandit_data = json.load(f)

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Bandit",
                        "informationUri": "https://github.com/PyCQA/bandit",
                        "version": bandit_data.get("metadata", {}).get("bandit_version", ""),
                        "rules": []
                    }
                },
                "results": [],
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "endTimeUtc": datetime.utcnow().isoformat() + "Z"
                    }
                ]
            }
        ]
    }

    # Convert results
    for result in bandit_data.get("results", []):
        sarif_result = {
            "ruleId": f"B{result.get('test_id', '')}",
            "level": "error" if result.get("issue_severity", "") == "HIGH" else "warning",
            "message": {
                "text": result.get("issue_text", "")
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": result.get("filename", "").replace("\\", "/")
                        },
                        "region": {
                            "startLine": result.get("line_number", 1)
                        }
                    }
                }
            ]
        }
        sarif["runs"][0]["results"].append(sarif_result)

        # Add rule if not already present
        rule_id = f"B{result.get('test_id', '')}"
        if not any(r.get("id") == rule_id for r in sarif["runs"][0]["tool"]["driver"]["rules"]):
            sarif["runs"][0]["tool"]["driver"]["rules"].append({
                "id": rule_id,
                "name": result.get("test_name", ""),
                "shortDescription": {
                    "text": result.get("issue_text", "")
                },
                "defaultConfiguration": {
                    "level": "error" if result.get("issue_severity", "") == "HIGH" else "warning"
                }
            })

    with open(sarif_file, 'w') as f:
        json.dump(sarif, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bandit-to-sarif.py <bandit-json-file> <sarif-output-file>")
        sys.exit(1)
    convert_to_sarif(sys.argv[1], sys.argv[2])
