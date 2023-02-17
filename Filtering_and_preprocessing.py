# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 18:08:55 2020

@author: msapkota
"""

from difflib import SequenceMatcher
import numpy as np
import re
from PDF_Reading import *

#It returns list of header, footer-1 and footer-2, footers seperated by page number which differes for different pages
def get_header_and_footer(segmented_pages_dictionary):
    
    def compare_previous_and_current_result(previous, current):
        seqMatching1 = SequenceMatcher(None, current,previous)
        longest_match = seqMatching1.find_longest_match(0, len(current), 0, len(previous))
        trimmed = current[longest_match.a:longest_match.a+longest_match.size]
        if len(trimmed) >= len(current)/2 and len(trimmed) >= len(previous)/2:
            current = trimmed
        else:
            current = previous
        return current
    
    str_list = []
    for idx, page in enumerate(segmented_pages_dictionary, start=1):
        if idx%15 == 0:
            str_list.append(segmented_pages_dictionary[page].text)
    
    possible_header = ''
    possible_footers = ['','']
    
    previous_possible_header = ''
    previous_possible_footers = ['','']
    
    header_matching_count = 0
    footer_matching_count = 0
    
    testing_str_count = min(len(str_list)-1,5)
    for index in range(testing_str_count):
        str1 = str_list[index]
        str2 = str_list[index+1]
        seqMatch = SequenceMatcher(None,str1,str2)
        
        matching_blocks = seqMatch.get_matching_blocks()
        if len(matching_blocks) ==0:
            continue
        first_match =  matching_blocks[0] 
        #a gives position in first string and b gives position in second string.
        #if both position is 0, then is the header
        if first_match.a == first_match.b:
            possible_header = str1[first_match.a: first_match.a + first_match.size]
            if not previous_possible_header == '':
                possible_header = compare_previous_and_current_result(previous_possible_header, possible_header)
            previous_possible_header = possible_header
            header_matching_count+= 1
            
        if len(matching_blocks) ==1:
            possible_footers[1] = ''
            continue
            
        last_match =  matching_blocks[-2]
        
        #check if last match lies to the last part of the match
        if len(str1) - last_match.a-last_match.size <=5 and len(str2) - last_match.b-last_match.size <=5:
            possible_footers[1] = str1[last_match.a: last_match.a + last_match.size]

            if not previous_possible_footers[1] == '':
                possible_footers[1] = compare_previous_and_current_result(previous_possible_footers[1], possible_footers[1])   
            previous_possible_footers[1] = possible_footers[1]
            footer_matching_count+= 1
            
            if len(matching_blocks) > 2:
                second_last_match = matching_blocks[-3]
                #print(str1[last_match.a: last_match.a + last_match.size])    
                if last_match.a-second_last_match.a - second_last_match.size <=7 and last_match.b-second_last_match.b - second_last_match.size <=7:
                    possible_footers[0] = str1[second_last_match.a: second_last_match.a + second_last_match.size]
                    #print(possible_footers[0])
                    if not previous_possible_footers[0] == '':
                         possible_footers[0] = compare_previous_and_current_result(previous_possible_footers[0], possible_footers[0])
            
                    previous_possible_footers[0] = possible_footers[0]
                    #print(possible_footers[0])
            else:
                possible_footers[0]=''
                
        #print(possible_header, possible_footers[0],possible_footers[1])
        #print(header_matching_count, footer_matching_count, testing_str_count)       
    if header_matching_count < testing_str_count-1:
        possible_header = ''
    if footer_matching_count <= testing_str_count-1:
        possible_footers = ['','']
        
    return [possible_header, possible_footers[0],possible_footers[1]] 


def clean_text(text,unwanted_lines): 
    for line in unwanted_lines:
        line_to_replace = '{}.*\n'.format(line)
        text = re.sub(line_to_replace, '', text, re.IGNORECASE, re.MULTILINE)     
    return text

def remove_content_repeated_in_table_from_text(text, data_frame):
    result = ''
    text_list_to_remove = []
    for column in data_frame.columns:
        text_list_to_remove.extend(data_frame[column].tolist())
    
    #split the lines inside the cell if exist.
    for idx, cell_content in enumerate(text_list_to_remove):
        cell_content = str(cell_content)
        if len(cell_content.splitlines()) == 1:
            continue
        text_list_to_remove[idx] = cell_content.splitlines()[0]
        for index in range(1,len(cell_content.splitlines())):
            text_list_to_remove.append(cell_content.splitlines()[index])
        
    for line in text.splitlines():    
        if line == '' or not line in text_list_to_remove:
            result = result + line + '\n'
    
    return result

# this function is created to find out starting body row count for the data frame for multiline header. The basis
# is for merged cell, it has one more header lower to it.
def find_the_body_starting_row_count(df):
    last_header = -1; 
    previous_column = ''
    for column in df.columns:
        if previous_column == column and previous_column != '':
            last_header = 0
            break
        previous_column = column
    
    if last_header == -1:
        return last_header+1
    #proceed to get other as well
    previous_cell_value = ''
    for index in range(len(df.index)):
        #print(index)
        for col_idx, column in enumerate(df.columns):
            cell_value = df.iloc[index, col_idx]
            if type(cell_value) is not str:
                cell_value = str(cell_value)
            #print(cell_value)
            if cell_value == previous_cell_value and cell_value !='':
                last_header +=1 
                break
            previous_cell_value = cell_value
        
        if last_header == index:
            return last_header+1
                    
    return last_header+1


def filtering_of_data_frame(d_f):  
    def check_if_all_columns_have_same_value(df):
        previous_list = None
        for index, value in enumerate(df.columns):
            list1 = df.iloc[:,index].tolist()
            if previous_list != None and previous_list != list1:
                return False
            previous_list = list1
        return True
    
    d_f = d_f.replace(r'', np.NaN)
    d_f = d_f.dropna(how = 'all')
    if d_f.empty or check_if_all_columns_have_same_value(d_f) or len(d_f.columns)==1:
        return None
    
    return d_f

def processing_of_data_frame(data_f):
    
    def change_first_row_to_heading_for_columns(d_f, replace_even_with_name):
        if not replace_even_with_name:
            if not all(type(column) is int for column in d_f.columns):
                #print('same returned')
                return d_f
    
        new_header = d_f.iloc[0] 
        # take the rest of your data minus the header row
        df = d_f[1:] 
        # set the header row as the df header
        df.columns = new_header 
        # Lets see the 5 first rows of the new dataset
        return df
    
    #this function will merge the header for each column and column index starts from 0.
    def merge_multi_line_header_to_a_single_name(df):
        body_starting_row = find_the_body_starting_row_count(df)
    
        if body_starting_row == 0 :
            return df
        if len(df.index) == 0:
            return df
        for idx in range(body_starting_row):
    
            new_header = [str(a)+'\n'+str(b) for a, b in zip(df.columns, df.iloc[0])] 
            # take the rest of your data minus the header row avoiding the case with no body row left
            if idx < len(df.index)-1:
                df = df[1:] 
            # set the header row as the df header
            df.columns = new_header 
            # Lets see the 5 first rows of the new dataset
        return df
    data_f = change_first_row_to_heading_for_columns(data_f, False)
    data_f = merge_multi_line_header_to_a_single_name(data_f)
    
    return data_f


def get_list_of_name_and_page_number(key_word_for_list, object_of_interest, text_pages_dictionary):
    name_and_page_list = []
    page_with_list = None
    
    for page, value in text_pages_dictionary.items():
        for line in value.text.splitlines():
            if line == '':
                continue
            #Looking for the key word for the list
            if key_word_for_list.lower() in line.lower():
                page_with_list = page
                continue
            if page_with_list != None:
                if line.lower().startswith(object_of_interest.lower()):
                    digit_list  = [s for s in re.findall(r'-?\d+\.?\d*', line) if s.isdigit()]
                    temp_page_number = digit_list[-1]
                    
                    temp_name = line.lower().replace(object_of_interest.lower(),'')
                    #removing the number for table
                    temp_name = temp_name.replace(digit_list[-1],'')
                    if temp_name.split()[0] == digit_list[0]:
                        temp_name = temp_name.replace(digit_list[0],'')
                    temp_name = temp_name.replace('.','')
                    name_and_page_list.append([temp_name, temp_page_number])
                else:
                    return name_and_page_list
                
    return name_and_page_list
   
             
def filtering_and_preprocessing_pages(segmented_pages_dictionary, table_index_page_error):
    result = {}
    header_and_footer = get_header_and_footer(segmented_pages_dictionary)
    table_list_name = get_list_of_name_and_page_number('Table of Tables', 'Table', segmented_pages_dictionary)

    if len(table_list_name) > 0:
        table_names_available = True
    else:
        table_names_available = False
    table_list_index = 0
    page_index = 0
    #print(header_and_footer)
    for page, item in segmented_pages_dictionary.items():
        page_index+=1
        #print(page)
        #initiate new page
        new_page = Segmented_Page(page)
        
        #text data cleaning and storing to new page
        new_page.text = clean_text(item.text, header_and_footer)
        temp_table_list = []
        for table in item.tables:
            #dataframe cleaning and storing in new new table list
            df = filtering_of_data_frame(table.data_frame)
            if df is None:
                continue
            
            #remove the table part from the text
            new_page.text = remove_content_repeated_in_table_from_text(new_page.text, df)
            
            df = processing_of_data_frame(df)
            
            new_table = Table_in_report(table.name)
            new_table.data_frame = df
            new_table.page_number = table.page_number
            new_table.arranged_header = True
            
            if table_names_available:
                if table_list_name[table_list_index][1] == str(page_index - table_index_page_error):
                    new_table.name = table_list_name[table_list_index][0]
                    
                    if table_list_index < len(table_list_name)-1:
                        table_list_index+=1
                    else:
                        table_names_available = False
            temp_table_list.append(new_table)
            
        new_page.tables = temp_table_list  
        #attributing same images to the new pages
        new_page.Images = item.Images
        
        result[page] = new_page
        
    return result