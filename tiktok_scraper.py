import re
import os
import time
import urllib.parse
import urllib
import csv
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
import math
import numpy as np
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
from base.base_scraper import BaseBot, BaseServices


class Services:
    PC = BaseServices.TIKTOK_PC.value



class TiktokBot(BaseBot):
    ROOT_URL = "https://www.tiktok.com"

    
    XPATH_LOGIN_USERNAME = ""
    XPATH_LOGIN_PASSWORD = ""

    
    # keyword XPATH
    XPATH_KEYWORD_VIDEO = "//div[@data-e2e='search_video-item']"
    XPATH_KEYWORD_VIDEO_URL = "//div[@data-e2e='search_video-item']//a"
    XPATH_KEYWORD_VIDEO_CAPTION = "//div[@data-e2e='search-card-video-caption']/h1"
    XPATH_KEYWORD_VIDEO_AUTHOR = "//p[@data-e2e='search-card-user-unique-id']"

    # Hashtag XPATH
    XPATH_HASHTAG_VIDEO_URL = "//*[@data-e2e='challenge-item']/div/div/a"
    XPATH_HASHTAG_VIDEO_CAPTION = "//*[@data-e2e='challenge-item-desc']"
    XPATH_HASHTAG_VIDEO_AUTHOR = "//p[@data-e2e='challenge-item-username']"

    # Author information
    XPATH_AUTHOR_FOLLWING_COUNT = "//*[@data-e2e='following-count']"
    XPATH_AUTHOR_FOLLOWERS_COUNT = "//*[@data-e2e='followers-count']"
    XPATH_AUTHOR_LIKES_COUNT = "//*[@data-e2e='likes-count']"
    

    def __init__(
        self, parameters, *args, **kwargs
    ):
        super(TiktokBot, self).__init__(
            parameters, *args, **kwargs
        )
        self.services = Services

    
        
    def login(self, username,password):
        time.sleep(3)

        username_field = self.driver.find_element(By.XPATH,self.XPATH_LOGIN_USERNAME)
        password_field = self.driver.find_element(By.XPATH,self.XPATH_LOGIN_PASSWORD)

        username_field.send_keys(username)
        time.sleep(self.TIME_INTERVAL_BASE)
        password_field.send_keys(password)
        time.sleep(self.TIME_INTERVAL_BASE)
        
        password_field.send_keys(Keys.RETURN)

        time.sleep(2.0)
        
 
    def fetch_author_information(self,authors):
        author_info = [] 
        for author in authors:
            url = f'{self.ROOT_URL}@{author}'
            self._get(url)
            author_followers = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.XPATH_AUTHOR_FOLLOWERS_COUNT))
            )
            author_following = self.driver.find_element(By.XPATH, self.XPATH_AUTHOR_FOLLWING_COUNT)
            author_like_count = self.driver.find_element(By.XPATH, self.XPATH_AUTHOR_FOLLWING_COUNT)
            author_info.append({
                'author_followers': author_followers.text,
                'author_following': author_following.text,
                'author_like_count': author_like_count.text
            })
        return author_info

    def fetch_post_user_hashtag(self, keyword, max_scrolls=10): 
        reels = []
        url = f'{self.ROOT_URL}/tag/{keyword}'

        self._get(url)
        
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, self.XPATH_HASHTAG_VIDEO_URL))
        )

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for i in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.TIME_INTERVAL_BASE)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        pass  

        video_urls = self.driver.find_elements(By.XPATH, self.XPATH_HASHTAG_VIDEO_URL)
        caption = self.driver.find_elements(By.XPATH, self.XPATH_HASHTAG_VIDEO_CAPTION)
        video_authors = self.driver.find_elements(By.XPATH, self.XPATH_HASHTAG_VIDEO_AUTHOR)
        for video_url, caption, video_author in zip(video_urls,caption,  video_authors):
            
            reels.append({
                'hastag': keyword,
                'url': video_url.get_attribute("href"),
                'caption': caption,
                'author': video_author.text
            })
        return reels
    
    def fetch_post_using_keyword(self, keyword, max_scrolls = 10):
        reels = []
        url = f'{self.ROOT_URL}/search/video?q={keyword}'
        self._get(url)
        

        WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, self.XPATH_KEYWORD_VIDEO))
        )

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for i in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.TIME_INTERVAL_BASE)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        video_urls = self.driver.find_elements(By.XPATH, self.XPATH_KEYWORD_VIDEO_URL)
        video_captions = self.driver.find_elements(By.XPATH, self.XPATH_KEYWORD_VIDEO_CAPTION)
        video_authors = self.driver.find_elements(By.XPATH, self.XPATH_KEYWORD_VIDEO_AUTHOR)
        
        for video_url, video_caption, video_author in zip(video_urls, video_captions, video_authors):
            reels.append({
                'keyword': keyword,
                'url': video_url.get_attribute("href"),
                'caption': video_caption.text,
                'author': video_author.text
            })
        
        return reels
    
    def find_uniq_author(reels):
        unique_authors = set(reel['author'] for reel in reels)
        unique_authors_list = list(unique_authors)
        return unique_authors_list
    

    def save_in_csv(self, file_name, data):
        if data:  
            with open(file_name, 'w', newline='') as csv_file:
                fieldnames = data[0].keys()  
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                writer.writeheader() 
                writer.writerows(data)  
        else:
            print("No data to write for hashtags.")

    def get_pages(self, service):
        self.service = service
        keyword_based_reels = []
        hashtag_based_reesl = []
        reels = []
        author_info = []
        keywords = self.parameters.get("keywords")
        hashtags = self.parameters.get("hashtags")


        # this is for witing manually solve puzzle
        self._get("https://www.tiktok.com/tag/traveltok")
        WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, self.XPATH_HASHTAG_VIDEO_URL))
        )

        for keyword in keywords:
            data = self.fetch_post_using_keyword(keyword)
            keyword_based_reels.extend(data)
        
        self.save_in_csv('reels_hashtag.csv', keyword_based_reels)

        for hashtag in hashtags:
            data = self.fetch_post_user_hashtag(hashtag)
            hashtag_based_reesl.extend(data)
        
        self.save_in_csv('reels_keyword.csv', hashtag_based_reesl)
        reels.append(hashtag)
        reels.append(keyword)

        all_uniq_author = self.find_uniq_author(reels)
        author_info = self.fetch_author_information(all_uniq_author)

        self.save_in_csv("author_info", author_info)

        


        
       



        
    

    
        
