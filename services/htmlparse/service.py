from bs4 import BeautifulSoup as bs

results = {}
parsed_data  = []

def parse_suggestion_from_html(htmlData:str = None):
    soup = bs(htmlData, 'html.parser')
    # Check for text input
    text_suggestions = soup.find_all('suggestion-start')
    for i in text_suggestions:
        current_content = i.next.get_text()
        results[i['name']] = current_content
    # for paragraph in paragraphs:
    #     # Initialize variables to store content and current suggestion name
    #     current_content = []
    #     current_name = None

    #     # Find all text nodes and suggestion tags within the current paragraph
    #     for child in paragraph.children:
    #         if child.name == 'suggestion-start':
    #             current_name = child['name']
    #             current_content = []  # Reset content for new suggestion-start tag
    #         elif child.name == 'suggestion-end' and current_name:
    #             if current_name in results:  # Check if name already exists in results
    #                 results[current_name] += ''.join(current_content).strip()
    #             else:
    #                 results[current_name] = ''.join(current_content).strip()
    #             current_name = None
    #         else:
    #             current_content.append(str(child))

    # #Check for other element input
    # figures = soup.find_all('figure', {"data-suggestion-end-after": True})
    
    # for figure in figures:
    #     current_content = []
    #     current_name = figure['data-suggestion-end-after']
    #     results[current_name] = figure.html
                
    
    # Print results
    for name, content in results.items():
        parsed_name = name.split(':')
        data = {
            "type": parsed_name[0],
            "suggestionId": parsed_name[1],
            "authorId": parsed_name[2],
            "data": content
        }
        parsed_data.append(data)
    return parsed_data