# -*- coding: utf-8 -*-
"""api.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1c9Jy3X1FWeok2kbGnFyG2T8-lIVQz7jJ
""" 
## importation des librairies
import requests
from bs4 import BeautifulSoup
from flask import Flask,jsonify
app = Flask(__name__)       ## créer une instance de l'application Flask pour la création d'API

def get_article_content(article_url):
    response = requests.get(article_url) ## envoie une requête HTTP get à l'url
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        ## recherche dans le contenu HTML de la page le premier élément <div> avec la classe "entry-meta", puis trouve le premier élément <span> à l'intérieur et récupère le texte associé
        date_published = soup.find("div", class_="entry-meta").find("span").get_text(strip=True)

        ## de même que pour la date de publication, pour la description de l'auteur
        author_description = soup.find("span", class_="author-name")
        author_description_text = author_description.get_text(strip=True) if author_description else "Auteur non disponible"

        ## de même pour le contenu. On exclu les articles pour lesquels le contenu n'existe pas ou n'est pas récupérable
        content_div = soup.find("div", class_="entry-content")
        if content_div:
            paragraphs = content_div.find_all("p")
            content_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
            if content_text: 
                return {
                    "date_published": date_published,
                    "author_description": author_description_text,
                    "content": content_text
                }
        return None
    else:
        return None

def get_articles_from_page(url, number_of_articles=5):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        articles = []
        for article_header in soup.find_all("h3", class_="entry-title"): ## fonction recherche tous les éléments <h3> ayant la classe "entry-title", soit les titres des articles
            if len(articles) >= 10:  
                break
            article_link = article_header.find("a")
            if article_link:
                title = article_link.text.strip()
                article_url = article_link['href']
                article_content = get_article_content(article_url) ## utilise la précédente fonction pour récuperer le contenu des articles via leur url
                ## Si le contenu de l'article est récupéré, les informations de l'article sont stockées dans un dictionnaire et ajoutées à la liste "articles"
                if article_content:  
                    articles.append({
                        "title": title,
                        "url": article_url,
                        "date_published": article_content["date_published"],
                        "author_description": article_content["author_description"],
                        "content": article_content["content"]
                    })
        return articles
    else:
        print("Échec de la récupération de la page.")
        return []

url = "https://www.actuia.com/actualite/"     ##url du site ActuIA duquel nous extrayions les articles

articles = get_articles_from_page(url)
for article in articles:     ## renvoie les principales caractéristiques des articles
    print("Titre:", article["title"])
    print("Date de publication:", article["date_published"])
    print("URL:", article["url"])
    print("Auteur:", article["author_description"])
    print('Contenu:', article['content'])

## Premier endpoint qui récupère les données d'un nombre d'article
@app.route('/get_data', methods=['GET'])
def get_data():
    url = "https://www.actuia.com/actualite/"
    articles = get_articles_from_page(url, 5)
    return jsonify(articles)


## Deuxième endpoint qui affiche des informations sur les articles, comme son numéro, titre, date de publication, url
@app.route('/articles', methods=['GET'])
def articles():
    url = "https://www.actuia.com/actualite/"
    articles = get_articles_from_page(url, 5)
    articles_info = [{"number": idx+1, "title": article["title"], "date_published": article["date_published"], "url": article["url"]} for idx, article in enumerate(articles)]
    return jsonify(articles_info)

## Troisième endpoint 
@app.route('/article/<int:number>', methods=['GET'])
def article(number):
    url = "https://www.actuia.com/actualite/"
    articles = get_articles_from_page(url)
    
    ## boucle qui renvoie un fichier json avec titre et contenu si le numero de l'article est dans le nombre d'article total
    if 1 <= number <= len(articles):
        article = articles[number-1]
        return jsonify({"title": article["title"], "content": article["content"]})
    else:
        return jsonify({"error": "Article not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
