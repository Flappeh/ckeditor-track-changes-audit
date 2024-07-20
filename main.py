from dotenv import load_dotenv
from services.ckeditor import service as ckeditor
from services.htmlparse.service import parse_suggestion_from_html as parse_html
import json

load_dotenv()


def main():
    data = ckeditor.get_document_by_id('demo-doc-1')
    result = parse_html(data)
    data = json.dumps(result)
    print(data)
    
if __name__ == '__main__':
    main()