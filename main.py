# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 17:39:35 2020

@author: msapkota
"""

from PDF_Reading import *
from Filtering_and_preprocessing import *
from NLP_and_data_exploration import *
import pickle
import os

if __name__ == "__main__":
    
    # Give file location
    pdf_file_with_path = 'Input_Output_Files/SOUTH_BUO_ReportV2.pdf'
        
    extracted_pickle_file_name_with_path = '{}_segmented_pages.pickle'.format(pdf_file_with_path.replace('.pdf',''))
    if not os.path.exists(extracted_pickle_file_name_with_path):
        extracted_segmented_pages = extract_text_from_pdf(pdf_file_with_path, None)
        get_table_extracted(pdf_file_with_path, extracted_segmented_pages, 'all')
        
        with open(extracted_pickle_file_name_with_path, 'wb') as fp:
            pickle.dump(extracted_segmented_pages, fp)
    
    else:
        with open(extracted_pickle_file_name_with_path,'rb') as fp:
            extracted_segmented_pages = pickle.load(fp)
    
    #the input is the segmented pages and the error 
    filtered_and_pre_processed_pages = filtering_and_preprocessing_pages(extracted_segmented_pages, -1)
    
    
    location_finding_strings = ['equipment description','location']
    location_available = extract_all_elements_from_columns_related_to_key_word(filtered_and_pre_processed_pages,
                                                                               location_finding_strings)
    
    #give some_location_list-if_needed 
    #manually_feeding_locations_name = []
    #location_available = location_available.extend(manually_feeding_locations_name)
        
    quality_describing_words = ['good', 'bad', 'critical', 'satisfactory']
    
    negative_directional_words = ['no', 'not', 'negative']
    
    sub_parts_string_list = ['the associated anode', 'the anode', 'the sacrificial anode', 'east', 'west', 
                             'associated', 'connector tube', 'the connector', 'the bracket']
    
    
    informations_from_text_part_list = get_list_of_information_explorer_from_text_in_segmented_pages(filtered_and_pre_processed_pages, 17, 
                                                                                                 location_available,sub_parts_string_list,
                                                                                                 quality_describing_words,negative_directional_words)
    
    information_from_text_dataframe = form_dataframe_from_list_of_object(informations_from_text_part_list)
    
    key_list_for_tables_of_interest = ['cp', 'potential', 'mV']
    
    information_from_tables_with_keywords = extract_informations_from_tables(filtered_and_pre_processed_pages, 
                                                                      key_list_for_tables_of_interest)
    
    dataframe_from_tables_of_interest = form_dataframe_from_list_of_object(information_from_tables_with_keywords)
    
    #print(dataframe_from_tables_of_interest)
    
    #give a folder name where we want to save the output excel(csv) files
    output_folder_for_tables_of_interest = '{}_tables_extracted.csv'.format(pdf_file_with_path.replace('.pdf',''))
    dataframe_from_tables_of_interest.to_csv(output_folder_for_tables_of_interest)
    
    
    output_folder_for_information_from_text = '{}_information_from_text.csv'.format(pdf_file_with_path.replace('.pdf',''))
    information_from_text_dataframe.to_csv(output_folder_for_information_from_text)
    
    #export individual table as well
    path = '{}_tables'.format(pdf_file_with_path.replace('.pdf',''))
    if not os.path.exists(path):
        os.mkdir(path)
    for table in get_tables_list_with_related_term(filtered_and_pre_processed_pages, key_list_for_tables_of_interest):
        name_and_path = '{}/{}.csv'.format(path, table.name)
        table.data_frame.to_csv(name_and_path)
