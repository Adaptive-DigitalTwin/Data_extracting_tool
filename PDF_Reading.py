# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 17:49:57 2020

@author: msapkota
"""
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
import io
import camelot


class Segmented_Page:
    def __init__(self, name):
        self.name = name
        self.text = ''
        self.tables = []
        self.Images = []
        
class Table_in_report:
    def __init__(self, name):
        self.name = name
        self.page_number = -1
        self.data_frame = -1
        arranged_header = False

def extract_text_from_pdf(pdf_file, input_extracted_pages_dictionary):
    if input_extracted_pages_dictionary == None:
        input_extracted_pages_dictionary = {}
        
    output_extracted_pages = {}
    print('Text extraction initiated')
    with open(pdf_file, 'rb') as fp:
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        #print(type(retstr))
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        page_no = 1
        for pageNumber, page in enumerate(PDFPage.get_pages(fp)):
            if pageNumber == page_no-1:
                interpreter.process_page(page)
                data = retstr.getvalue()
                
                #giving the name for each page with pdf_name+page_no
                key = pdf_file.replace('.pdf','')+'_page_'+str(page_no)
                if not key in input_extracted_pages_dictionary or type(input_extracted_pages_dictionary[key]) is not Extracted_Page:
                    new_page = Segmented_Page(key)
                else:
                    new_page = input_extracted_pages_dictionary[key]
                #new_page.text = data.encode('utf-8')
                new_page.text = data
                
                output_extracted_pages[key] = new_page
                    #file.write(data.encode('utf-8'))
                data = ''
                retstr.truncate(0)
                retstr.seek(0)

            page_no += 1
        print('Text extraction finished')
    return output_extracted_pages

def get_table_extracted(pdf_file, input_extracted_pages_dictionary, pages_to_read):
    print('table extraction initiated')
    
    Tables_extracted = camelot.read_pdf(pdf_file, pages = pages_to_read, copy_text=['h', 'v'])
    
    for table in Tables_extracted:
        page_no = table.page
        name_for_table = 'page_'+str(page_no)+'_'+str(table.order)
        temp_table = Table_in_report(name_for_table)
        
        #get the name for extracted Page of corresponding table
        key = pdf_file.replace('.pdf','')+'_page_'+str(page_no)

        if not key in input_extracted_pages_dictionary or type(input_extracted_pages_dictionary[key]) is not Segmented_Page:
            new_page = Segmented_Page(key)
        else:
            new_page = input_extracted_pages_dictionary[key]
            
        tables_list_for_the_page = new_page.tables
        
        temp_table.page_no= page_no
        temp_table.data_frame = table.df
        
        tables_list_for_the_page.append(temp_table)
        
        new_page.tables = tables_list_for_the_page
        
        input_extracted_pages_dictionary[key] = new_page
    
    print('Table extraction finished')