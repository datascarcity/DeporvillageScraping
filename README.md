# DeporvillageScraping
# PRA1
This repository contains the code with the solution of the Práctica 1 - Web Scraping.
It navigates and scrapes all the bikes from the deporvillage.com website, the code uses scrapy, beautifulsoap and selenium.
The main steps are:

* Navigates all the pages with the products (bikes) starting from https://www.deporvillage.com/bicicletas and following this page numeration pattern https://www.deporvillage.com/bicicletas?p=2
* For each page collects all the links to the pages of a single bike and saves them in a list
* Loops trhough the address in the list passing the link to the scraper
* The scraper collects the information about the bike (price, model, technical info, etc.)
* The scraper downloads the images and saves them in a separate folder for each bike
* The main program finally saves the dataset in a json file

## Using the program
### Steps to run main.py

1. ```cd ./source/```
2. ```pip install -r requirements.txt```
3. ```python3 ./main.py```

### Program Output
The program will generate the following output:
1. deporvillage_bicicletas_date.json where date is the date of the download.
This file contains all the information that has been scraped, the structure of the information might vary slightly depending on each bike but generally the strucutre is the following:
+ identificador del producto (product ID, part of the URL) {

	+ Nombre Producto (product name)
	+ Precio Original (original price with no discount)
	+ Precio Venta (retail price with discount)
	+ Marca (brand)
	+ Breadcrumb (products category)
	+ Tags
	+ Estrellas (stars rating)
	+ Descripción (description)
	 From this point the information might vary slightly but generally contains: Talla, Peso, Cuadro, Horquilla, Cambio, Manetas de cambio, Bielas y platos, Cassette, Cadena, Frenos, Neumáticos, Manillar, Potencia, Sillín, Tija, Pedales, etc.
	+ Datetime (of the scraping)

}
2. the /img directory, with a subdirectory for each product
The name of the subdirectory is the product ID (idendificador del producto) and each folder contains the pictures available for each product.

## DOI en Zenodo

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7855025.svg)](https://doi.org/10.5281/zenodo.7855025)


## License

CC0 1.0 Universal

