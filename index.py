''' This script is responsible for scraping the recipes from the website '''
from random import randint
from time import sleep
import os
import logging
from bs4 import BeautifulSoup
import cloudscraper
from dotenv import load_dotenv
from db import put_item, get_item, get_all_items
from ai import nlp_entities

# Configure logging to write to a file
logging.basicConfig(filename='logs.log', level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()


def generate_random_sleep():
    '''Generate a random sleep time between 0.5 and 3.5 seconds'''

    seconds = randint(5, 35) / 10
    print('')
    print(f'Sleeping for {seconds} seconds...')
    sleep(seconds)


def get_page_urls(page):
    '''Get all the recipes urls for a certain page'''

    base_url = os.getenv('BASE_URL')
    info = scraper.get(f"{base_url}/receitas?page={page}")
    soup = BeautifulSoup(info.text, "html.parser")

    page_urls = []

    for url in soup.select('h2.card-title > a.card-link'):
        page_urls.append(url.get('href'))

    return page_urls


def scrape_recipe(path):
    '''Scrape a recipe from a given url'''

    generate_random_sleep()

    base_url = os.getenv('BASE_URL')
    url = f"{base_url}{path}"

    if not path.startswith('/receita/'):
        url = path

    info = scraper.get(url)
    soup = BeautifulSoup(info.text, "html.parser")

    title = soup.select_one('header > span.u-title-page.u-align-center').text
    stars = soup.select_one('span.rating-grade > span').text

    infos = []
    for info in soup.select('div.recipe-info-item'):
        infos.append(info.text)

    description = soup.select_one(
        'div.recipe-chapo > div.is-wysiwyg').text

    portion_size = soup.select_one(
        'section.recipe-ingredients > header > h2').text[14:-1]

    ingredients = []

    for ingredient_section in soup.select('section.recipe-ingredients > section'):
        section_title = ingredient_section.select_one(
            'h3.recipe-ingredients-subtitle')

        if section_title is not None:
            section_title = section_title.text
        else:
            section_title = 'Ingredientes'

        ingredients_section = {
            'title': section_title,
            'ingredients': []
        }

        for ingredient in ingredient_section.select('li.recipe-ingredients-item > span.recipe-ingredients-item-label'):
            ingredients_section['ingredients'].append(ingredient.text)

        ingredients.append(ingredients_section)

    preparation_steps = {}
    step_title_text = 'default'
    for step in soup.select('li.recipe-steps-item'):
        step_title = step.select_one('h3.recipe-steps-title')

        position_element = step.select_one('span.recipe-steps-position')

        step_description = step.select_one('div.recipe-steps-text').text

        if step_title is not None:
            step_title_text = step_title.text

        if step_title_text not in preparation_steps:
            preparation_steps[step_title_text] = {'steps': []}

        preparation_steps[step_title_text]['steps'].append({
            'step': position_element.text if position_element is not None else 0,
            'text': step_description
        })

    tags = []
    for tag in soup.select('section.recipe-section > ul > li > a'):
        tags.append(tag.text)

    recipe = {
        'key': path,
        'stars': stars,
        'title': title,
        'infos': infos,
        'description': description,
        'portion_size': portion_size,
        'ingredients': ingredients,
        'preparation_steps': preparation_steps,
        'tags': tags
    }

    print(f'Saving recipe: {url} on DB...')
    put_item('recipes', recipe)


if __name__ == "__main__":
    scraper = cloudscraper.create_scraper()

    # page = 11
    # while page <= 20:
    #     print(f'Getting page {page}...')
    #     try:
    #         page_urls = get_page_urls(page)
    #     except Exception as e:
    #         logging.error(e)
    #         continue

    #     for url in page_urls:
    #         recipe = get_item('recipes', url)

    #         if recipe is not None:
    #             print(f'Recipe: {url} already exists on DB...')
    #             logging.info("Recipe: %s already exists on DB...", url)

    #             continue

    #         scrape_recipe(url)

    #     page += 1

    # get all recipes from DB
    recipes = get_all_items('recipes')

    for recipe in recipes:
        ingredients = recipe['ingredients']
        nlp_entities(ingredients)
