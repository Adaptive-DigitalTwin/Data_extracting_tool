# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 14:11:45 2020

@author: msapkota
"""
import numpy as np
import nltk
from dateutil.parser import parse
import re
import pandas as pd

class information_ontology_predefined:
    def __init__(self ,string):
        self.string = string
        self.date = None
        self.location = None
        self.sub_part = None  
        self.quantitative = None
        self.data_type_quan = None
        self.qualitative = None
        self.negative_inducing = False
        self.data_type_qual = None
        
    def update(self, other_information):
        if other_information.location != None:
            self.location = other_information.location
        if other_information.date !=None:
            self.date = other_information.date
            
class Information_Ontology_undefined:
    def __init__(self ,string):
        self.string = string

class Parsed_tagged_text:
    def __init__(self, string, tag):
        self.string = string
        self.tag = tag      
        
def extract_all_elements_from_columns_related_to_key_word(segmented_pages, items_related_wordlist):
    result = []
    for page, value in segmented_pages.items():
        for table in value.tables:
            df = table.data_frame
            [result.extend(df[name].tolist()) for name in df.columns for s in items_related_wordlist if
             s.lower() in name.lower()]
    return result


def get_tables_list_with_related_term(segmented_pages, related_terms_list):
    result = []
    for page, value in segmented_pages.items():
        for table in value.tables:
            table_name = table.name
            if any(key in table_name for key in related_terms_list):
                result.append(table)
                continue
            for idx, column in enumerate(table.data_frame.columns):
                if any(data in column.lower() for data in related_terms_list):
                    result.append(table)
                    break
                if any(data in str(cell).lower() for cell in table.data_frame.iloc[:,idx].tolist() for data in related_terms_list):
                    result.append(table)
                    break
    return result

def extract_informations_from_tables(segmented_pages, related_terms_list):
    
    related_tables_list = get_tables_list_with_related_term(segmented_pages, related_terms_list)
    
    result = []
    explored_tables = []
    
    #first we are exploring the tables 
    for table in related_tables_list:
        total_information = len(result)
        d_f = table.data_frame
        
        for col_idx, column in enumerate(d_f.columns):
            extracted_row = []
            for row_idx, data in enumerate(d_f[column].tolist()):
                if row_idx in extracted_row or data is np.NaN or data == 'nan':
                    continue
                
                try:
                    float(data)
                except ValueError:
                    continue
                
                information_temp = Information_Ontology_undefined(data)
                
                for (key, value) in zip(d_f.columns, d_f.values[row_idx]):
                    information_temp.__dict__[key] = value
                extracted_row.append(row_idx)
                
                result.append(information_temp)
        if len(result) > total_information:
            explored_tables.append(table.name)
            
    return result


class Parsed_tagged_text:
    def __init__(self, string, tag):
        self.string = string
        self.tag = tag

def get_string_from_parsed_branch(subtree):
    string =''
    result = Parsed_tagged_text(string, 'none')
    if type(subtree) == string:
        return
    if type(subtree) == tuple:
        return Parsed_tagged_text(subtree[0],subtree[1])
    
    #if node contains only one branch, then change from phrase form to single form again.
    if len(subtree) == 1:
        for branch in subtree:
            return Parsed_tagged_text(branch[0],branch[1])
    for branch in subtree:
        if type(branch) == tuple:
            string = string + branch[0]+' '
        else:
            string = string + get_string_from_parsed_branch(branch)
    result.string = string
    result.tag = 'NP'
    return result

#this function return the list of Parsed_tagged_text after from the given strings.
def get_list_of_parsed_string_for_individual_line(line): 
    #Define your grammar using regular expressions
    grammar = r"""
    NP: {<DT|PP\$>?<JJ.*|CD>*<CD|NN.*>+}   # chunk determiner/possessive, adjectives/integer and nouns
               # chunk sequences of proper nouns
               """
    chunkParser = nltk.RegexpParser(grammar)
    tagged1 = nltk.pos_tag(nltk.word_tokenize(line))    
    tree1 = chunkParser.parse(tagged1)
    parsed_text=[]
    for subtree_count, subtree in enumerate(tree1.subtrees()):
        if subtree_count ==0:
            for parsed in subtree:
                parse_string = get_string_from_parsed_branch(parsed)
                parsed_text.append(parse_string)
    
    return parsed_text

#shortest word string is matched with longest word string
def matching_considered(string_list_1, string_list_2): 
    least_word_string = min([string_list_1, string_list_2], key=len) 
    most_word_string = string_list_1 if least_word_string == string_list_2 else string_list_2
    least_length = len(least_word_string)
    

    total_matching_needed = least_length
    if least_length > 6:
        total_matching_needed = least_length-2
    elif least_length > 3:
        total_matching_needed = least_length-1
    total_match = 0

    for str1 in least_word_string:   
        for str2 in most_word_string:
            st_s = min([str1, str2], key=len) 
            st_l = str1 if st_s == str2 else str2

            if not st_s.isnumeric() and len(st_s) >=3: 
                if len(st_s) >= 4:
                    st_s = st_s[:-1]
                if st_l.startswith(st_s):
                    total_match +=1
                    break
            else:
                if st_s.isnumeric():
                    total_matching_needed = least_length
                if st_l == st_s:
                    total_match +=1
                    break
    #print(total_match, total_matching_needed )       
    if total_match >= total_matching_needed:
        return True
    return False

def check_if_carries_date_information(string, fuzzy=False):
    try: 
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False

def check_for_information_from_phrase(information_to_be_extracted, phrase, possible_words_for_main_attribute, 
                                      possible_words_for_sub_attribute, quality_describing_word_list, negativity_inducing_words_list):
    
    def check_if_carries_attribute_information(string1,possible_words_for_attribute):
        result = None
        words_to_check = string1.lower().split()
        for attribute in possible_words_for_attribute:
            words_for_matching = attribute.lower().split()
            if matching_considered(words_to_check, words_for_matching):
                result = attribute
        return result
    
    def check_if_percentage_information(string):
        if any('%' in word1 for word1 in string.split()) and any(any(s.isdigit() for s in word) for word in string.split()):
            return re.sub(r'[^0-9]', '', string) + ' %'
        return None
    
    best_matching_location = check_if_carries_attribute_information(phrase, possible_words_for_main_attribute)
    if best_matching_location is not None:
        #if the information is carried, then temp_information_carrier is 
        information_to_be_extracted.location = best_matching_location.replace('\n', " ")

    elif check_if_carries_date_information(phrase):
        information_to_be_extracted.date = phrase
                
    elif check_if_percentage_information(phrase) is not None:
        information_to_be_extracted.qualitative = phrase
                
    elif check_if_carries_attribute_information(phrase, possible_words_for_sub_attribute):
        information_to_be_extracted.sub_part = phrase
    
    else:
        #print(phrase)
        individual_tagging_list_from_phrase = nltk.pos_tag(nltk.word_tokenize(phrase))
        for tagging in individual_tagging_list_from_phrase:
            information_to_be_extracted = check_for_information_with_word_and_tag(information_to_be_extracted, tagging[0],
                                                                                  tagging[1], quality_describing_word_list, negativity_inducing_words_list)
        
    return information_to_be_extracted


def check_for_information_with_word_and_tag(information_to_be_extracted, string, tag, quality_describing_word_list,
                                            negativity_inducing_words_list):
    if tag == 'CD':
        information_to_be_extracted.data_type = string
            
    elif tag == 'NNP':
        if re.search(r'[0-9]', string) != None:
            #clean it from the alpha charecter and save it as 
            information_to_be_extracted.quantitative = re.sub(r'[^0-9-]', '',string)
            #print(information_to_be_extracted.quantitative)
            information_to_be_extracted.data_type_quan = re.sub(r'[0-9-]', '',string)
                    
    elif tag == 'VBN' or tag == 'VBD':
        information_to_be_extracted.data_type_qual = string
        
            #adjective word with qualitative data
    elif tag.startswith('JJ'):
        if any(word == string for word in quality_describing_word_list):
            information_to_be_extracted.qualitative = string
        
    elif  tag == 'DT' or tag == 'RB':
        if any(word == string for word in negativity_inducing_words_list):
            information_to_be_extracted.negative_inducing = True
            
    return information_to_be_extracted

#split sentences in a line and merge sentence in 2 or more lines.
def merge_continuous_lines_of_a_sentence_and_split_terminating(text):
    result = []
    new_line_formed = ''
    for line_count, line in enumerate(text.splitlines(), start = 1):

        if line_count >= len(text.splitlines())-2:
            next_line = ''
        else:
            next_line = text.splitlines()[line_count+1]      
        lines_splitted_with_dot = line.split('.')
        
        if len(lines_splitted_with_dot) == 1:
            new_line_formed = new_line_formed +' '+ line if new_line_formed != '' else line
        else:
            #merging back the digits like 1.1.1
            for idx, char in enumerate(lines_splitted_with_dot):
                if char.isdigit():
                    for index in range(idx+1,len(lines_splitted_with_dot)):
                        if lines_splitted_with_dot[index] == '':
                            continue
                        if lines_splitted_with_dot[index][0].isdigit():
                            lines_splitted_with_dot[idx] = lines_splitted_with_dot[idx]+'.'+lines_splitted_with_dot[index]
                            lines_splitted_with_dot[index] = ''
            
            if '' in lines_splitted_with_dot:
                lines_splitted_with_dot.remove('')
            
            for sub_idx, sub_line in enumerate(lines_splitted_with_dot, start =1):
                if sub_idx == 1:
                    new_line_formed = new_line_formed +' '+ sub_line if new_line_formed != '' else sub_line
                    result.append(new_line_formed)
                    
                elif sub_idx == len(lines_splitted_with_dot):
                    new_line_formed = sub_line
                else:
                    result.append(sub_line)
        if next_line == '':
            continue
        if next_line[0].isupper():
            result.append(new_line_formed)
            new_line_formed = ''
                
    return result

def extract_information_from_multiline_text(multi_line_text, possible_words_for_main_attribute, possible_words_for_sub_attribute, quality_describing_word_list,
                                            negativity_inducing_words_list):
    
    parsed_text_from_lines = []
    
    #seperate sentences and form the list
    seperated_sentences = merge_continuous_lines_of_a_sentence_and_split_terminating(multi_line_text)
    
    for sentence in seperated_sentences:
        clean_sentence = re.sub('[^a-zA-Z0-9-%]+', ' ', sentence.lower())
        if clean_sentence == '':
            continue
        parsed_text_from_lines.append(get_list_of_parsed_string_for_individual_line(clean_sentence))
    
    extracted_information = []
    # initiated a space string to the information carrier
    temp_information_carrier = information_ontology_predefined('')

    #explore all the parsed words 
    for parsed_line in parsed_text_from_lines:
        #init_location_information = temp_information_carrier.location
    
        #initiate new information explorer for every new_line
        information_to_be_extracted = information_ontology_predefined('')
        for parse_word in parsed_line:
            #print(parse_word.string, parse_word.tag)
            if parse_word.tag == 'NP':
                information_to_be_extracted = check_for_information_from_phrase(information_to_be_extracted, parse_word.string, possible_words_for_main_attribute,
                                                                                possible_words_for_sub_attribute, quality_describing_word_list, negativity_inducing_words_list) 
                #print(parse_word.string)  
            else:
                information_to_be_extracted = check_for_information_with_word_and_tag(information_to_be_extracted, parse_word.string, parse_word.tag,
                                                                                     quality_describing_word_list, negativity_inducing_words_list)
            
        #check if new qualitative or quantitative information is obtained            
        if information_to_be_extracted.quantitative != None or information_to_be_extracted.qualitative != None:
            if information_to_be_extracted.quantitative != None and information_to_be_extracted.qualitative != None:
                dup_information = information_to_be_extracted
                dup_information.quantitative = None
                dup_information.data_type.quan = None
                extracted_information.append(dup_information)
                information_to_be_extracted.qualitative = None
                information_to_be_extracted.data_type.qual = None            
        
            information_to_be_extracted.update(temp_information_carrier)
        
            extracted_information.append(information_to_be_extracted)
    
        temp_information_carrier.update(information_to_be_extracted)
        
    return extracted_information


def get_list_of_information_explorer_from_text_in_segmented_pages(segmented_pages_dictionary, beginning_page_number, 
                                                                  possible_words_for_main_attribute, possible_words_for_sub_attribute,
                                                                 quality_describing_word_list,negativity_inducing_words_list): 
    result = []
    
    for page_no, page in enumerate(segmented_pages_dictionary, start=1):
        if beginning_page_number <page_no:
            result.extend(extract_information_from_multiline_text(segmented_pages_dictionary[page].text, 
                                                                  possible_words_for_main_attribute, possible_words_for_sub_attribute, 
                                                                  quality_describing_word_list,negativity_inducing_words_list))
    return result


def form_dataframe_from_list_of_object(object_list):
    df = pd.DataFrame([t.__dict__ for t in object_list ])
    if 'string' in df.columns:
        df = df.drop('string',1)
    return df



