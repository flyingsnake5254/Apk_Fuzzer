import xmltodict
import json

def convert_xml_to_json(xml_file, json_file):
    with open(xml_file, 'r') as file:
        xml_content = file.read()
        dict_data = xmltodict.parse(xml_content, process_namespaces=True)

        # 將屬性放入 'attr' 鍵中
        def process_dict(d):
            if isinstance(d, dict):
                return {"attr": d} if all(key.startswith('@') for key in d) else {k: process_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [process_dict(v) for v in d]
            else:
                return d

        processed_data = process_dict(dict_data)
        with open(json_file, 'w') as json_out:
            json.dump(processed_data, json_out, indent=4)

convert_xml_to_json('AndroidManifest.xml', 'exported_true_tags.json')
