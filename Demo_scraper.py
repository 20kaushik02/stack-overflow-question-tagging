"""
Any tag:
https://stackoverflow.com/questions?tab=newest&page=5&pagesize=50

possible sorting options - Newest, Active, Bounties, Unanswered, Frequent, Votes

Specific tag:
e.g compiler-errors
https://stackoverflow.com/questions/tagged/compiler-errors?tab=newest&page=2&pagesize=50

"""

#%%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import math

#%%

def tag_scrape(tag_keyword):
    url = "https://stackoverflow.com/filter/tags-for-index"
    data_obj = { 'filter': tag_keyword, 'tab': 'Name', 'fkey': 'StackExchange.options.user.fkey' }
    
    response = requests.post(url, data = data_obj)
    soup = BeautifulSoup(response.content, 'html.parser')
    tags = soup.find_all("a", class_="post-tag")
    
    tags_list = []
    for tag in tags: 
        tags_list.append(tag.text)
    
    print(f'\nFound {len(tags_list)} tag(s):\n{tags_list}')
    
    return tags_list

def question_scrape(page_count, sort_param="Newest", filter_b=False, tag_keyword=None):
    page_no = 1

    if(filter_b):
        tag_keyword = tag_keyword.replace("#", "%23")
        url = f'https://stackoverflow.com/questions/tagged/{tag_keyword}?tab={sort_param}&page={page_no}&pagesize=50'
    else:
        url = f'https://stackoverflow.com/questions?tab={sort_param}&page={page_no}&pagesize=50'
    
    response = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    qns_t = soup.find_all("div", class_="fs-body3 flex--item fl1 mr12 sm:mr0 sm:mb12")
    
    max_qns = int(re.sub('[^0-9]', "", qns_t[0].text.replace(",","")))
    max_pages = math.ceil(max_qns/50)
    page_count = min(page_count, max_pages)
    
    if(filter_b):
        print(f'\nFound {max_pages} page(s) or {max_qns} questions for tag {tag_keyword}')
        print(f'\nScraping {page_count} pages for tag {tag_keyword}')
    else:
        print(f'\nFound {max_pages} page(s) or {max_qns} questions')
        print(f'Scraping {page_count} pages')
        
    for page_no in range(1, page_count+1):
        if(filter_b):
            url = f'https://stackoverflow.com/questions/tagged/{tag_keyword}?tab={sort_param}&page={page_no}&pagesize=50'
        else:
            url = f'https://stackoverflow.com/questions?tab={sort_param}&page={page_no}&pagesize=50'
        
        resp_page = requests.get(url, allow_redirects=True)
        soup = BeautifulSoup(resp_page.content, 'html.parser')
        qns_f = soup.find_all("div", class_="summary")
        
        for qn in qns_f:
            print(qn.text)
        
def scraper():
    """
    Scraping function
    """
    print("\n----------------Stackoverflow Scraper----------------\n")
    sort_param = input("Sort questions based on - Newest (Default), Active, Bounties, Unanswered, Frequent, Votes\n>")
    sort_param = sort_param.capitalize()
    
    filter_b = ((input("Filter questions by tag [Y/n] >").capitalize()) == "Y")
    
    tag_keyword = None
    if(filter_b):
        tag_keyword = input("Enter a keyword to find all matching tags >")
        tags_list = tag_scrape(tag_keyword)
        
        page_count = int(input("Enter number of pages to scrape per tag >"))
        for tag in tags_list:
            question_scrape(page_count=page_count, sort_param=sort_param, filter_b=filter_b, tag_keyword=tag)
    else:
        page_count = int(input("Enter number of pages to scrape >"))
        question_scrape(page_count=page_count, sort_param=sort_param, filter_b=filter_b)
        
        
if __name__ == "__main__":
    scraper()