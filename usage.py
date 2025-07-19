import io
import os
import re
from pydoc import classname
from google.cloud import vision
from PIL import Image, ImageDraw
from datetime import datetime,timedelta


# Set credentials and image
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'api_json.json'
image_path = "data/scheduleex_gray.jpg"
with io.open(image_path, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)
client = vision.ImageAnnotatorClient()
response = client.document_text_detection(image=image)

# Load image
img = Image.open(image_path)
draw = ImageDraw.Draw(img)

# Define columns
columns = {
    "col1": (600, 800),
    "col2": (1100, 1350)
}

# Store words with positions
column_words = {"col1": [], "col2": []}

for page in response.full_text_annotation.pages:
    for block in page.blocks:
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                word_text = ''.join([symbol.text for symbol in word.symbols])
                box = word.bounding_box.vertices
                avg_x = sum([v.x for v in box]) / 4
                avg_y = sum([v.y for v in box]) / 4

                # Assign to a column if within X range
                for col, (xmin, xmax) in columns.items():
                    if xmin <= avg_x <= xmax:
                        column_words[col].append((avg_y, avg_x, word_text))
                        draw.polygon([(v.x, v.y) for v in box], outline="green")

#img.show()

# Group words into rows by Y proximity
def group_by_rows(words, y_threshold=20):
    words.sort(key=lambda x: (x[0], x[1]))  # sort by Y then X
    rows = []
    current_row = []
    last_y = None

    for y, x, text in words:
        if last_y is None or abs(y - last_y) < y_threshold:
            current_row.append(text)
        else:
            rows.append(" ".join(current_row))
            current_row = [text]
        last_y = y
    if current_row:
        rows.append(" ".join(current_row))

    return rows

# Process columns
col1_rows = group_by_rows(column_words["col1"])
col2_rows = group_by_rows(column_words["col2"])

# Join rows with a delimiter
col1_text = "#".join(col1_rows)
col2_text = "#".join(col2_rows)
col2_text += "#"

print("\nColumn 1 Text:\n", col1_text)
# print(type(col1_text))
print("\nColumn 2 Text:\n", col2_text)
# print(type(col2_text))
#Puts each class in a list of classes 
classes = []
class_ = ""
for char in col1_text:
    if char == '#':
        classes.append(class_)
        class_ = ""
    else:
        class_ += char
#Remove the seciton header
classes.pop(0)
times = []
time_ = ""
for char in col2_text:
    if char == '#':
        times.append(time_)
        time_= ""
    else:
        time_ += char
times.pop(0)
times.pop(0)
print(classes)
print(times)
classes_list = []
daymap = {
    "monday": "MO", "tuesday": "TU", "wednesday": "WE",
    "thursday": "TH", "friday": "FR", "saturday": "SA", "sunday": "SU"
}
for c, t in zip(classes, times):
    temp = {}
    temp["class_name"] = c

    # Extract days
    days_found = re.findall(r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", t.lower())
    days = [daymap[d] for d in days_found]
    temp["days"] = days

    # Location
    location = t.split("|")[-1].strip()
    temp["location"] = location

    # Pattern for normal case: both times have AM/PM
    time_match = re.search(r"(\d{1,2}:\d{2}\s*[APMapm]{2})\s*-\s*(\d{1,2}:\d{2}\s*[APMapm]{2})", t)

    if time_match:
        start_time = time_match.group(1)
        end_time = time_match.group(2)
    else:
        # Check for case like "10:00 10:50 AM"
        partial_match = re.search(r"(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2}\s*[APMapm]{2})", t)
        if partial_match:
            start_time = partial_match.group(1) + " " + partial_match.group(2)[-2:]  # infer AM/PM from second time
            end_time = partial_match.group(2)
        #Check for cases like "12:00PM 1:45"
        else:
            partial_match = re.search(r"(\d{1,2}:\d{2}\s*[APMapm]{2})\s*-\s*(\d{1,2}:\d{2})(?![APMapm])", t)
            if partial_match:
                start_time = partial_match.group(1) 
                end_time = partial_match.group(2)+ " " + partial_match.group(1)[-2:]  # infer AM/PM from first time
            else:
                # Handle single time or fallback
                time_match_list = re.findall(r"\d{1,2}:\d{2}\s*[APMapm]{2}", t)
                if len(time_match_list) >= 2:
                    start_time = time_match_list[0]
                    end_time = time_match_list[1]
                elif len(time_match_list) == 1:
                    start_time = time_match_list[0]
                    time_obj = datetime.strptime(start_time, "%I:%M %p")
                    end_time = (time_obj + timedelta(minutes=50)).strftime("%I:%M %p")
                else:
                    start_time = None
                    end_time = None
    temp["start_time"] = start_time
    temp["end_time"] = end_time
    classes_list.append(temp)
print(classes_list)

