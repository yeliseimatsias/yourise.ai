from parsers import ParserFactory
import json, os

file_path = '' #FILE PATH!!!
extension = file_path.split('.')[-1]

parser = ParserFactory.get_parser(extension)
document_json = parser.parse(file_path)

output_json_path = os.path.splitext(file_path)[0] + ".json"
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(document_json, f, ensure_ascii=False, indent=4)

print(document_json)