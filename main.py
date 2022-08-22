from fastapi import FastAPI, Path

import psycopg2
import json
import collections

with open(r'./keys/database.json', 'r') as f:
	database_keys = json.load(f)

database = database_keys['PostgreSQL']['database']
entry_point = database_keys['PostgreSQL']['entry_point']
port = database_keys['PostgreSQL']['port']
pswd = database_keys['PostgreSQL']['password']


print('prihlasujem sa do DB')
conn = psycopg2.connect(database=database, user='postgres', password=pswd, host=entry_point, port=port)
c = conn.cursor()
print('prihlaseny...')

description = '''
ProduktyApp 🄯 API ti pomôže vytvoriť veľké a pekné veci. 🚀\n
vizualizácia dát, nákupné rozhodnutia, odhad budúcich zliav a mnohé iné.

### TODO:
* **čítať dáta** - ✅
* **vpisovať dáta** - ❌

'''
version = '0.1.0'
contact = {
		'name': 'Marcel Suleiman',
		'url': 'https://www.linkedin.com/in/marcel-suleiman/',
		'email': 'marcelsuleiman@gmail.com',
		'tel': '+421 951 022 141'
		}

tags_metadata = [
	{
		"name": "volania EAN",
		"description": "Requesty založené na hladaní podla EAN kódu produktu.",
	},
	{
		"name": "volania Meno",
		"description": "Requesty založené na hladaní podla mena / názvu produktu.",
	},
	{
		"name": "Žolík",
		"description": "Requesty fungujú na báze ILIKE alebo LIKE. Vždy vkladaj iba jedno slovo alebo výraz",
	},
	{
		"name": "__DEVS",
		"description": "Občania rozíďte sa! Tu už nie je nič k videniu."
	}
]

vocabulary = {
		0: 'date',
		1: 'product_name',
		2: 'price_per_pack',
		3: 'price_per_unit',
		4: 'unit_of_measure',
		5: 'discount_verbose',
		6: 'dicount_percentage',
		7: 'old_price',
		8: 'department_l1',
		9: 'department_l2',
		10: 'department_l3',
		11: 'plu',
		12: 'category',
		13: 'ean'
	}

def create_output_data(note: tuple, data: dict, header: str) -> dict:
	data[header] = {}
	for i in range(len(note)):
		data[header][vocabulary[i]] = note[i]
		data = collections.OrderedDict(sorted(data.items()))
	
	return data


app = FastAPI(
		title='ProduktyApp 🄯 API',
		description=description,
		version=version,
		contact=contact
	)


@app.get('/about')
def about():
	'''
	Vstupný parameter nie je žiadny.\n
	Vráti základné údaje o API.
	'''
	return {
		'Data': 'About',
		'Version': version,
		'Relase': 'Test mode',
		'Database': 'PostgreSQL 14',
		'Author': 
			{
			'name': 'Marcel Suleiman',
			'link': 'https://www.linkedin.com/in/marcel-suleiman/',
			'mail': 'marcelsuleiman@gmail.com',
			'tel': '+421 951 022 141'
			}
		}

@app.get('/get-item-by-ean/{date}', tags=['volania EAN'])
def get_item_by_ean(date: str, ean: str):
	'''
	Funkcia vracia element na základe zadaného EAN kódu produktu k zadanému dňu.

	### Povinné:
	@param date: Dátum ku ktorému očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param ean: EAN kod produktu\n

	return: dict
	'''

	c.execute('SELECT * FROM product WHERE date = %s AND ean = %s;', (date, ean))

	results = c.fetchall()

	data = {}
	if results:
		for note in results:
			ean = note[13]
			data = create_output_data(note, data, header = ean)

		return data

	else:
		return {'Product': 'Not found'}

@app.get('/get-item-by-ean-between/{date_start}/{date_end}', tags=['volania EAN'])
def get_item_by_ean_between(date_start: str, date_end: str, ean: str):
	'''
	Funkcia vracia produkt pre každý deň samostatne v danom rozsahu dátumov.

	### Povinné:
	@param date_start: Dátum od ktorého očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param date_end: Dátum ku ktorému očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param ean: EAN kod produktu\n

	return: dict
	'''

	c.execute('SELECT * FROM product WHERE date BETWEEN %s AND %s AND ean = %s;', (date_start, date_end, ean))

	results = c.fetchall()

	data = {}
	if results:
		for note in results:
			date = note[0]
			data = create_output_data(note, data, header = date)

		return data

	else:
		return {'Product': 'Not found'}

@app.get('/get-item-by-name/{date}', tags=['volania Meno'])
def get_item_by_name(date: str, name: str):
	'''
	Funkcia vracia element na základe zadaného mena produktu k zadanému dňu.

	### Povinné:
	@param date: Dátum ku ktorému očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param name: Meno (presné) produktu\n
	pomôcka: endpoint /get-item-like\n

	return: dict
	'''

	c.execute('SELECT * FROM product WHERE date = %s AND product_name = %s;', (date, name))

	results = c.fetchall()
	
	data = {}
	if results:
		for note in results:
			product_name = note[1]
			data = create_output_data(note, data, header = product_name)
			
		return data

	else:
		return {'Product': 'Not found'}

@app.get('/get-item-by-name-between/{date_start}/{date_end}', tags=['volania Meno'])
def get_item_by_name_between(date_start: str, date_end: str, name: str):
	'''
	Funkcia vracia produkt pre každý deň samostatne v danom rozsahu dátumov.

	### Povinné:
	@param date_start: Dátum od ktorého očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param date_end: Dátum ku ktorému očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param name: Meno (presne) produktu\n
	pomocka: endpoint /get-item-like\n

	return: dict
	'''

	c.execute('SELECT * FROM product WHERE date BETWEEN %s AND %s AND product_name = %s;', (date_start, date_end, name))

	results = c.fetchall()

	data = {}
	if results:
		for note in results:
			date = note[0]
			data = create_output_data(note, data, header = date)

		return data

	else:
		return {'Product': 'Not found'}

@app.get('/get-item-by-ean/compare/{date_start}/{date_end}', tags=['volania EAN'])
def get_item_by_name_compare(date_start: str, date_end: str, ean: str):
	'''
	Funkcia vracia produkt pre každý deň samostatne ako porovnanie 2 zadaných dátumov.\n
	V prípade že sa vráti iba 1 alebo 0 elementov, v daných dňoch nebol tovar dostupný a treba zvoliť iný deň\n
	(ideálne skúsiť +/- 1d)

	### Povinné:
	@param date_start: Dátum od ktorého očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param date_end: Dátum ku ktorému očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param ean: EAN kód produktu\n

	return: dict
	'''

	c.execute('SELECT * FROM product WHERE (date = %s OR date = %s) AND ean = %s;', (date_start, date_end, ean))

	results = c.fetchall()

	data = {}
	if results:
		for note in results:
			date = note[0]
			data = create_output_data(note, data, header = date)

		return data

	else:
		return {'Product': 'Not found'}

@app.get('/get-item-by-name/compare/{date_start}/{date_end}', tags=['volania Meno'])
def get_item_by_name_compare(date_start: str, date_end: str, name: str):
	'''
	Funkcia vracia produkt pre každý deň samostatne ako porovnanie 2 zadaných dátumov.\n
	V prípade že sa vráti iba 1 alebo 0 elementov, v daných dňoch nebol tovar dostupný a treba zvoliť iný deň\n
	(ideálne skúsiť +/- 1d)\n

	### Povinné:
	@param date_start: Dátum od ktorého očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param date_end: Dátum ku ktorému očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param name: Meno (presné) produktu\n
	pomôcka: endpoint /get-item-like\n

	return: dict
	'''

	c.execute('SELECT * FROM product WHERE (date = %s OR date = %s) AND product_name = %s;', (date_start, date_end, name))

	results = c.fetchall()

	data = {}
	if results:
		for note in results:
			date = note[0]
			data = create_output_data(note, data, header = date)

		return data

	else:
		return {'Product': 'Not found'}

@app.get('/get-all-items/{date}', tags=["__DEVS"])
def get_all_items_for_date(date: str, token:str, department: str = None):
	'''
	Funkcia vracia všetky produkty k zadanému dňu.

	### Povinné:
	@param date: Dátum ku ktorému očakávaš výsledok v tvare 'YYYY-MM-DD'\n
	@param token: API token - momentálne dostupný iba pre úzku skupinu ľudí.\n
	ochrana pred vykrádaním DB na pár requestov. Vyžiadať sa dá iba mailom alebo osobne - problém je, že maily nečítam a dvere neotváram :D GL.

	### Nepovinné:
	@department: sekcia, slúži na odfiltrovanie nežiadúchich výsledkov
	príklad: 'pecivo' vráti iba tie podukty z daného dňa, ktoré spadajú do sekcie pečivo

	dostupné sekcie:
	* ovocie-a-zelenina
	* mliecne-vyrobky-a-vajcia
	* pecivo
	* maso-ryby-a-lahodky
	* trvanlive-potraviny
	* specialna-a-zdrava-vyziva
	* mrazene-potraviny
	* napoje
	* alkohol
	* starostlivost-o-domacnost
	* zdravie-a-krasa
	* starostlivost-o-dieta
	* chovateske-potreby
	* domov-a-zabava

	return: dict
	'''

	with open(r'./keys/token.json', 'r') as f:
		keys = json.load(f)

	tokens = keys['tokens']

	if token not in tokens:
		return {"msg": "Zlý token."}

	if department == None:
		c.execute('SELECT * FROM product WHERE date = %s ;', (date,))
	else:
		c.execute('SELECT * FROM product WHERE date = %s AND department_l1 = %s;', (date, department))

	results = c.fetchall()

	data = {}
	if results:
		for note in results:
			product_name = note[1]
			data = create_output_data(note, data, header = product_name)

		return data

	else:
		return {'Product': 'Not found'}

@app.get('/get-items-like', tags=['Žolík'])
def get_item_like(pseudo_name: str, department: str = None):
	'''
	Funkcia vracia všetky zhody k nekompletnému menu produku za celé sledované obdobie.

	### Povinné:
	@pseudo_name: neúplný názov podľa ktorého sa hľadajú zhody ako napríklad mlieko / olej / múka ...

	### Nepovinné:
	@department: sekcia, slúži na odfiltrovanie nežiadúchich výsledkov
	príklad: mlieko, vráti Mlieko Polotučné ale aj telové mlieko

	dostupné sekcie:
	* ovocie-a-zelenina
	* mliecne-vyrobky-a-vajcia
	* pecivo
	* maso-ryby-a-lahodky
	* trvanlive-potraviny
	* specialna-a-zdrava-vyziva
	* mrazene-potraviny
	* napoje
	* alkohol
	* starostlivost-o-domacnost
	* zdravie-a-krasa
	* starostlivost-o-dieta
	* chovateske-potreby
	* domov-a-zabava

	## Hint:
	Používaj interpunkciu.\n
	Nepoužívaj viac slov - iba ak si si istý že to máš správne
	príklad: "Rajo maslo" nevráti nič, ale "Rajo Tradičné maslo" už hej.\n

	return: dict
	'''

	response_limit = 20
	if department == None:
		c.execute(f"SELECT * FROM product WHERE product_name ILIKE '%{pseudo_name}%' LIMIT {response_limit};")
	else:
		c.execute(f"SELECT * FROM product WHERE product_name ILIKE '%{pseudo_name}%' AND department_l1 = '{department}' LIMIT {response_limit};")

	results = c.fetchall()

	data = {}
	if results:
		for note in results:
			product_name = note[1]
			data = create_output_data(note, data, header = product_name)

		return data

	else:
		return {'Product': 'Not found'}
