from pypdf import PdfReader, PdfWriter
import pdfplumber
import copy

def word_position(page, first_word):
    words = page.extract_words()
    for word in words:
        if word['text'] == first_word:
            line_word = word
    return line_word['top'] - 7

#This function finds the next line where the pdf should be split and returns its vertical position. 
#If the page doesn't need to be split, the function returns 1
def find_next_line(start_page, set, char):
    with pdfplumber.open("Check-Out2.pdf") as pdf: #So I can use methods in pdfplumber
        for page_num, page in enumerate(reader.pages[start_page:], start = start_page):
            lines = page.extract_text().splitlines()
            for line in lines:
                first_word = line.split()[0] if line.split() else None
                if first_word not in set:
                    if (first_word[0] == char or first_word[0] >= char):
                        p = word_position(pdf.pages[page_num], first_word) #position of the top of the word
                        return [page_num, p]
    
    return -1 #returns -1 if nothing is found on that page

def find_section_type(page):
    lines = page.extract_text().splitlines()
    if lines[0] == "4:20pm Check-Out":
        return 2
    else:
        return 1

#This function crops the page from the top and the bottom by the specified amount
def crop_page(page, amount_top, amount_bottom):
    page.mediabox.upper_right = (page.mediabox.upper_right[0], page.mediabox.upper_right[1] - amount_top)
    page.mediabox.lower_left = (page.mediabox.lower_left[0], page.mediabox.lower_left[1] + amount_bottom)

    return page

#This function splits the page into two separate pages at the given position
def split_page(page, writer, position):
    page1 = copy.copy(page)
    page2 = copy.copy(page)

    #crops the pages
    page_one = crop_page(page1, 0, page2.mediabox.height - position)
    page_two = crop_page(page2, position, 0)

    writer.add_page(page_one)
    writer.add_page(page_two)  

#def split_alphabetically():


#Beginning of main program

# Set of words for program to skip over when checking for words
not_names = {"DK/AM", "DM/PM", "DM/AM", "Check-Out:", "JB/AM", "Guardian:", "Phone", "DM/FD", "DK/FD", "Pick-ups:", "JB/2W/AM"}

# A-F, G-M, N-T, T-Z
letter_list = ['G', 'N', 'T']

reader = PdfReader("Check-Out2.pdf")
writer = PdfWriter() # the new pdf

#Finds split for first section
line_position = find_next_line(0, not_names, 'N') #returns line where page should be split

for i in range(line_position[0]):
    writer.add_page(reader.pages[i])

split_page(reader.pages[line_position[0]], writer, line_position[1])

#Finds split for biggest section
for letter in letter_list:
    old_pos = line_position
    line_position = find_next_line(old_pos[0], not_names, letter) #returns line where page should be split

    for i in range(old_pos[0]+1, line_position[0]):
        writer.add_page(reader.pages[i])

    split_page(reader.pages[line_position[0]], writer, line_position[1])

#Adds in the rest of the pages
for i, page in enumerate(reader.pages[line_position[0]+1:], start = line_position[0]+1):
    writer.add_page(reader.pages[i])


with open("modified2.pdf", "wb") as output:
    writer.write(output)



