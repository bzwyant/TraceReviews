from bs4 import BeautifulSoup
# import json


def parse_instructor_summary(text: str):
    review_map = {}

    soup = BeautifulSoup(text, features="lxml")
    try:
        # NOTE: there is probably a better way to write this
        comments = find_student_comments(soup, parse_new_report, parse_old_report)

        review_map["comments"] = comments

        # print(",\n".join(comments))

    except:
        review_map["comments"] = []
        print("Could not find data")

    return review_map


def find_student_comments(soup: BeautifulSoup, *parse_functions) -> list:
    comments = ''
    for parse_func in parse_functions:
        try:
            comments = parse_func(soup)
            return comments
        except:
            continue

    print("Found a new instructor report type")
    return comments


def parse_new_report(soup: BeautifulSoup):
    instructor_qs_div = soup.find('div', id='cat_3')
        
    tbody_elems = instructor_qs_div.find_all('tbody')
    comments = []
    for tbody in tbody_elems:
        for tr_elem in tbody.find_all('tr'):
            comment = tr_elem.find_all('td')[-1]
            # Replace <br> tags with newlines
            for br in comment.find_all('br'):
                br.replace_with('\n')
            comments.append(comment.get_text().strip())

    return comments


def parse_old_report(soup: BeautifulSoup):
    prof = soup.find('div', id="chart_3").find('h4').get_text()
    prof = prof.rsplit(':', 1)[1].strip()

    comments = []
    general_comments_div = soup.find('div', id="cat_15")

    tbody = general_comments_div.find('tbody')
    for tr_elem in tbody.find_all('tr'):
        comment = tr_elem.find_all('td')[-1]
        # Replace <br> tags with newlines
        for br in comment.find_all('br'):
            br.replace_with('\n')
        comments.append(comment.get_text().strip())

    return comments